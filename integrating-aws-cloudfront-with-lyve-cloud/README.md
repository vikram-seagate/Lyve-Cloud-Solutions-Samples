# Lyve Cloud integration with Amazon CloudFront

## Introduction
The following document explains how to integrate Amazon CloudFront with Lyve Cloud as the source of media content.

Fronting Lyve Cloud S3 media contents with CloudFront using Lambda allows you to cache content closer to the viewer by leveraging the globally distributed content distribution network. 

Amazon CloudFront and Lyve Cloud Object Storage are used together to improve the delivery and security of your mission critical applications. When a user requests for content through CloudFront, the request is routed to the edge location that provides the lowest latency and is delivered with optimal performance.

## How it Works
The AWS Lambda function provided in this repository returns, upon request, the content of the specified S3 object and its content type. When accessed via a CloudFront URL, the content is retrieved from CloudFront's cache, rather than performing an additional GET operation to retrieve the object from Lyve Cloud's storage.

The sequence diagram below shows how the high level data flow looks like.
<p align="center" style="text-align:left"><img alt="Figure 1: Architecture – CloudFront with Lambda as origin" src="images/data_flow.png" width="600"/></p>

## Supported Content Types
Since the AWS Lambda function retrieves the object's 'Content-Type' header and passes it along with the object's content, when the CloudFront URL is accessed through a web browser, the object will be displayed as long as the web browser supports displaying that content type while other file types such as Word documents, Excel sheets, and various other formats will be prompted to be downloaded.

Generally speaking, common file types such as images (JPEG, PNG, GIF, etc.), videos (MP4, WebM, etc.), audio (MP3, WAV, etc.) and text files (HTML, CSS, JavaScript) will be displayed within the browser.

These are the file types that were tested and successfully displayed when accessing the CloudFront URL in Microsoft Edge: MP4, HTML, TXT, PNG, JPG, and PDF.
 
## Requirements
* A Lyve Cloud Service Account with valid credentials and read permission for the bucket that holds the object to be distributed.
* An AWS account with access to the IAM, Lambda, CloudFormation, and CloudFront services.

## Known Limitations
1. The maximum object size that can be distributed is 6mb due to AWS Lambda limitations.
2. This solution provides a guide for distributing a single object which will be accessed through a CloudFront URL. Access to different objects via URL (e.g https://{cloudfront-id}.cloudfront.net/{object-name}) is not supported, although it could be added with additional development.

## Running Steps
### Step 1: Create IAM Role for AWS Service execution.
1. Login to AWS Console and navigate to **IAM** dashboard.
2. Navigate to **Roles** in the left panel under **Access Management**.
3. Click on **Create Role**. 
4. Select **AWS service** under **Trusted entity type** and **Lambda** under **Use case**. Click on **Next**.
5. Select policy **AWSLambdaBasicExecutionRole** and click on **Next**.
6. Give a name to the Role under **Role name** and click on **Create role**.

### Step 2: Create Lambda Function and Obtain the Function URL.
1. Navigate to the **AWS Lambda** console in the AWS region you want to deploy the function in.
2. Click on **Create function**.
3. Provide the function name and select **Python 3.9** under **Runtime**.  
4. Under **Permissions** click on **Change default execution role**, select **Use an existing role** and choose the role that we created in the previous step.
5. Under **Advanced settings**, check the **Enable function URL** field. Since the Lambda function needs to be publicly accessible select **NONE** for **Auth type**. This also creates the necessary resource-based policies to allow public access to the function.
6. Click **Creation function** to finish the function creation setup.
7. After the function creation process is finished, click on the **Configuration** tab and navigate to **Environmental variables** tab on left panel. 
8. Click on **edit** and add the following environmental variables and its respective values: 
  
  | Key  | Value |
  | ------------- | ------------- |
  | ACCESS_KEY  | Access Key to the Lyve Cloud S3 API  |
  | SECRET_KEY  | Secret Key to the Lyve Cloud S3 API  |
  | ENDPOINT  | Lyve Cloud S3 Endpoint URL  |
  | BUCKET_NAME  | Name of the bucket that contains the media object that you want to distribute  |
  | OBJECT_KEY  | Name of the media object that will be distributed  |
  
9. Navigate back to **Code**, copy and paste the contents of [s3_object_reader.py](code/s3_object_reader.py) into the Code source section, and click on **Deoploy**
10. Note down the Lambda Function URL as shown in below figure.
  <p align="center" style="text-align:left"><img alt="Figure 3: Lambda Function " src="images/lambda_url.png" width="600"/></p>

### Step 3: Create the Amazon CloudFront configuration.
1. Navigate to **CloudFormation** service and click on **Create Stack**.
2. Under **Prerequisite - Prepare template** opt for the option **Template is Ready**. 
3. Under **Specify template** select **Upload a template file**, click on **Choose File** and choose [CFT_Cloudfront.yml](code/CFT_Cloudfront.yml). Click on **Next**.
4. Under **Lambda Function Endpoint** enter the function URL obtained earlier as shown in below screenshot.
     <p align="center" style="text-align:left"><img alt="Figure 4: cloudfront " src="images/cloudformation.png" width="600"/></p>
     Remove https:// and trailing slash from the Function URL while providing the input.
5. Once the CloudFormation template is deployed, navigate to the **Outputs** tab of the CloudFormation stack to access the default CloudFront domain name created. You should see the media object that you stored in your bucket when the distribution domain is accessed through browser.
    <p align="center" style="text-align:left"><img alt="Figure 5: cloudfront_url " src="images/cloudfront_url.png" width="600"/></p>
     

## Results 
Hit the CloudFront URL and your local browser will open the media object that stored in your Lyve Cloud bucket.
<p align="center" style="text-align:left"><img alt="Figure 6: result  " src="images/result.png" width="600"/></p>



## Tested by
* Jan 6, 2023: Rahul Gode (rahul.gode@seagate.com)
* Jan 16, 2023: Alexander Chernin (alexander.chernin@seagate.com)

### Project Structure
```
.
├── README.md
├── code
│   └── CFT_Cloudfront.yml
│   └── s3_object_reader.py
└── images
    └── cloudformation.png
        cloudfront_url.png
        result.png
        data_flow.png
        lambda_url.png
```

### `/code`
This folder contains all the code files.

### `/images`
This folder contains all the images.