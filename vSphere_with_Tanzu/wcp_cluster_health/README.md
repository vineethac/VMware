# Overview
Script to verify the health of WCP/ supervisor cluster.

```
❯ python3 wcp_cluster_health.py --vcsa=wdc-08-vc04.xxxxxxx.com --vuser=administrator@vsphere.local
Enter adm password:
2024-07-04 14:53:46 C02F82H9MD6M root[75781] INFO Validating supervisor cluster status
2024-07-04 14:53:46 C02F82H9MD6M root[75781] INFO Supervisor cluster: wdc-08-vc04c01
2024-07-04 14:53:46 C02F82H9MD6M root[75781] INFO Supervisor cluster config_status: RUNNING
2024-07-04 14:53:46 C02F82H9MD6M root[75781] INFO Supervisor cluster kubernetes_status: WARNING
2024-07-04 14:53:46 C02F82H9MD6M root[75781] INFO ---Supervisor cluster is HEALTHY---
❯ 
```

# WCP cluster health API attributes
Here we are considering mainly two attributes to determine whether the WCP/ Supervisor cluster is healthy or not.  
* [`config_status`](https://developer.broadcom.com/xapis/vsphere-automation-api/latest/vcenter/data-structures/NamespaceManagement_Clusters_ConfigStatus/) - If all healthy, value of this should be `RUNNING`.
* [`kubernetes_status`](https://developer.broadcom.com/xapis/vsphere-automation-api/latest/vcenter/data-structures/NamespaceManagement_Clusters_KubernetesStatus/) - If all healthy, vaule of this should be `READY`.

When some of the system pods are not running, the `kubernetes_status` will be in `WARNING`. In this script, if the `config_status` is `RUNNING` and `kubernetes_status` is `READY` or `WARNING`, the supervisor cluster is considered healthy.

# Slack notification
* Function call to the `slack_post()` function is commented now.
* If you already have a slack app configured, then you can set and export the environment variable `SLACK_API_TOKEN`.
* You can also provide a Channel ID of the slack channel to which the alerts should be posted.

