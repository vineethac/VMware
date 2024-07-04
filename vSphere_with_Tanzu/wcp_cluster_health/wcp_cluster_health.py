'''
Script to verify the health of WCP/ supervisor cluster.
'''

import argparse
import getpass
import logging
import os
import coloredlogs
import requests
from slack import WebClient
from slack.errors import SlackApiError

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Slack alert channel ID
CH_ID = "XXXXXXXXX"

def slack_post(slack_message, channel_id=CH_ID):
    """
    This function sends message to slack channel.
    """
    # Env varibale SLACK_API_TOKEN
    client = WebClient(token=os.environ["SLACK_API_TOKEN"])

    try:
        # Call the conversations.list method using the WebClient
        logging.info(f"Sending slack message to channel {CH_ID}.")
        client.chat_postMessage(
            channel=channel_id,
            blocks=[
                dict(type="section", text={"type": "mrkdwn", "text": slack_message})
            ],
        )
    except SlackApiError as e:
        logging.error(
            'While trying to send message: "\n{}\n"\nGot an error: {}'.format(
                slack_message, e.response["error"]
            )
        )
        logging.error("Unable to send slack message")


def verify_wcp_cluster_health(vcsa, result, pipeline):
    """
    Verifies supervisor cluster health from the api response, and 
    sends slack message if not healthy.
    """
    health = True
    logging.info("Validating supervisor cluster status")
    logging.info(f"Supervisor cluster: {result[0]['cluster_name']}")
    logging.info(f"Supervisor cluster config_status: {result[0]['config_status']}")
    logging.info(
        f"Supervisor cluster kubernetes_status: {result[0]['kubernetes_status']}"
    )

    try:
        assert (
            result[0]["config_status"] == "RUNNING"
        ), "Supervisor cluster config_status is NOT RUNNING"
        assert (
            result[0]["kubernetes_status"] == "READY"
            or result[0]["kubernetes_status"] == "WARNING"
        ), "Supervisor cluster kubernetes_status is ERROR"

    except Exception as e:
        health = False
        slack_message = f'vCenter server: {vcsa}. \n{result[0]["cluster_name"]} \
                        Supervisor cluster is NOT HEALTHY. \n{e}'
        logging.error(slack_message)

        # Send alert to slack channel
        # slack_post(slack_message, channel_id=CH_ID)

    if health is True:
        logging.info("---Supervisor cluster is HEALTHY---")
    elif pipeline and health is False:
        assert (
            health is True
        ), "---Supervisor cluster is NOT HEALTHY. Alert sent to slack channel.---"
    elif not pipeline and health is False:
        logging.error("---Supervisor cluster is NOT HEALTHY---")


def get_vc_session(vcsa, username, password):
    """
    Creates a session to vCenter.
    """
    s = requests.Session()
    s.verify = False
    s.post(f"https://{vcsa}/rest/com/vmware/cis/session", auth=(username, password))
    return s


def get_wcp_cluster_health(vcip, s):
    """
    Invokes vCenter api to get supervisor cluster status.
    """
    wcp_cluster_details = s.get(
        f"https://{vcip}/api/vcenter/namespace-management/clusters",
    )

    return wcp_cluster_details.json()


def main():
    """
    This script checks supervisor cluster status.
    
    Example usage: 
    python3 wcp_cluster_health.py --vcsa sof2-01-vc11 --vuser administrator@vsphere.local
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--vcsa", required=True, help="vCenter server")
    parser.add_argument("--vuser", required=True, help="username")
    parser.add_argument("--vpass", required=False, type=str, help="password")
    parser.add_argument("--pipeline", action="store_true", help="use if running this in a pipeline")
    parser.add_argument(
        "-l",
        "--loglevel",
        required=False,
        type=str,
        default="INFO",
        help="Logging Levels",
        choices=["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"],
    )
    args = parser.parse_args()
    vc_username = args.vuser

    if not args.vpass:
        vc_password = getpass.getpass(prompt="Enter adm password:")
    else:
        vc_password = args.vpass

    coloredlogs.install()

    # Setting log level
    logging.basicConfig(level=args.loglevel)

    vc_session = get_vc_session(args.vcsa, vc_username, vc_password)
    result = get_wcp_cluster_health(args.vcsa, vc_session)
    verify_wcp_cluster_health(args.vcsa, result, args.pipeline)


if __name__ == "__main__":
    main()
