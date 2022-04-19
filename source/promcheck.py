"""
A quick url checker to make sure prometheus
servers are up
"""
import sys
import time
import logging
import yaml
import requests


def load_config():
    """
    takes config.yaml and returns a dict with the config
    The config has a main list key of endpoints
    and each endpoint has a:
        url:
        optionally an endpoint can have params:
        which is just a yaml dict passed to requests

    other config options include:
        interval: how long between checks in seconds
        report_frequency: afyer how many checks do I print a report
    """
    try:
        with open("config.yaml", encoding="utf-8") as configfile:
            return yaml.safe_load(configfile)
    except FileNotFoundError:
        LOG.critical("!!! config.yaml is missing")
        sys.exit(1)


def clean_url(endpoint):
    """
    removes any trailing slashes
    """
    while endpoint["url"].endswith("/"):
        endpoint["url"] = endpoint["url"][:-1]
    return endpoint


def test_endpoint(endpoint):
    """
    sets up the url, adds the config for counting tries vs successes
    and returns the altered endpoint after checking
    """
    endpoint = clean_url(endpoint)
    if not endpoint.get("tries"):
        endpoint["tries"] = 0
    if not endpoint.get("failures"):
        endpoint["failures"] = 0
    if not endpoint.get("params"):
        endpoint["params"] = {"query": "kube_namespace_created"}
    return check_url(endpoint)


def check_url(endpoint):
    """
    use requests to test that the endpoint is functioning
    as expected
    """
    endpoint["tries"] += 1
    url = f'{endpoint["url"]}/api/v1/query'

    try:
        response = requests.get(url, params=endpoint["params"])
        if response.status_code == 200:
            LOG.info("connection to %s succeeded", endpoint["url"])
        else:
            endpoint["failures"] += 1
            LOG.warning(
                "connection to %s returned %s : data: %s",
                endpoint["url"],
                response.status_code,
                response.text,
            )
        return endpoint
    except requests.exceptions.ConnectionError as error_message:
        endpoint["failures"] += 1
        LOG.warning("could not connect to %s - %s", endpoint["url"], error_message)
        return endpoint


def main(config):
    """
    Primary entrypoint for the code
    """
    counter = 0
    if not config.get("interval"):
        config["interval"] = 5
    if not config.get("report_frequency"):
        config["report_frequency"] = 5
    while True:
        for item in config["endpoints"]:
            item = test_endpoint(item)
        # every so often print out a report
        if counter % config["report_frequency"] == config["report_frequency"] - 1:
            LOG.warning("***** Report so far *****")
            for item in config["endpoints"]:
                LOG.warning(
                    "%s has failed %d/%d times",
                    item["url"],
                    item["failures"],
                    item["tries"],
                )
            LOG.warning("*****  Report ends  *****")
        time.sleep(config["interval"])
        counter += 1


if __name__ == "__main__":
    FORMAT = "%(asctime)s %(message)s"
    logging.basicConfig(format=FORMAT)
    LOG = logging.getLogger("test")
    config_file = load_config()
    main(config_file)
