const moment = require("moment");
const {
    getGeneralS3AllObjectsInBucket,
    decryptWithAES,
    getLyveS3AllObjectsInBucket,
    getPassphraseFromEnv,
    MULTI_PART_SIZE,
    getAlibabaAllObjectsInBucket,
} = require("./Utils");
const {AzureProxyExecute} = require("../api/azure.api");
const {GoogleProxyExecute} = require("../api/google.api");


class SyncTaskManager {
    constructor(mongoDAO) {
        // the tasks are mongoose documents
        this.mongoDAO = mongoDAO;
        this.passphrase = null;
        this.tasks = {};
        this.timeouts = {};
    }

    // called only when the backend is first started
    async setupExistingTasks() {
        await this.mongoDAO.synchronizationJobModel.deleteMany({}).exec();

        const tasks = await this.mongoDAO.synchronizationTaskModel.find({status: "ACTIVE"});
        for (const task of tasks) {
            this.tasks[task.id] = task;
            await this.scheduleTaskNextExecution(task);
        }
    }

    async createSyncTask(taskData) {
        // check for duplicate destination bucket
        const {destination_region, destination_bucket} = taskData;

        const existingTask = await this.mongoDAO.synchronizationTaskModel.findOne({
            destination_region, destination_bucket
        }).exec();

        if (existingTask) {
            throw new Error(`There already exists a synchronization task with the same bucket on the same Lyve Region.`);
        }

        const task = await this.mongoDAO.createSynchronizationTask(taskData);
        this.tasks[task.id] = task;

        // execute the task immediately. by each end of execution, the task's scheduled sync time will be calculated
        this.timeouts[task.id] = setTimeout(async () => {
            try {
                await this.executeTask(task);
            } catch (e) {
                console.log(e);
                clearTimeout(this.timeouts[task.id]);
                delete this.timeouts[task.id];
                delete this.tasks[task.id];
            }
        }, 0);
        return task.toJSON();
    }

