# **Auto Scalling Face Recognition Service using AWS**

This project implements a face recognition system using **AWS EC2, S3, SQS, and boto3**. It consists of three main components:

## **1. Web Tier (`server.py`)**
- Handles HTTP `POST` requests to receive image uploads.
- Stores images in **S3 Input Bucket** (`in-bucket`).
- Sends processing requests to **SQS Request Queue** (`req-queue`).
- Polls **SQS Response Queue** (`resp-queue`) to fetch results and return them.

## **2. App Tier (`backend.py`)**
- Polls the **SQS Request Queue** for new image processing requests.
- Fetches the image from **S3 Input Bucket**.
- Runs face recognition using a deep learning model.
- Stores results in **S3 Output Bucket** (`out-bucket`).
- Sends results to **SQS Response Queue**.

## **3. Autoscaling Controller (`controller.py`)**
- Monitors the **SQS Request Queue** to scale the **App Tier** dynamically.
- Launches new **App Tier** instances (`app-tier-instance-<index>`) when needed.
- Stops instances when no pending requests remain.

## **Setup & Deployment**
1. **Set up AWS credentials** using a `.env` file:
   ```ini
   AWS_ACCESS_KEY_ID=your-access-key
   AWS_SECRET_ACCESS_KEY=your-secret-key
   AWS_REGION=us-east-1
