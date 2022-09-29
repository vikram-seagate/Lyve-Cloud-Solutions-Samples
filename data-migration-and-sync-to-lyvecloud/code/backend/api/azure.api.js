const {BlobServiceClient} = require("@azure/storage-blob");
require("dotenv").config();

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

module.exports = {
    AzureProxyExecute
};