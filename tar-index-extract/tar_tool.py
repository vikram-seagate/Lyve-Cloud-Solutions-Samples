"""
This tool provides a script to partially extract files from a tar object that resides inside your S3 bucket.

| $File: tar_tool.py $
| $Revision: #1 $
| $Author: arati.kulkarni@seagate.com $
| $DateTime: 2021/11/12 12:34:29 $
"""

import os
import csv
import boto3
import tarfile
import datetime
from art import tprint
from argparse import ArgumentParser
from botocore.exceptions import ClientError

def extract_files(filenames, outputdir, conn_details, bucketname):
    '''
    Extract given files from a tar file.

    :param filenames: tarfilename,file0,file1.. files to be extracted from tarfilename
    :param outputdir: Directory to store the extracted files
    :param conn_details: S3 connection details
    :param bucketname: Name of the bucket that containts the tar file
    :return:
    '''

    s3 = boto3.resource('s3', aws_access_key_id=conn_details["accessKey"],
                        aws_secret_access_key=conn_details["secretKey"], endpoint_url=conn_details["endpoint"], )

    tarfilename = filenames.pop(0)
    outputdir = os.path.join(outputdir, os.path.basename(tarfilename).split('.')[0])
    ensure_dir(outputdir)
    indexfile = f"{os.path.basename(tarfilename).split('.')[0]}.index"

    fetch_index(indexfile, outputdir, bucketname, s3)
    print(f'Extracting files to {outputdir}')

    try:
        with open(os.path.join(outputdir, indexfile), 'r') as indf:
            reader = csv.reader(indf)
            index = {rows[0]: rows for rows in reader}
    except FileNotFoundError:
        print(f"!!!Didn't found index file for {tarfilename} locally!!!")
        print('Exiting!')
        exit()

    for file in filenames:
        fetch_object_by_range(index[file][2], index[file][3], index[file][0], outputdir, tarfilename, bucketname, s3)

    print(f'\nDone extracting {filenames} to {outputdir}')


def extract_range(args, outputdir, conn_details, bucketname):
    '''
    Extract given range from a tar file.

    :param args: tarfilename,start-range,end-range,destination-file-name.
    :param outputdir: Directory to store the extracted file
    :param conn_details: S3 connection details
    :param bucketname: Name of the bucket that containts the tar file
    :return:
    '''

    s3 = boto3.resource('s3', aws_access_key_id=conn_details["accessKey"],
                        aws_secret_access_key=conn_details["secretKey"], endpoint_url=conn_details["endpoint"], )

    tarfilename = args[0]
    startrange = args[1]
    endrange = args[2]
    filename = args[3]

    outputdir = os.path.join(outputdir, os.path.basename(tarfilename).split('.')[0])
    ensure_dir(outputdir)

    print(f'Extracting file to {outputdir}')

    fetch_object_by_range(startrange, endrange, filename, outputdir, tarfilename, bucketname, s3)

    print(f'\nDone extracting range {startrange},{endrange} to {outputdir}')    


def fetch_index(indexfile, outputdir, bucketname, s3_config):
    '''
    Fetch index file for the tar file before extracting partial object.

    :param indexfile: Index file
    :param outputdir: Directory to store the extracted file
    :param bucketname: Name of the bucket that containts the tar file
    :param s3_config: S3 connection object
    :return:
    '''

    print(f"Collecting index file {indexfile}")
    index_object = s3_config.Object(bucketname, indexfile)
    try:
        response = index_object.get()
    except ClientError as ex:
        if ex.response['Error']['Code'] == 'NoSuchKey':
            print(f"!!!Index file {indexfile} is missing in the bucket, please create and upload index before extracting!!!")
            print('Exiting!')
            exit()
        else:
            raise

    with open(os.path.join(outputdir, indexfile), 'wb') as outfile:
        outfile.write(response['Body']._raw_stream.data)
    print(f"Done writing the index file {indexfile}")

