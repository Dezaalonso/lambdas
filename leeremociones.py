import json
import boto3
import logging
import uuid
from datetime import datetime

s3 = boto3.client('s3')
rekognition = boto3.client('rekognition')
dynamodb = boto3.client('dynamodb')

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    logger.info("Received event: %s", json.dumps(event))
    
    try:
        username = event['username']
        image_name = event['image_name']
        
        s3_key = f"{username}/{image_name}"
        
        s3_response = s3.get_object(Bucket='proyecto-final-cloud', Key=s3_key)
        image_bytes = s3_response['Body'].read()
        
        rekognition_response = rekognition.detect_faces(
            Image={'Bytes': image_bytes},
            Attributes=['ALL']
        )

        emotions = []
        for faceDetail in rekognition_response['FaceDetails']:
            face_emotions = {emotion['Type']: emotion['Confidence'] for emotion in faceDetail['Emotions']}
            emotions.append(face_emotions)
        
        # Save the response to DynamoDB
        request_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        
        item = {
            'request_id': {'S': request_id},
            'Username': {'S': username},
            'ImageName': {'S': image_name},
            'Emotions': {'S': json.dumps(emotions)},
            'Timestamp': {'S': timestamp}
        }
        
        dynamodb.put_item(
            TableName='t_emociones',
            Item=item
        )

        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Emotions detected and saved successfully', 'request_id': request_id, 'emotions': emotions})
        }
    except Exception as e:
        logger.error("Error processing request: %s", str(e))
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'Error processing request', 'error': str(e)})
        }