    async executeTask(task) {
        clearTimeout(this.timeouts[task.id]);
        delete this.timeouts[task.id];

        console.log(`executing synchronous task of id ${task.id}`);
        await this.updateSyncTaskProgress(task, {last_sync_time: new Date().toISOString()});

        this.passphrase = getPassphraseFromEnv();

        if (!this.passphrase) {
            console.log(`Passphrase not defined.`);
            task.logs.push({
                type: "manual", severity: "error", content: "Passphrase is not defined on the backend server.",
            });
            await task.save();
            return this.scheduleTaskNextExecution(task);
        }

        let {
            source_project_id,
            source_credentials,
            source_platform,
            source_endpoint,
            source_container,
            source_connection_string,
            source_region,
            source_bucket,
            source_key_id,
            source_key_secret,
            destination_region,
            destination_bucket,
            destination_key_id,
            destination_key_secret,
            status,
            sync_before,
            sync_after,
            enable_upload,
            enable_delete,
            enable_update,
        } = task;

        if (status !== "ACTIVE") {
            return;
        }

        let decrypted_source_key_id, decrypted_source_key_secret, decrypted_destination_key_id,
            decrypted_destination_key_secret, decrypted_source_connection_string, decrypted_source_credentials;

        try {
            // decryption
            console.log(`\n\ncalling decryptWithAES`);
            decrypted_source_key_id = decryptWithAES(this.passphrase, source_key_id);
            decrypted_source_key_secret = decryptWithAES(this.passphrase, source_key_secret);
            decrypted_destination_key_id = decryptWithAES(this.passphrase, destination_key_id);
            decrypted_destination_key_secret = decryptWithAES(this.passphrase, destination_key_secret);
            decrypted_source_connection_string = decryptWithAES(this.passphrase, source_connection_string);
            if (source_credentials) {
                decrypted_source_credentials = JSON.parse(decryptWithAES(this.passphrase, source_credentials));
            }
        } catch (e) {
            console.error(e);
            console.trace("\n\nerror encountered");
            task.logs.push({
                type: "manual",
                severity: "error",
                content: `Failed to decrypt the authentication data with provided passphrase: ${this.passphrase}`,
                trace: e.stack,
            });
            return this.updateSyncTaskProgress(task, {status: "ERROR"});
        }

        let sourceBucketObjectList, lyveBucketObjectList;
        try {
            // requires format:
            // object: Key, Size, LastModified
            switch (source_platform) {
                case "fromGeneralS3": {
                    sourceBucketObjectList = await getGeneralS3AllObjectsInBucket(source_bucket, source_endpoint, decrypted_source_key_id, decrypted_source_key_secret);
                    break;
                }
                case "fromAlibaba": {
                    sourceBucketObjectList = await getAlibabaAllObjectsInBucket(source_bucket, source_region, decrypted_source_key_id, decrypted_source_key_secret);
                    sourceBucketObjectList.forEach(obj => {
                        obj.key = obj.name;
                        obj.Key = obj.name;
                        obj.Size = obj.size;
                        obj.LastModified = obj.lastModified;
                    });
                    break;
                }
                case "fromAzure": {
                    sourceBucketObjectList = await AzureProxyExecute(decrypted_source_connection_string, "listBlobsFlat", undefined, source_container);
                    sourceBucketObjectList.forEach(blob => {
                        blob.key = blob.name;
                        blob.Key = blob.name;
                        blob.Size = blob.properties.contentLength;
                        blob.LastModified = blob.properties.lastModified;
                    });
                    break;
                }
                case "fromGoogle": {
                    sourceBucketObjectList = await GoogleProxyExecute(decrypted_source_credentials, "getFiles", undefined, source_project_id, source_bucket);
                    sourceBucketObjectList.forEach(obj => {
                        obj.key = obj.name;
                        obj.Key = obj.name;
                        obj.Size = +obj.metadata.size;
                        obj.LastModified = obj.metadata.updated;
                    });
                    break;
                }
                default: {
                    throw new Error(`Unknown source platform: ${source_platform}`);
                }
            }
        } catch (e) {
            console.error(e);
            console.trace("\n\nerror encountered");
            task.logs.push({
                type: "manual",
                severity: "error",
                content: `Failed to get object list from source S3 bucket: ${e.message}`,
                trace: e.stack,
            });
            return this.updateSyncTaskProgress(task, {status: "ERROR"});
        }

        try {
            lyveBucketObjectList = await getLyveS3AllObjectsInBucket(destination_bucket, destination_region, decrypted_destination_key_id, decrypted_destination_key_secret);
        } catch (e) {
            console.error(e);
            console.trace("\n\nerror encountered");
            task.logs.push({
                type: "manual",
                severity: "error",
                content: `Failed to get object list from lyve S3 bucket: ${e.message}`,
                trace: e.stack,
            });
            return this.updateSyncTaskProgress(task, {status: "ERROR"});
        }

        // filter sourceBucketObjectList first
        if (sync_before !== null && sync_before !== undefined) {
            sourceBucketObjectList = sourceBucketObjectList.filter(object => moment(object.LastModified).isBefore(moment(sync_before)));
        }

        if (sync_before !== null && sync_before !== undefined) {
            sourceBucketObjectList = sourceBucketObjectList.filter(object => moment(object.LastModified).isAfter(moment(sync_after)));
        }

        const sourceBucketObjectDict = sourceBucketObjectList.reduce((dict, obj) => {
            dict[obj.Key] = obj;
            return dict;
        }, {});
        const lyveBucketObjectDict = lyveBucketObjectList.reduce((dict, obj) => {
            dict[obj.Key] = obj;
            return dict;
        }, {});
        const totalBucketObjectSet = new Set([...sourceBucketObjectList, ...lyveBucketObjectList].map(obj => obj.Key));
        const synchronizationJobs = [];

        totalBucketObjectSet.forEach(source_obj_key => {
            // check upload
            if (enable_upload && sourceBucketObjectDict.hasOwnProperty(source_obj_key) && !lyveBucketObjectDict.hasOwnProperty(source_obj_key)) {
                const objectToMigrate = sourceBucketObjectDict[source_obj_key];

                const partitions = [];
                if (objectToMigrate.Size > MULTI_PART_SIZE) {
                    // requires multi-part upload
                    const partitionCount = Math.ceil(objectToMigrate.Size / MULTI_PART_SIZE);
                    for (let i = 0; i < partitionCount; i++) {
                        const start = i * MULTI_PART_SIZE;
                        partitions.push({
                            start,
                            end: start + Math.min(objectToMigrate.Size - start, MULTI_PART_SIZE) - 1,
                            PartNumber: i + 1,
                        });
                    }
                }

                synchronizationJobs.push({
                    sync_task_id: task.id,
                    action: "upload",
                    source_project_id,
                    source_credentials,
                    source_platform,
                    source_endpoint,
                    source_container,
                    source_connection_string,
                    source_region,
                    source_bucket,
                    source_key_id,
                    source_key_secret,
                    source_obj_key,
                    size: sourceBucketObjectDict[source_obj_key].Size,
                    status: "NOT_STARTED",
                    bytes_migrated: 0,
                    destination_bucket,
                    destination_key: "/",
                    destination_region,
                    destination_key_id,
                    destination_key_secret,
                    partitions,
                });
            }

            if (enable_update && sourceBucketObjectDict.hasOwnProperty(source_obj_key) && lyveBucketObjectDict.hasOwnProperty(source_obj_key) && moment(sourceBucketObjectDict[source_obj_key].LastModified).isAfter(moment(lyveBucketObjectDict[source_obj_key].LastModified))) {
                const objectToMigrate = sourceBucketObjectDict[source_obj_key];

                const partitions = [];
                if (objectToMigrate.Size > MULTI_PART_SIZE) {
                    // requires multi-part upload
                    const partitionCount = Math.ceil(objectToMigrate.Size / MULTI_PART_SIZE);
                    for (let i = 0; i < partitionCount; i++) {
                        const start = i * MULTI_PART_SIZE;
                        partitions.push({
                            start,
                            end: start + Math.min(objectToMigrate.Size - start, MULTI_PART_SIZE) - 1,
                            PartNumber: i + 1,
                        });
                    }
                }

                synchronizationJobs.push({
                    sync_task_id: task.id,
                    action: "update",
                    source_project_id,
                    source_credentials,
                    source_platform,
                    source_endpoint,
                    source_container,
                    source_connection_string,
                    source_region,
                    source_bucket,
                    source_key_id,
                    source_key_secret,
                    source_obj_key,
                    size: sourceBucketObjectDict[source_obj_key].Size,
                    status: "NOT_STARTED",
                    bytes_migrated: 0,
                    destination_bucket,
                    destination_key: "/",
                    destination_region,
                    destination_key_id,
                    destination_key_secret,
                    partitions,
                });
            }

            if (enable_delete && !sourceBucketObjectDict.hasOwnProperty(source_obj_key) && lyveBucketObjectDict.hasOwnProperty(source_obj_key)) {

                synchronizationJobs.push({
                    source_project_id,
                    source_credentials,
                    source_platform,
                    source_endpoint,
                    source_container,
                    source_connection_string,
                    source_region,
                    source_bucket,
                    source_key_id,
                    source_key_secret,
                    source_obj_key,
                    sync_task_id: task.id,
                    action: "delete",
                    size: lyveBucketObjectDict[source_obj_key].Size,
                    status: "NOT_STARTED",
                    destination_bucket,
                    destination_key: "/",
                    destination_region,
                    destination_key_id,
                    destination_key_secret,
                });
            }
        });

        // console.log(synchronizationJobs);
        // remove duplicate synchronization jobs

        await this.mongoDAO.createSynchronizationJobsNoDuplication(synchronizationJobs);
        return this.scheduleTaskNextExecution(task);
    }

