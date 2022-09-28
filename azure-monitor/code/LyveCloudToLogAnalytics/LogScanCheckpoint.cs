using Microsoft.WindowsAzure.Storage.Table;
using System;

namespace LyveCloudToLogAnalytics
{
    // Stores latest checkpoint, which is the datetime of the most recent .gz file.
    internal class LogScanCheckpoint : TableEntity
    {
        public const string CheckpointId = "Checkpoint";
        public string Id { get; set; } = CheckpointId;
        public DateTime LastModificationTime { get; set; }
        public string CustomLogName { get; set; }
    }
}
