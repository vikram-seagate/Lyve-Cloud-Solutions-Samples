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
*Please click on the arrows to expand !*
<details><summary>Migrating and Syncing to LyveCloud Soultions</summary> 

| Solution|Source |Technology|Installation|
|  --- |  --- | ---| ---|
| 1. [On-demand sync of Linux local directory to LyveCloud bucket.](s3sync-local-to-lyvecloud/)| Linux |Cronjob|Manual
| 2. [Migrating and syncing between AWS and LyveCloud buckets.](syncer/)|AWS|AWS Lambda|Cli-Tool|
| 3. [Replicating new objects created in AWS S3 bucket to a Lyve Cloud bucket.](s3-replication-to-lyvecloud/)|AWS|AWS Lambda|Manual|

</details>

<details><summary>Pull and send audit logs from LyveCloud to different monitoring infrastructure </summary> 

| Solution|Monitoring Infrastructure|Technology|
| :---:| :---:| :---:|
| 1. [Sending Lyve Cloud S3 API Audit Log events to be consumed and displayed in AWS CloudWatch.](CloudWatch/)|CloudWatch|Docker Container|
| 2. [Sending Lyve Cloud S3 API Audit Log events to be consumed and displayed in Azure Monitor(Log Analytics).](AzureMonitor/)| AzureMonitor|Function app|

</details>

<details><summary>Calculating Lyve Cloud bucket metrics</summary> 

| Solution|Monitoring Infrastructure|Technology|
| :---:| :---:| :---:|
| 1. [Calculating Lyve Cloud bucket metrics and displaying them in AWS CloudWatch.](bucket-metrics-collection/)|CloudWatch|AWS Lambda|

</details>


The repository is licensed under the [Apache 2.0 License](LICENSE).
