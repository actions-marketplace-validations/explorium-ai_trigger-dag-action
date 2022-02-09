import json
import os
import string
import sys
import time

import requests
from google.auth.transport.requests import Request
from google.oauth2 import id_token

IAM_SCOPE = "https://www.googleapis.com/auth/iam"
OAUTH_TOKEN_URI = "https://www.googleapis.com/oauth2/v4/token"
USE_EXPERIMENTAL_API = True
ENTITY_CLIENT_VERSION = os.environ["INPUT_ENTITY_CLIENT_VERSION"]
dag_run_id = os.environ["INPUT_DAG_RUN_ID"]
client_id = os.environ["INPUT_CLIENT_ID"]
compare_threshold = float(os.environ["INPUT_COMPARE_THRESHOLD"])
send_slack_on_errors = os.environ["INPUT_SEND_SLACK_ON_ERRORS"]
webserver_id = os.environ["INPUT_WEBSERVER_ID"]
run_type = os.environ["INPUT_RUN_TYPE"]
dag_name = os.environ["INPUT_DAG_NAME"]

def main():
    trigger_dag(
        {
            "config": {
                "entity-client-version": ENTITY_CLIENT_VERSION,
                "compare_threshold": compare_threshold,
                "send_slack_on_errors": send_slack_on_errors,
                "run_type": run_type,
            }
        },
        dag_run_id,
    )
    status_code = "running"
    while status_code not in {'success', 'failed'}:
        status_code = get_dag_status(dag_run_id)
        time.sleep(1)
    if status_code != "success":
        print(f"::set-output name=result::Failed")
        sys.exit("Dag Failed")
    else:
        print(f"::set-output name=result::Success")
        sys.exit(0)

def trigger_dag(data: json, dag_run_id: string):
    if USE_EXPERIMENTAL_API:
        endpoint = f"api/experimental/dags/{dag_name}/dag_runs"
        json_data = {
            "conf": data,
            "replace_microseconds": "false",
            "run_id": dag_run_id,
        }
    else:
        endpoint = f"api/v1/dags/{dag_name}/dagRuns"
        json_data = {"conf": data, "run_id": dag_run_id}
    webserver_url = "https://" + webserver_id + ".appspot.com/" + endpoint
    make_iap_request_trigger(webserver_url, method="POST", json=json_data)


def get_dag_status(run_id: string) -> string:
    if USE_EXPERIMENTAL_API:
        endpoint = f"api/experimental/dags/{dag_name}/dag_runs"
    else:
        endpoint = f"api/v1/dags/{dag_name}/dagRuns/{run_id}"
    webserver_url = "https://" + webserver_id + ".appspot.com/" + endpoint
    return make_iap_request_poll(run_id, webserver_url, method="GET")


def auth_google(**kwargs: object) -> string:
    if "timeout" not in kwargs:
        kwargs["timeout"] = 90

    google_open_id_connect_token = id_token.fetch_id_token(Request(), client_id)
    return google_open_id_connect_token


def make_iap_request_poll(run_id: string, url: string, method: string = "GET", **kwargs: object) -> string:
    resp = requests.request(
        method,
        url,
        headers={"Authorization": "Bearer " + auth_google(**kwargs)},
    )

    return handle_request(resp, run_id)


def handle_request(resp: requests.request, run_id: string) -> string:
    if resp.status_code == 403:
        raise Exception(
            "Service account does not have permission to "
            "access the IAP-protected application."
        )
    elif resp.status_code != 200:
        raise Exception(
            "Bad response from application: " + str(resp.status_code) + " / " + resp.headers + " / " + resp.text
        )
    else:
        if run_id:
            data = json.loads(str(resp.text).replace("'", ""))
            for item in data:
                if item["run_id"] == run_id:
                    return item["state"]
            return resp.text
        else:
            return resp.text


def make_iap_request_trigger(url: string, method: string = "GET", **kwargs: object) -> string:
    resp = requests.request(
        method,
        url,
        headers={"Authorization": "Bearer " + auth_google(**kwargs)},
        **kwargs)
    return handle_request(resp, False)

if __name__ == "__main__":
    main()