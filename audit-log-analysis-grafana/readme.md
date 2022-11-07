# Log Gateway

![flow.png](doc/flow.png)

# Introduction

This solution sends Lyve Cloud S3 API Audit Log events to be consumed and displayed in Grafana dashboard.

# Prerequisites

- 1 Physical server or VM (Linux / Window) with Docker
- [`Python 3`](https://www.python.org/downloads/) and above is required.
- Lyve Cloud access and secret keys. These can be obtained from the Lyve Cloud Console by creating a new Service Account to be used by this solution.
- [`InfluxDB 2.0`](https://docs.influxdata.com/influxdb/v2.0/)
- [`Grafana`](https://grafana.com/docs/grafana/latest/)

# Install InfluxDB

On your server with Docker installed, Run this command below

```Shell
docker run -d --name influxdb -p 8086:8086 influxdb:2.0.9
```

Test by go to [localhost:8086](http://localhost:8086).

See more information [ `here` ](https://docs.influxdata.com/influxdb/v2.0/install/?t=Docker)

# Install Grafana
Download the Installer for your machine [`here`](https://grafana.com/grafana/download)

# Known Limitations

There are limitations and functionality gaps to handle before this sample code can be used in a production environment:

- This solution pulls new generated S3 API Audit Logs from Lyve Cloud once an hour. Notice, S3 API Audit Logs generated before the application is started will not be pulled.
- Credentials are kept in a clear text.
- The max month of the S3 Audit logs date shown in Grafana depends on the limitation of influxdb bucket which has maximum period only 30 days.

# Running Steps

### **Step 1: Get your Lyve Cloud bucket credentials**

Here's what you'll need:

- Access Key
- Secret key
- Bucket name
- Endpoint URL

### **Step 2: Set up InfluxDB**

With InfluxDB running, visit [localhost:8086](http://localhost:8086).

**Set up your initial user**

1. Click Get Started

![influx1.png](doc/influx1.png)

2. Enter a Username for your initial user.
3. Enter a Password and Confirm Password for your user.
4. Enter your initial Organization Name.
5. Enter your initial Bucket Name.
6. Click Continue.

> **Note**  
> An organization is a workspace for a group of user requiring access to time series data, dashboards. and other resources. You can create organizations for different functional group, teams, or projects.
>
> A bucket is where your time series data is stores with a retention policy, It's an InfluxDB Bucket, not a LyveCloud Bucket.
>
> In this initial phase, the Bucket is used to hold analytical data such as InfluxDB performance data however, we must create another Bucket to store LyveCloud S3 API Audit log data by following the Step to **Set up a S3 API Audit Log Bucket** below.

![influx2.png](doc/influx2.png)

7. Click Quick Start

![influx3.png](doc/influx3.png)

**Set up S3 API Audit log bucket**

1. In the "Data" icon, Click on the "Buckets" tab.
2. Click on "Create Bucket" button.
3. Provide the "Name" for the bucket (We recommend using the same name as the S3 API Audit log bucket in Lyve Cloud).

![influx5.png](doc/influx5.png)

4. In the "Data" icon, Click on the "Tokens" tab.
5. Click on "Generate Token" button, and Select "Read/Write Token".
6. Provide the "Description" for the token.
7. Scope the bucket for the token, Click on the "Save" button.

![influx6.png](doc/influx6.png)

8. Click on the created token name to see a token and you can click on the "Copy to Clipboard" button to use it.

![influx7.png](doc/influx7.png)

<!-- 9. Use "Organization Name", "Bucket Name" and "Token" in `config.yaml` -->

### Set up your config.yaml configuaration

Fill in the relevant configurations under the root `influxdb:` section.

- host: The host name or IP of the server with influxdb installed.
- token: The token that you already generated on step above.
- org: The Organization name.
- bucket: The InfluxDB Bucket name.

```yaml
lyvecloud: ...

datasources:
  - influxdb

influxdb:
  host: 'http://explicit ip of running machine:8086'
  token: 'token from influx'
  org: 'STX-Lyve-Demo'
  bucket: 'Demo-Lyve-Logs'
```

<!-- ![influx-setup.png](doc/influx-setup.png) -->

### **Step 3: Pulling Log Data into InfluxDB**

### Option 1 
### Streaming Data

The application will operate in `Streaming mode` by default.
The schedule will begin at minute 0 of each hour.

Streaming mode will continue load data from Lyve Cloud S3 API AuditLog bucket to influxdb after start application

**In case** you need to change a schedule, You can edit the `Streaming` function in `main.py`

On this line
```python
scheduler.add_job(executor.run,trigger='cron',minute='0',hour='*')
```
Follow this [`link`](https://apscheduler.readthedocs.io/en/3.x/modules/triggers/cron.html) for more information about `cron`

### Option 2 
### One Time Pulling (Manual adjust period)

This feature is for pulling data from Lyve Cloud S3 API Auditlog bucket to influxdb manually by input specific period.

As **Known Limitations** 
>S3 API AuditLogs generated before the application is started will not be pulled.

If you want to pulling the S3 API Auditlog before the application start, You need to run `OnetimePulling` function in `main.py` 

```python
def OnetimePulling():
   from_date = datetime.now(timezone.utc) - timedelta(hours=3)
   executor.run(from_date)

if __name__ == '__main__':
    # Streaming()
    OnetimePulling()
```
As the example code above the Application will pull the S3 API Audit logs that generated 3 hours ago.

You need to edit the the `timedelta` function to the time period for which you wish to pull the S3 API Audit logs.

> **Note:** The `OnetimePulling` function is not a scheduler, Don't use it in a production

### In case, you want to see if any S3 API Audit logs were received in influxdb.

![influx-explore-data.png](doc/influx-explore-data.png)

1. Select "Explore"
2. Select "Table"
3. Select your S3 API Audit logs bucket
4. Change the period to Past 30 Day
5. Click "Submit"

### **Step 4: Set up S3 API Audit Log Gateway service on your environment**

There are 2 options to run the S3 API Audit Log Gateway service. you can select each of one below

**Start service with python program:**

1.  Download project into your local and extract .zip file
2.  Update the config.yaml file - [`setup config`](#setup-your-config.yaml-configuaration)
3.  Install all required packages:
    ```Shell
    pip3 install -r requirements.txt
    ```
4.  Fill in the relevant configurations in `config.yaml`.
5.  Run main program for start get S3 API Audit logs data from LyveCloud
    ```Shell
    python3 main.py
    ```

**Start service with Docker:**

If you don't have docker engine in your local environment, we recommmend to install the docker engine first by following the instruction from [`docker website`](https://docs.docker.com/engine/install/).

1.  Download project into your local and extract .zip file
2.  Update the config.yaml file - [`setup config`](#set-up-your-config.yaml-configuaration)
3.  Build a docker image
after going over "# Install InfluxDB steps" 
cd to main directory, a.k.a : .../audit-log-analysis-grafana
and run the folowing commands.

      1. Build Dockerfile
      ```Shell
      docker build -f Dockerfile -t loggateway .
      ```
      2. Create network. 
      ```Shell
      docker network create lyve-net
      ```
      3. Add influxdb in to a network
      ```Shell
      docker network connect lyve-net influxdb
      ```
      4. Finally run the docker with specify network
      ```Shell
      docker run -it --rm --net lyve-net loggateway:latest
      ```
 


> **Note:** To run the application in detached mode, include the -d flag in the docker run command.

### **Step 5: Set up Grafana data source**

Go to [localhost:3000](http://localhost:3000)

1. In the "Configuration" menu, Click on the "Add data source" button.

   ![grafana-e-1.png](doc/grafana-e-1.png)

   ![grafana-e-2.png](doc/grafana-e-2.png)

2. Click on "InfluxDB".

   ![grafana-e-3.png](doc/grafana-e-3.png)

3. Provide the name of the data source.

   ![grafana-datasource-1.png](doc/grafana-datasource-1.png)

4. Change the Query Language to Flux query language.

   ![grafana-datasource-2.png](doc/grafana-datasource-2.png)

5. Fill in "URL", "Organization", "Token" and "Bucket Name" of InfluxDB same as `config.yaml`.

   ![grafana-datasource-3.png](doc/grafana-datasource-3.png)

   ![grafana-datasource-4.png](doc/grafana-datasource-4.png)

6. Click on "Save & test" button

### **Step 6: Create Lyve Cloud S3 API Audit Logs Analysis Using Grafana Dashboard**

From Lyve Cloud audit logs bucket it stores
[`Console logs`](https://help.lyvecloud.seagate.com/en/console-audit-log.html#example-of-a-console-audit-log)
,
[`IAM logs`](https://help.lyvecloud.seagate.com/en/console-audit-log.html#example-of-an-iam-audit-log)
and
[`S3 logs`](https://help.lyvecloud.seagate.com/en/s3-api-audit-logs.html#example-of-s3-api-audit-logs)

Create simple dashboard for analysis and monitoring
- Average response time by API per day
- API time to response by bucket
- API Call by bucket per day
- Error count by bucket per day
- Total API call by bucket
- Max API Response time



1. In the "Dashboards" menu, Click on "manage" or "browse".

   ![grafana-dashboard-1.png](doc/grafana-dashboard-1.png)

2. Click on "New Dashboard".

   ![grafana-dashboard-2.png](doc/grafana-dashboard-2.png)

3. Click on "Add an empty panel".

   ![grafana-dashboard-3.png](doc/grafana-dashboard-3.png)

4. Select chart type "Time series"
   
   ![Grafana_x_1.png](doc/Grafana_x_1.png)

   ![Grafana_x_2.png](doc/Grafana_x_2.png)

5. Select the data source

   ![Grafana_x_3.png](doc/Grafana_x_3.png)

6. Fill in a query
      ```
         from(bucket: "Demo-Lyve-Logs")
         |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
         |> filter(fn: (r) => r["_measurement"] == "audit-01")
         |> filter(fn: (r) => r["_field"] == "auditEntry.api.timeToResponse")
         |> filter(fn: (r) => r["auditEntry.api.bucket"] != "")
         |> group(columns: ["auditEntry.api.name"])
         |> aggregateWindow(every: 1d, fn: mean, createEmpty: false)
         |> map(fn: (r) => ({ r with _value: r["_value"]/1000000.0 }))
         |> yield()

      ```
   > **Note:** You may view the language's documentation here [`Flux query language`](https://docs.influxdata.com/flux/v0.x/get-started/query-basics/)

7. Change the time range to cover your S3 API Audit log data.

   ![Grafana_f_1.png](doc/Grafana_f_1.png)

8. Now, you can see the line chart. This is an API Response time.

   ![Grafana_f_2.png](doc/Grafana_f_2.png)

9. Add the panel title

      ![Grafana_f_3.png](doc/Grafana_f_3.png)

      **Result**

      ![Grafana_f_4.png](doc/Grafana_f_4.png)

10. In the "Standard options" section, Change the "Unit" to Time > milliseconds (ms)

      ![Grafana_x_10.png](doc/Grafana_x_10.png)

      **Result**

      ![Grafana_f_5.png](doc/Grafana_f_5.png)

> **Note:** You may view the documentation about setting a chart on Grafana here [`Visualization panels`](https://grafana.com/docs/grafana/latest/visualizations/)

11. When you're through with your visualization design, click "Apply".

      ![grafana-dashboard-6.png](doc/grafana-dashboard-6.png)

      **Result**

      ![Grafana_f_6.png](doc/Grafana_f_6.png)      


      From S3 S3 API Audit log it store API name and time to response. We use this data to create a timeline chart to show the average response time as milliseconds by API per day.


12. Add a new chart panel to describe more about which bucket is take more time to response.

      In this example, we need to describe the CompleteMultipartUpload API that take 2.03 seconds to response.
      
      ![Grafana_f_7.png](doc/Grafana_f_7.png)

      12.1 Click on "Add panel" button

      ![Grafana_f_8.png](doc/Grafana_f_8.png)

      And click on "Add an empty panel"

      12.2 Select the data source and fill in this query

      The following influx query demonstrates, average response time of PutObjectPart API by bucket per day

      ```
      from(bucket: "Demo-Lyve-Logs")
      |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
      |> filter(fn: (r) => r["_measurement"] == "audit-01")
      |> filter(fn: (r) => r["_field"] == "auditEntry.api.timeToResponse")
      |> filter(fn: (r) => r["auditEntry.api.name"] == "CompleteMultipartUpload")
      |> group(columns: ["auditEntry.api.bucket"])
      |> aggregateWindow(every: 1d, fn: mean, createEmpty: false)
      |> map(fn: (r) => ({ r with _value: r["_value"]/1000000.0 }))
      |> yield()
      ```

      12.3 Add the panel title and change the "Unit" to Time > milliseconds (ms)

      ![Grafana_f_9.png](doc/Grafana_f_9.png)

      ![Grafana_x_10.png](doc/Grafana_x_10.png)

      **Result**

      ![Grafana_f_10.png](doc/Grafana_f_10.png)

            

13. Add panel "Error count by bucket per day"


      ![Grafana_f_11.png](doc/Grafana_f_11.png)

      **Query**

      The following influx query demonstrates, Count the error by bucket per day by using 
      the "auditEntry.api.statusCode" from S3 API Audit log that is not equal to 200

      ```
      from(bucket: "Demo-Lyve-Logs")
      |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
      |> filter(fn: (r) => r["_measurement"] == "audit-01")
      |> filter(fn: (r) => r["_field"] == "message")
      |> filter(fn: (r) => r["auditEntry.api.statusCode"] != "200")
      |> filter(fn: (r) => r["auditEntry.api.bucket"] != "")
      |> group(columns: ["auditEntry.api.bucket"])
      |> aggregateWindow(every: 1d, fn: count, createEmpty: false)
      ```

      **Setting**

      Graph styles  
      
         1. Style = Bars
         2. Fill opacity = 100


      ![Grafana_f_12.png](doc/Grafana_f_12.png)

      **Result**

      ![Grafana_f_13.png](doc/Grafana_f_13.png)

14. Add panel "API calls by bucket per day"

      ![Grafana_f_14.png](doc/Grafana_f_14.png)

      **Query**

      The following influx query demonstrates, timeseries chart for show count of API call by bucket per day from S3 API Audit log.

      ```
      from(bucket: "Demo-Lyve-Logs")
      |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
      |> filter(fn: (r) => r["_measurement"] == "audit-01")
      |> filter(fn: (r) => r["_field"] == "message")
      |> filter(fn: (r) => r["auditEntry.api.bucket"] != "")
      |> group(columns: ["auditEntry.api.bucket"])
      |> aggregateWindow(every: 1d, fn: count, createEmpty: false)
      ```

      **Setting**

      Graph styles  
      
         1. Style = Bars
         2. Fill opacity = 100

      ![Grafana_f_12.png](doc/Grafana_f_12.png)

      **Result**

      ![Grafana_f_15.png](doc/Grafana_f_15.png)

15. Add panel "Total API Call by bucket"

      ![Grafana_f_16.png](doc/Grafana_f_16.png)

      **Query**

      The following influx query demonstrates, pie chart for show total API call by bucket from S3 API Audit log.

      ```
      from(bucket: "Demo-Lyve-Logs")
      |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
      |> filter(fn: (r) => r["_measurement"] == "audit-01")
      |> filter(fn: (r) => r["_field"] == "message")
      |> filter(fn: (r) => r["auditEntry.api.bucket"] != "")
      |> group(columns: ["auditEntry.api.bucket"])
      |> aggregateWindow(every: 1d, fn: count, createEmpty: false)
      ```

      **Setting**

      Select "Pie chart"

      ![Grafana_f_17.png](doc/Grafana_f_17.png)

      Value options  
      
         Calculation = Total

      ![Grafana_f_18.png](doc/Grafana_f_18.png)

      **Result**

      ![Grafana_f_19.png](doc/Grafana_f_19.png)

16. Add panel "Max API Response Time"

      ![Grafana_f_20.png](doc/Grafana_f_20.png)

      **Query**

      The following influx query demonstrates, histogram chart for show max API response time by API name from S3 API Audit log.

      ```
      from(bucket: "Demo-Lyve-Logs")
      |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
      |> filter(fn: (r) => r["_measurement"] == "audit-01")
      |> filter(fn: (r) => r["_field"] == "auditEntry.api.timeToResponse")
      |> filter(fn: (r) => r["auditEntry.api.bucket"] != "")
      |> group(columns: ["auditEntry.api.name"])
      |> aggregateWindow(every: 1d, fn: mean, createEmpty: false)
      |> map(fn: (r) => ({ r with _value: r["_value"]/1000000.0 }))
      |> yield()
      ```

      **Setting**

      Select "Bar gauge"

      ![Grafana_f_26.png](doc/Grafana_f_26.png)

      Value options  
      
         Show = All values

      ![Grafana_f_27.png](doc/Grafana_f_27.png)

      Bar gauge
      
         Orientation = Horizontal

      ![Grafana_f_28.png](doc/Grafana_f_28.png)

      Standard options  
      
         Unit = Time > milliseconds (ms)

      ![Grafana_x_10.png](doc/Grafana_x_10.png)

      **Transform**

      Select "Reduce"

      ![Grafana_f_21.png](doc/Grafana_f_21.png)

         Mode = Series to rows
         Calculation = Max

      ![Grafana_f_22.png](doc/Grafana_f_22.png)

      Click "Add transformation"

      ![Grafana_f_23.png](doc/Grafana_f_23.png)

      Select "Sort by"

      ![Grafana_f_24.png](doc/Grafana_f_24.png)

         Field = Max
         Reverse = true

      ![Grafana_f_25.png](doc/Grafana_f_25.png)

      **Result**

      ![Grafana_f_29.png](doc/Grafana_f_29.png)

17. You can move the panel by drag it on the top.

      ![Grafana_f_30.png](doc/Grafana_f_30.png)

18. You can resize the panel by drag it on the bottom right

      ![Grafana_f_31.png](doc/Grafana_f_31.png)

# Results

![Grafana_f_32.png](doc/Grafana_f_32.png)

# Tested by

- Feb 24, 2022: Chanathip Plaboothong ([chanathip.plaboothong@seagate.com](mailto:chanathip.plaboothong@seagate.com)) on Windows .
- July 04, 2022: Leon Markovich (leon.markovich@seagate.com) on Ubuntu 20.4 .
- August 10, 2022: Ophir Rom (ophir.rom@seagate.com) on Centos 7.9 .
- September 12, 2022: Sasha Chernin(alexander.chernin@seagate.com) Ubuntu 20.4 .

# Project Structure

This section will describe the representation of each of the folders or files in the structure.

```
.
├── readme.md
├── datasources
│   └── influxdb.py
├── doc
│   ├── draft.png
│   ├── grafana_result.png
│   └── logtypes.png
├── helpers
│    ├── config_manager.py
│    ├── s3.py
│    └── utils.py
├── job
│    └── executor.py
├── parsers
│    ├── audit.py
│    ├── console.py
│    ├── enums.py
│    ├── iam.py
│    └── logparser.py
├── .gitignore
├── config.yaml
├── Dockerfile
├── main.py
└── requirements.txt
```

### `/datasources`

This folder contains the scripts that are used for connecting and operating with the datasource.

### `/job`

This folder contains the scripts that are used for fetching and uploading the S3 API Audit logs.

### `/parsers`

This folder contains the scripts that are used for parsing a S3 API Audit log format.

### `/helpers`

This folder contains scripts that are used as helpers for the scripts.

### `/doc`

Contains images for the documentation.
