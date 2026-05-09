import json
import boto3

CLIENT_ID ='593rqnm2smj1lfganm9cnhaigb'

client = boto3.client('cognito-idp', region_name='us-east-1')

def lambda_handler(event, context):
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,Authorization',
        'Access-Control-Allow-Methods': 'POST,OPTIONS'
    }
    
    if event.get('httpMethod') == 'OPTIONS':
        return {'statusCode': 200, 'headers': headers, 'body': ''}
    
    try:
        body = json.loads(event.get('body', '{}'))
        email = body.get('email', '').strip()
        password = body.get('password', '')
        
        response = client.initiate_auth(
            ClientId=CLIENT_ID,
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={'USERNAME': email, 'PASSWORD': password}
        )
        
        token = response['AuthenticationResult']['IdToken']
        return {'statusCode': 200, 'headers': headers, 'body': json.dumps({'message': 'Login successful', 'token': token, 'email': email})}
        
    except client.exceptions.NotAuthorizedException:
        return {'statusCode': 401, 'headers': headers, 'body': json.dumps({'message': 'Incorrect email or password.'})}
    except client.exceptions.UserNotFoundException:
        return {'statusCode': 404, 'headers': headers, 'body': json.dumps({'message': 'No account found. Please sign up first.'})}
    except Exception as e:
        return {'statusCode': 500, 'headers': headers, 'body': json.dumps({'message': str(e)})}