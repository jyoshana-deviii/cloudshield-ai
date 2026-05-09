import json
import boto3

dynamodb = boto3.resource('dynamodb')
table    = dynamodb.Table('CloudShieldLogs')

def lambda_handler(event, context):
    try:
        response = table.scan()
        items    = response.get('Items', [])

        # Sort by timestamp newest first
        items.sort(key=lambda x: x.get('timestamp', ''), reverse=True)

        return {
            'statusCode': 200,
            'headers'   : {
                'Access-Control-Allow-Origin' : '*',
                'Access-Control-Allow-Headers': '*',
                'Content-Type'               : 'application/json'
            },
            'body': json.dumps(items[:20], default=str)
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'headers'   : {
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': str(e)})
        }