# This document contains examples of various queries for the Lyve Cloud audit logs

## Count of failed response statuses
```
fields auditEntry.api.statusCode, auditEntry.api.bucket
|filter auditEntry.api.statusCode>206
| stats count(*) by auditEntry.api.statusCode
```

## Top 5 most used buckets
```
fields auditEntry.api.bucket
| stats count(*) by auditEntry.api.bucket
| limit 5
```

## Which bucket has the most failed responses
```
fields auditEntry.api.statusCode, auditEntry.api.bucket
|filter auditEntry.api.statusCode > 206
|stats count(*) by auditEntry.api.bucket
```

## List of failed requests in a specific month
```
fields auditEntry.api.statusCode, auditEntry.api.bucket, auditEntry.time
|filter auditEntry.api.statusCode > 206
|filter auditEntry.time like "2022-05"
|display auditEntry.api.statusCode, auditEntry.api.bucket, auditEntry.time
```

## List of failed statuses between two specific dates
```
fields auditEntry.time as datetime
| parse datetime "*-*-*T" as Year, Month, Date
| filter auditEntry.api.statusCode > 400
| filter (Month=4 and Date>15) or (Month=5 and Date<15)
| filter ispresent(serviceAccountName)
| display auditEntry.api.statusCode, auditEntry.api.bucket, serviceAccountName, datetime
```
