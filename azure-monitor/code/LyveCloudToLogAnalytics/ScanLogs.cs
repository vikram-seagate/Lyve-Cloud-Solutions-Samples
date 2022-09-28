using Amazon.S3;
using Amazon.S3.Model;
using ICSharpCode.SharpZipLib.Core;
using ICSharpCode.SharpZipLib.GZip;
using Microsoft.Azure.WebJobs;
using Microsoft.Extensions.Logging;
using Microsoft.WindowsAzure.Storage.Table;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;

namespace LyveCloudToLogAnalytics
{
    public class ScanLogs
    {
        AmazonS3Client S3Client;
        string BucketName = Utils.GetBucketName();
        string StartTime = Utils.GetStartTime();
        string logType = Utils.GetLogType();
        const string lc = "lyvecloud";
        const string al = "auditlogs";
        string customLogName;

        IAzureLogAnalyticsClient _logAnalyticsClient;

        public ScanLogs(IAzureLogAnalyticsClient logAnalyticsClient)
        {
            _logAnalyticsClient = logAnalyticsClient;

        }

        // Timer Trigger that runs every round hour.
        [FunctionName("ScanLogs")]
        public async Task RunAsync([TimerTrigger("0 * * * *")] TimerInfo myTimer, ILogger log, [Table("logrunscheckpoint", Connection = "AzureWebJobsStorage")] CloudTable logsCheckpoint)
        {
            log.LogInformation($"C# Timer trigger function executed at: {DateTime.Now}");


            DateTime now = DateTime.Now.ToUniversalTime();

            var checkpoint = await GetLastCheckpointFileAsync(logsCheckpoint);
            // check if custom log name exists
            if (checkpoint?.CustomLogName != null)
                customLogName = checkpoint.CustomLogName;
            else
                // set custom log name
                if (StartTime != "")
                    customLogName = lc + "_" + logType + "_" + al + "_" + DateTime.Parse(StartTime).ToString("MM_dd_yy_HH_mm_ss");
                else
                    customLogName = lc + "_" + logType + "_" + al + "_" + now.ToString("MM_dd_yy_HH_mm_ss");

            S3Client = Utils.ConnectLyveS3();
            log.LogInformation($"Connected to Lyve S3: {DateTime.Now}");

            S3Bucket logsBucket = await GetLogsBucket(log);

            var lastModificationTime = DateTime.MinValue;
            if (checkpoint?.LastModificationTime != null)
            {
                lastModificationTime = checkpoint.LastModificationTime;
            }
            else if (StartTime.Equals(""))
            {
                lastModificationTime = now.AddHours(-1);
            }
            else
            {
                lastModificationTime = DateTimeOffset.Parse(StartTime).UtcDateTime;
            }

            List<S3Object> allFiles = new List<S3Object>();
            ListObjectsV2Request request = new ListObjectsV2Request { BucketName = logsBucket.BucketName };
            ListObjectsV2Response response;

            do
            {
                response = await S3Client.ListObjectsV2Async(request);
                allFiles.AddRange(response.S3Objects.Where(x => x.Key.EndsWith("gz")).Where(x => x.LastModified.ToUniversalTime() > lastModificationTime).Where(x => x.Key.Contains(logType)));

                request.ContinuationToken = response.NextContinuationToken;
            } while (response.IsTruncated);

            if (allFiles.Count() == 0)
            {
                log.LogInformation($"No new audit logs were found between {lastModificationTime} to {now}. Please make sure that the bucket is not empty.");
                return;
            }
            else
                log.LogInformation($"Got {allFiles.Count()} new log files between {lastModificationTime} to {now} ");

            if (allFiles.Count() > 0)
            {
                allFiles = allFiles.OrderByDescending(x => x.LastModified).ToList();
                lastModificationTime = allFiles[0].LastModified;

                await SetCheckpointAsync(logsCheckpoint, lastModificationTime, customLogName);
            }

            try
            {
                await UploadLogsAsync(allFiles, log);
            } 
            catch(Exception ex)
            {
                throw new Exception(ex.Message);
            }
        }

