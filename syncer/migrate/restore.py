import os
from subprocess import check_output


exclude = []
include = []
source_prefix = ''
endpoint = os.getenv('ENDPOINT')
region = os.getenv('AWS_DEFAULT_REGION')
source_folder = os.getenv('SOURCE_FOLDER')
target_bucket = os.getenv('TARGET_BUCKET')

sync_cmd = f'aws s3 sync {source_folder} s3://{target_bucket}{source_prefix} --region {region} --endpoint-url {endpoint}'

if len(exclude) > 0:
    sync_cmd += ' --exclude ' + ' --exclude '.join(exclude)
if len(include) > 0:
    sync_cmd += ' --include ' + ' --include '.join(include)

print(f'Running {sync_cmd}')
out = check_output(sync_cmd.split(' '))
print("Output:")
print(out)
