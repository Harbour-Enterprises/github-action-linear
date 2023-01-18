# Update Linear action

Github Action that updates a Linear issue

## Inputs

## `token`

**Required** Access token for Linear API.

## `object_type`

**Required** Name of the branch containing Linear ref number. This is used to find assotiated Linear ticket.

## `object_value`

**Required** Title of the PR containing Linear ref number. This is used to find assotiated Linear ticket.

## `search_value`

*Optional* Description of the PR containing Linear ref number. This is used to find assotiated Linear ticket.

## `label`

*Optional* Label name to be added in the Linear issue.

## Example usage

```
uses: Harbour-Enterprises/github-action-linear@v1.0.2
with:
  token: "${{ secrets.LINEAR_TOKEN }}"
  object_type: "comment"
  object_value: "This is a comment"
  search_value: "${{ github.head_ref }}"
  label: "Label name"
```