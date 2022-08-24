# CloudWatch – how to send Lyve Cloud Audit Logs to AWS CloudWatch

## Introduction
This integration solution sends Lyve Cloud API Audit Log events to be consumed and displayed in AWS CloudWatch.
The procedure will continuously send Lyve Cloud API Audit Logs to AWS CloudWatch. AWS CloudWatch collects monitoring and operational data in the form of audit logs, metrics, and events and provides you with actionable insights to improve your IT operations using S3 storage.

### How it Works
The process runs each round hour by a cron job. The audit logs are uploaded to a log stream which is created by this integration, inside a log group which is provided by the user.
Each iteration it pulls from Lyve Cloud the necessary audit logs, and sends them in chunks to a CloudWatch.

### Integration Modes
You will have to [specify the mode](#step-4-set-up-your-environment) in which the integration will run. You can choose one of the following modes:
1. Pull and upload all existing audit logs. On the first iteration the integration will start pulling all existing audit logs. From the second iteration the integration will collect and upload new audit logs only.
2. Pull and upload existing audit logs from a specific date. On the first iteration the integration will start pulling audit logs from the specified date. From the second iteration the integration will collect and upload new audit logs only.
3. Every hour, the integration will scan for new audit logs only and upload them to CloudWatch. (Without uploading audit logs created before the start time of this integration)

#### Notes
* Audit logs that were created before the integrations start time will be uploaded to a log stream named "lyve_fromdate_LogType_audit_logs".<br>
* New audit logs from last hour will be uploaded to a log stream name "lyve_lasthour_LogType_audit_logs".
* Prevention of duplicates is ensured in all modes.
* [Click here](documentation/configExamples.md) to find configuration examples.

### Logging
In order to monitor the integration activity, the itegration creates and uploads its own logs to a unique log streams. For example, if you choose to pull S3 logs from a specific date, the integration will send its self created logs to a stream named "lyve_fromdate_integration_logs_S3" for all the logs that were uploaded to CloudWatch and were created before integration's start time. Information about logs that were created after the integration's start time will be logged to a stream named "lyve_lasthour_integration_logs_S3". On a successful pull and upload attempt, it will log a message "Finished Uploading: LogName.gz". In case of a failure, it will log the failure cause. Example log for successful upload:
```
{
  "integration-log": "Finished Uploading: February-2022/S3-logs0001-2022-02-28-21-35-08.gz"
}
```

## Requirements
Before you start, please make sure you have these requirements and information in place:
* [`Python 3`](https://www.python.org/downloads/) and above is required.
* [`Docker 20.10`](https://docs.docker.com/get-docker/) and above.
* Lyve Cloud access and secret keys. These can be obtained from the Lyve Cloud Console by creating a new Service Account to be used by this solution.
* Bucket which contains audit logs.
* IAM user with CloudWatchAgentServerPolicy to AWS CloudWatch.

## Known Limitations
This repository provides sample code to show how API audit Logs can be pulled from Lyve Cloud into AWS CloudWatch, but it’s by no means a complete solution. 
There are limitations and functionality gaps to handle before this sample code can be used in a production environment:
* This integration solution sequentially processes API audit logs from a single tenant.
* In case of a crash, there's no implemented mechanism that recovers lost audit logs that were not uploaded during the crash period.
* More than one instance of the integration with the same configuration for audit logs type(S3/Console/IAM) can't upload audit logs to the same log group.
* If an attempt is made to pull too many logs, the integration may crash. For example, the integration uses Python's [list object](https://svn.python.org/projects/python/trunk/Objects/listobject.c?revision=69227&view=markup) to hold the names of the pulled gz files, whose constraint in the 32-bit system is 536,870,912 elements.

## Running Steps
### Step 1: Get your Lyve Cloud bucket credentials for use with CloudWatch.
Here's what you'll need:
* Access Key
* Secret key
* Region

### Step 2: Generate AWS keys for CloudWatch
1. Login to AWS and go over to [IAM](https://console.aws.amazon.com/iamv2/home).
2. Click on the "Users" tab.
3. Click "Add Users".
4. Enter any username you would like. Under the "Select AWS access type" select "Access key - Programmatic access".
5. In the permissions page, select "Attach existing policies directly".
6. Search for "CloudWatchFullAccess" and select it. **Warning: this policy will provide access to all CloudWatch. To limit access, you can read more about IAM policies for CloudWatch [here](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/iam-identity-based-access-control-cw.html)**.
7. Click "Next: Tags".
8. Click "Next: Review".
9. Click "Create user".
10. Your keys are now generated, copy the "Access Key ID" and "Secret access key". These will be used to upload the audit logs into CloudWatch.

### Step 3: Create CloudWatch log group
1. In the AWS console go over to CloudWatch. **Important: notice the region you are on and using. It is critical for configuration.**
2. Select "Log groups".
3. Click on "Create log group".
4. Provide a name for your log group.
5. Click on "Create". **Save this name! You will need it for configuration**.

### Step 4: Set up your environment
1. Edit config.json file
    * bucket_name - The name of the bucket from which the audit logs will be taken.
    * log_type - The type of audit logs to be captured (S3/IAM/Console).
    * mode - The mode in which the integration will run. keep empty for new audit logs only, "all" for all existing audit logs, or specify a date in a format "mm/dd/yy".
    * log_group - Name of the log group in CloudWatch

	Examples of different ways to configure config.json file and their expected results can be viewed [here](documentation/configExamples.md).

2. Run `docker build -f Dockerfile -t logscollector .`
3. Run
      ```bash
   docker run -d \
	-e LYVE_ACCESS=lyve cloud access key \
	-e LYVE_SECRET=lyve cloud secret key \
	-e LYVE_REGION=lyve cloud region \
	-e AWS_ACCESS=aws access key \
	-e AWS_SECRET=aws secret key \
	-e AWS_REGION=aws region \
 	logscollector
      ```

### Step 5: Set up CloudWatch dashboard
1. Go to AWS CloudWatch.
2. Select "Dashboards".
3. Click "Create Dashboard".
4. Name your dashboard and click "Create dashboard".
5. A popup will appear, if you would like to create your own dashboard, you can do so from here. If you would like to use a template, choose from the `dashboards` and continue from here.
6. Click "Cancel".
7. open the dashboard file you would like to use under and replace the fields written with `<>`.
8. Click on "Actions" -> "View/Edit source".
9. Delete anything in the textboxt and copy the source from the dashboard file.

## Results 
After a successful implementation you should see the following dashboard using the [following file](documentation/dashboards/requests_count.json):
![CloudWatch Dashboard](images/operationsDashboard.png)
* [Click here](documentation/dashboards/) to find more examples for a dashboard configuration.
* [Click here](documentation/queryExamples.md) to find more queries examples.

## Tested by:
* December 12, 2021: Avi Wolicki on Linux
* December 12, 2021: Yinnon Hadad on Linux
* March 23, 2022: Bari Arviv (bari.arviv@seagate.com) on CentOS
* June 26, 2022: Alexander Chernin (alexander.chernin@seagate.com) on Ubuntu 20.04

### Project Structure
This section will describe the representation of each of the folders or files in the structure.
```
.
├── README.md
├── documentation
│   └── dashboards
|       └── dashboards
|           └── requests_count.json
|           └── failed_status.json
|           └── README.md
|   └── configExamples.md
|   └── queryExamples.md
├── services
│   └── pull_and_upload_logs_service.py
├── requirements.txt
├── engine.py
├── config.json
├── run-crond.sh
└── .gitignore
```

### `/documentation`
This folder contains different examples of dashboards that can be imported to CloudWatch, examples of queries for CloudWatch insights, and examples of diffrent way to configure config.json file.

### `/services`
This folder contains the scripts that are used for fetching and uploading the audit logs.

### `/images`
Contains images for the documentation.

