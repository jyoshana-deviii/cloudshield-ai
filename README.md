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

## Problem Statement
AWS account owners have no real-time visibility when someone logs into their cloud account. Traditional security alerts treat every login the same, flooding users with irrelevant notifications or missing actual threats entirely. CloudShield AI solves this by automatically detecting every login, using AI to analyze the risk, and sending instant verification alerts.

## How It Works
1. Someone logs into AWS Console
2. CloudTrail records the login event automatically
3. EventBridge detects the event and triggers Lambda function
4. Lambda fetches the IP geolocation using ip-api.com
5. Amazon Bedrock Claude Haiku 4.5 analyzes the login and decides SAFE or SUSPICIOUS
6. SNS sends an instant email alert with YES and NO verification links
7. User clicks YES to confirm or NO to trigger automatic IAM user block
8. All logs are saved to DynamoDB and displayed on the live dashboard

## Security Flow
- SAFE login: India location, known IAM user, private IP
- SUSPICIOUS login: Foreign country IP, root account login, unknown location
- On NO click: IAM user is automatically blocked using PasswordResetRequired and access key deactivation

## Future Enhancements
- Multi-tenant SaaS platform where anyone can signup and monitor their own AWS account
- SMS alerts via AWS SNS
- Auto-block after 5 failed login attempts
- Timezone-based anomaly detection
- Mobile application
- AWS GuardDuty deep integration
- WhatsApp notifications

## Local Setup
This project is fully serverless on AWS. To deploy on your own AWS account, configure the following services as described in the architecture and upload the Lambda functions from this repository.

## Repository Structure
- CloudShieldLoginMonitor.py - Main Lambda for login detection and AI analysis
- CloudShieldVerifyResponse.py - Lambda for YES/NO email verification and auto-block
- CloudShieldGetLogs.py - Lambda for fetching logs to dashboard
- CloudShieldLogin.py - Lambda for website Cognito login
- CloudShieldSignup.py - Lambda for website Cognito signup
- index.html - Website login page
- dashboard.html - Security dashboard with live login statistics
