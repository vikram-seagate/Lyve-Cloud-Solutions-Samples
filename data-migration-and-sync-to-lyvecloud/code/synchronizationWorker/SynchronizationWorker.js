const {
    apiGetNewSyncJobToRun,
    GeneralS3ProxyExecute,
    LyveProxyExecute,
    aptUpdateSyncJobProgress,
    apiPostSyncJobLog,
    apiUpdateSyncJobPartitionProgress,
    aptUpdateSyncTaskProgress,
    AlibabaProxyExecute,
    GoogleProxyExecute,
    AzureProxyExecute,
} = require("./api");
const {getPassphraseFromEnv, decryptWithAES} = require("./Encryption");

// 50MB per part
const MULTI_PART_SIZE = 5 * 1e7;

class SynchronizationWorker {
    constructor() {
        this.passphrase = null;
        this.currentJob = null;

        this.stopping = false;
    }

    async start() {
        if (this.stopping) {
            console.trace(`\n\nexiting start()`);
            process.exit(0);
        }

        if (!process.env.BACKEND_IP) {
            console.trace(`\n\nBackend IP address is not set. Please set BACKEND_IP env variable.`);
            return setTimeout(() => {
                this.start();
            }, 5000);
        }

        this.passphrase = getPassphraseFromEnv();
        console.log(this.passphrase);
        if (this.passphrase === undefined || this.passphrase === null) {
            console.trace(`\n\nPassphrase is not set. Please set PASSPHRASE env variable.`);
            return setTimeout(() => {
                this.start();
            }, 5000);
        }

        try {
            console.trace(`\n\ncalling apiGetNewSyncJobToRun`);
            const res = await apiGetNewSyncJobToRun();
            this.currentJob = res.data;
        } catch (e) {
            console.error(e);
            console.trace("\n\nerror encountered");
            return setTimeout(() => {
                this.start();
            }, 5000);
        }

        if (this.currentJob === null) {
            console.trace(`\n\nno new task available.`);
            return setTimeout(() => {
                this.start();
            }, 5000);
        }

        let {
            _id,
            sync_task_id,
            action,
            source_project_id,
            source_credentials,
            source_platform,
            source_endpoint,
            source_container,
            source_connection_string,
            source_region,
            source_bucket,
            source_obj_key,
            source_key_id,
            source_key_secret,
            destination_region,
            destination_bucket,
            destination_key,
            destination_key_id,
            destination_key_secret,
            size,
            status,
            bytes_migrated,
        } = this.currentJob;

        console.log({
            _id,
            sync_task_id,
            action,
            source_project_id,
            source_credentials,
            source_platform,
            source_endpoint,
            source_container,
            source_connection_string,
            source_region,
            source_bucket,
            source_obj_key,
            source_key_id,
            source_key_secret,
            destination_region,
            destination_bucket,
            destination_key,
            destination_key_id,
            destination_key_secret,
            size,
            status,
            bytes_migrated,
        });

        if (this.stopping) {
            console.trace(`\n\nresetting the task to not started`);
            await aptUpdateSyncJobProgress(_id, {status: "NOT_STARTED"});
            process.exit(0);
        }

        try {
            // decryption
            console.trace(`\n\ncalling decryptWithAES`);
            source_key_id = decryptWithAES(this.passphrase, source_key_id);
            source_key_secret = decryptWithAES(this.passphrase, source_key_secret);
            source_connection_string = decryptWithAES(this.passphrase, source_connection_string);
            destination_key_id = decryptWithAES(this.passphrase, destination_key_id);
            destination_key_secret = decryptWithAES(this.passphrase, destination_key_secret);
            if (source_credentials) {
                source_credentials = JSON.parse(decryptWithAES(this.passphrase, source_credentials));
            }
        } catch (e) {
            console.error(e);
            console.trace("\n\nerror encountered");
            await apiPostSyncJobLog(_id, {
                type: "manual",
                severity: "error",
                content: `Failed to decrypt the authentication data with provided passphrase: ${this.passphrase}`,
                trace: e.stack,
            });
            await aptUpdateSyncJobProgress(_id, {status: "ERROR"});
            await aptUpdateSyncTaskProgress(_id, {status: "ERROR"});
            return setTimeout(() => {
                this.start();
            }, 100);
        }

        // execute delete action if applicable
        if (action === "delete") {
            try {
                const deleteParams = {
                    Bucket: destination_bucket, Key: source_obj_key,
                };
                await LyveProxyExecute(destination_region, destination_key_id, destination_key_secret, "deleteObject", deleteParams);
                await aptUpdateSyncJobProgress(_id, {bytes_migrated: size, status: "COMPLETED"});
            } catch (e) {
                console.error(e);
                console.trace("\n\nerror encountered");
                await apiPostSyncJobLog(_id, {
                    type: "manual",
                    severity: "error",
                    content: `Failed to delete file in lyve bucket. \n${e.message}`,
                    trace: e.stack,
                });
                await aptUpdateSyncJobProgress(_id, {status: "ERROR"});
                await aptUpdateSyncTaskProgress(_id, {status: "ERROR"});
                return setTimeout(() => {
                    this.start();
                }, 100);
            }

            return setTimeout(() => {
                this.start();
            }, 10);
        }

        let Key;
        if (destination_key === "/") {
            Key = source_obj_key;
        } else {
            // destination_key is sure to endsWith "/"
            if (source_obj_key.startsWith("/")) {
                // remove the leading "/";
                source_obj_key = source_obj_key.replace("/", "");
            }
            Key = `${destination_key}${source_obj_key}`;
        }

        if (this.stopping) {
            console.trace(`\n\nresetting the task to not started`);
            await aptUpdateSyncJobProgress(_id, {status: "NOT_STARTED"});
            process.exit(0);
        }

        // for stopping checking,
        //      single part upload: only check once before the upload
        //      multipart upload:   only checks after every partition has been uploaded.

        // --------------- SINGLE PART UPLOAD ---------------
        // for size less than 50MB, transfer directly
        if (size <= MULTI_PART_SIZE) {
            let fileToMigrate;

            try {
                switch (source_platform) {
                    case "fromGeneralS3": {
                        const getParams = {
                            Bucket: source_bucket, Key: source_obj_key,
                        };
                        fileToMigrate = await GeneralS3ProxyExecute(source_endpoint, source_key_id, source_key_secret, "getObject", getParams);
                        break;
                    }
                    case "fromAlibaba": {
                        fileToMigrate = await AlibabaProxyExecute(source_region, source_key_id, source_key_secret, "get", [source_obj_key], source_bucket);
                        fileToMigrate.Body = fileToMigrate.content;
                        break;
                    }
                    case "fromAzure": {
                        fileToMigrate = await AzureProxyExecute(source_connection_string, "download", undefined, source_container, source_obj_key);
                        break;
                    }
                    case "fromGoogle": {
                        fileToMigrate = await GoogleProxyExecute(source_credentials, "download", undefined, source_project_id, source_bucket, source_obj_key);
                        fileToMigrate = {Body: fileToMigrate};
                        break;
                    }
                    default: {
                        throw new Error(`Unknown source platform: ${source_platform}`);
                    }
                }
            } catch (e) {
                console.error(e);
                console.trace("\n\nerror encountered");
                await apiPostSyncJobLog(_id, {
                    type: "manual",
                    severity: "error",
                    content: `Failed to download file from the source using authentication decrypted with provided passphrase: ${this.passphrase}. \n${e.message}`,
                    trace: e.stack,
                });
                await aptUpdateSyncJobProgress(_id, {status: "ERROR"});
                await aptUpdateSyncTaskProgress(_id, {status: "ERROR"});
                return setTimeout(() => {
                    this.start();
                }, 100);
            }

            if (this.stopping) {
                console.trace(`\n\nresetting the task to not started`);
                await aptUpdateSyncJobProgress(_id, {status: "NOT_STARTED"});
                process.exit(0);
            }

            try {
                const putParams = {
                    Body: fileToMigrate.Body, Bucket: destination_bucket, Key,
                };
                await LyveProxyExecute(destination_region, destination_key_id, destination_key_secret, "putObject", putParams);
                await aptUpdateSyncJobProgress(_id, {bytes_migrated: size, status: "COMPLETED"});
            } catch (e) {
                console.error(e);
                console.trace("\n\nerror encountered");
                await apiPostSyncJobLog(_id, {
                    type: "manual",
                    severity: "error",
                    content: `Failed to upload file to destination using authentication decrypted with provided passphrase: ${this.passphrase}. \n${e.message}`,
                    trace: e.stack,
                });
                await aptUpdateSyncJobProgress(_id, {status: "ERROR"});
                await aptUpdateSyncTaskProgress(_id, {status: "ERROR"});
                return setTimeout(() => {
                    this.start();
                }, 10);
            }

            return setTimeout(() => {
                this.start();
            }, 10);
        }

        // --------------- MULTI PART UPLOAD ---------------
        // for size larger than 50MB, use multipart upload
        // check if the task has multi_part_upload_id: String.

        if (!this.currentJob.multi_part_upload_id) {
            try {
                const multiPartParams = {
                    Bucket: destination_bucket, Key,
                };
                const {UploadId} = await LyveProxyExecute(destination_region, destination_key_id, destination_key_secret, "createMultipartUpload", multiPartParams);
                this.currentJob.multi_part_upload_id = UploadId;
                // update status check for pending-termination
                status = (await aptUpdateSyncJobProgress(_id, {multi_part_upload_id: UploadId})).data.status;
                console.log(`multipart upload iD: ${UploadId}`);
            } catch (e) {
                console.error(e);
                console.trace("\n\nerror encountered");
                await apiPostSyncJobLog(_id, {
                    type: "manual",
                    severity: "error",
                    content: `Failed to create multi-part upload.\n${e.message}`,
                    trace: e.stack,
                });
                await aptUpdateSyncJobProgress(_id, {status: "ERROR"});
                await aptUpdateSyncTaskProgress(_id, {status: "ERROR"});
                return setTimeout(() => {
                    this.start();
                }, 10);
            }
        }

        // now current task has the multi_part_upload_id defined.
        // start uploading partitions
        const partitions = this.currentJob.partitions;
        for (let partitionIndex = 0; partitionIndex < partitions.length; partitionIndex++) {
            const partition = partitions[partitionIndex];
            const {start, end, PartNumber} = partition;
            if (partition.ETag) {
                // partition has been uploaded.
                continue;
            }

            // upload current partition
            let partToUpload;

            try {
                switch (source_platform) {
                    case "fromGeneralS3": {
                        const getParams = {
                            Bucket: source_bucket, Key: source_obj_key, Range: `bytes=${start}-${end}`
                        };
                        partToUpload = await GeneralS3ProxyExecute(source_endpoint, source_key_id, source_key_secret, "getObject", getParams);
                        break;
                    }
                    case "fromAlibaba": {
                        partToUpload = await AlibabaProxyExecute(source_region, source_key_id, source_key_secret, "get", [source_obj_key, {headers: {Range: `bytes=${start}-${end}`}}], source_bucket);
                        partToUpload.Body = partToUpload.content;
                        break;
                    }
                    case "fromAzure": {
                        partToUpload = await AzureProxyExecute(source_connection_string, "download", [start, end - start + 1], source_container, source_obj_key);
                        break;
                    }
                    case "fromGoogle": {
                        partToUpload = await GoogleProxyExecute(source_credentials, "createReadStream", [{
                            start,
                            end
                        }], source_project_id, source_bucket, source_obj_key);
                        break;
                    }
                    default: {
                        throw new Error(`Unknown source platform: ${source_platform}`);
                    }
                }
            } catch (e) {
                console.error(e);
                console.trace("\n\nerror encountered");
                await apiPostSyncJobLog(_id, {
                    type: "manual",
                    severity: "error",
                    content: `Failed to download part ${PartNumber} from the source.\n${e.message}`,
                    trace: e.stack,
                });
                await aptUpdateSyncJobProgress(_id, {status: "ERROR"});
                await aptUpdateSyncTaskProgress(_id, {status: "ERROR"});
                return setTimeout(() => {
                    this.start();
                }, 10);
            }

            if (this.stopping) {
                console.trace(`\n\nresetting the task to not started`);
                await aptUpdateSyncJobProgress(_id, {status: "NOT_STARTED"});
                process.exit(0);
            }

            const uploadParam = {
                Body: partToUpload.Body,
                Bucket: destination_bucket,
                Key,
                PartNumber,
                UploadId: this.currentJob.multi_part_upload_id,
            };

            try {
                const {ETag} = await LyveProxyExecute(destination_region, destination_key_id, destination_key_secret, "uploadPart", uploadParam);
                partition.ETag = ETag;
                await apiUpdateSyncJobPartitionProgress(_id, partitionIndex, {ETag});
                bytes_migrated = end;
                status = (await aptUpdateSyncJobProgress(_id, {bytes_migrated})).data.status;
            } catch (e) {
                console.error(e);
                console.trace("\n\nerror encountered");
                await apiPostSyncJobLog(_id, {
                    type: "manual",
                    severity: "error",
                    content: `Failed to upload part ${PartNumber} to the destination.\n${e.message}`,
                    trace: e.stack,
                });
                await aptUpdateSyncJobProgress(_id, {status: "ERROR"});
                await aptUpdateSyncTaskProgress(_id, {status: "ERROR"});
                return setTimeout(() => {
                    this.start();
                }, 10);
            }

            if (status === "PENDING-TERMINATION") {
                // terminate the current task
                try {
                    const params = {
                        Bucket: destination_bucket, Key, UploadId: this.currentJob.multi_part_upload_id,
                    };
                    await LyveProxyExecute(destination_region, destination_key_id, destination_key_secret, "abortMultipartUpload", params);
                    await aptUpdateSyncJobProgress(_id, {status: "TERMINATED"});
                } catch (e) {
                    console.error(e);
                    console.trace("\n\nerror encountered");
                    await apiPostSyncJobLog(_id, {
                        type: "manual",
                        severity: "error",
                        content: `Failed to abort multi-part upload.\n${e.message}`,
                        trace: e.stack,
                    });
                    await aptUpdateSyncJobProgress(_id, {status: "ERROR"});
                    await aptUpdateSyncTaskProgress(_id, {status: "ERROR"});
                }
                return setTimeout(() => {
                    this.start();
                }, 10);
            }

            if (this.stopping) {
                console.trace(`\n\nresetting the task to not started`);
                await aptUpdateSyncJobProgress(_id, {status: "NOT_STARTED"});
                process.exit(0);
            }
        }

        // finish the multipart upload
        const finalParam = {
            Bucket: destination_bucket, Key, MultipartUpload: {
                Parts: partitions.map(partition => ({
                    ETag: partition.ETag, PartNumber: partition.PartNumber
                }))
            }, UploadId: this.currentJob.multi_part_upload_id,
        };

        try {
            await LyveProxyExecute(destination_region, destination_key_id, destination_key_secret, "completeMultipartUpload", finalParam);
            await aptUpdateSyncJobProgress(_id, {bytes_migrated: size, status: "COMPLETED"});
        } catch (e) {
            console.error(e);
            console.trace("\n\nerror encountered");
            await apiPostSyncJobLog(_id, {
                type: "manual",
                severity: "error",
                content: `Failed to complete multipart upload.\n${e.message}`,
                trace: e.stack,
            });
            await aptUpdateSyncJobProgress(_id, {status: "ERROR"});
            await aptUpdateSyncTaskProgress(_id, {status: "ERROR"});
            return setTimeout(() => {
                this.start();
            }, 10);
        }

        return setTimeout(() => {
            this.start();
        }, 10);
    }

    shutdown() {
        console.log("shutdown called");
        this.stopping = true;
    }
}

module.exports = SynchronizationWorker;