def fetch_object_by_range(start, end, filename, outputdir, tarfilename, bucketname, s3_config):
    '''
    Fetch object given its byte range.

    :param start: Byte Range - start
    :param end: Byte Range - end
    :param filename: Filename to be downloaded, will be used to save the byte range into this filename
    :param outputdir: Directory to store the extracted file
    :param tarfilename: The tar object name
    :param bucketname: Name of the bucket that containts the tar file
    :param s3_config: S3 connection object
    :return:
    '''

    partial_obj = s3_config.Object(bucketname, os.path.basename(tarfilename))

    byterange = f"bytes={start}-{end}"
    print(f"Collecting {filename} from byte range: {byterange}")

    response = partial_obj.get(
        Range=byterange,
        ResponseContentType='byte',
    )

    with open(os.path.join(outputdir, filename), 'wb') as outfile:
        outfile.write(response['Body']._raw_stream.data)
    print(f"Done writing the file {filename}")


def index_tarfile(tarfilename):
    '''
    Index a given tar file. Produces CSV with filename, size, start-byte, end-byte.

    :param tarfilename: A tar filename to be indexed
    :return:
    '''

    index = [["filename", "size", "start", "end"]]
    with tarfile.open(tarfilename, 'r') as tfile:
        for member in tfile.getmembers():
            index.append([member.name, member.size, member.offset_data, member.offset_data + member.size - 1])

    #Write the list to a csv file
    indexfilename = os.path.join(os.path.dirname(tarfilename),
                           f"{os.path.basename(tarfilename).split('.')[0]}.index")
    with open(indexfilename, 'w', newline='') as f:
        csv_writer = csv.writer(f)
        csv_writer.writerows(index)

    print(f'\nDone indexing tar {tarfilename}, \nIndex file: {indexfilename}')

def get_connection_details(configfile):
    '''
    Get connection details from config file.

    :param configfile: Path to config file
    :return:
    '''

    conn_details = {}
    with open(configfile) as f:
        for line in f.readlines():
            conn_details[line.split('=')[0]] = line.split('=')[-1].rstrip('\n')
    return conn_details

def process_directory(path):
    '''
    Process and index all tar files in the directory.

    :param path: Directory to be processed
    :return:
    '''

    for (dirpath, dirnames, filenames) in os.walk(path):
        for filename in filenames:
            if tarfile.is_tarfile(os.path.join(dirpath, filename)):
                index_tarfile(os.path.join(dirpath, filename))

def dump_cli_options(args):
    '''
    Dump CLI options this program was run with.

    :param args: All arguments
    :return:
    '''

    print(f'Running the tar tool with the following options: ')
    for k, v in vars(args).items():
        print(f'   {k}: {v}')


def ensure_dir(path):
    '''
    Check if this directory exists, and if not, create them.

    :param path: The directory path to check
    :return:
    '''

    if not os.path.exists(path):
        os.makedirs(path)
    return path

if __name__ == '__main__':
    print('#' * 80)
    tprint("            Tar-Tool")
    print('                      A TAR File Index and Extract Tool \n')
    print('#' * 80)
    parser = ArgumentParser()
    parser.add_argument("--tarfile", help="Name of the tar file that needs to be indexed")
    parser.add_argument("--path", help="Path to a directory containing tar files, all *.tar files in dir will be indexed")
    parser.add_argument("--extract", help="Comma separated list of the tar file and files to be extracted from that tar file")
    parser.add_argument("--getrange", help="Comma separated list of the tar file, the range to be extracted from that tar file, and the destination filename")
    parser.add_argument("--outputpath", help="Path to a directory where extracted files will be kept", default=os.getcwd())
    parser.add_argument("--bucketname", help="Name of the bucket that containts the tar file", default='tar-exp0')
    parser.add_argument("--configfile", help="Path to config file",
                        default=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config', 'conn.conf'))
    args = parser.parse_args()

    starttime = datetime.datetime.now()
    dump_cli_options(args)

    conn_details = get_connection_details(args.configfile)

    if args.tarfile:
        print(f"Starting indexing for {args.tarfile}")
        index_tarfile(args.tarfile)
    elif args.path:
        print(f"Starting indexing for all tars in {args.path}")
        process_directory(args.path)
    elif args.extract:
        files_to_extract = args.extract.split(',')
        extract_files(files_to_extract, args.outputpath, conn_details, args.bucketname)
    elif args.getrange:
        range_to_extract = args.getrange.split(',')
        extract_range(range_to_extract, args.outputpath, conn_details, args.bucketname)
