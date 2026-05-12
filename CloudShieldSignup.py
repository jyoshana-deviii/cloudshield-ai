import json
import boto3
import os

USER_POOL_ID = os.environ.get('USER_POOL_ID', 'us-east-1_R7rctkxXd')
CLIENT_ID    = os.environ.get('CLIENT_ID', '593rqnm2smj1lfganm9cnhaigb')
client       = boto3.client('cognito-idp', region_name='us-east-1')

def lambda_handler(event, context):
    headers = {
        'Access-Control-Allow-Origin' : '*',
        'Access-Control-Allow-Headers': 'Content-Type,Authorization',
        'Access-Control-Allow-Methods': 'POST,OPTIONS'
    }

    if event.get('httpMethod') == 'OPTIONS':
        return {'statusCode': 200, 'headers': headers, 'body': ''}

    try:
        body     = json.loads(event.get('body', '{}'))
        email    = body.get('email', '').strip()
        password = body.get('password', '')

        if not email or not password:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'message': 'Email and password are required.'})
            }

        if len(password) < 8:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'message': 'Password must be at least 8 characters.'})
            }

        client.sign_up(
            ClientId=CLIENT_ID,
            Username=email,
            Password=password,
            UserAttributes=[{'Name': 'email', 'Value': email}]
        )

        client.admin_confirm_sign_up(
            UserPoolId=USER_POOL_ID,
            Username=email
        )

        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({'message': 'Account created successfully!'})
        }

    except client.exceptions.UsernameExistsException:
        return {
            'statusCode': 400,
            'headers': headers,
            'body': json.dumps({'message': 'Email already exists. Please login.'})
        }
    except client.exceptions.InvalidPasswordException:
        return {
            'statusCode': 400,
            'headers': headers,
            'body': json.dumps({'message': 'Password must be 8+ chars with uppercase, lowercase and number.'})
        }
    except client.exceptions.InvalidParameterException:
        return {
            'statusCode': 400,
            'headers': headers,
            'body': json.dumps({'message': 'Invalid email format.'})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'message': str(e)})
        }
