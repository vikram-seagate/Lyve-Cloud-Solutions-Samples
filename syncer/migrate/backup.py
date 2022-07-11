import os
from subprocess import check_output

exclude = []
include = []
source_prefix = ''
region = os.getenv('AWS_DEFAULT_REGION')
source_bucket = os.getenv('SOURCE_BUCKET')
target_folder = os.getenv('TARGET_FOLDER', './data')

sync_cmd = f'aws s3 sync s3://{source_bucket}{source_prefix} {target_folder} --region {region}'

if len(exclude) > 0:
    sync_cmd += ' --exclude ' + ' --exclude '.join(exclude)
if len(include) > 0:
    sync_cmd += ' --include ' + ' --include '.join(include)

print(f'Running {sync_cmd}')
out = check_output(sync_cmd.split(' '))
print("Output:")
print(out)
