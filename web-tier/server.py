from flask import Flask, request
import boto3
from gevent.pywsgi import WSGIServer
from dotenv import load_dotenv
import os

load_dotenv()
REQ_QUEUE_URL = 'https://sqs.us-east-1.amazonaws.com/820242917421/1230434441-req-queue'
RESP_QUEUE_URL = 'https://sqs.us-east-1.amazonaws.com/820242917421/1230434441-resp-queue'

app = Flask(__name__)


s3 = boto3.client('s3', region_name='us-east-1')
sqs = boto3.client('sqs', region_name='us-east-1')

def get_number_of_messages():
    response = sqs.get_queue_attributes(
        QueueUrl=RESP_QUEUE_URL,
        AttributeNames=["ApproximateNumberOfMessages"]
    )
    return int(response["Attributes"]["ApproximateNumberOfMessages"])


@app.route('/', methods=['POST'])
def process_image():
	file = request.files['inputFile']
	filename = file.filename.split(".")[0]
	s3.upload_fileobj(file,"1230434441-in-bucket" , filename)

	#request sqs
	sqs.send_message(QueueUrl= REQ_QUEUE_URL, MessageBody= filename)

	#response sqs
	while True:
		number_of_messages = get_number_of_messages()
		if number_of_messages > 0:
			response = sqs.receive_message(
				QueueUrl=RESP_QUEUE_URL,
				MaxNumberOfMessages=5,
				VisibilityTimeout=0
			)
			if "Messages" in response:
				for message in response["Messages"]:
					result = message["Body"]
					if result.startswith(filename):
						receipt_handle = message["ReceiptHandle"]
						sqs.delete_message(QueueUrl=RESP_QUEUE_URL, ReceiptHandle=receipt_handle)
						print(result)
						return result, 200


app.run(host="0.0.0.0",port=8000,threaded=True)
