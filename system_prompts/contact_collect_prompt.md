# Contact Collect Prompt

The user wants to contact Jonathan and Pablo but some required information is still missing.

## Provided Information

{provided_fields}

## Missing Information

{missing_fields}

## Instructions

- Politely ask the user to provide the missing information.
- Do **NOT** make up any data.
- Do **NOT** send the message until all fields are provided.

## Required Fields

| Field     | Required |
|-----------|----------|
| `name`    | Yes      |
| `email`   | Yes      |
| `subject` | Yes      |
| `message` | Yes      |
| `country` | No       |
