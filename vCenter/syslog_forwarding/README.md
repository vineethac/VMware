# Overview
This script can be used to get/ test/ set syslog forwarding configuration for a given list of VCSAs.

# Get syslog forwarding 
```
python3 syslog_forwarding.py --vcsa=vcenter01,vcenter02,vcenter03 --username=root --action=get 
```
# Test syslog forwarding 
```
python3 syslog_forwarding.py --vcsa=vcenter01,vcenter02,vcenter03 --username=root --action=test
```
# Set syslog forwarding 
Note: Desired syslog forwarding config for all generic Calatrava VCs are pre-defined in syslog.config file.  

Example to set the desired syslog forwarding config on wdc-08-vc04 and wdc-08-vc05:  
```
python3 syslog_forwarding.py --vcsa=vcenter01,vcenter02 --username=root --action=set 

```
# syslog.config file
* Make sure you edit this config file and update with your vCenter server names, and the respective syslog forwarding configurations including the hostname, port, and protocol for each vCenter server.
