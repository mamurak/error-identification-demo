from datetime import datetime, timezone, timedelta
import json
import logging
import os

from llama_stack_client.lib.agents.client_tool import client_tool
import requests


logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


def parse_log_message(raw_log: str) -> str:
    """
    Parse log message similar to jq logic:
    Try to parse as JSON and extract msg/message/log fields, 
    otherwise return the raw log.
    """
    try:
        # Try to parse as JSON
        log_json = json.loads(raw_log)

        # Extract the message field (similar to jq: .msg // .message // .log // .)
        if isinstance(log_json, dict):
            # Priority order: msg -> message -> log -> entire object
            message = (
                log_json.get('msg') or 
                log_json.get('message') or 
                log_json.get('log') or 
                str(log_json)
            )
            return str(message)
        else:
            # If it's not a dict, return as string
            return str(log_json)

    except (json.JSONDecodeError, TypeError):
        # If it's not JSON, return the raw log
        return raw_log


@client_tool
def query_loki_logs(namespace: str, container_name: str, hours: str = '1') -> str:
    """Query logs from a namespace and container in Loki with enhanced JSON parsing.
    :param namespace: Kubernetes namespace name
    :param container_name: Container name to query logs from
    :param hours: Age of oldest logs to filter in hours
    :returns: Log messages
    """
    logger.info(
        f'loki function called with: namespace={namespace}, '
        f'container_name={container_name}, hours={hours}')
    try:
        print(
            f"🔍 Querying Loki logs for namespace: {namespace}, "
            f"container: {container_name}, hours: {hours}")

        # Updated token (use your actual token)
        token = os.getenv("TOKEN")

        # Calculate time range in ISO format
        now = datetime.now(timezone.utc)
        start_time = now - timedelta(hours=int(hours))

        # Format timestamps as ISO 8601 strings
        start_iso = start_time.strftime("%Y-%m-%dT%H:%M:%SZ")
        end_iso = now.strftime("%Y-%m-%dT%H:%M:%SZ")

        # Base URL for Loki
        base_url = os.getenv("LOKI_BASE_URL")
        url = f"{base_url}/api/logs/v1/application/loki/api/v1/query_range"

        # Use the working LogQL query pattern - search by container name in pod names
        # Since container names are often part of pod names, we'll use regex matching
        logql_query = (
            f'{{kubernetes_namespace_name="{namespace}",'
            f'kubernetes_pod_name=~".*{container_name}.*"}}'
        )

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        params = {
            "query": logql_query,
            "start": start_iso,
            "end": end_iso,
            "limit": 5000
        }

        print(f"📡 Making request to: {url}")
        print(f"📋 Query: {logql_query}")
        print(f"🕒 Time range: {start_iso} to {end_iso}")

        res = requests.get(
            url, 
            params=params, 
            headers=headers, 
            timeout=30
        )

        print(f"📊 Response Status: {res.status_code}")

        if res.status_code == 200:
            try:
                response_data = res.json()

                # Check if we got data
                if response_data.get("status") == "success":
                    parsed_logs = []
                    results = response_data.get("data", {}).get("result", [])

                    for result in results:
                        for entry in result.get("values", []):
                            if len(entry) >= 2:
                                # entry[0] is timestamp (nanoseconds), entry[1] is log message
                                timestamp_ns = entry[0]
                                raw_log = entry[1]

                                # Convert timestamp from nanoseconds to human-readable format
                                try:
                                    timestamp_seconds = int(timestamp_ns) / 1_000_000_000
                                    formatted_timestamp = datetime.fromtimestamp(
                                        timestamp_seconds, tz=timezone.utc
                                    ).strftime("%Y-%m-%d %H:%M:%S UTC")
                                except (ValueError, TypeError):
                                    formatted_timestamp = str(timestamp_ns)

                                # Parse the log message (similar to jq logic)
                                parsed_message = parse_log_message(raw_log)

                                # Format output: timestamp + parsed message
                                log_line = f"{formatted_timestamp} {parsed_message}"
                                parsed_logs.append(log_line)
                                print(log_line)

                    if parsed_logs:
                        log_output = "\n".join(parsed_logs)
                        print(
                            f"✅ Successfully retrieved and parsed "
                            f"{len(parsed_logs)} log entries")
                        return_string = (
                            f"Found {len(parsed_logs)} parsed log entries "
                            f"for container '{container_name}' in namespace "
                            f"'{namespace}':\n\n{log_output}"
                        )
                        return return_string
                    else:
                        print("📭 No log entries found in results")
                        return_string = (
                            f"❌ No logs found for container '{container_name}' "
                            f"in namespace '{namespace}' for the last {hours} hour(s)"
                        )
                        return return_string
                else:
                    error_msg = (
                        f"❌ Loki returned error status: "
                        f"{response_data.get('error', 'Unknown error')}"
                    )
                    print(error_msg)
                    return error_msg

            except json.JSONDecodeError as je:
                error_msg = f"❌ JSON decode error: {je}"
                print(error_msg)
                return error_msg

        else:
            error_msg = f"❌ HTTP Error {res.status_code}: {res.text}"
            print(error_msg)
            return error_msg

    except requests.exceptions.RequestException as e:
        error_msg = f"❌ Request failed: {str(e)}"
        print(error_msg)
        return error_msg
    except Exception as e:
        error_msg = f"❌ Unexpected error querying Loki: {str(e)}"
        print(error_msg)
        return error_msg