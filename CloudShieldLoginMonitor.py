import json
import boto3
import urllib.request
import urllib.parse
import uuid
import os
from datetime import datetime

sns      = boto3.client('sns')
bedrock  = boto3.client('bedrock-runtime', region_name='us-east-1')
dynamodb = boto3.resource('dynamodb')
table    = dynamodb.Table('CloudShieldLogs')

TOPIC_ARN = os.environ.get('SNS_TOPIC_ARN', 'arn:aws:sns:us-east-1:989923171840:CloudShieldAlerts')
API_URL   = os.environ.get('API_URL', 'https://vz3hnf6n5f.execute-api.us-east-1.amazonaws.com')

def get_ip_location(ip):
    try:
        req  = urllib.request.urlopen(f"http://ip-api.com/json/{ip}", timeout=5)
        data = json.loads(req.read().decode())
        if data['status'] == 'success':
            return f"{data['city']}, {data['regionName']}, {data['country']}"
        return "Unknown"
    except:
        return "Unknown"

def analyze_with_bedrock(user, ip, location):
    try:
        prompt = f"""You are a cloud security expert. Analyze this AWS login event:
User: {user}
IP Address: {ip}
Location: {location}

Respond in exactly this format:
Risk Level: [Low or High]
Reason: [one sentence explanation]
Action: [what to do]
Decision: [SAFE or SUSPICIOUS]

Rules:
- India location + IAM user = Low risk, SAFE
- Private IPs 10.x 192.168.x = Low risk, SAFE
- Root account login = High risk, SUSPICIOUS
- Foreign country IP = High risk, SUSPICIOUS
- Unknown location = Low risk, SAFE"""

        native_request = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 512,
            "messages": [
                {
                    "role": "user",
                    "content": [{"type": "text", "text": prompt}]
                }
            ]
        }

        response = bedrock.invoke_model(
            modelId='us.anthropic.claude-haiku-4-5-20251001-v1:0',
            contentType='application/json',
            accept='application/json',
            body=json.dumps(native_request)
        )
        model_response = json.loads(response['body'].read())
        return model_response['content'][0]['text']

    except Exception as e:
        location_lower = location.lower()
        if 'india' in location_lower or 'unknown' in location_lower:
            return f"Risk Level: Low\nReason: Login from {location}.\nAction: No action needed.\nDecision: SAFE"
        else:
            return f"Risk Level: High\nReason: Login from foreign location {location}.\nAction: Verify immediately.\nDecision: SUSPICIOUS"

def parse_decision(ai_verdict):
    verdict_lower = ai_verdict.lower()
    if 'suspicious' in verdict_lower or 'high' in verdict_lower:
        return 'SUSPICIOUS'
    return 'SAFE'

def lambda_handler(event, context):
    detail        = event.get("detail", {})
    source_ip     = detail.get("sourceIPAddress", "Unknown")
    event_name    = detail.get("eventName", "Unknown")
    event_time    = detail.get("eventTime", datetime.utcnow().isoformat())
    aws_region    = detail.get("awsRegion", "Unknown")
    user_identity = detail.get("userIdentity", {})
    user          = user_identity.get("arn", user_identity.get("userName", "Unknown"))
    user_type     = user_identity.get("type", "IAMUser")

    location   = get_ip_location(source_ip)
    ai_verdict = analyze_with_bedrock(user, source_ip, location)
    decision   = parse_decision(ai_verdict)

    login_id = str(uuid.uuid4())
    table.put_item(Item={
        'loginId'  : login_id,
        'timestamp': event_time,
        'user'     : user,
        'userType' : user_type,
        'ip'       : source_ip,
        'location' : location,
        'event'    : event_name,
        'region'   : aws_region,
        'aiVerdict': ai_verdict,
        'decision' : decision
    })

    yes_url = f"{API_URL}/verify?" + urllib.parse.urlencode({
        'action': 'yes', 'user': user,
        'ip': source_ip, 'location': location, 'loginId': login_id
    })
    no_url = f"{API_URL}/verify?" + urllib.parse.urlencode({
        'action': 'no', 'user': user,
        'ip': source_ip, 'location': location, 'loginId': login_id
    })

    subject = '[CloudShield] SUSPICIOUS Login Detected!' if decision == 'SUSPICIOUS' \
              else '[CloudShield] New Login - Was it you?'

    message = f"""CloudShield AI Security Alert
=====================================
User     : {user}
User Type: {user_type}
Location : {location}
IP       : {source_ip}
Decision : {decision}
Time     : {event_time}

AI Analysis:
{ai_verdict}

Was this you?
YES - It was me : {yes_url}
NO - Not me     : {no_url}
=====================================
Powered by CloudShield + Amazon Bedrock"""

    sns.publish(TopicArn=TOPIC_ARN, Subject=subject, Message=message)
    return {'statusCode': 200, 'body': 'Done'}