    async scheduleTaskNextExecution(task) {
        clearTimeout(this.timeouts[task.id]);
        delete this.timeouts[task.id];

        const now = moment();
        const lastSyncTime = moment(task.last_sync_time);
        const {value, unit} = task.frequency;

        const newScheduledSyncTime = lastSyncTime.add(value, unit);

        // if the last sync time is long ago. set the next scheduled execution time to be now
        if (newScheduledSyncTime.isBefore(now)) {
            await this.updateSyncTaskProgress(task, {scheduled_sync_time: now.toISOString()});
            this.timeouts[task.id] = setTimeout(async () => {
                try {
                    await this.executeTask(task);
                } catch (e) {
                    console.log(e);
                    clearTimeout(this.timeouts[task.id]);
                    delete this.timeouts[task.id];
                    delete this.tasks[task.id];
                }
            }, 0);
            return;
        }

        // else schedule according to the time diff
        await this.updateSyncTaskProgress(task, {scheduled_sync_time: newScheduledSyncTime.toISOString()});
        console.log(`newScheduledSyncTime.Diff(now) => ${newScheduledSyncTime.diff(now)}`);
        this.timeouts[task.id] = setTimeout(async () => {
            try {
                await this.executeTask(task);
            } catch (e) {
                console.log(e);
                clearTimeout(this.timeouts[task.id]);
                delete this.timeouts[task.id];
                delete this.tasks[task.id];
            }
        }, newScheduledSyncTime.diff(now));
    }

