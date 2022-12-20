[![ license](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://github.com/Seagate/Lyve-Cloud-Solutions-Samples/blob/main/LICENSE)
[![GitHub contributors](https://img.shields.io/github/contributors/Seagate/Lyve-Cloud-Solutions-Samples)](https://github.com/Seagate/Lyve-Cloud-Solutions-Samples/graphs/contributors/)

# Lyve Cloud solutions samples

<img src="images/LyveCloud-logo.png?raw=true" width="700">

[Lyve Cloud](https://www.seagate.com/gb/en/services/cloud/storage/) by [Seagate](https://www.seagate.com) is an S3-compatible storage-as-a-service platform designed as a simple, trusted, and efficient service allowing enterprises to unlock the value of their massive unstructured datasets and enabling them to store more for longer.

This repository holds integration solutions written by Lyve Cloud community developers who contributed them for the benefit of the Lyve Cloud users` community. We are happy to see you here and encourage you to take part in this community.

Notice the integration solutions are not part of the Lyve Cloud product. The integrations listed on this page are made available and contributed “as-is”, without warranty, and disclaiming liability for damages resulting from using the projects.

## Getting Started

- Browse our repository to find usefull tools for your needs (as listed below) or to get inspiration for building your integration solution.
- Jumpstart your integration with our [S3 actions code samples](s3-actions-code-samples).
- Have a question? Let's have a [discussion](https://github.com/Seagate/Lyve-Cloud-solutions-samples/discussions) (don't be shy).
- Want to create and contribute your own solution? Read our [Contribution Guide](CONTRIBUTING.md).

# Integration Solutions

*Please click on the arrows to expand*
<details><summary>Migrating and syncing to Lyve Cloud</summary> 

| Solution|Source |Technology|Installation|
|  --- |  --- | ---| ---|
| 1. [On-demand sync of Linux local directory to Lyve Cloud bucket.](s3sync-local-to-lyvecloud/)| Linux |Cronjob|Manual
| 2. [Migrating and syncing between AWS and Lyve Cloud buckets.](syncer/)|AWS|AWS Lambda|Cli-Tool|
| 3. [Replicating new objects created in AWS S3 bucket to a Lyve Cloud bucket.](s3-replication-to-lyvecloud/)|AWS|AWS Lambda|Manual|
| 4. [Full-stack solution for easily migrating and synchronizing files from other cloud services to Lyve Cloud](data-migration-and-sync-to-lyvecloud/). | Generic S3, GCP, Alibaba, Azure Containers | Web App| ---|

</details>

<details><summary>Pull and send audit logs from Lyve Cloud to different monitoring solutions </summary> 

| Solution|Monitoring service
| ---| ---|
| 1. [Sending Lyve Cloud S3 API Audit Log events to be consumed and displayed in AWS CloudWatch.](cloudwatch/)|CloudWatch|
| 2. [Sending Lyve Cloud S3 API Audit Log events to be consumed and displayed in Azure Monitor(Log Analytics).](azure-monitor/)| Azure Monitor|
| 3. [Sending Lyve Cloud S3 API Audit Log events to be consumed and displayed in Grafana.](audit-log-analysis-grafana/) | Grafana|

</details>

<details><summary>Calculating Lyve Cloud bucket metrics</summary>

[bucket-metrics-collection](bucket-metrics-collection/)

The purpose of this integration solution is to demonstrate how Lyve Cloud bucket metrics can be securely pulled using AWS Lambda and displayed in AWS CloudWatch. The bucket metrics displayed in this solution are: number of objects and bucket size. These metrics are calculated for the buckets that Lyve Cloud credentials can access. Once the metrics are pulled, it can be displayed using AWS CloudWatch dashboards.

</details>

<details><summary>Streaming media from Lyve Cloud bucket</summary> 

[media-streamer](media-streamer/)

Middleware solution built with Python and FastAPI, which is optimized for video streaming.

It serves as a middleware from the browser request to the requested object, which is the video file. The implementation is based on the Range Requests Specification in RFC 7233.

</details>


<details><summary>Terraform Provider for Lyve Cloud</summary>

[Terraform Lyve Cloud provider](https://registry.terraform.io/providers/Seagate/lyvecloud)

Terraform provider plugin for managing Lyve Cloud S3 buckets, objects, permissions and service accounts.

</details>

<details><summary>Using tar file index to extract data efficiently</summary>

[tar-index-extract](/tar-index-extract)

This tool extracts a selection of files from a tar archive stored in an a Lyve Cloud bucket.

</details>

<details><summary>Integrating Apache Spark with Lyve Cloud</summary>

[apache-spark](/apache-spark)

Apache Spark is a powerful data processing engine that can be used to analyze large volumes of data. By combining it with Lyve Cloud, users can easily access and process their data stored on the platform. This solution provides a guide on how to use Apache Spark with Lyve Cloud, including setup instructions.

</details>

The repository is licensed under the [Apache 2.0 License](LICENSE).
