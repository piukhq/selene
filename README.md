# Mids processing

The current version of selene supports:
- Amex and Visa merchant files on-boarding.
- MasterCard handback files processing.
- MasterCard handback files duplicates checking.

This project is meant to be used trough the helios web interface.

## Amex and Visa merchants on-boarding

### Request

POST `/mids/import_mids`

File to process as JSON

## MasterCard handback

### Request

POST `/mids/mastercard_handbacks`

File to process as JSON

## MasterCard handback duplicates

### Request

POST `/mids/handback_duplicates`

File to process as JSON

## Wipe output folder

### Request

GET `/mids/wipe_folders`

## Cassandra database operations:

### Request

POST `/mids/cassandra`

### Payload

Type: JSON provide one of the following
- Cassandra input file with A for Add or D for delete in action column as list of lists
- Merchant to be removed (slug) as `{"merchant": <merchant name>}`

## Response

### success

code 200

```json
{
  "success": true,
  "error": null
}
```

The output files are placed in the **merchants** folder in `/tmp/mids_output`

### failure

code 500

```json
{
  "success": false,
  "error": "<RETURNED EXCEPTION>"
}
```
