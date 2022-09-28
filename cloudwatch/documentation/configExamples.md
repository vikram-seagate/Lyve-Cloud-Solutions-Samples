# config.json examples
This document will show different ways to configure the config.json file

## Example 1: Start uploading new S3 audit logs from last hour
```
{
    "lyvecloud": {
        "input_bucket": "logs0001",
        "log_type": "S3",
        "mode": ""
    },
    "aws": {
        "log_group": "Lyve-Log-Group"
    }
}
```

### Expected Results
Every **round** hour, S3 audit logs that were created in the last hour will be pulled from Lyve Cloud and uploaded to a log stream named "lyve_lasthour_S3_audit_logs".

## Example 2: Upload S3 audit logs from specific date
```
{
    "lyvecloud": {
        "input_bucket": "logs0001",
        "log_type": "S3",
        "mode": "05/30/22"
    },
    "aws": {
        "log_group": "Lyve-Log-Group"
    }
}
```

### Expected Results
At the closest round hour, the integration will start a process that will pull and upload all S3 audit logs that were created between 05/30/22 and the start time of this process to a log stream named "lyve_fromdate_S3_audit_logs".
The next round hour, while older audit logs might still be uploading, audit logs that were created in the last hour will be pulled from Lyve Cloud and uploaded to a log stream named "lyve_lasthour_S3_audit_logs".

## Example 3: Upload all existing S3 audit logs in a bucket
```
{
    "lyvecloud": {
        "input_bucket": "logs0001",
        "log_type": "S3",
        "mode": "all"
    },
    "aws": {
        "log_group": "Lyve-Log-Group"
    }
}
```

### Expected Results
At the closest round hour, the integration will start a process that will pull and upload all S3 audit logs that are inside the specified bucket, up to the audit logs that were created after the start time of this process to a log stream named "lyve_fromdate_audit_logs_S3".
The next round hour, while older audit logs might still be uploading, audit logs that were created in the last hour will be pulled from Lyve Cloud and uploaded to a log stream named "lyve_lasthour_S3_audit_logs".

## Example 4: Upload Console audit logs from specific date
```
{
    "lyvecloud": {
        "input_bucket": "logs0001",
        "log_type": "Console",
        "mode": "05/30/22"
    },
    "aws": {
        "log_group": "Lyve-Log-Group"
    }
}
```

### Expected Results
At the closest round hour, the integration will start a process that will pull and upload all **Console** audit logs that were created between 05/30/22 and the start time of this process to a log stream named "lyve_fromdate_Console_audit_logs".
The next round hour, while older audit logs might still be uploading, audit logs that were created in the last hour will be pulled from Lyve Cloud and uploaded to a log stream named "lyve_lasthour_Console_audit_logs".

## Example 5: Upload all existing IAM audit logs in a bucket
```
{
    "lyvecloud": {
        "input_bucket": "logs0001",
        "log_type": "IAM",
        "mode": "all"
    },
    "aws": {
        "log_group": "Lyve-Log-Group"
    }
}
```

### Expected Results
At the closest round hour, the integration will start a process that will pull and upload all **IAM** audit logs that are inside the specified bucket, up to the audit logs that were created after the start time of this process to a log stream named "lyve_fromdate_IAM_audit_logs".
The next round hour, while older audit logs might still be uploading, audit logs that were created in the last hour will be pulled from Lyve Cloud and uploaded to a log stream named "lyve_lasthour_IAM_audit_logs".