    async updateSyncTaskProgress(task, data) {
        console.log(`updating async ${task.id} ${JSON.stringify(data)}`);

        // create auto log
        const contentObj = {};
        for (const [key, value] of Object.entries(data)) {
            contentObj[key] = [task[key], value];
        }

        task.logs.push({
            type: "auto", severity: "info", content: JSON.stringify(contentObj), trace: null,
        });

        // update task value
        for (const [key, value] of Object.entries(data)) {
            task[key] = value;
        }

        // check for error status
        if (data.status && data.status === "ERROR") {
            task.scheduled_sync_time = undefined;
            clearTimeout(this.timeouts[task.id]);
            delete this.timeouts[task.id];
            delete this.tasks[task.id];
        }

        return task.save();
    }

    async pauseSyncTask(id) {
        console.log(`pausing sync task ${id}`);
        const task = await this.mongoDAO.synchronizationTaskModel.findById(id).exec();
        await this.updateSyncTaskProgress(task, {status: "PAUSED", scheduled_sync_time: undefined});
        clearTimeout(this.timeouts[task.id]);
        delete this.timeouts[task.id];
        delete this.tasks[task.id];
        return task.save();
    }

    async enableSyncTask(id) {
        console.log(`enabling sync task ${id}`);
        const task = await this.mongoDAO.synchronizationTaskModel.findById(id).exec();
        await this.updateSyncTaskProgress(task, {status: "ACTIVE", scheduled_sync_time: undefined, logs: []});
        this.tasks[task.id] = task;
        await this.scheduleTaskNextExecution(task);
        return task;
    }

    async deleteSyncTask(id) {
        console.log(`deleting task ${id}`);
        // check if all the sync jobs have completed or not
        const task = await this.mongoDAO.synchronizationTaskModel.findById(id).exec();
        const jobs = await this.mongoDAO.synchronizationJobModel.find({sync_task_id: task.id}).exec();

        if (jobs.some(job => job.status === "IN_PROGRESS" || job.status === "NOT_STARTED")) {
            throw new Error("Current task has unfinished synchronization jobs. cannot be deleted.");
        }
        // delete confirm
        clearTimeout(this.timeouts[task.id]);
        delete this.timeouts[task.id];
        delete this.tasks[task.id];
        await task.delete();

        // delete jobs as well
        for (const job of jobs) {
            await job.delete();
        }
        return null;
    }
}

module.exports = SyncTaskManager;