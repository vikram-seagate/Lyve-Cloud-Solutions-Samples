# Using Apache Spark with Lyve Cloud

## Introduction
Apache Spark is a powerful open-source distributed computing system that can be used for large-scale data processing. It is designed to be fast and efficient, and it has features that make it well-suited for working with data stored in S3 object storage. Using Spark with Lyve Cloud allows you to easily access, and process data stored in Lyve Cloud without the need to download it first. This can be a great way to manage and analyze large datasets efficiently and cost-effectively.

To use Lyve Cloud with Apache Spark, you will need to configure Spark tools to use the Hadoop-AWS library. You can then access data stored in S3 bucket by using the `s3a://` URI scheme when reading or writing data.

## Requirements
* [`Apache Spark 3+`](https://spark.apache.org/downloads.html): You will need to have Apache Spark with Hadoop installed on your local machine or on a cluster of machines. Earlier versions of Apache Spark may not work.
* Lyve Cloud S3 credentials: To access your S3 data from Spark, you will need to provide the following Lyve Cloud credentials:
    - Access Key
    - Secret Key
    - S3 API Endpoint
    
## Spark Shell
**Step 1:** Run Spark Shell with the `Hadoop-AWS` dependency. Please make sure that the `Hadoop-AWS` version is the same as Apache Spark.
```
$ spark-shell --packages org.apache.hadoop:hadoop-aws:3.3.1
```
**Step 2:** Configure Lyve Cloud S3 credentials inside Spark Shell.
```
scala> sc.hadoopConfiguration.set("fs.s3a.endpoint", "S3 API Endpoint")
scala> sc.hadoopConfiguration.set("fs.s3a.access.key","YOUR ACCESS KEY")
scala> sc.hadoopConfiguration.set("fs.s3a.secret.key","YOUR SECRET KEY")
```

**Step 3:** Configure stored data location.
```
scala> val myRDD = sc.textFile("s3a://my-data-bucket/data1.txt")
```

**Step 4:** Run data analysis jobs on your data.

Here's some simple commands example:
```
scala> myRDD.count
res3: Long = 12
scala> myRDD.take(3)
res4: Array[String] = Array(name,inspection_result,inspection_closed_business,violation_type,violation_points, 100 LB CLAM,Incomplete,FALSE,,0, 100 LB CLAM,Unsatisfactory,FALSE,BLUE,5)
```

To save your RDD in a bucket:
```
scala> myRDD.saveAsTextFile("s3a://my-other-bucket/output")
```

### Dockerfile
For convenience, and running tasks on a Spark standalone cluster, you can use the dockerfile attached to this repo, which already runs Spark Shell with the Hadoop-AWS dependency.
1. Build the Docker image.
```
docker build -t lyvecloud-spark .
```

2. Run the Docker container.
```
docker run -it lyvecloud-spark
```

3. Configure Lyve Cloud credentials and data path inside the Spark Shell.
```
scala> sc.hadoopConfiguration.set("fs.s3a.endpoint", "S3 API Endpoint")
scala> sc.hadoopConfiguration.set("fs.s3a.access.key","YOUR ACCESS KEY")
scala> sc.hadoopConfiguration.set("fs.s3a.secret.key","YOUR SECRET KEY")
scala> val myRDD = sc.textFile("s3a://my-data-bucket/data1.txt")
```

Now you can perform data analysis inside the Docker container.

## PySpark
**Step 1:** Install the boto3 library for Python.
```
pip install boto3
```

Note: if you run PySpark Shell, include the Hadoop-AWS dependency
```
pyspark --packages org.apache.hadoop:hadoop-aws:3.3.1
```

**Step 2:** Add necessary imports.
```
>>> from pyspark.sql import SparkSession
>>> from pyspark import SparkContext, SparkConf
```
**Step 3:** Create a SparkContext with the Hadoop-AWS dependency.
```
>>> conf = SparkConf().set('spark.jars.packages', 'org.apache.hadoop:hadoop-aws:3.3.1')
>>> sc = SparkContext(conf=conf)
```

**Step 4:** Configure S3 bucket credentials.
```
>>> sc._jsc.hadoopConfiguration().set('fs.s3a.access.key', ACCESS_KEY_ID)
>>> sc._jsc.hadoopConfiguration().set('fs.s3a.secret.key', SECRET_ACCESS_KEY)
>>> sc._jsc.hadoopConfiguration().set('fs.s3a.endpoint', ENDPOINT)
```


**Step 5:** Create a SparkSession.
```
>>> spark = SparkSession(sc)
```

**Step 5:** Read data from S3 bucket.
```
>>> df = spark.read.option('header', 'true').csv("s3a://my-data-bucket/data.csv")
```

**Step 6:** Process and analyze the data.
```
>>> df.show()
```


The full Python code can be found [here](/pyspark_example.py).

## Additional Information
* Hadoop-AWS is a library that provides support for using Hadoop and other related technologies, such as PySpark and Hive, with Lyve Cloud. For more information on Hadoop-AWS and additonal implementations of it, please refer to it's [official documentation](https://hadoop.apache.org/docs/stable/hadoop-aws/tools/hadoop-aws/index.html).

* For more information on integrating Apache Spark with cloud infrastructures, visit official documentation [here](https://spark.apache.org/docs/latest/cloud-integration.html#spark-streaming-and-object-storage).


## Tested by
* December 05, 2022: Alexander Chernin (alexander.chernin@seagate.com) on Ubuntu 20.4

### Project Structure
```
.
├── README.md
├── Dockerfile
└── pyspark_example.py
```
