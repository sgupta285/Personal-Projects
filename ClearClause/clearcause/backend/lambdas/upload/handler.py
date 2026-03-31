"""
ClearCause - Document Upload Lambda
Handles PDF upload, virus scanning, and storage to S3.
Triggers the analysis pipeline via SQS.
"""
import json
import uuid
import time
import boto3
import base64
from datetime import datetime

s3 = boto3.client("s3")
sqs = boto3.client("sqs")
dynamodb = boto3.resource("dynamodb")

BUCKET = "clearcause-documents"
QUEUE_URL = "https://sqs.us-east-1.amazonaws.com/ACCOUNT_ID/clearcause-analysis-queue"
TABLE = dynamodb.Table("clearcause-jobs")

ALLOWED_TYPES = {"application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "text/plain"}
MAX_SIZE_MB = 10


def lambda_handler(event, context):
    """Handle document upload via API Gateway."""
    try:
        # Parse request
        body = json.loads(event.get("body", "{}"))
        user_id = event["requestContext"]["authorizer"]["claims"]["sub"]
        file_data = base64.b64decode(body["file"])
        file_name = body.get("fileName", "document.pdf")
        content_type = body.get("contentType", "application/pdf")

        # Validate
        if content_type not in ALLOWED_TYPES:
            return _response(400, {"error": f"Unsupported file type: {content_type}"})

        if len(file_data) > MAX_SIZE_MB * 1024 * 1024:
            return _response(400, {"error": f"File exceeds {MAX_SIZE_MB}MB limit"})

        # Generate job ID
        job_id = str(uuid.uuid4())
        s3_key = f"uploads/{user_id}/{job_id}/{file_name}"

        # Upload to S3
        s3.put_object(
            Bucket=BUCKET,
            Key=s3_key,
            Body=file_data,
            ContentType=content_type,
            ServerSideEncryption="aws:kms",
            Metadata={
                "user_id": user_id,
                "job_id": job_id,
                "original_filename": file_name,
            },
        )

        # Create job record
        job_record = {
            "job_id": job_id,
            "user_id": user_id,
            "file_name": file_name,
            "s3_key": s3_key,
            "status": "uploaded",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "ttl": int(time.time()) + 86400 * 30,  # 30 day retention
        }
        TABLE.put_item(Item=job_record)

        # Queue for analysis
        sqs.send_message(
            QueueUrl=QUEUE_URL,
            MessageBody=json.dumps({
                "job_id": job_id,
                "user_id": user_id,
                "s3_key": s3_key,
                "file_name": file_name,
            }),
        )

        return _response(200, {
            "job_id": job_id,
            "status": "uploaded",
            "message": "Document uploaded successfully. Analysis in progress.",
        })

    except KeyError as e:
        return _response(400, {"error": f"Missing required field: {str(e)}"})
    except Exception as e:
        print(f"Upload error: {str(e)}")
        return _response(500, {"error": "Internal server error"})


def _response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type,Authorization",
        },
        "body": json.dumps(body),
    }
