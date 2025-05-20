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

def parse_datetime(dt_str):
    """Parse datetime string from Jira format to SQLite format."""
    if not dt_str:
        return None
    try:
        # Handle timezone offset
        if dt_str.endswith('Z'):
            dt_str = dt_str[:-1]  # Remove Z
            dt_str = dt_str + '+00:00'  # Add UTC timezone
        elif len(dt_str) >= 5 and dt_str[-5] in ['+', '-']:
            # Handle timezone offset in format -0700
            tz_offset = dt_str[-5:]
            dt_str = dt_str[:-5] + tz_offset[:3] + ':' + tz_offset[3:]
        
        dt = datetime.fromisoformat(dt_str)
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except (ValueError, TypeError):
        return None

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

def date_time_to_string(date_param):
    return date_param.strftime(f_timezone)

def date_to_string(date_param):
    return date_param.strftime(f_short)



