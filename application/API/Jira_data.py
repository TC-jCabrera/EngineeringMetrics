import requests
import logging


logger = logging.getLogger(__name__)
def get_JiraTickets(config,jiraAlias,startDate,endDate):

    jira_api_core = config["jira_api_base"]
    token = config["jira_api_key"]


   
    headers = {
                    "Authorization": f"Basic {token}",
                    "Content-Type": "application/json",
                }
    # Look for tickets that are assigned to the user and resolved between the start and end date
    url ="{}{}{}{}{}{}{}{}".format(
             jira_api_core,
             "/search?jql=assignee=",
             jiraAlias,
             " AND resolved>=",
              startDate,
             " AND resolved<=",
              endDate,
             "&validateQuery=true&fields=subtasks,customfield_10004,customfield_10007,customfield_12858,summary,resolutiondate,issuetype,assignee") #Issue Type

    url = url.replace(" ", "%20")
   
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        members = response.json()
        return members
    else:
        logger.info(f"Failed to get metrics for {url}:{response.status_code}")


