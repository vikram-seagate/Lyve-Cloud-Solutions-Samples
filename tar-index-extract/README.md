# Using tar file index to extract data efficiently

             _____                      _____                _
            |_   _|  __ _  _ __        |_   _|  ___    ___  | |
              | |   / _` || '__| _____   | |   / _ \  / _ \ | |
              | |  | (_| || |   |_____|  | |  | (_) || (_) || |
              |_|   \__,_||_|            |_|   \___/  \___/ |_|
              

## Introduction

This tool provides a script to partially extract files from a tar object that resides inside your S3 bucket.

The idea is to minimize the number of uploads to an S3 bucket by tarring several small files into a tar file and downloading only the necessary files from this tar file later. It helps with a better throughput during the upload process and saves time and network costs during the download process.

To only get some of the files that are part of the tar file, this tool allows to create an index file, which is used to find the location of each file within the tar. The start and end location of the files is used along with the *get byte range* operation on an S3 object to achieve this.

## Requirements
* [`Python 3.8`](https://www.python.org/downloads/) and above.
* Lyve Cloud bucket credentials - Access Key, Secret Key, region and endpoint URL.

## Known Limitations 
This is a proof of concept for tar file indexing capabilities and partial tar File retrieval capabilities. 
Additional features or customization is left up to the reader.
Some of the features that can be added: 
* Indexing and extraction of compressed tar file.
* Safe storing of the credentials (currently stored in a plain text).

## Running Steps
**Step 1: Install required libraries**

Run 
```pip install -r requirements.txt```

**Step 2: Set Lyve Cloud credentials**

Replace the placeholders in config/conn.conf with valid credentials with access to the desired bucket.
```
endpoint=<Lyve Cloud Endpoint URL>
accessKey=<Access Key to the Lyve Cloud API>
secretKey=<Secret Key to the Lyve Cloud API>
```

**Step 3: Create index file of the tar**

Run 
```python3 tar_tool.py --tarfile <path of the tar file>```

This will create an index file that you will need to upload with the tar file to your S3 bucket.

Sample output for the command ```python3 tar_tool.py --tarfile C:\Users\akulkarni\tools\index-tar\tfile.tar```
```
Running the tar tool with the following options:
   tarfile: C:\Users\akulkarni\tools\index-tar\tfile.tar
   path: None
   extract: None
   outputpath: C:\Users\akulkarni\tools
   bucketname: tar-exp0
   configfile: C:\Users\akulkarni\tools\index-tar\config\conn.conf
Starting indexing for C:\Users\akulkarni\tools\index-tar\tfile.tar

Done indexing tar C:\Users\akulkarni\tools\index-tar\tfile.tar,
Index file: C:\Users\akulkarni\tools\index-tar\tfile.index
```
**Step 4: Upload tar file**

Upload your tar file **with** the generated index file to your desired bucket.

**Step 5: Extract files from the tar**

Now that you have your tar file with its index file in your bucket, you can extract specific files from that tar.

Run the following command to extract specific file from the tar:
```
python3 tar_tool.py
--extract <tar file name>,<list of files to be extracted, delimited by comma>
--outputpath <output path for files to be extracted>
--bucket <name of your bucket>
```

It is also possible to extract by specific byte range. This operation won't use the index file.
```
python3 tar_tool.py
--getrange <tar filename>,<start-byte>,<end-byte>,<destination filename>
--outputpath <output path for file to be extracted>
--bucket <name of your bucket>
```

## Results 
Your extracted files will be placed in the path that you have specifed.

Sample output for the command ```python3 tar_tool.py --extract tfile.tar,one.txt,four.txt --outputpath C:\Users\akulkarni\tools\index-tar\output --bucket tar-exp0```
```
Running the tar tool with the following options:
   tarfile: None
   path: None
   extract: tfile.tar,one.txt,four.txt
   outputpath: C:\Users\akulkarni\tools\index-tar\output
   bucketname: tar-exp0
   configfile: C:\Users\akulkarni\tools\index-tar\config\conn.conf
Collecting index file tfile.index
Done writing the index file tfile.index
Extracting files to C:\Users\akulkarni\tools\index-tar\output\tfile
Collecting one.txt from Byte Range: bytes=62976-63017
Done writing the file one.txt
Collecting four.txt from Byte Range: bytes=512-62363
Done writing the file four.txt

Done extracting ['one.txt', 'four.txt'] to C:\Users\akulkarni\tools\index-tar\output\tfile
```

## Usage
```
The usage of the tool is as follows:

usage: tar_tool.py [-h] [--tarfile TARFILE] [--path PATH] [--extract EXTRACT]
                   [--getrange GETRANGE] [--outputpath OUTPUTPATH] [--bucketname BUCKETNAME]
                   [--configfile CONFIGFILE]

optional arguments:
  -h, --help            show this help message and exit
  --tarfile TARFILE     Name of the tar file that needs to be indexed
  --path PATH           Path to a directory containing tarfiles, all *.tar
                        files in dir will be indexed
  --extract EXTRACT     Comma separated list of the tar file and files to be 
                        extracted from that tar file
  --getrange GETRANGE   Comma separated list of the tar file, the range to be 
                        extracted from that tar file, and the destination filename  
  --outputpath OUTPUTPATH
                        Path to a directory where extracted files will be kept
  --bucketname BUCKETNAME
                        Name of the bucket that containts the tar file
  --configfile CONFIGFILE
                        Path to config File
```
## Tested by
Sep 25, 2022: Leon Markovich (leon.markovich@seagate.com) on Ubuntu 20.04.3 LTS

Sep 18, 2022: Sasha Chernin (alexander.chernin@seagate.com) on Windows 10

Sep 04, 2022: Arati Kulkarni (arati.kulkarni@seagate.com) on Windows 10

## Structure
This section will describe the representation of each of the folders or files in the structure.
```
.
├── README.md
├── requirements.txt
├── config
│   └── conn.conf
├── output
│   └── placeholder for output
├── __init__.py
├── tar_tool.py
├── tfile.index
├── tfile.tar
├── tfile1.index
├── tfile1.tar
```
