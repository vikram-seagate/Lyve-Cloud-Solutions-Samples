from pyspark.sql import SparkSession
from pyspark import SparkContext, SparkConf

# Create a SparkContext with the Hadoop-AWS dependency
conf = SparkConf().set('spark.jars.packages', 'org.apache.hadoop:hadoop-aws:3.3.1')
sc = SparkContext(conf=conf)

# Configure S3 bucket credentials
ACCESS_KEY_ID = "YOUR ACCESS KEY"
SECRET_ACCESS_KEY = "YOUR SECRET KEY"
ENDPOINT = "S3 API Endpoint"

sc._jsc.hadoopConfiguration().set('fs.s3a.access.key', ACCESS_KEY_ID)
sc._jsc.hadoopConfiguration().set('fs.s3a.secret.key', SECRET_ACCESS_KEY)
sc._jsc.hadoopConfiguration().set('fs.s3a.endpoint', ENDPOINT)

# Create a SparkSession
spark = SparkSession(sc)

# Read data from S3
df = spark.read.option('header', 'true').csv("s3a://XXXXXX/data.csv")

# Process and analyze the data
df.show()
