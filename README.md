# AlertPlus
## Smart Medicine Inventory Management System

AlertPlus is an AWS-based medicine inventory management system designed to help pharmacies manage medicine stock, monitor expiry dates, and receive automated alerts.

## Key Features

- Add, edit and delete medicines
- Track medicine stock
- Monitor medicine expiry dates
- Identify low-stock medicines
- Daily automated email alerts
- Secure user login
- Single active login session
- Export inventory data to CSV
- Backup inventory data in JSON format

## AWS Services Used

- Amazon S3
- Amazon CloudFront
- AWS Certificate Manager (ACM)
- Amazon Cognito
- Amazon API Gateway
- AWS Lambda
- Amazon DynamoDB
- Amazon EventBridge Scheduler
- Amazon SNS
- AWS IAM
- Amazon CloudWatch

## How It Works

1. Amazon CloudFront delivers the website stored in Amazon S3.
2. Amazon Cognito handles user authentication.
3. API Gateway receives frontend API requests.
4. AWS Lambda processes medicine operations.
5. Amazon DynamoDB stores medicine and session data.
6. EventBridge Scheduler triggers the daily alert process.
7. Lambda scans medicine records for stock and expiry conditions.
8. Amazon SNS sends email alerts when conditions are found.

## Daily Alert Automation

- Runs daily at 9:00 AM IST.
- Checks medicine expiry dates and stock levels.
- Identifies expired, expiring-soon and low-stock medicines.
- Sends an email summary through Amazon SNS when alert conditions are found.

## Project Structure

- `Architecture/` – AWS architecture diagram
- `Lambda/` – Backend Lambda function code
- `Database/` – DynamoDB structure documentation
- `Documentation/` – AWS services, API routes and project workflow
- `Screenshots/` – Application screenshots
- `index.html` – Frontend application

## Project Website

https://alertplus.online/

## Architecture

See the `Architecture` folder for the AWS architecture diagram.

## Future Enhancements

- Barcode scanning
- Purchase and sales tracking
- Mobile application
- Medicine demand prediction

## Author

Developed as an AWS cloud project.