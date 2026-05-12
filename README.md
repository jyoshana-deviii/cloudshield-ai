# CloudShield AI

AI-Powered AWS Security Monitoring System

## What is CloudShield AI?
CloudShield AI is a real-time AWS security monitoring system that automatically detects every login to your AWS account, analyzes it using Amazon Bedrock Claude AI, and instantly sends email alerts with YES/NO verification buttons to confirm if the login was legitimate or unauthorized.

## Features
- Real-time AWS login detection using CloudTrail and EventBridge
- AI-powered risk analysis using Amazon Bedrock Claude Haiku 4.5
- Instant email alerts with YES/NO verification buttons
- Automatic blocking of suspicious IAM users on NO click
- Live security dashboard with login history and statistics
- Secure website authentication via Amazon Cognito
- IP-based geolocation using ip-api.com
- Multi-category dashboard cards for Total, IAM, Root, Suspicious, and Blocked logins

## Architecture
CloudTrail detects login events, EventBridge triggers Lambda function, Lambda fetches IP location and calls Bedrock AI for risk analysis, SNS sends email alert with verification links, DynamoDB stores all logs, and S3 with CloudFront serves the secure dashboard.

## AWS Services Used
- AWS CloudTrail
- Amazon EventBridge
- AWS Lambda
- Amazon Bedrock (Claude Haiku 4.5)
- Amazon SNS
- Amazon DynamoDB
- Amazon API Gateway
- Amazon S3 and CloudFront
- Amazon Cognito
- AWS IAM
- AWS GuardDuty

## Team
Team 56

## Live Demo
https://d3s3nxq8afdbi9.cloudfront.net
