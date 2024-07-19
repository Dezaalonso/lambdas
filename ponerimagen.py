import json
import boto3
import base64
import logging
import os

s3 = boto3.client('s3')
bucket_name = 'proyecto-final-cloud'

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    logger.info("Received event: %s", json.dumps(event))
    
    try:
        username = event['username']
        image_data = event['image_data']
        image_name = event['image_name']
        
        logger.info("Decoding base64 image data.")
        image_bytes = base64.b64decode(image_data)
        logger.info("Successfully decoded base64 image data.")
        
        local_file_path = f"/tmp/{image_name}"
        with open(local_file_path, 'wb') as image_file:
            image_file.write(image_bytes)
        logger.info("Image saved to local file.")
        
        s3_key = f"{username}/{image_name}"
        s3.upload_file(local_file_path, bucket_name, s3_key, ExtraArgs={'ContentType': 'image/jpeg'})
        
        os.remove(local_file_path)
        
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Imagen subida correctamente', 's3_key': s3_key})
        }
    except Exception as e:
        logger.error("Error processing request: %s", str(e))
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'Error con la imagen', 'error': str(e)})
        }
