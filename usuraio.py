import boto3
import hashlib
import json

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def lambda_handler(event, context):
    try:
        user_id = event.get('user_id')
        password = event.get('password')
        
        if user_id and password:
            hashed_password = hash_password(password)
            dynamodb = boto3.resource('dynamodb')
            t_usuarios = dynamodb.Table('t_usuarios')
            t_usuarios.put_item(
                Item={
                    'user_id': user_id,
                    'password': hashed_password,
                }
            )
            mensaje = {
                'message': 'Usuario creado',
                'user_id': user_id
            }
            return {
                'statusCode': 200,
                'body': json.dumps(mensaje)
            }
        else:
            mensaje = {
                'error': 'user_id and password are required'
            }
            return {
                'statusCode': 400,
                'body': json.dumps(mensaje)
            }
    except Exception as e:
        mensaje = {
            'error': 'An error occurred',
            'details': str(e)
        }
        return {
            'statusCode': 500,
            'body': json.dumps(mensaje)
        }
