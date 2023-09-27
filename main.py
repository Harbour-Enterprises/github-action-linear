import base64
import mimetypes
import re
import sys
from io import BytesIO

import requests

LINEAR_TOKEN = sys.argv[1]

args = sys.argv[2:]

url = "https://api.linear.app/graphql"
headers = {"Authorization": LINEAR_TOKEN, "Content-Type": "application/json"}
if LINEAR_TOKEN.split("_")[1] == "oauth":
    headers = {"Authorization": f"Bearer {LINEAR_TOKEN}", "Content-Type": "application/json"}


def get_file_url(splitted_value):
    file_data, file_base64 = splitted_value.split(",")
    file_type = file_data.split(";")[0].split(":")[1]
    file_bytes = base64.b64decode(file_base64)
    file_stream = BytesIO(file_bytes)
    file_stream.seek(0, 2)
    file_size = file_stream.tell()
    file_extension = mimetypes.guess_extension(file_type)
    upload_url, asset_url, headers = get_signed_urls(f"file{file_extension}", file_size, file_type)
    upload_file(BytesIO(file_bytes), upload_url, headers)
    return asset_url


def get_signed_urls(file_name: str, file_size: int, content_type: str):
    query = """
    mutation FileUpload($size: Int!, $contentType: String!, $filename: String!) {
        fileUpload(size: $size, contentType: $contentType, filename: $filename) {
            uploadFile {
                filename
                contentType
                size
                uploadUrl
                assetUrl
                headers {
                    key
                    value
                }                
            }
            success
            lastSyncId
        }
    }
    """
    variables = {
        "size": file_size,
        "contentType": content_type,
        "filename": file_name,
    }
    payload = {"query": query, "variables": variables}

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    upload_file = response.json().get("data", {}).get("fileUpload", {}).get("uploadFile", {})

    resp_headers = upload_file.get("headers")
    resp_headers = {header["key"]: header["value"] for header in resp_headers}
    resp_headers["Content-Type"] = content_type
    resp_headers["Cache-Control"] = "public, max-age=31536000"

    return upload_file.get("uploadUrl"), upload_file.get("assetUrl"), resp_headers


def upload_file(file_bytes: str, upload_url: str, headers: dict):
    resp = requests.put(url=upload_url, headers=headers, data=file_bytes)
    print(resp.text)
    resp.raise_for_status()


def get_issue(team_key: str, issue_number: str):
    query = """
    query Issues($teamKey: String!, $issueNumber: Float) { 
        issues(filter: {team: {key: {eq: $teamKey}}, number: {eq: $issueNumber}}) {
            nodes {
                id,
                branchName,
                parent {
                    id
                },
                team {
                    id
                },
                labels {
                    nodes {
                        id
                    }
                }
            }
        }
    }
    """
    variables = {"teamKey": team_key, "issueNumber": issue_number}
    payload = {"query": query, "variables": variables}

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    matched_issues = response.json()["data"]["issues"]["nodes"]

    if len(matched_issues) == 0:
        return None
    else:
        return matched_issues[0]


def get_state(state_name: str):
    query = """
    query WorkflowState($stateName: String!) { 
        workflowStates(filter: {name: {eq: $stateName}}) {
            nodes {
                id,
                description
            }
        }
    }
    """
    variables = {"stateName": state_name}
    payload = {"query": query, "variables": variables}

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    matched_states = response.json()["data"]["workflowStates"]["nodes"]

    if len(matched_states) == 0:
        return None
    else:
        return matched_states[0]


def get_label_id(team_id: str, label_name: str):
    query = """
    query LabelsByTeam ($after: String, $teamId: ID) {
        issueLabels(first: 250, after: $after, filter: {team: {id: {eq: $teamId}}}) {
            edges {
                node {
                    id,
                    name
                }
            }
            pageInfo {
                hasNextPage
                endCursor
            }
        }
    }
    """
    variables = {"teamId": team_id}
    payload = {"query": query, "variables": variables}

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    response_json = response.json()
    if not response_json:
        return None
    issue_labels = response_json.get("data", {}).get("issueLabels", {})
    page_info = issue_labels.get("pageInfo", {})
    has_next_page = page_info.get("hasNextPage", False)
    end_cursor = page_info.get("endCursor")
    edges = issue_labels.get("edges", [])
    if has_next_page:
        while has_next_page:
            variables["after"] = end_cursor
            payload = {"query": query, "variables": variables}
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            response_json = response.json()
            if not response_json:
                return None
            issue_labels = response_json.get("data", {}).get("issueLabels", {})
            page_info = issue_labels.get("pageInfo", {})
            has_next_page = page_info.get("hasNextPage", False)
            end_cursor = page_info.get("endCursor")
            edges.extend(issue_labels.get("edges", []))

    labels = [edge["node"] for edge in edges]
    matched_label = list(filter(lambda x: x["name"] == label_name, labels))

    if len(matched_label) == 0:
        return None
    else:
        return matched_label[0]["id"]


