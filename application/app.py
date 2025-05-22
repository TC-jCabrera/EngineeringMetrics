from common.metrics_util import load_config
from API.Flow_data import get_FlowTeams, get_JiraAliases
from API.Jira_data import get_JiraTickets
from repository.rds_repository import storeTeamMembers, updateJiraAliases, storeJiraIssues, updateSubtasksStoryPoints
from repository.db_connection import DatabaseConnection
import logging
import os
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def process_jira_data(start_date: str, end_date: str):
    config = load_config()

    try:
        # Get Flow Team members
        team_members = get_FlowTeams(config)
        email_list = storeTeamMembers(config,team_members)
        logging.info("Flow Team Members fetched successfully")

        for email in email_list:
            jiraAlias = get_JiraAliases(config, email)
       
            returnExternalId = updateJiraAliases(config,jiraAlias)
            if returnExternalId:
                jiraTickets = get_JiraTickets(config,returnExternalId,start_date,end_date)
                storeJiraIssues(config,jiraTickets)

        updateSubtasksStoryPoints(config, start_date, end_date)

        logging.info("Jira Aliases fetched successfully")
    finally:
        # Close database connection
        DatabaseConnection.get_instance().close_connection()

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python app.py <start_date> <end_date>")
        print("Example: python app.py 2024-04-01 2024-04-30")
        sys.exit(1)
    
    start_date = sys.argv[1]
    end_date = sys.argv[2]
    process_jira_data(start_date, end_date)


