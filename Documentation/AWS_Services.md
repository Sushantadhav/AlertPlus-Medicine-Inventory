# AlertPlus – AWS Services

AlertPlus is a serverless medicine inventory management application deployed on AWS.

## Core AWS services

| AWS service | Role in AlertPlus |
|---|---|
| Amazon S3 | Stores the website's frontend files. |
| Amazon CloudFront | Delivers the frontend globally and serves the website through the custom domain. |
| AWS Certificate Manager (ACM) | Provides the TLS certificate used for HTTPS on CloudFront. |
| Amazon Cognito | Handles user authentication and issues login tokens. |
| Amazon API Gateway | Exposes API routes used by the frontend. |
| AWS Lambda | Runs backend logic for medicine operations and scheduled alert processing. |
| Amazon DynamoDB | Stores medicine inventory records and active-session information. |
| Amazon EventBridge Scheduler | Triggers the daily medicine-alert process on its schedule. |
| Amazon SNS | Sends email notifications when alert conditions are found. |

## Supporting AWS services

- **AWS IAM:** Controls permissions for AWS services and Lambda execution roles.
- **Amazon CloudWatch:** Provides logs and monitoring for supported AWS resources.

## Main service flows

### Website delivery
1. Website files are stored in Amazon S3.
2. Amazon CloudFront delivers the website.
3. ACM provides the certificate used for HTTPS.

### Login and inventory operations
1. Amazon Cognito authenticates the user.
2. The frontend sends API requests to API Gateway with the required authentication.
3. API Gateway invokes the relevant Lambda integration.
4. Lambda reads or updates records in DynamoDB.

### Daily email alerts
1. EventBridge Scheduler triggers the daily alert Lambda.
2. MedicineDailyAlertFunction scans the MedicineInventory DynamoDB table.
3. Lambda checks medicine stock and expiry conditions.
4. SNS sends an email summary when alert conditions are found.
## Deployment notes

- AWS Region for the application's main resources: `ap-south-1`.
- The ACM certificate used by CloudFront is managed in `us-east-1`.
- The custom website domain is `https://alertplus.online/`.
- DNS is managed through Hostinger; Route 53 was not used for this setup.
