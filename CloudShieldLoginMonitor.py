import json
import boto3
import urllib.request
import urllib.parse
import uuid
from datetime import datetime

sns = boto3.client('sns')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('CloudShieldLogs')

TOPIC_ARN = 'arn:aws:sns:us-east-1:989923171840:CloudShieldAlerts'
API_URL = 'https://vz3hnf6n5f.execute-api.us-east-1.amazonaws.com'

def get_ip_location(ip):
    try:
        req = urllib.request.urlopen(f"http://ip-api.com/json/{ip}", timeout=5)
        data = json.loads(req.read().decode())
        if data['status'] == 'success':
            return f"{data['city']}, {data['country']}"
        return "Unknown"
    except:
        return "Unknown"

def parse_decision(location):
    loc = location.lower()
    if 'india' in loc:
        return 'SAFE'
    if 'unknown' in loc:
        return 'SAFE'
    return 'SUSPICIOUS'

def lambda_handler(event, context):
    detail = event.get("detail", {})
    source_ip = detail.get("sourceIPAddress", "Unknown")
    event_name = detail.get("eventName", "Unknown")
    event_time = detail.get("eventTime", datetime.utcnow().isoformat())
    aws_region = detail.get("awsRegion", "Unknown")
    user_identity = detail.get("userIdentity", {})
    user = user_identity.get("arn", "Unknown")

    location = get_ip_location(source_ip)
    decision = parse_decision(location)
    ai_verdict = f"Login from {location}. Decision: {decision}."

    login_id = str(uuid.uuid4())
    table.put_item(Item={
        'loginId': login_id,
        'timestamp': event_time,
        'user': user,
        'ip': source_ip,
        'location': location,
        'event': event_name,
        'region': aws_region,
        'aiVerdict': ai_verdict,
        'decision': decision
    })

    yes_url = f"{API_URL}/verify?" + urllib.parse.urlencode({'action':'yes','user':user,'ip':source_ip,'location':location,'loginId':login_id})
    no_url = f"{API_URL}/verify?" + urllib.parse.urlencode({'action':'no','user':user,'ip':source_ip,'location':location,'loginId':login_id})

    subject = '[CloudShield] SUSPICIOUS Login Detected!' if decision == 'SUSPICIOUS' else '[CloudShield] New Login - Was it you?'
    message = f"""CloudShield Security Alert
User: {user}
Location: {location}
IP: {source_ip}
Decision: {decision}
Time: {event_time}

Was this you?
YES: {yes_url}
NO: {no_url}"""

    sns.publish(TopicArn=TOPIC_ARN, Subject=subject, Message=message)
    return {'statusCode': 200, 'body': 'Done'}
