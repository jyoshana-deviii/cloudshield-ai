import json
import boto3
import os
from datetime import datetime

sns      = boto3.client('sns')
dynamodb = boto3.resource('dynamodb')
iam      = boto3.client('iam')
table    = dynamodb.Table('CloudShieldLogs')

TOPIC_ARN = os.environ.get('SNS_TOPIC_ARN', 'arn:aws:sns:us-east-1:989923171840:CloudShieldAlerts')

def block_iam_user(username):
    try:
        iam.update_login_profile(
            UserName=username,
            PasswordResetRequired=True
        )
        keys = iam.list_access_keys(UserName=username)
        for key in keys['AccessKeyMetadata']:
            iam.update_access_key(
                UserName=username,
                AccessKeyId=key['AccessKeyId'],
                Status='Inactive'
            )
        return True
    except Exception as e:
        print(f"Block error: {str(e)}")
        return False

def lambda_handler(event, context):
    params   = event.get('queryStringParameters', {}) or {}
    action   = params.get('action', '')
    user     = params.get('user', 'Unknown')
    ip       = params.get('ip', 'Unknown')
    location = params.get('location', 'Unknown')
    login_id = params.get('loginId', '')

    if login_id:
        try:
            table.update_item(
                Key={'loginId': login_id},
                UpdateExpression='SET userVerified = :v',
                ExpressionAttributeValues={':v': 'YES' if action == 'yes' else 'NO'}
            )
        except Exception as e:
            print(f"DynamoDB update failed: {e}")

    if action == 'yes':
        sns.publish(
            TopicArn=TOPIC_ARN,
            Subject='[CloudShield] Login Confirmed Safe',
            Message=f"""
CloudShield AI - Login Verified

You confirmed this login WAS YOU. All good!

LOGIN DETAILS:
User     : {user}
IP       : {ip}
Location : {location}
Time     : {datetime.utcnow().isoformat()}

No action needed. Stay safe!
=====================================
Powered by CloudShield + Amazon Bedrock
            """
        )
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'text/html'},
            'body': '''<!DOCTYPE html>
<html>
<head>
<style>
body{font-family:Arial;text-align:center;padding:80px;
background:linear-gradient(135deg,#0a0a1a,#0d0d2b);color:white;}
.box{background:rgba(15,10,35,0.9);border:1px solid rgba(139,92,246,0.4);
border-radius:20px;padding:50px 40px;display:inline-block;
box-shadow:0 0 40px rgba(139,92,246,0.2);}
h1{color:#a78bfa;font-size:2.5rem;margin-bottom:15px;}
p{color:rgba(167,139,250,0.7);font-size:1.1rem;margin-top:15px;}
.badge{display:inline-block;margin-top:20px;padding:8px 20px;
background:rgba(139,92,246,0.15);border:1px solid rgba(139,92,246,0.3);
border-radius:20px;color:#a78bfa;font-size:0.85rem;}
</style>
</head>
<body>
<div class="box">
<h1>Login Verified!</h1>
<p>You confirmed this login was YOU.</p>
<p>Your AWS account is SAFE.</p>
<div class="badge">CloudShield AI - Secured by AWS</div>
</div>
</body>
</html>'''
        }

    elif action == 'no':
        username = user.split('/')[-1] if '/' in user else ''
        blocked  = False

        if username and 'root' not in username.lower():
            blocked = block_iam_user(username)

        block_msg = f"IAM user {username} has been automatically blocked!" if blocked \
                    else "Root account detected - please secure manually!"

        sns.publish(
            TopicArn=TOPIC_ARN,
            Subject='[CloudShield] URGENT: Unauthorized Login Detected!',
            Message=f"""
CloudShield AI - SECURITY ALERT

UNAUTHORIZED LOGIN CONFIRMED!

YOU SAID THIS LOGIN WAS NOT YOU!

INTRUDER DETAILS:
User     : {user}
IP       : {ip}
Location : {location}
Time     : {datetime.utcnow().isoformat()}
Action   : {block_msg}

IMMEDIATE STEPS:
1. Go to IAM and verify all users
   https://console.aws.amazon.com/iam/
2. Rotate all access keys immediately
3. Check CloudTrail for damage
   https://console.aws.amazon.com/cloudtrail/
4. Review all recently created resources
5. Contact AWS Support if needed
   https://aws.amazon.com/support

ACT NOW - every minute counts!
=====================================
Powered by CloudShield + Amazon Bedrock
            """
        )
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'text/html'},
            'body': f'''<!DOCTYPE html>
<html>
<head>
<style>
body{{font-family:Arial;text-align:center;padding:80px;
background:linear-gradient(135deg,#1a0a0a,#2d0d0d);color:white;}}
.box{{background:rgba(35,10,10,0.9);border:1px solid rgba(239,68,68,0.4);
border-radius:20px;padding:50px 40px;display:inline-block;
box-shadow:0 0 40px rgba(239,68,68,0.2);}}
h1{{color:#f87171;font-size:2.5rem;margin-bottom:15px;}}
p{{color:rgba(248,113,113,0.7);font-size:1.1rem;margin-top:15px;}}
.block-msg{{margin:20px 0;padding:14px;background:rgba(239,68,68,0.1);
border:1px solid rgba(239,68,68,0.3);border-radius:10px;
color:#fca5a5;font-size:0.9rem;}}
.steps{{text-align:left;margin-top:20px;padding:14px;
background:rgba(239,68,68,0.06);border-radius:10px;line-height:2;}}
.steps p{{color:rgba(248,113,113,0.8);font-size:0.85rem;margin:4px 0;}}
</style>
</head>
<body>
<div class="box">
<h1>Security Alert!</h1>
<p>You confirmed this was NOT you.</p>
<div class="block-msg">{block_msg}</div>
<div class="steps">
<p><b>Immediate Actions:</b></p>
<p>1. Go to IAM and verify all users</p>
<p>2. Rotate all access keys</p>
<p>3. Check CloudTrail logs</p>
<p>4. Contact AWS Support</p>
</div>
</div>
</body>
</html>'''
        }

    else:
        return {
            'statusCode': 400,
            'headers': {'Content-Type': 'text/html'},
            'body': '<h1>Invalid action</h1>'
        }
