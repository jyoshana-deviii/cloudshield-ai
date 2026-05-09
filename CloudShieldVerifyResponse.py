import json
import boto3

sns      = boto3.client('sns')
dynamodb = boto3.resource('dynamodb')
table    = dynamodb.Table('CloudShieldLogs')

TOPIC_ARN = 'arn:aws:sns:us-east-1:989923171840:CloudShieldAlerts'

def lambda_handler(event, context):
    params   = event.get('queryStringParameters', {}) or {}
    action   = params.get('action', '')
    user     = params.get('user', 'Unknown')
    ip       = params.get('ip', 'Unknown')
    location = params.get('location', 'Unknown')
    login_id = params.get('loginId', '')

    # Update DynamoDB with user response
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
        # Send safe confirmation email
        sns.publish(
            TopicArn=TOPIC_ARN,
            Subject='[CloudShield] ✅ Login Confirmed Safe by You',
            Message=f"""
=====================================
  CloudShield - Login VERIFIED ✅
=====================================

You confirmed this login WAS YOU. All good!

LOGIN DETAILS:
User     : {user}
IP       : {ip}
Location : {location}

No action needed. Stay safe!
=====================================
            """
        )
        return {
            'statusCode': 200,
            'headers'   : {'Content-Type': 'text/html'},
            'body'      : '''
<!DOCTYPE html>
<html>
<head>
  <style>
    body {{
        font-family: Arial;
        text-align: center;
        padding: 80px;
        background: #f0fff0;
    }}
    .box {{
        background: white;
        border-radius: 16px;
        padding: 40px;
        display: inline-block;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    }}
    h1 {{ color: #2e7d32; font-size: 3rem; }}
    p  {{ color: #555; font-size: 1.2rem; margin-top: 20px; }}
  </style>
</head>
<body>
  <div class="box">
    <h1>✅ Login Verified!</h1>
    <p>You confirmed this was <b>YOU</b>.</p>
    <p>Your AWS account is <b style="color:green">SAFE</b>.</p>
    <p style="color:#aaa; margin-top:30px;">You can close this tab.</p>
  </div>
</body>
</html>'''
        }

    elif action == 'no':
        # Send URGENT alert email
        sns.publish(
            TopicArn=TOPIC_ARN,
            Subject='[CloudShield] 🚨 URGENT: UNAUTHORIZED LOGIN CONFIRMED!',
            Message=f"""
🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨
  UNAUTHORIZED LOGIN CONFIRMED!
🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨

YOU SAID THIS LOGIN WAS NOT YOU!

INTRUDER DETAILS:
User     : {user}
IP       : {ip}
Location : {location}

TAKE THESE STEPS IMMEDIATELY:

1. DISABLE the compromised user:
   https://console.aws.amazon.com/iam/

2. ROTATE all access keys immediately

3. CHECK CloudTrail for damage:
   https://console.aws.amazon.com/cloudtrail/

4. REVIEW all recently created resources

5. CONTACT AWS Support:
   https://aws.amazon.com/support

ACT NOW — every minute counts!
=====================================
            """
        )
        return {
            'statusCode': 200,
            'headers'   : {'Content-Type': 'text/html'},
            'body'      : '''
<!DOCTYPE html>
<html>
<head>
  <style>
    body {{
        font-family: Arial;
        text-align: center;
        padding: 80px;
        background: #fff0f0;
    }}
    .box {{
        background: white;
        border-radius: 16px;
        padding: 40px;
        display: inline-block;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    }}
    h1 {{ color: #c62828; font-size: 3rem; }}
    p  {{ color: #555; font-size: 1.2rem; margin-top: 20px; }}
    .steps {{
        text-align: left;
        margin-top: 20px;
        background: #fff5f5;
        padding: 20px;
        border-radius: 8px;
        line-height: 2;
    }}
  </style>
</head>
<body>
  <div class="box">
    <h1>🚨 Alert Triggered!</h1>
    <p>You confirmed this was <b>NOT you</b>.</p>
    <p>Security alert sent to your email!</p>
    <div class="steps">
      <b>Take action NOW:</b><br>
      1. Go to IAM and disable the user<br>
      2. Rotate all access keys<br>
      3. Check CloudTrail logs<br>
      4. Contact AWS Support
    </div>
    <p style="color:#aaa; margin-top:30px;">You can close this tab.</p>
  </div>
</body>
</html>'''
        }

    else:
        return {
            'statusCode': 400,
            'headers'   : {'Content-Type': 'text/html'},
            'body'      : '<h1>Invalid action</h1>'
        }