const axios = require("axios");
const AWS = require("aws-sdk");
const OSS = require("ali-oss");
const {Storage} = require("@google-cloud/storage");
const {BlobServiceClient} = require("@azure/storage-blob");
require("dotenv").config();

function apiGetNewSyncJobToRun() {
    return axios.get(`http://${process.env.BACKEND_IP}:10086/common/new-sync-job-to-run`);
}

function aptUpdateSyncJobProgress(id, data) {
    return axios.put(`http://${process.env.BACKEND_IP}:10086/synchronization-jobs/${id}`, data);
}

function aptUpdateSyncTaskProgress(id, data) {
    return axios.put(`http://${process.env.BACKEND_IP}:10086/synchronization-tasks/${id}`, data);
}

function apiUpdateSyncJobPartitionProgress(id, partitionIndex, data) {
    return axios.put(`http://${process.env.BACKEND_IP}:10086/synchronization-jobs/${id}/partitions/${partitionIndex}`, data);
}

function apiPostSyncJobLog(id, log) {
    return axios.post(`http://${process.env.BACKEND_IP}:10086/synchronization-jobs/${id}/logs`, log);
}

function GeneralS3ProxyExecute(endpoint, accessKeyId, accessKeySecret, cmd, params) {
    const s3 = new AWS.S3({
        endpoint, apiVersion: "2006-03-01", accessKeyId: accessKeyId, secretAccessKey: accessKeySecret
    });

    return new Promise(((resolve, reject) => {
        if (params) {
            s3[cmd](params, (err, data) => {
                if (err) {
                    reject(err);
                } else {
                    resolve(data);
                }
            });
        } else {
            s3[cmd]((err, data) => {
                if (err) {
                    reject(err);
                } else {
                    resolve(data);
                }
            });
        }
    }));
}

function LyveProxyExecute(region, accessKeyId, accessKeySecret, cmd, params) {
    const s3 = new AWS.S3({
        endpoint: `https://s3.${region}.lyvecloud.seagate.com`,
        apiVersion: "2006-03-01",
        region: region,
        accessKeyId: accessKeyId,
        secretAccessKey: accessKeySecret
    });

    return new Promise(((resolve, reject) => {
        if (params) {
            s3[cmd](params, (err, data) => {
                if (err) {
                    reject(err);
                } else {
                    resolve(data);
                }
            });
        } else {
            s3[cmd]((err, data) => {
                if (err) {
                    reject(err);
                } else {
                    resolve(data);
                }
            });
        }
    }));
}


function AlibabaProxyExecute(region, accessKeyId, accessKeySecret, cmd, params, bucket) {
    let client;
    if (bucket) {
        client = new OSS({
            region,
            accessKeyId,
            accessKeySecret,
            bucket
        });
    } else {
        client = new OSS({
            region,
            accessKeyId,
            accessKeySecret,
        });
    }

    return new Promise(async (resolve, reject) => {
        try {
            let result;
            if (params) {
                result = client[cmd](...params);
            } else {
                result = client[cmd]();
            }
            resolve(result);
        } catch (e) {
            reject(e);
        }
    });
}

async function AzureProxyExecute(connection_string, cmd, params, container, blob_key) {
    let serviceClient = BlobServiceClient.fromConnectionString(connection_string);
    let containerClient, blobClient;
    if (container) {
        containerClient = serviceClient.getContainerClient(container);
        if (blob_key) {
            blobClient = containerClient.getBlobClient(blob_key);
        }
    }

    switch (cmd) {
        case "listContainers": {
            return new Promise(async (resolve, reject) => {
                try {
                    let result = [];
                    let containers = serviceClient.listContainers();
                    for await (const container of containers) {
                        result.push(container);
                    }
                    resolve(result);
                } catch (e) {
                    reject(e);
                }
            });
        }
        case "listBlobsFlat": {
            return new Promise(async (resolve, reject) => {
                try {
                    let result = [];
                    for await (const blob of containerClient.listBlobsFlat()) {
                        result.push(blob);
                    }
                    resolve(result);
                } catch (e) {
                    reject(e);
                }
            });
        }
        case "download": {
            return new Promise(async (resolve, reject) => {
                try {
                    let downloadBlockBlobResponse;
                    if (params) {
                        downloadBlockBlobResponse = await blobClient.download(...params);
                    } else {
                        downloadBlockBlobResponse = await blobClient.download();
                    }
                    const downloaded = await streamToBuffer(downloadBlockBlobResponse.readableStreamBody);
                    resolve({Body: downloaded});
                } catch (e) {
                    reject(e);
                }
            });
        }
    }
}

function GoogleProxyExecute(credentials, cmd, params, projectId, bucket, file) {
    let client = new Storage({
        projectId, credentials
    });

    // change to bucket client
    if (bucket) {
        client = client.bucket(bucket);
        if (file) {
            client = client.file(file);
        }
    }

    if (cmd === "createReadStream") {
        return new Promise((resolve, reject) => {
            const data = [];
            const readStream = params ? client.createReadStream(...params) : client.createReadStream();

            readStream
                .on("data", (chunk) => {
                    data.push(chunk);
                })
                .on("end", () => {
                    resolve({Body: Buffer.concat(data)});
                })
                .on("error", (e) => {
                    reject(e);
                });
        });
    }

    return new Promise(((resolve, reject) => {
        if (params) {
            client[cmd](...params, (err, data) => {
                if (err) {
                    reject(err);
                } else {
                    resolve(data);
                }
            });
        } else {
            client[cmd]((err, data) => {
                if (err) {
                    reject(err);
                } else {
                    resolve(data);
                }
            });
        }
    }));
}

async function streamToBuffer(readableStream) {
    return new Promise((resolve, reject) => {
        const chunks = [];
        readableStream.on("data", (data) => {
            chunks.push(data instanceof Buffer ? data : Buffer.from(data));
        });
        readableStream.on("end", () => {
            resolve(Buffer.concat(chunks));
        });
        readableStream.on("error", reject);
    });
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

module.exports = {
    apiGetNewSyncJobToRun,
    GeneralS3ProxyExecute,
    LyveProxyExecute,
    aptUpdateSyncJobProgress,
    sleep,
    apiPostSyncJobLog,
    aptUpdateSyncTaskProgress,
    apiUpdateSyncJobPartitionProgress,
    AlibabaProxyExecute,
    AzureProxyExecute,
    GoogleProxyExecute
};