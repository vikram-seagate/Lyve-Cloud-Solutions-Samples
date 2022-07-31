// Bari Arviv - S3 Actions Code Sample - Golang
package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"io/ioutil"
	"os"
	"strings"
	"text/tabwriter"

	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/aws/credentials"
	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/aws/aws-sdk-go/service/s3"
	"github.com/aws/aws-sdk-go/service/s3/s3manager"
	PrintlnC "github.com/fatih/color"
)

type Config struct {
	AccessKey   string `json:"access_key"`
	SecretKey   string `json:"secret_key"`
	RegionName  string `json:"region_name"`
	EndpointUrl string `json:"endpoint_url"`
	BucketName  string `json:"bucket_name"`
}

type S3Client struct {
	Session    *session.Session
	s3Client   *s3.S3
	BucketName *string
}

var (
	Operation, BucketName, ObjectPath, ConfigPath string
)

// Usage prints a usage message documenting all defined command-line flags in a nice way formatted so u can use it to override
// the default flag.Usage func also added the to set the Usage and Example print so the Usage Msg will look much clear
func usage(mustUseFlags, examples []string) func() {
	return func() {
		f := flag.CommandLine
		if len(mustUseFlags) > 0 {
			fmt.Println("Usage:")
			for _, useFlag := range mustUseFlags {
				fmt.Fprintf(f.Output(), "  %s %s\n", os.Args[0], useFlag)
			}
		}
		if len(examples) > 0 {
			fmt.Println("Example:")
			for _, example := range examples {
				fmt.Fprintf(f.Output(), "  %s %s\n", os.Args[0], example)
			}
			fmt.Println()
		}
		fmt.Fprintf(f.Output(), "All optional flag's:\n")
		writer := tabwriter.NewWriter(os.Stdout, 0, 8, 1, '\t', tabwriter.AlignRight)
		defer writer.Flush()
		flag.VisitAll(func(flag_ *flag.Flag) {
			if flag_.Usage == "" {
				return
			}
			s := fmt.Sprintf("  --%s", flag_.Name)
			name, usage := flag.UnquoteUsage(flag_)
			if len(name) > 0 {
				s += " " + name
			}
			usage = strings.ReplaceAll(usage, "\n", "")
			if flag_.DefValue != "" {
				usage += fmt.Sprintf(" (default %v)", flag_.DefValue)
			}
			_, _ = fmt.Fprintf(writer, "%s\t    %s\t\n", s, usage)
		})
	}
}

// readConfigFile returns the credentials from the config file
func readConfigFile(configPath string) (Config, error) {
	var config Config
	data, err := ioutil.ReadFile(configPath)
	if err != nil {
		return config, err
	}
	if err = json.Unmarshal(data, &config); err != nil {
		return config, err
	}
	return config, nil
}

// configCredentials initializes the credentials and creates an S3 service client
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

// makeBucket makes a new bucket
func (c *S3Client) makeBucket() error {
	if _, err := c.s3Client.CreateBucket(&s3.CreateBucketInput{Bucket: c.BucketName}); err != nil {
		return err
	}
	PrintlnC.Green("Bucket %s was created successfully\n", *c.BucketName)
	return nil
}

// removeBucket removes a bucket
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

// listBuckets prints the list of the existing buckets
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

// putObject puts an object to the bucket
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

// removeObject removes an object from the bucket
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

// getObject gets an object from the bucket
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

// listObjects prints the list of the objects in the bucket
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

func main() {
	flagsInit()
	if !verifyFlags() {
		return
	}
	var client S3Client
	if err := client.configCredentials(ConfigPath, BucketName); err != nil {
		PrintlnC.Red(err.Error())
	}

	var err error
	switch Operation {
	case "mb", "MakeBucket":
		err = client.makeBucket()
	case "rb", "RemoveBucket":
		err = client.removeBucket()
	case "lb", "ListBuckets":
		err = client.listBuckets()
	case "put", "PutObject":
		err = client.putObject(ObjectPath)
	case "rm", "RemoveObject":
		err = client.removeObject(ObjectPath)
	case "get", "GetObject":
		err = client.getObject(ObjectPath)
	case "ls", "ListObjects":
		err = client.listObjects()
	default:
		PrintlnC.Red("Unknown operation!!\n")
	}
	if err != nil {
		PrintlnC.Red(err.Error())
	}
}

func flagsInit() {
	flag.Usage = usage([]string{"--Op=<value> --Bucket=<value> --Path=<value>"}, []string{fmt.Sprintf("--Op=put --Bucket=bari-test --Path=example.txt\n\n")})
	flag.StringVar(&BucketName, "Bucket", "", "The bucket name")
	flag.StringVar(&ConfigPath, "ConfigPath", "config.json", "The config file path")
	flag.StringVar(&ObjectPath, "Path", "", "The object path for put, get, and remove object")
	flag.StringVar(&Operation, "Op", "", "mb[MakeBucket]/rb[RemoveBucket]/lb[ListBuckets]/put[PutObject]/rm[RemoveObject]/get[GetObject]/ls[ListObjects]")
	flag.Parse()
}

func verifyFlags() bool {
	if Operation == "" {
		PrintlnC.Red("ERROR: --Op flag cannot be empty! Please provide an operation\n")
		flag.Usage()
		return false
	}
	if BucketName == "" && Operation != "ls" {
		PrintlnC.Red("ERROR: --Bucket flag cannot be empty! Please provide a bucket name\n")
		flag.Usage()
		return false
	}
	if (Operation == "put" || Operation == "rm" || Operation == "get") && ObjectPath == "" {
		PrintlnC.Red("ERROR: --Path flag cannot be empty! Please provide an object path\n")
		flag.Usage()
		return false
	}
	return true
}
