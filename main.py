import argparse
import re
import sys
from functools import wraps

import requests

LINEAR_TOKEN = sys.argv[1]

args = sys.argv[2:]

url = "https://api.linear.app/graphql"
headers = {"Authorization": LINEAR_TOKEN, "Content-Type": "application/json"}


def get_issue(team_key, issue_number):
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


def get_state(state_name):
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


def get_label_id(team_id, label_name):
    query = """
    query LabelsByTeam ($teamId: ID) {
        issueLabels(filter: {team: {id: {eq: $teamId}}}) {
            nodes {
                id,
                name
            }
        }
    }
    """
    variables = {"teamId": team_id}
    payload = {"query": query, "variables": variables}

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    labels = response.json()["data"]["issueLabels"]["nodes"]
    matched_label = list(filter(lambda x: x["name"] == label_name, labels))

    if len(matched_label) == 0:
        return None
    else:
        return matched_label[0]["id"]


def add_labels(issue_id, label_ids):
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


def create_label(team_id, label_name):
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


def add_comment(issue_id, comment):
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


def update_issue_state(issue_id, state_id):
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


def update_linear(object_type, object_value, label, branch=None, title=None, description=None):

    ## Linear supports three ways to link issues with your pull requests:
    # Include *issue ID* in the branch name
    # Include *issue ID* in the PR title
    # Include *issue ID* with a magic word in the PR description (e.g. Fixes ENG-123) similar to GitHub Issues

    # Find issue through branch name
    match = re.search("(?i)(\w+)-(\d+)", branch)
    if not match:
        print("Unable to infer issue code from branch name", flush=True)

        # Find issue through branch name
        match = re.search("(?i)(\w+)-(\d+)", title)
        if not match:
            print("Unable to infer issue code from PR title", flush=True)

            # Find issue through pr description
            match = re.search("(?i)(\w+)-(\d+)", description)
            if not match:
                print("Unable to infer issue code from PR description", flush=True)
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
    label_ids = list(set([label.get("id") for label in issue.get("labels").get("nodes")]))

    if object_type == "comment":

        # Add comment
        add_comment(issue_id, object_value)

    elif object_type == "state":

        # Get state id
        state = get_state(object_value)
        state_id = state.get("id")

        # Update issue state
        update_issue_state(issue_id, state_id)

    if label:

        # Get label id
        label_id = get_label_id(team_id, label)
        if not label_id:

            # Create label
            label_id = create_label(team_id, label)

        # Append to existing ones
        label_ids.append(label_id)

        # Add label to issue
        add_labels(issue_id, label_ids)


if __name__ == "__main__":
    try:
        update_linear(*args)
    except requests.HTTPError as e:
        print("API response: {}".format(e.response.text), flush=True)
        raise

    print("All done!")
