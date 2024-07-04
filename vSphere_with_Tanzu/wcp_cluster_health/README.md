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