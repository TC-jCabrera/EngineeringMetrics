import requests
import logging


logger = logging.getLogger(__name__)


def get_JiraTickets(config, jiraAlias, startDate, endDate):
    jira_api_core = config["jira_api_base"]
    token = config["jira_api_key"]

    headers = {
        "Authorization": f"Basic {token}",
        "Content-Type": "application/json",
    }

    jql = (
        f'assignee = "{jiraAlias}" '
        f'AND resolved >= "{startDate}" '
        f'AND resolved < "{endDate}"'
    )

    params = {
        "jql": jql,
        "validateQuery": "true",
        "fields": "subtasks,customfield_10004,customfield_10007,customfield_12858,summary,resolutiondate,issuetype,assignee",
        "maxResults": 100,
    }

    url = f"{jira_api_core}/search/jql"
    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        return response.json()

    # Jira's /search/jql silently returns 200 + empty issues on bad auth, so surface real failures loudly
    logger.error(
        f"Jira request failed. status={response.status_code} url={response.url} body={response.text[:500]}"
    )
    return {"issues": []}