        // Retrieves latest checkpoint - the datetime of the most recent .gz file.
        private async Task<LogScanCheckpoint> GetLastCheckpointFileAsync(CloudTable logsCheckpoint)
        {
            var result = await logsCheckpoint.ExecuteAsync(TableOperation.Retrieve<LogScanCheckpoint>(LogScanCheckpoint.CheckpointId, LogScanCheckpoint.CheckpointId));
            var checkpoint = result.Result as LogScanCheckpoint;
            return checkpoint;
        }

        // Retrieves and returns logs bucket as an object.
        private async Task<S3Bucket> GetLogsBucket(ILogger log)
        {
            ListBucketsResponse response = await S3Client.ListBucketsAsync();
            var logsBucket = response.Buckets.FirstOrDefault(b => b.BucketName == BucketName);

            if (logsBucket == null)
            {
                throw new Exception($"Bucket named '{BucketName}' doesn't exists");
            }

            return logsBucket;
        }

        // Sets new checkpoint - the datetime of the latest .gz file.
        private async Task SetCheckpointAsync(CloudTable logsCheckpoint, DateTime lastModificationTime, string customLogName)
        {
            var checkpoint = new LogScanCheckpoint()
            {
                PartitionKey = LogScanCheckpoint.CheckpointId,
                RowKey = LogScanCheckpoint.CheckpointId,
                LastModificationTime = lastModificationTime,
                CustomLogName = customLogName,
                ETag = "*"
            };
            var operation = TableOperation.InsertOrReplace(checkpoint);
            await logsCheckpoint.ExecuteAsync(operation);
        }


        // Iterates over s3 objects, extracts them and uploads the rows of their contents in chunks of 1000 rows.
        private async Task UploadLogsAsync(List<S3Object> allFiles, ILogger log)
        {
            List<string> logsList = new List<string>();
            string json;

            foreach (var file in allFiles)
            {
                var s3Object = await S3Client.GetObjectAsync(BucketName, file.Key);

                var tempFile = Path.GetTempFileName();
                var extractedDir = tempFile + "_e";
                Directory.CreateDirectory(extractedDir);
                string extractedFile = Path.Combine(extractedDir, Path.GetFileName(file.Key));
                File.Delete(tempFile);

                await s3Object.WriteResponseStreamToFileAsync(tempFile, false, CancellationToken.None);

                ExtractLogFile(tempFile, extractedFile);

                using (var content = new StreamReader(extractedFile))
                {
                    var line = "";
                    while ((line = await content.ReadLineAsync()) != null)
                    {
                        logsList.Add(line);
                        if (logsList.Count >= 1000)
                        {
                            string allLines = String.Join(",", logsList);
                            json = "[" + allLines + "]";
                            await _logAnalyticsClient.WriteLog(customLogName, json);
                            logsList.Clear();
                        }
                    }
                }
                Directory.Delete(extractedDir, true);
                log.LogInformation($"Processed: {file.Key}");
            }

            if (logsList.Count > 0)
            {
                string allLines = String.Join(",", logsList);
                json = "[" + allLines + "]";
                await _logAnalyticsClient.WriteLog(customLogName, json);
                logsList.Clear();
            }
        }

        // Extracts gz file.
        private static void ExtractLogFile(string compressedFile, string extractedFile)
        {
            byte[] dataBuffer = new byte[4096];
            using (Stream fs = new FileStream(compressedFile, FileMode.Open, FileAccess.Read))
            {
                using (GZipInputStream gzipStream = new GZipInputStream(fs))
                {
                    using (FileStream fsOut = File.Create(extractedFile))
                    {
                        StreamUtils.Copy(gzipStream, fsOut, dataBuffer);
                    }
                }
            }
        }
    }
}
