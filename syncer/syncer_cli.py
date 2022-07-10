import os
import json
import click
import boto3


@click.group()
def syncer_operations():
    pass


@click.command()
@click.argument('lc_region')
@click.argument('lc_endpoint')
@click.argument('secret_name')
@click.argument('lc_access_key')
@click.argument('lc_secret_key')
@click.argument('source_bucket')
@click.argument('target_bucket')
@click.option('--exist', '-e', is_flag=True, prompt="Boolean flag to use an existing key, for example: -e=true",
                help="Boolean flag to use an existing key, for example: -e=true")
def run(exist, secret_name, lc_access_key, lc_secret_key, lc_region, lc_endpoint, source_bucket, target_bucket):
    '''The tool has two options:\n
       - Create a new secret from AWS SecretManager\n
       - Use an existing secret using -e or --exit flag\n
       -----------------------------------\n
       lc_region:     lyve cloud region name\n
       lc_endpoint:   lyve cloud endpoint\n
       secret_name:   secret key for secret manager\n
       lc_access_key: lyve cloud access key\n
       lc_secret_key: lyve cloud secret key\n
       source_bucket: aws bucket name\n
       target_bucket: lyve cloud bucket name\n
       '''
    
    # connection to the secret manager
    session = boto3.session.Session()
    client = session.client(service_name='secretsmanager')

    if exist:
        print("Using an existing secret")
    else: # create new secret
        response = client.create_secret(Name = secret_name,
            SecretString = str({"lc_access_key": lc_access_key, "lc_secret_key": lc_secret_key}).replace("\'", "\""))
    
    insert_to_config(secret_name, lc_endpoint, lc_region, source_bucket, target_bucket)
    # after inserting variables to the chalice config file, enter into the ".chalice" dir
    os.chdir('..')
    os.system("pip3 install -r requirements.txt") 
    os.system("chalice deploy")


# Insert all necessary user vars to chalice config files
def insert_to_config(secret_name, lc_endpoint, lc_region, source_bucket, target_bucket):
    cur_dir = os.getcwd()
    os.chdir(cur_dir + "/syncer/.chalice")
    # open the config file and insert it into temp one
    with open('config.json', 'r') as f:
        config = json.load(f)

    config["stages"]["dev"]["environment_variables"]["lc_region"] = lc_region
    config["stages"]["dev"]["environment_variables"]["lc_secrets"] = secret_name
    config["stages"]["dev"]["environment_variables"]["lc_endpoint"] = lc_endpoint
    config["stages"]["dev"]["environment_variables"]["source_bucket"] = source_bucket
    config["stages"]["dev"]["environment_variables"]["target_bucket"] = target_bucket

    with open('config.json', 'w', encoding='utf8') as f:
        json.dump(config, f, indent=2)
      

syncer_operations.add_command(run)

if __name__ == '__main__':
    syncer_operations()