def add_labels(issue_id: str, label_ids: list):
    query = """
    mutation IssueUpdate ($issueId: String!, $labelIds: [String!])  {
        issueUpdate(
            id: $issueId,
            input: {
                labelIds: $labelIds
            }
        ) {
            success
            issue {
                id
            }
        }
    }
    """
    variables = {"labelIds": label_ids, "issueId": issue_id}
    payload = {"query": query, "variables": variables}

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return None


def create_label(team_id: str, label_name: str):
    query = """
    mutation IssueLabelCreate ($teamId: String, $labelName: String!)  {
        issueLabelCreate(
            input: {
                name: $labelName,
                teamId: $teamId
            }
        ) {
            success
            issueLabel {
                id
            }
        }
    }
    """
    variables = {"teamId": team_id, "labelName": label_name}
    payload = {"query": query, "variables": variables}

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    label = response.json()["data"]["issueLabelCreate"].get("issueLabel")

    if not label:
        return None
    else:
        return label.get("id")


def add_comment(issue_id: str, comment: str):
    query = """
    mutation CommentCreateInput ($issueId: String!, $body: String!)  {
        commentCreate(
            input: {
                issueId: $issueId,
                body: $body
            }
        ) {
            success
            comment {
                id
            }
        }
    }
    """
    variables = {"body": comment, "issueId": issue_id}
    payload = {"query": query, "variables": variables}

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return None


def update_issue_state(issue_id: str, state_id: str):
    query = """
    mutation IssueUpdate ($issueId: String!, $stateId: String!)  {
        issueUpdate(
            id: $issueId,
            input: {
                stateId: $stateId
            }
        ) {
            success
            issue {
                id
            }
        }
    }
    """
    variables = {"stateId": state_id, "issueId": issue_id}
    payload = {"query": query, "variables": variables}

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return None


def process_linear(ref_value: str, object_type: str, object_value: str):
    """Process Linear API action

    :param ref_value: Reference value to search for
    :type ref_value: str
    :param object_type: Linear object type
    :type object_type: str
    :param object_value: Linear object value
    :type object_value: str
    """
    ## Linear supports three ways to link issues with your pull requests:
    # Include *issue ID* in the branch name
    # Include *issue ID* in the PR title
    # Include *issue ID* with a magic word in the PR description (e.g. Fixes ENG-123) similar to GitHub Issues

    # Match search value against regex
    match = re.search("(?i)(\w+)-(\d+)", ref_value)
    if not match:
        print("Unable to infer issue code from search value", flush=True)
        sys.exit()

    # Extract team key and issue number
    team_key = match.group(1).upper()
    issue_number = int(match.group(2))

    # Get issue
    issue = get_issue(team_key, issue_number)
    if not issue:
        print("No matching issues found!", flush=True)
    issue_id = issue.get("id")
    team_id = issue.get("team").get("id")

    if object_type == "comment":
        # split by pipe | using regex
        splitted_values = re.split(r"\s*\|\s*", object_value)
        joined_values = []
        for splitted_value in splitted_values:
            # Check if object value is a file
            if splitted_value.startswith("data"):
                file_url = get_file_url(splitted_value)
                splitted_value = f"![alt]({file_url})"
            joined_values.append(splitted_value)
        add_comment(issue_id, "\n".join(joined_values))

    elif object_type == "state":
        state = get_state(object_value)
        state_id = state.get("id")
        update_issue_state(issue_id, state_id)

    elif object_type == "label":
        label_id = get_label_id(team_id, object_value)
        if not label_id:
            # Create label
            label_id = create_label(team_id, object_value)

        # Append to existing ones
        label_ids = list(set([label.get("id") for label in issue.get("labels").get("nodes")]))
        label_ids.append(label_id)

        # Add label to issue
        add_labels(issue_id, label_ids)


if __name__ == "__main__":
    try:
        process_linear(*args)
    except requests.HTTPError as e:
        print("API response: {}".format(e.response.text), flush=True)
        raise
