import os
import boto3
import json
from tkinter import *
import tkinter as tk
import time
import multiprocessing.dummy as mp


def generate_client(params):
    return boto3.client("s3", **params)


def load_config():
    with open(
        os.path.dirname(os.path.realpath(__file__)) + "/config.json", "r"
    ) as file:
        config = json.loads(file.read())
    return config


def run_migration(num_threads, migrate_from="aws", send_to="client"):
    global config, migration_label

    def update(o):
        print(f"Downloading {o['Key']}...")
        data = aws_client.get_object(Bucket=bucket_from, Key=o["Key"])
        lyve_client.upload_fileobj(data["Body"], bucket_to, o["Key"])

    top_logs = Toplevel(m)
    lab = Label(top_logs)
    lab.pack()

    aws_client = generate_client(config["aws"]["params"])
    lyve_client = generate_client(config["lyve"]["params"])

    bucket_from = config["aws"]["bucket_name"]
    bucket_to = config["lyve"]["bucket_name"]

    bucket_from_objects = aws_client.list_objects_v2(Bucket=bucket_from)
    num_objects = len(bucket_from_objects["Contents"])

    p = mp.Pool(num_threads)
    p.map(update, bucket_from_objects["Contents"])
    p.close()
    p.join()

    migration_label.configure(text=f"Transfer successful! {num_objects}/{num_objects}")


def generate_config(lyve_id, lyve_secret, lyve_bucket, aws_id, aws_secret, aws_bucket):
    global config, config_label
    top = Toplevel(m)
    top.geometry("400x280")
    top.title("Generated Configuration")

    config["lyve"]["params"]["aws_access_key_id"] = lyve_id.get()
    config["lyve"]["params"]["aws_secret_access_key"] = lyve_secret.get()
    config["lyve"]["bucket_name"] = lyve_bucket.get()
    config["aws"]["params"]["aws_access_key_id"] = aws_id.get()
    config["aws"]["params"]["aws_secret_access_key"] = aws_secret.get()
    config["aws"]["bucket_name"] = aws_bucket.get()

    Label(top, text=json.dumps(config, indent=2), justify=LEFT).pack()
    if lyve_id and lyve_secret and lyve_bucket and aws_id and aws_secret and aws_bucket:
        config_label.configure(text="Config generated successfully!")
    else:
        config_label.configure(text="Please fill out all fields.")
    return config


def open_popup():
    top = Toplevel(m)
    top.geometry("750x250")
    top.title("Child Window")
    Label(top, text="Hello World!", font=("Mistral 18 bold")).place(x=150, y=80)


if __name__ == "__main__":
    m = Tk()
    m.geometry("1000x200")
    m.title("AWS S3 <> Lyve Cloud Migration Solution")

    config = {
        "lyve": {
            "params": {
                "aws_access_key_id": "",
                "aws_secret_access_key": "",
                "region_name": "ap-southeast-1",
                "endpoint_url": "https://s3.ap-southeast-1.lyvecloud.seagate.com",
            },
            "bucket_name": "",
        },
        "aws": {
            "params": {
                "aws_access_key_id": "",
                "aws_secret_access_key": "",
                "region_name": "us-east-1",
            },
            "bucket_name": "",
        },
    }

    # Row 1
    Label(m, text="Configuration").grid(row=1, column=1)

    # Row 2
    Label(m, text="Lyve Cloud Access Key ID:", width=20).grid(row=2, column=1)
    lyve_id = Entry(m, width=20)
    lyve_id.grid(row=2, column=2)

    Label(m, text="AWS Access Key ID:", width=20).grid(row=2, column=3)
    aws_id = Entry(m, width=20)
    aws_id.grid(row=2, column=4)

    # Row 3
    Label(m, text="Lyve Cloud Secret Access Key:").grid(row=3, column=1)
    lyve_secret = Entry(m, width=20)
    lyve_secret.grid(row=3, column=2)

    Label(m, text="AWS Secret Access Key:").grid(row=3, column=3)
    aws_secret = Entry(m, width=20)
    aws_secret.grid(row=3, column=4)

    # Row 4
    Label(m, text="Lyve Cloud Bucket to Transfer:").grid(row=4, column=1)
    lyve_bucket = StringVar()
    lyve_client = generate_client(config["lyve"]["params"])
    lyve_buckets = [bucket["Name"] for bucket in lyve_client.list_buckets()["Buckets"]]
    drop = OptionMenu(m, lyve_bucket, *lyve_buckets)
    drop.grid(row=4, column=2)

    Label(m, text="AWS Bucket to Transfer:").grid(row=4, column=3)
    aws_bucket = StringVar()
    aws_client = generate_client(config["aws"]["params"])
    aws_buckets = [bucket["Name"] for bucket in aws_client.list_buckets()["Buckets"]]
    drop = OptionMenu(m, aws_bucket, *aws_buckets)
    drop.grid(row=4, column=4)

    # Row 5
    Label(m, text="Number of threads").grid(row=5, column=1)
    num_threads = Entry(m, width=20, textvariable=4)
    num_threads.grid(row=5, column=2)

    # Row 6
    Button(
        m,
        text="Generate Config File",
        command=lambda: generate_config(
            lyve_id, lyve_secret, lyve_bucket, aws_id, aws_secret, aws_bucket
        ),
    ).grid(row=6, column=1)
    config_label = Label(m, text="Please fill out all the fields.")
    config_label.grid(row=6, column=2)

    # Row 7
    Button(
        m,
        text="Migrate Data (AWS -> S3)",
        command=lambda: run_migration(int(num_threads.get())),
    ).grid(row=7, column=1)
    migration_label = Label(m, text="", justify=LEFT)
    migration_label.grid(row=7, column=2)

    # Row 8
    Button(m, text="Quit Application", command=m.quit).grid(row=8, column=1)

    m.mainloop()
