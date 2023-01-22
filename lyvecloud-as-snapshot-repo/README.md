# lyvecloud-as-snapshot-repo
Lyve Cloud snapshot and restore to Elasticsearch.

## Requirements
* Elastic search installed.
* HTTPie for making local HTTP requests to Elasticsearch.


# Known Limitations 
## Snapshot restoring version limitations
These snapshots can only be read by a version of Elasticsearch that is capable to read the index version stored inside the snapshot.

So if you want to restore ES snapshots versions examples:

    A snapshot of an index created in 6.x can be restored to 7.x.
    A snapshot of an index created in 5.x can be restored to 6.x.
    A snapshot of an index created in 2.x can be restored to 5.x.

**Snapshots of indices created with ES 1.x cannot be restored to 5.x or 6.x, snapshots of indices created in 2.x cannot be restored to 6.x or 7.x, and snapshots of indices created in 5.x cannot be restored to 7.x or 8.x. and so on...**

## Snapshot with ".geoip_databases" restoring limitations
Restoring a snapshot for  the first cluster or any with ".geoip_databases" index 
won't work, as the fact that can't be deleted and will return errors for 
restoring undeleted snapshots. 


## Prerequisites
Setup Elastic search cluster using Elastic search main documantation from
[Elasticsearch website](https://www.elastic.co/guide/en/elasticsearch/reference/current/targz.html).

Please keep in mind, to use searchable snapshots, you will need to have an Elasticsearch cluster running version 7.9 or higher.

## Minimal configuration (please advise security team before running in production)

1. Open Elasticsearch configuration file

``` bash
sudo nano /etc/elasticsearch/elasticsearch.yml
```

2. Search for '#network.host:ip' and change to 'network.host:localhost' and save

    *If you’re using nano, you can do so by pressing CTRL+X, followed by Y and then ENTER* 

3. Search for '# Enable security features' and change the next flag to false 

    xpack.security.enabled: false

## Connecting to Lyve Cloud 

Get your Lyve Cloud bucket credentials.   
Here's what you'll need:
* Access Key
* Secret key
* Endpoint URL

# Snapshot and restore to Lyve Cloud running steps



1. Load  access key and secret key to Elastic key store

Change in the next commands the access-key and secret-key to the
service account credentials for the bucket which will hold the snapshot.

``` bash
echo access-key | sudo /usr/share/elasticsearch/bin/elasticsearch-keystore add s3.client.default.access_key
```

``` bash
 echo secret-key | sudo /usr/share/elasticsearch/bin/elasticsearch-keystore add s3.client.default.secret_key
 ```

2. Reload the settings
``` bash
http POST 127.0.0.1:9200/_nodes/reload_secure_settings
```

3. Create a snapshot repo

Paste the next command to the terminal, change the bucket name to one where the snapshots will be restored to, corresponding to the credentials which were set before. you can change the name of the repo as well.

```bash
echo '{ "type":"s3","settings":{"bucket":"my-es-bucket","endpoint":"https://s3.us-east-1.lyvecloud.seagate.com"}}' | http PUT 127.0.0.1:9200/_snapshot/lyve_cloud_repository
```

4. Create an index to take a snapshot of
```bash
curl -X POST "localhost:9200/lyve-cloud-index/_doc?pretty" -H 'Content-Type: application/json' -d'
{
    "field" : "foo"
}
'
```
output:

    {
    "_index" : "lyve-cloud-index",
    "_type" : "1",
    "_id" : "__8e4oQBtRX7Vq8bd7ua",
    "_version" : 1,
    "result" : "created",
    "_shards" : {
        "total" : 2,
        "successful" : 1,
        "failed" : 0
    },
    "_seq_no" : 0,
    "_primary_term" : 1
    }

5. Take a snapshot of that index

```bash
curl -X PUT "localhost:9200/_snapshot/lyve_cloud_repository-name/snapshot-name?wait_for_completion=true&pretty" -H 'Content-Type: application/json' -d'
{
  "indices": "lyve-cloud-index",
  "ignore_unavailable": true,
  "include_global_state": false,
  "metadata": {
    "taken_by": "insert name",
    "taken_because": "testing"
  }
}
'
```
Output:

    {
    "snapshot" : {
        "snapshot" : "snapshot-name",
        "uuid" : "nurFQDM0TYuPnNAbkjO2eA",
        "repository" : "lyve_cloud_repository-name",
        "version_id" : 7170799,
        "version" : "8.5.3",
        "indices" : [
        "lyve-cloud-index"
        ],
        "data_streams" : [ ],
        "include_global_state" : false,
        "metadata" : {
        "taken_by" : "insert name",
        "taken_because" : "testing"
        },
        "state" : "SUCCESS",
        "start_time" : "2022-12-05T12:35:14.688Z",
        "start_time_in_millis" : 1670243714688,
        "end_time" : "2022-12-05T12:35:24.898Z",
        "end_time_in_millis" : 1670243724898,
        "duration_in_millis" : 10210,
        "failures" : [ ],
        "shards" : {
        "total" : 1,
        "failed" : 0,
        "successful" : 1
        },
        "feature_states" : [ ]
    }
    }

6. Remove original index to recover snapshot 

To avoid conflicts, it is better to remove the original index before restoring

```bash
curl -X DELETE "localhost:9200/lyve-cloud-index?pretty"
```
output:

    {
    "acknowledged" : true
    }

7. Restore the snapshot

First lets see that the index was really removed 

```bash
http 127.0.0.1:9200/_cat/indices?v=true
```
Lets restore

```bash
curl -X POST "localhost:9200/_snapshot/lyve_cloud_repository-name/snapshot-name/_restore?pretty" -H 'Content-Type: application/json' -d'
{
  "indices": "lyve-cloud-index"
}
'

```
Output:
    {
  "accepted" : true
    }

Now the snapshot is restored.

# Searchable snapshot 
 A searchable snapshot is a snapshot of an Elasticsearch index that can be used to search and analyze data without having to restore the data to an index.
 Searchable snapshots can be used to create a read-only copy of an index for use in analytics or testing, or as a backup that can be restored in case of data loss.

To use the searchable snapshot, enterprice edition is required.
to start trial run the next command

```bash
curl -X POST "localhost:9200/_license/start_trial?acknowledge=true&pretty"
```

# Example of searching a searchable snapshot

1. Mount a snapshot as a searchable snapshot
```bash
curl -X POST "localhost:9200/_snapshot/lyve_cloud_repository-name/snapshot-name/_mount?wait_for_completion=true&pretty" -H 'Content-Type: application/json' -d'
> {
>   "index": "lyve-cloud-index", 
>   "renamed_index": "lyve-cloud-index-after-mount", 
>   "index_settings": { 
>     "index.number_of_replicas": 0
>   },
>   "ignore_index_settings": [ "index.refresh_interval" ] 
> }
> '
```
Output  

    {
    "snapshot" : {
        "snapshot" : "snapshot-name",
        "indices" : [
        "lyve-cloud-index-after-mount"
        ],
        "shards" : {
        "total" : 1,
        "failed" : 0,
        "successful" : 1
        }
    }
    }
2. Search a snapshot example

```bash
curl -X GET "localhost:9200/lyve-cloud-index-after-mount/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "query": {
    "match": {
      "field": "foo"
    }
  }
}
'
```
Output

    {
    "took" : 4,
    "timed_out" : false,
    "_shards" : {
        "total" : 1,
        "successful" : 1,
        "skipped" : 0,
        "failed" : 0
    },
    "hits" : {
        "total" : {
        "value" : 1,
        "relation" : "eq"
        },
        "max_score" : 0.2876821,
        "hits" : [
        {
            "_index" : "lyve-cloud-index-after-mount",
            "_id" : "EDK1SYUBYCGM6PPjBrfk",
            "_score" : 0.2876821,
            "_source" : {
            "field" : "foo"
            }
        }
        ]
    }
    } 



## Tested by
* December 25, 2022: Leon (leon.markovich@seagate.com) on Ubuntu 20.4


```
.
├── README.md
├── elasticsearch.yml 
```

### `elasticsearch.yml`
Example file for configurations of elastic search cluster.

