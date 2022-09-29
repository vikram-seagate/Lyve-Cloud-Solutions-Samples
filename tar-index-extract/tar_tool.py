"""
Tar File Index and Extract Tool

This script will perform 2 functions.
1. Index a give tar file or tar files in a directory
2. Extract only those files inside a tar given the names of the files inside the tar and the tar file name from an
S3 bucket.

The idea is to minimize uploads to an s3 bucket by taring a lot of small files into a big tar.
Then upload the tar to a bucket. In order to only pull out small chunk of the files in a big tar, the index is used to
find the location of each file within the tar. The start and end location of the files is used along with get byterange
operation on an S3 bucket to achieve this.

| $File: tar_tool.py $
| $Revision: #1 $
| $Author: arati.kulkarni@seagate.com $
| $DateTime: 2021/11/12 12:34:29 $

"""

from argparse import ArgumentParser
import tarfile
import os
import datetime
import boto3
import csv
from art import tprint

def extract_files(filenames, outputdir, conn_details, bucketname):
    '''
    Extract given files from a tarfile
    :param filenames: tarfilename,file0,file1.. Files to be extracted from tarfilename
    :param outputdir: Directory to store extracted files
    :param conn_details: S3 Connection details
    :param bucketname:
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
        print(f"!!!Index file for tarfile {tarfilename} does not exist, please create index before extracting!!!")
        print('Exiting!')
        exit()

    for file in filenames:
        fetch_object_by_range(index[file][2], index[file][3], index[file][0], outputdir, tarfilename, bucketname, s3)

    print(f'\nDone extracting {filenames} to {outputdir}')


def fetch_index(indexfile, outputdir, bucketname, s3_config):
    '''
    Fetch Index file for a tar file before extracting partial object
    :param indexfile: Index file
    :param outputdir: Destination where downloaded files will be stored
    :param bucketname: Bucket where the tar object resides
    :param s3_config: S3 Connection Object
    :return:
    '''
    print(f"Collecting Index file {indexfile}")
    index_object = s3_config.Object(bucketname, indexfile)
    response = index_object.get()

    with open(os.path.join(outputdir, indexfile), 'wb') as outfile:
        outfile.write(response['Body']._raw_stream.data)
    print(f"Done writing the Index file {indexfile}")

def fetch_object_by_range(start, end, filename, outputdir, tarfilename, bucketname, s3_config):
    '''
    Fetch object given its byte range
    :param start: Byte Range - start
    :param end: Byte Range - end
    :param filename: File name to be downloaded, will be used to save the byte range into this filename
    :param outputdir: Destination where the file will be saved
    :param tarfilename: Tar object name
    :param bucketname: Bucket name where tar resids
    :param s3_config: S3 Connection object
    :return:
    '''

    partial_obj = s3_config.Object(bucketname, os.path.basename(tarfilename))

    byterange = f"bytes={start}-{end}"
    print(f"Collecting {filename} from Byte Range: {byterange}")

    response = partial_obj.get(
        Range=byterange,
        ResponseContentType='byte',
    )

    with open(os.path.join(outputdir, filename), 'wb') as outfile:
        outfile.write(response['Body']._raw_stream.data)
    print(f"Done writing the file {filename}")


def index_tarfile(tarfilename):
    '''
    Index given tar file, produce CSV, with filename,size,startbyte,endbyte
    :param tarfilename: Tar File name that is to be indexed
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
    Get Connection Details from Config File
    :param configfile: path to config file
    :return:
    '''
    conn_details = {}
    with open(configfile) as f:
        for line in f.readlines():
            conn_details[line.split('=')[0]] = line.split('=')[-1].rstrip('\n')
    return conn_details

def process_directory(path):
    '''
    Process and Index all tar files in the directory
    :param path: directory to be processed
    :return:
    '''
    for (dirpath, dirnames, filenames) in os.walk(path):
        for filename in filenames:
            if tarfile.is_tarfile(os.path.join(dirpath, filename)):
                index_tarfile(os.path.join(dirpath, filename))

def dump_cli_options(args):
    '''
    Dump CLI options this program was run with
    :param args: All arguments
    :return:
    '''
    print(f'Running Tar Tool with following options: ')
    for k, v in vars(args).items():
        print(f'   {k}: {v}')


def ensure_dir(path):
    '''
    Check if this directory exists and if not create them
    :param path:
    :return:
    '''
    if not os.path.exists(path):
        os.makedirs(path)
    return path

if __name__ == '__main__':
    print('#' * 80)
    tprint("            Tar-Tool")
    print('                      Tar File Index and Extract Tool \n')
    print('#' * 80)
    parser = ArgumentParser()
    parser.add_argument("--tarfile", help="Name of the tarfile that needs to be indexed")
    parser.add_argument("--path", help="Path to a directory containing tarfiles, all *.tar files in dir will be indexed")
    parser.add_argument("--extract", help="Comma separated list of the tarfile and files to be extracted from that tarfile")
    parser.add_argument("--outputpath", help="Path to a directory where extracted files will be kept", default=os.getcwd())
    parser.add_argument("--bucketname", help="Name of the S3 bucket to get data from", default='tar-exp0')
    parser.add_argument("--configfile", help="Path to config File",
                        default=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config', 'conn.conf'))
    args = parser.parse_args()

    starttime = datetime.datetime.now()
    dump_cli_options(args)

    conn_details = get_connection_details(args.configfile)

    if args.tarfile:
        print(f"Starting Indexing for {args.tarfile}")
        index_tarfile(args.tarfile)
    elif args.path:
        print(f"Starting Indexing for all tars in {args.path}")
        process_directory(args.path)
    elif args.extract:
        files_to_extract = args.extract.split(',')
        extract_files(files_to_extract, args.outputpath, conn_details, args.bucketname)
