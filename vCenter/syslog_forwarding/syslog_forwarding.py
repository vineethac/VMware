'''
Script to get, set, and test syslog forwarding configuration in vCenter server.
'''

import json
import getpass
import argparse
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class Syslog():
    """
    Syslog class and methods.
    """
    def get_syslog_forwarding(self, vc: str, auth_username: str, auth_password: str) -> None:
        """
        This function invokes VCSA rest api and prints the syslog forwarding hosts configured on it.
        """
        r = requests.get(
            f"https://{vc}:5480/rest/appliance/logging/forwarding",
            auth=(auth_username, auth_password),
            verify=False, timeout=60
        )

        result_dict = r.json()
        print(f"VCSA: {vc} \n")

        for each_syslog_host in result_dict["value"]:
            print(f"{each_syslog_host}")
        print("----------------------------------------------------------\n")


    def test_syslog_forwarding(self, vc: str, auth_username: str, auth_password: str) -> None:
        """
        This function invokes VCSA rest api and prints the test result of syslog forwarding hosts 
        configured on it.
        """
        r = requests.post(
            f"https://{vc}:5480/rest/appliance/logging/forwarding?action=test",
            auth=(auth_username, auth_password),
            verify=False,
            json={"send_test_message": "false"}, timeout=60
        )

        test_result_dict = r.json()
        print(f"VCSA: {vc} \n")

        for each_syslog_host in test_result_dict["value"]:
            print(f"{each_syslog_host}")
        print("----------------------------------------------------------\n")


    def set_syslog_forwarding(self, vc: str, auth_username: str, auth_password: str,
                              cfg_list: dict) -> None:
        """
        This function invokes VCSA rest api, sets syslog forwarding remote host config on VCSA, 
        and prints response status code.
        """
        r = requests.put(
            f"https://{vc}:5480/rest/appliance/logging/forwarding",
            auth=(auth_username, auth_password),
            verify=False,
            json=cfg_list, timeout=60
        )

        print(f"VCSA: {vc}")
        print(f"Response status code: {r.status_code}")
        print("----------------------------------------------------------\n")


def read_config_file() -> dict:
    """
    This function reads syslog forwarding remote host info from the config file.
    """
    filename = "syslog.config"
    with open(filename) as file:
        data = file.read()
        config = json.loads(data)
    return config


def main():
    """
    Overview: This script will get/ test/ set syslog forwarding hosts configured 
    on a given list of VCSAs.
    Usage: python3 syslog_forwarding.py --vcsa=sc2-01-vc16,sc2-01-vc17 --username=root --action=get
    """

    parser = argparse.ArgumentParser()
    parser.add_argument("--vcsa", required=True, help="vCenter server")
    parser.add_argument("--username", required=True, help="vCenter server username")
    parser.add_argument("--password", required=False, type=str, help="password")
    parser.add_argument(
        "--action",
        required=True,
        help="get or test syslog forwarding config",
        choices=["get", "test", "set"],
    )

    args = parser.parse_args()
    all_vcsa = args.vcsa
    auth_username = args.username
    if not args.password:
        auth_password = getpass.getpass(prompt="Enter password: ")
    else:
        auth_password = args.password

    vc_list = all_vcsa.split(",")

    syslog = Syslog()

    print("\n*** Syslog forwarding configuration on VCSA appliance ***\n")

    if args.action == "get":
        for vc in vc_list:
            syslog.get_syslog_forwarding(vc, auth_username, auth_password)

    elif args.action == "test":
        for vc in vc_list:
            syslog.test_syslog_forwarding(vc, auth_username, auth_password)

    elif args.action == "set":
        # read config file
        config = read_config_file()
        for vc in vc_list:
            syslog.set_syslog_forwarding(vc, auth_username, auth_password, config[vc])


if __name__ == "__main__":
    main()
