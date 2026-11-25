# AlertPlus – Project Workflow

## 1. Website access

1. The user opens `https://alertplus.online/`.
2. Amazon CloudFront delivers the frontend files stored in Amazon S3.
3. HTTPS is provided through the ACM certificate configured for CloudFront.

## 2. User authentication

1. The user signs in through Amazon Cognito.
2. Cognito authenticates the user and provides tokens.
3. The frontend uses the authentication information when making protected API requests.
4. The application uses the `MedicineActiveSessions` DynamoDB table for its active-session behavior.

## 3. Medicine inventory operations

1. The user views, searches, or filters medicine records on the dashboard.
2. The frontend sends requests to Amazon API Gateway.
3. API Gateway invokes `MedicineInventoryFunction`.
4. The Lambda function performs the requested medicine operation.
5. Medicine records are stored in or retrieved from `MedicineInventory`.

Supported operations include adding, viewing, editing, deleting, and adjusting stock.

## 4. Medicine status checks

The application identifies medicine conditions such as:
- Low stock
- Expiring soon
- Expired
- Available

The low-stock condition uses the medicine's configured reorder level. Expiry checks use the medicine expiry date.

## 5. Daily automated email alerts

1. Amazon EventBridge Scheduler triggers `MedicineDailyAlertFunction` daily at the configured schedule (planned for 9:00 AM IST).
2. The Lambda function checks medicine inventory records.
3. It evaluates expiry and stock conditions, including medicines expiring within 30 days or already expired, and medicines at or below the configured low-stock threshold/reorder level.
4. If alert conditions are found, Amazon SNS sends an email summary.
5. If no alert conditions are found, no alert email is sent.

## 6. Frontend utility features

The dashboard also supports:
- CSV export of inventory data
- JSON backup of inventory data
- Activity history stored locally in the browser/device

## Important scope note

The current stock-in/stock-out feature adjusts inventory quantity. It is not a full sales-management module with transaction records or sales analytics.
