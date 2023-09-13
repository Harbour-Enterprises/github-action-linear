# Update Linear action

Github Action that updates a Linear issue

## Inputs

## `token`

**Required** Access token for Linear API (it can be a personal API key or an OAuth2 access token)

## `object_type`

**Required** Name of the branch containing Linear ref number. This is used to find assotiated Linear ticket.

## `object_value`

**Required** Title of the PR containing Linear ref number. This is used to find assotiated Linear ticket.

## `search_value`

**Required** Description of the PR containing Linear ref number. This is used to find assotiated Linear ticket.

## `label`

_Optional_ Label name to be added in the Linear issue.

## Example usage

```
uses: Harbour-Enterprises/github-action-linear@v1.0.5
with:
  token: "${{ secrets.LINEAR_TOKEN }}"
  object_type: "comment"
  object_value: "This is a comment"
  search_value: "${{ github.head_ref }}"
  label: "Label name"
```
