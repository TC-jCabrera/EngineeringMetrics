import requests
import logging


logger = logging.getLogger(__name__)

########################################################
## Get Flow Teams
########################################################
def get_FlowTeams(config):

    flow_api_core = config["flow_api_base"]
    flow_token = config["flow_api_key"]
    flow_group = config["flow_group"].replace(" ", "%20")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {flow_token}"
    }
    # Get the team members for the group
    url ="{}{}{}{}".format(
            flow_api_core,
            "/team_membership/?membership_type=contributor&team__name=",
            flow_group,
            "&limit=100&offset=0",
        )

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        team_members = response.json()
        return team_members
    else:
        logger.info(f"Failed to get metrics for {url}:{response.status_code}")


########################################################
## Get Jira Aliases
########################################################
def get_JiraAliases(config, email):
    flow_api_core = config["flow_api_base"]
    flow_token = config["flow_api_key"]
  

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {flow_token}"
    }

    # Get the Jira alias for the user
    url ="{}{}".format(
            flow_api_core,
            "/user_alias/?integration=9398&email={}".format(email))
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        alias = response.json()
        return alias
    else:

        logger.info(f"Failed to get metrics for {url}:{response.status_code}")



