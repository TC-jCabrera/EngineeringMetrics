from common.metrics_util import load_config
from API.Flow_data import get_FlowTeams, get_JiraAliases
from API.Jira_data import get_JiraTickets
from repository.rds_repository import storeTeamMembers, updateJiraAliases
import logging
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def lambda_handler(event, context):

    config = load_config()

    # Get Flow Team members
    team_members = get_FlowTeams(config)
    email_list = storeTeamMembers(config,team_members)
    logging.info("Flow Team Members fetched successfully")


    for email in email_list:
        jiraAlias = get_JiraAliases(config, email)
        returnExternalId = updateJiraAliases(config,jiraAlias)
        jiraTickets = get_JiraTickets(config,returnExternalId,"2025-04-01","2025-04-30")
        print(jiraTickets)

    logging.info("Jira Aliases fetched successfully")


if __name__ == '__main__':
    lambda_handler(None, None)


