from face_recognition import face_match
import sys
import boto3
from dotenv import load_dotenv

load_dotenv()

S3_INPUT_BUCKET = "1230434441-in-bucket"
S3_OUTPUT_BUCKET = "1230434441-out-bucket"
REQ_QUEUE_URL = "https://sqs.us-east-1.amazonaws.com/820242917421/1230434441-req-queue"
RESP_QUEUE_URL = "https://sqs.us-east-1.amazonaws.com/820242917421/1230434441-resp-queue"

s3 = boto3.client("s3", region_name="us-east-1")
sqs = boto3.client("sqs", region_name="us-east-1")

def get_number_of_messages():
    response = sqs.get_queue_attributes(
        QueueUrl=REQ_QUEUE_URL,
        AttributeNames=["ApproximateNumberOfMessages"]
    )
    return int(response["Attributes"]["ApproximateNumberOfMessages"])


def process_request():
	if get_number_of_messages() > 0:
		response = sqs.receive_message(
		    QueueUrl=REQ_QUEUE_URL,
		    MaxNumberOfMessages=1
		)

		if "Messages" in response:
			for message in response["Messages"]:
				receipt_handle = message["ReceiptHandle"]
				filename = message["Body"]
				print(filename)

				s3.download_file(S3_INPUT_BUCKET, filename, filename)

				prediction = face_match(filename, "/home/ubuntu/backend/data.pt")[0]
				print(prediction)

				s3.put_object(Bucket=S3_OUTPUT_BUCKET, Key=filename, Body=prediction)

				sqs.send_message(QueueUrl=RESP_QUEUE_URL,MessageBody=f"{filename}:{prediction}")

				sqs.delete_message(QueueUrl=REQ_QUEUE_URL, ReceiptHandle=receipt_handle)


while True:
	process_request()
