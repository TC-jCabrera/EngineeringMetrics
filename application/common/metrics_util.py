import json
import logging
import os
import re
from cloud.bridge import get_parameter_value, get_secret_value
from datetime import datetime, timedelta, time

logger = logging.getLogger(__name__)


log_levels = {
    "CRITICAL": logging.CRITICAL,
    "ERROR": logging.ERROR,
    "WARNING": logging.WARNING,
    "INFO": logging.INFO,
    "DEBUG": logging.DEBUG,
    "NOTSET": logging.NOTSET,
}

f_long = "%Y-%m-%dT%H:%M:%S.%fZ"
f_timezone = "%Y-%m-%dT%H:%M:%S.%f%z"
f_short = "%Y-%m-%d"


# Function to divide date range into chunks of chunk_size_days
def divide_into_chunks(start_date_str, end_date_str, chunk_size_days=14):

    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")

    if end_date_str is None or not end_date_str.strip():
        end_date = datetime.now()
    else:
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d")

    chunks = []
    current_date = start_date

    while current_date < end_date:
        chunk_end_date = min(
            current_date + timedelta(days=chunk_size_days - 1), end_date
        )

        chunks.append(
            {
                "start_date": current_date,
                "end_date": chunk_end_date,
                "name": "Period",
                "id": 9999,
            }
        )
        current_date = chunk_end_date + timedelta(days=1)

        if chunk_size_days >= (end_date - start_date).days:
            break

    return chunks, end_date.strftime("%Y-%m-%d")


def short_format_date(sprint_date):
    target_time = time(21, 0)
    try:
        date_sprint = datetime.strptime(sprint_date, f_long)
    except ValueError:
        date_sprint = datetime.strptime(sprint_date, f_timezone)

    date_target = datetime.combine(date_sprint, target_time)
    ref_date = date_target.strftime(f_short)
    return datetime.strptime(ref_date, f_short)


def handle_end_date(end_date):
    now = datetime.now()
    return now if end_date > now else end_date


def completion_percentage(member_tickets, remain_tickets):
    completed_count = len(member_tickets)
    total_count = completed_count + len(remain_tickets)

    if total_count == 0:
        return 0, 0  # Return 0 if there are no tickets

    completion_percentage = (completed_count / total_count) * 100
    return completion_percentage, total_count


def get_jira_boards_by_team(project_name):
    return jira_boards.get(project_name, None)


def get_available_teams():
    return jira_boards.keys()


def get_log_level(log_level):
    return log_levels.get(log_level, None)


def load_config():
    file_path = "config.json"
    prefix = "/engineering-metrics/config/"
    region = "us-east-1"

    with open(file_path, "r") as file:
        config = json.load(file)

    return load_config_dict(config, prefix, region)


def load_config_dict(element, prefix, region):
    config_parse = {}
    for key_string in element.keys():
        key_val = element.get(key_string)
        if type(key_val) is dict:
            cloud_value = load_config_dict(key_val, prefix, region)
        else:
            key_p = key_val.split(":")
            # Validate that we have exactly 4 parts
            if len(key_p) != 4:
                raise ValueError(
                    "Key must have exactly four parts separated by colons.'{} - {}'".format(
                        key_string, key_val
                    )
                )
            key_name = prefix + key_p[3]
            if key_p[1] == "secret":
                # special hanldling for rds password
                if key_p[2] == "false":
                    key_name = key_p[3]
                    rds_credentials_value = get_secret_value(key_name, region)
                    rds_cred = json.loads(rds_credentials_value)
                    cloud_value = rds_cred.get("password")
                else:
                    cloud_value = get_secret_value(key_name, region)
            else:
                cloud_value = get_parameter_value(key_name, region, key_p[2] == "True")

        config_parse[key_string] = cloud_value
    return config_parse


def handling_dates_settings(config):
    start_date = config.get("report_start_date")
    end_date = config.get("report_end_date")

    if start_date == "today":
        today = datetime.today()
        config["report_start_date"] = today.strftime("%Y-%m-%d")
    else:
        config["report_start_date"] = start_date

    if end_date == "None":
        config["report_end_date"] = None

    return config


def handling_dates_engineer_settings(config):
    # Get today's date
    today = datetime.today()
    # Calculate the first day of the current month
    day_one_current_month = today.replace(day=1)
    # Calculate the last day of the previous month
    last_day_previous_month = day_one_current_month - timedelta(days=1)
    # Calculate the first day of the previous month
    first_day_of_previous_month = last_day_previous_month.replace(day=1)
    
    logger.info("First day of previous month: %s", first_day_of_previous_month)
    logger.info("Last day of previous month: %s", last_day_previous_month)

    config["report_start_date"] = first_day_of_previous_month.strftime("%Y-%m-%d")
    config["report_end_date"] = last_day_previous_month.strftime("%Y-%m-%d")
    return config


def date_time_to_string(date_param):
    return date_param.strftime(f_timezone)


def date_to_string(date_param):
    return date_param.strftime(f_short)


def validate_query_parameters(
    name,
    param,
    required=False,
    min_length=None,
    max_length=None,
    date_format=None,
    is_email=False,
):
    # Check if param is None and required
    if param is None:
        if required:
            return False, f"{name} is missing."
        return True, None

    # Validate length
    if min_length is not None and len(param) < min_length:
        return False, f"{name} is shorter than min length of {min_length}"
    if max_length is not None and len(param) > max_length:
        return False, f"{name} is longer than max length of {max_length}"

    # Validate date format
    if date_format is not None:
        try:
            datetime.strptime(param, date_format)
        except ValueError:
            return False, f"{name} doesnt match the date format {date_format}"

    if is_email:
        email_regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
        if not re.match(email_regex, param):
            return False, f"{name} is not a valid email address."

    return True, None


def handle_non_valid_values(result_list):
    """
    Check if at least one tuple in the list contains False
    and append the message of such tuples into a single string with new lines
    """

    non_valid_values = [t[1] for t in result_list if t[0] is False]
    if non_valid_values:
        return True, "\n".join(non_valid_values)
    else:
        return False, None
