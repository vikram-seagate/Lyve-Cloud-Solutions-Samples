const mongoose = require("mongoose");
const {MigrationTaskSchema} = require("./MigrationTaskSchema");
const {Mutex} = require("async-mutex");
const SynchronizationTaskSchema = require("./SynchronizationTaskSchema");
const SynchronizationJobSchema = require("./SynchronizationJobSchema");

const MongoDBURL = `mongodb://${process.env.DATABASE_IP}:27017`;

class MongoDAO {
    constructor() {
        this.migrationTaskModel = null;
        this.synchronizationTaskModel = null;
        this.synchronizationJobModel = null;
        this.migrationMutex = new Mutex();
        this.synchronizationMutex = new Mutex();

        this.setupCallbacks = [];
    }

    async connect() {
        return mongoose.connect(MongoDBURL)
            .then(() => {
                this.migrationTaskModel = mongoose.model("MigrationTask", MigrationTaskSchema);
                this.synchronizationTaskModel = mongoose.model("SynchronizationTask", SynchronizationTaskSchema);
                this.synchronizationJobModel = mongoose.model("SynchronizationJob", SynchronizationJobSchema);
                this.setupCallbacks.forEach(func => func());
            });
    }

    async createMigrationTasks(taskList) {
        return this.migrationTaskModel.create(taskList);
    }

    async createSynchronizationTask(task) {
        const {source_platform, source_endpoint, source_bucket, destination_region, destination_bucket, status} = task;
        const existingTask = await this.synchronizationTaskModel.findOne({
            source_platform, source_endpoint, source_bucket, destination_region, destination_bucket, status
        }).exec();

        if (existingTask !== null) {
            console.log(existingTask);
            throw new Error("There is already an active task of the same configuration.");
        }

        return this.synchronizationTaskModel.create(task);
    }

    async createSynchronizationJobsNoDuplication(jobs) {
        const jobsWithoutDuplication = [];

        for (const job of jobs) {
            const {source_endpoint, source_bucket, destination_region, destination_bucket, source_platform} = job;
            const existingJobs = await this.synchronizationJobModel.find({
                source_endpoint, source_bucket, destination_region, destination_bucket, source_platform
            }).exec();

            // do not create new jobs for those of status NOT_STARTED, IN_PROGRESS, PENDING_TERMINATION, TERMINATED, and ERROR.
            if (existingJobs.some(job => job.status !== "COMPLETED")) {
                continue;
            }
            jobsWithoutDuplication.push(job);
        }

        return this.synchronizationJobModel.create(jobsWithoutDuplication);
    }

    getMigrationTasksByPlatform(source_platform) {
        return this.migrationTaskModel.find({source_platform}).exec();
    }

    getSynchronizationTasks() {
        return this.synchronizationTaskModel.find().exec();
    }

    getSynchronizationTasksByPlatform(source_platform) {
        return this.synchronizationTaskModel.find({source_platform}).exec();
    }

    getSynchronizationJobsByPlatform(source_platform) {
        return this.synchronizationJobModel.find({source_platform}).exec();
    }

    getMigrationTaskToRun() {
        return this.migrationMutex.runExclusive(async () => {
            const newTask = await this.migrationTaskModel.findOne({
                status: "NOT_STARTED"
            }).exec();
            if (newTask) {
                return this.updateMigrationTaskProgress(newTask._id, {status: "IN_PROGRESS"});
            }

            return newTask;
        });
    }

    getSyncJobToRun() {
        return this.synchronizationMutex.runExclusive(async () => {
            const newJob = await this.synchronizationJobModel.findOne({
                status: "NOT_STARTED"
            }).exec();
            if (newJob) {
                return this.updateSynchronizationJobProgress(newJob._id, {status: "IN_PROGRESS"});
            }
            return newJob;
        });
    }

    async updateMigrationTaskProgress(id, data) {
        console.log(`updating ${id} ${JSON.stringify(data)}`);

        const task = await this.migrationTaskModel.findById(id).exec();

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
        return task.save();
    }

    async updateSynchronizationTaskProgress(id, data) {
        console.log(`updating ${id} ${JSON.stringify(data)}`);

        const task = await this.synchronizationTaskModel.findById(id).exec();

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
        return task.save();
    }

    async updateSynchronizationJobProgress(id, data) {
        console.log(`updating ${id} ${JSON.stringify(data)}`);

        const job = await this.synchronizationJobModel.findById(id).exec();

        // create auto log
        const contentObj = {};
        for (const [key, value] of Object.entries(data)) {
            contentObj[key] = [job[key], value];
        }

        job.logs.push({
            type: "auto", severity: "info", content: JSON.stringify(contentObj), trace: null,
        });

        // update job value
        for (const [key, value] of Object.entries(data)) {
            job[key] = value;
        }
        return job.save();
    }

    async addMigrationTaskLog(id, log) {
        console.log(`updating ${id} ${JSON.stringify(log)}`);
        const task = await this.migrationTaskModel.findById(id).exec();
        task.logs.push(log);
        return task.save();
    }

    async addSynchronizationTaskLog(id, log) {
        console.log(`updating ${id} ${JSON.stringify(log)}`);
        const task = await this.synchronizationTaskModel.findById(id).exec();
        task.logs.push(log);
        return task.save();
    }

    async addSynchronizationJobLog(id, log) {
        console.log(`updating ${id} ${JSON.stringify(log)}`);
        const job = await this.synchronizationJobModel.findById(id).exec();
        job.logs.push(log);
        return job.save();
    }

    async deleteMigrationTask(id) {
        console.log(`deleting task ${id}`);
        return this.migrationTaskModel.findByIdAndDelete(id);
    }

    async rerunMigrationTask(id) {
        console.log(`rerunning ${id}`);
        const task = await this.migrationTaskModel.findById(id).exec();
        task.logs = [];
        task.multi_part_upload_id = undefined;
        task.bytes_migrated = 0;
        if (task.partitions.length > 0) {
            for (let i = 0; i < task.partitions.length; i++) {
                task.partitions[i].ETag = undefined;
            }
        }
        task.status = "NOT_STARTED";
        return task.save();
    }

    async updateMigrationTaskPartition(id, partitionIndex, partitionBody) {
        console.log(`updating ${id} partition ${partitionIndex} ${JSON.stringify(partitionBody)}`);
        const task = await this.migrationTaskModel.findById(id).exec();

        // create auto log
        const contentObj = {partition: partitionIndex};
        for (const [key, value] of Object.entries(partitionBody)) {
            contentObj[key] = [task[key], value];
        }

        task.logs.push({
            type: "auto", severity: "info", content: JSON.stringify(contentObj), trace: null,
        });

        // update task value
        for (const [key, value] of Object.entries(partitionBody)) {
            task.partitions[partitionIndex][key] = value;
        }

        return task.save();
    }

    async updateSynchronizationJobPartition(id, partitionIndex, partitionBody) {
        console.log(`updating ${id} partition ${partitionIndex} ${JSON.stringify(partitionBody)}`);
        const job = await this.synchronizationJobModel.findById(id).exec();

        // create auto log
        const contentObj = {partition: partitionIndex};
        for (const [key, value] of Object.entries(partitionBody)) {
            contentObj[key] = [job[key], value];
        }

        job.logs.push({
            type: "auto", severity: "info", content: JSON.stringify(contentObj), trace: null,
        });

        // update job value
        for (const [key, value] of Object.entries(partitionBody)) {
            job.partitions[partitionIndex][key] = value;
        }

        return job.save();
    }
}

module.exports = MongoDAO;