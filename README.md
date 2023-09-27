# Linear GHA Client

Exposes Linear GraphQL API to GitHub Actions

## Inputs

## `token`

**Required** Access token for Linear API (it can be a personal API key or an OAuth2 access token)

## `ref_value`

**Required** Reference value to search for. This is used to find assotiated Linear ticket.

## `object_type`

**Required** Linear object type. Possible values are `comment`, `state` and `label`.

## `object_value`

**Required** Linear object value. Multiple values can be passed by separating them with `|` character.

## Example usage

### Add single comment to a Linear ticket

```
uses: Harbour-Enterprises/github-action-linear@v1
with:
  token: "${{ secrets.LINEAR_TOKEN }}"
  ref_value: "${{ github.head_ref }}"
  object_type: "comment"
  object_value: "This is a comment"
```

### Upload a single file to a Linear ticket

```
uses: Harbour-Enterprises/github-action-linear@v1
with:
  token: "${{ secrets.LINEAR_TOKEN }}"
  ref_value: "${{ github.head_ref }}"
  object_type: "comment"
  object_value: "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAoAAAAKCAYAAACNMs+9AAAAFUlEQVR42mP8z8BQz0AEYBxVSF+FABJADveWkH6oAAAAAElFTkSuQmCC"
```

### Add multi type comment to a Linear ticket

```
uses: Harbour-Enterprises/github-action-linear@v1
with:
  token: "${{ secrets.LINEAR_TOKEN }}"
  ref_value: "${{ github.head_ref }}"
  object_type: "comment"
  object_value: "This is a multiline comment|data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAoAAAAKCAYAAACNMs+9AAAAFUlEQVR42mP8z8BQz0AEYBxVSF+FABJADveWkH6oAAAAAElFTkSuQmCC|This is another comment"
```

### Add label to a Linear ticket

```
uses: Harbour-Enterprises/github-action-linear@v1
with:
  token: "${{ secrets.LINEAR_TOKEN }}"
  ref_value: "${{ github.head_ref }}"
  object_type: "label"
  object_value: "My Label"
```

### Change state of a Linear ticket

```
uses: Harbour-Enterprises/github-action-linear@v1.0.5
with:
  token: "${{ secrets.LINEAR_TOKEN }}"
  ref_value: "${{ github.head_ref }}"
  object_type: "state"
  object_value: "In Review"
```
