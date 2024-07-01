'''
This script can be used to check cpu and memory resource utilization 
of a vSphere with Tanzu Supervisor Kubernetes cluster.
'''

import json
import argparse
from prettytable import PrettyTable
from kubernetes import client, config
from kubernetes.utils.quantity import parse_quantity


def load_kubeconfig(cluster):
    """
    Load kubeconfig with the selected context.
    """
    config.load_kube_config(context=cluster)
    v1 = client.CoreV1Api()
    return v1.list_node(_preload_content=False)


def k8s_node_utilization(
    cpu_capacity, cpu_allocatable, memory_capacity, memory_allocatable
):
    """
    This function calculates and returns K8s cluster node cpu and memory utilization.
    """
    cpu_utilzation = round(((cpu_capacity - cpu_allocatable) / cpu_capacity) * 100)
    memory_utilization = round(
        (
            (parse_quantity(memory_capacity) - parse_quantity(memory_allocatable))
            / parse_quantity(memory_capacity)
        )
        * 100
    )
    return cpu_utilzation, memory_utilization


def k8s_cluster_utilization(
    cluster_cpu_total_utilization, cluster_memory_total_utilization, cluster_agent_count
):
    """
    This function calculates and returns cluster cpu and memory utilization.
    """
    cluster_cpu_utilization = round(cluster_cpu_total_utilization / cluster_agent_count)
    cluster_memory_utilization = round(
        cluster_memory_total_utilization / cluster_agent_count
    )
    return cluster_cpu_utilization, cluster_memory_utilization


def utilization(cluster, cluster_utilization_table):
    """
    This function takes cluster name and cluster_utilization_table as input.
    Switch to the cluster context.
    Collects and returns node_utilization_table, cluster_utilization_table.
    """
    print(f"\n [INFO] Collecting resource utilization details from {cluster}")
    get_nodes_info = load_kubeconfig(cluster)
    get_nodes_dict = json.loads(get_nodes_info.data)

    node_utilization_table = PrettyTable(
        [
            "cluster_name",
            "node_name",
            "cpu_allocatable",
            "cpu_capacity",
            "memory_allocatable",
            "memory_capacity",
            "% cpu_allocated",
            "% memory_allocated",
        ]
    )

    cluster_cpu_total_utilization = 0
    cluster_memory_total_utilization = 0
    cluster_agent_count = 0

    for each_node in get_nodes_dict["items"]:
        node_name = each_node["metadata"]["name"]
        cpu_capacity = int(each_node["status"]["capacity"]["cpu"])
        cpu_allocatable = int(each_node["status"]["allocatable"]["cpu"])
        memory_capacity = each_node["status"]["capacity"]["memory"]
        memory_allocatable = each_node["status"]["allocatable"]["memory"]

        cpu_utilzation, memory_utilization = k8s_node_utilization(
            cpu_capacity, cpu_allocatable, memory_capacity, memory_allocatable
        )

        node_utilization_table.add_row(
            [
                cluster,
                node_name,
                cpu_allocatable,
                cpu_capacity,
                memory_allocatable,
                memory_capacity,
                cpu_utilzation,
                memory_utilization,
            ]
        )

        # Check whether the node is worker/ agent
        # if each_node["status"]["nodeInfo"]["operatingSystem"] == "ESXi":

        if (
            not "node-role.kubernetes.io/control-plane"
            in each_node["metadata"]["labels"]
        ):
            cluster_cpu_total_utilization += cpu_utilzation
            cluster_memory_total_utilization += memory_utilization
            cluster_agent_count += 1

    cluster_cpu_utilization, cluster_memory_utilization = k8s_cluster_utilization(
        cluster_cpu_total_utilization,
        cluster_memory_total_utilization,
        cluster_agent_count,
    )

    cluster_utilization_table.add_row(
        [
            cluster,
            cluster_cpu_utilization,
            cluster_memory_utilization,
        ]
    )

    return node_utilization_table, cluster_utilization_table


def main():
    """
    Usage: kubectl-util --detailed --context sc2-05-vc46
    This invokes utilization function for a given WCP cluster.
    Resource allocatable and capacity details are obtained from 'v1.list_node()' output.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--context", required=False, help="Kubernetes context name")
    parser.add_argument("--detailed", action="store_true")

    args = parser.parse_args()
    context = args.context

    cluster_utilization_table = PrettyTable(
        [
            "cluster_name",
            "% average_cluster_cpu_allocated",
            "% average_cluster_memory_allocated",
        ]
    )

    contexts, active_context = config.list_kube_config_contexts()

    if not context:
        active_context = active_context["name"]
    else:
        active_context = context

    node_utilization_table, cluster_utilization_table = utilization(
        active_context, cluster_utilization_table
    )
    if args.detailed:
        print(node_utilization_table)

    print("\n ***** Average cluster utilization summary ***** \n")
    print(cluster_utilization_table)


if __name__ == "__main__":
    main()
