# AlertPlus – API Routes

## API base URL

```text
https://vgtmgl32xh.execute-api.ap-south-1.amazonaws.com
```

## Medicine endpoints

| HTTP method | Route | Purpose |
|---|---|---|
| GET | `/medicines` | Retrieve medicine records. |
| POST | `/medicines` | Add a medicine record. |
| PUT | `/medicines/{medicineId}` | Update a medicine record. |
| DELETE | `/medicines/{medicineId}` | Delete a medicine record. |
| POST | `/medicines/{medicineId}/stock` | Process a stock adjustment. |

## Session endpoint

The project also uses a `/session` route for active-session verification.

**HTTP method:** Confirm the configured method in API Gateway before publishing this document. It is intentionally not guessed here.

## Authentication and request flow

1. The user signs in through Amazon Cognito.
2. The frontend obtains the authentication token.
3. The frontend calls the API with the required authorization information.
4. API Gateway and the backend process the request.

## Notes

- `{medicineId}` is a path parameter identifying the medicine record.
- The stock endpoint is used for stock-in/stock-out adjustments; it should not be described as a complete sales transaction module.
- Do not publish Cognito client secrets, access tokens, refresh tokens, API keys, or other credentials in this repository.
