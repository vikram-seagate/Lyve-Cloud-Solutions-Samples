using Amazon.S3;
using System;

namespace LyveCloudToLogAnalytics
{
    public static class Utils
    {

        // Connecting to Lyve Cloud using AWS SDK.
        public static AmazonS3Client ConnectLyveS3()
        {
            string EndpointUrl = Environment.GetEnvironmentVariable("LyveCloudS3APIEndpoint");
            string AccessKey = Environment.GetEnvironmentVariable("LyveCloudAccessKey");
            string SecretKey = Environment.GetEnvironmentVariable("LyveCloudSecretKey");

            AmazonS3Config config = new AmazonS3Config();
            config.ServiceURL = EndpointUrl;

            return new AmazonS3Client(AccessKey, SecretKey, config);
        }

        // Returns bucket name.
        public static string GetBucketName()
        {
            return Environment.GetEnvironmentVariable("AuditLogsBucketName");
        }

        // Returns start time for scanning.

        public static string GetStartTime()
        {
            string value = Environment.GetEnvironmentVariable("StartTime");
            if (value == null)
            {
                return "";
            }
            else
                return value;
        }

        // Returns log type set inside environment variables
        public static string GetLogType()
        {
            string value = Environment.GetEnvironmentVariable("LogType");
            if (value == null)
            {
                return "";
            }
            else
                return value;
        }

        // Returns log name inside of Log Analytics to which the lyve audit logs should be uploaded to.
        public static string GetLogName()
        {
            return Environment.GetEnvironmentVariable("LogAnalyticsLogName");
        }



    }
}
