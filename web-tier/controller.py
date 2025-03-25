import boto3
from dotenv import load_dotenv
import time

load_dotenv()

REQ_QUEUE_URL = "https://sqs.us-east-1.amazonaws.com/820242917421/1230434441-req-queue"
MAX_INSTANCES = 14

ec2 = boto3.client("ec2", region_name='us-east-1')
sqs = boto3.client("sqs", region_name='us-east-1')


def get_number_of_messages():
    response = sqs.get_queue_attributes(
        QueueUrl=REQ_QUEUE_URL,
        AttributeNames=["ApproximateNumberOfMessages"]
    )
    return int(response["Attributes"]["ApproximateNumberOfMessages"])

def get_stopped_instances():
    response = ec2.describe_instances(
        Filters=[
            {"Name": "instance-state-name", "Values": ["stopped"]},
            {"Name": "tag:Name", "Values": ["app-tier-instance-*"]}
        ]
    )
    return [i["InstanceId"] for r in response["Reservations"] for i in r["Instances"]]

def get_running_instances():
    response = ec2.describe_instances(
        Filters=[
            {"Name": "instance-state-name", "Values": ["running", "pending"]},
            {"Name": "tag:Name", "Values": ["app-tier-instance-*"]}
        ]
    )
    return len([i for r in response["Reservations"] for i in r["Instances"]])

def launch_new_instance():
   instance_name = "app-tier-instance-" + str(get_running_instances()+1)
   instance = ec2.run_instances(
        ImageId="ami-06a722a970b69b580",
        InstanceType="t2.micro",
        MinCount=1,
        MaxCount=1,
        KeyName="cc",
	Placement={"AvailabilityZone":"us-east-1d"},
        TagSpecifications=[{
            "ResourceType": "instance",
            "Tags": [{"Key": "Name", "Value": instance_name}]
        }]
    )

def start_stopped_instance(instance_id):
    ec2.start_instances(InstanceIds=[instance_id])

def stop_idle_instances():
    response = ec2.describe_instances(
        Filters=[{"Name": "instance-state-name", "Values": ["running"]},
		 {"Name": "tag:Name", "Values": ["app-tier-instance-*"]}
		]
    )
    for reservation in response["Reservations"]:
        for instance in reservation["Instances"]:
            instance_id = instance["InstanceId"]
            ec2.stop_instances(InstanceIds=[instance_id])

def auto_scale():
    print('controller running...')
    while True:
        pending_requests = get_number_of_messages()
        running_instances = get_running_instances()

        if pending_requests > running_instances and running_instances < MAX_INSTANCES:
            stopped_instances = get_stopped_instances()
            if stopped_instances:
                start_stopped_instance(stopped_instances[0])
                print(f'stopped instance started:{stopped_instances[0]}')
            else:
                launch_new_instance()
                print('launched new instance')

        if running_instances > 0 and pending_requests == 0:
            time.sleep(1.5)
            stop_idle_instances()

auto_scale()