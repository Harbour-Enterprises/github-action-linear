# Update Linear action

Github Action that updates a Linear issue

## Inputs

## `token`

**Required** Access token for Linear API.

## `branch`

**Required** Name of the branch containing Linear ref number. This is used to find assotiated Linear ticket.

## `title`

*Optional* Title of the PR containing Linear ref number. This is used to find assotiated Linear ticket.

## `description`

*Optional* Description of the PR containing Linear ref number. This is used to find assotiated Linear ticket.

## `comment`

**Required** Comment text body (markdown accepted) to be added in the Linear issue.

## `label`

*Optional* Label name to be added in the Linear issue.

## Example usage

```
uses: Harbour-Enterprises/github-action-linear@v1.0.1
with:
  branch: "${{ github.head_ref }}"
  comment: "`Livetest link:` [Click here](http://livetest.link)"
  token: "${{ secrets.LINEAR_TOKEN }}"
```