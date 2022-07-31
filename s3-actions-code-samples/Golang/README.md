# S3 Actions Code Sample - Golang

## Prerequisites
* [Golang](https://go.dev/doc/install)

## Running the CLI Tool
1. Enter your credentials in [config.json file](config.json):
   * access key
   * secret key
   * region name
   * endpoint URL
2. Build binary: `go run .`
3. Run the `./s3-actions --help` to see all options:
```
[bari ~]$ ./s3-actions -h     
Usage:
  ./s3-actions --Op=<value> --Bucket=<value> --Path=<value>
Example:
  ./s3-actions --Op=put --Bucket=bari-test --Path=example.txt



All optional flag's:
  --Bucket string           The bucket name                                                                                                     
  --ConfigPath string       The config file path (default config.json)                                                                          
  --Op string               mb[MakeBucket]/rb[RemoveBucket]/lb[ListBuckets]/put[PutObject]/rm[RemoveObject]/get[GetObject]/ls[ListObjects]      
  --Path string             The object path for put, get, and remove object  
```

### Sessions Setup
```go
func (c *S3Client) configCredentials(configPath, bucketName string) error {
	config, err := readConfigFile(configPath)
	if err != nil {
		return err
	}
	s3Config := &aws.Config{
		Credentials:      credentials.NewStaticCredentials(config.AccessKey, config.SecretKey, ""),
		Endpoint:         aws.String(config.EndpointUrl),
		Region:           aws.String(config.RegionName),
		S3ForcePathStyle: aws.Bool(true),
	}
	// Creates S3 service client
	c.Session = session.Must(session.NewSession(s3Config))
	c.BucketName = aws.String(bucketName)
	c.s3Client = s3.New(c.Session)
	return nil
}
```

### Make Bucket
```go
func (c *S3Client) makeBucket() error {
   if _, err := c.s3Client.CreateBucket(&s3.CreateBucketInput{Bucket: c.BucketName}); err != nil {
	   return err
   }
   PrintlnC.Green("Bucket %s was created successfully\n", *c.BucketName)
   return nil
}
```

### Remove Bucket
```go
func (c *S3Client) removeBucket() error {
	if _, err := c.s3Client.DeleteBucket(&s3.DeleteBucketInput{Bucket: c.BucketName}); err != nil {
		return err
   }
   PrintlnC.Magenta("Waiting for bucket %s to be deleted...\n", *c.BucketName)
   if err := c.s3Client.WaitUntilBucketNotExists(&s3.HeadBucketInput{Bucket: c.BucketName}); err != nil {
	   return err
   }
   PrintlnC.Green("The bucket %s was successfully deleted\n", *c.BucketName)
   return nil
}
```

### List Buckets
```go
func (c *S3Client) listBuckets() error {
   result, err := c.s3Client.ListBuckets(nil)
   if err != nil {
	   return err
   }
   PrintlnC.Cyan("List Buckets:")
   for _, bucket := range result.Buckets {
	   PrintlnC.Cyan("* %s\n", aws.StringValue(bucket.Name))
   }
   return nil
}
```

### Put Object
```go
func (c *S3Client) putObject(objectName string) error {
   object, err := os.Open(objectName)
   if err != nil {
	   return err
   }
   defer object.Close()
   
   if _, err = c.s3Client.PutObject(&s3.PutObjectInput{Body: object, Bucket: c.BucketName, Key: aws.String(objectName)}); err != nil {
	   return err
   }
   PrintlnC.Green("The object %s has been uploaded successfully\n", *c.BucketName)
   return nil
}
```

### Remove Object
```go
func (c *S3Client) removeObject(objectName string) error {
   if _, err := c.s3Client.DeleteObject(&s3.DeleteObjectInput{Bucket: c.BucketName, Key: aws.String(objectName)}); err != nil {
	   return err
   }
   if err := c.s3Client.WaitUntilObjectNotExists(&s3.HeadObjectInput{Bucket: c.BucketName, Key: aws.String(objectName)}); err != nil {
	   return err
   }
   PrintlnC.Green("The object %q was successfully deleted\n", objectName)
   return nil
}
```

### Get Object
```go
func (c *S3Client) getObject(objectName string) error {
   object, err := os.Create(objectName)
   if err != nil {
	   return err
   }
   defer object.Close()
   
   downloader := s3manager.NewDownloader(c.Session)
   if _, err = downloader.Download(object, &s3.GetObjectInput{Bucket: c.BucketName, Key: aws.String(objectName)}); err != nil {
	   return err
   }
   PrintlnC.Green("The object %s has been successfully downloaded\n", object.Name())
   return nil
}
```

### List Objects
```go
func (c *S3Client) listObjects() error {
   resp, err := c.s3Client.ListObjectsV2(&s3.ListObjectsV2Input{Bucket: c.BucketName})
   if err != nil {
	   return err
   }
   if len(resp.Contents) == 0 {
	   PrintlnC.Red("The bucket is empty!\n")
	   return nil
   }
   for _, item := range resp.Contents {
	   PrintlnC.Cyan("Object Name: %s, Object Size: %d, Last modified: %s\n", *item.Key, *item.Size, *item.LastModified)
   }
   return nil
}
```

## Tested By:
* March 13, 2022: Bari Arviv (bari.arviv@seagate.com) on macOS