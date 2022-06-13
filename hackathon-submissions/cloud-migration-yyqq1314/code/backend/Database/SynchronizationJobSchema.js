const mongoose = require("mongoose");

const PartitionSchema = require("./PartitionSchema");
const LogSchema = require("./LogSchema");

// Synchronization Jobs are similar to migration jobs.
const SynchronizationJobSchema = new mongoose.Schema({
    // id of the corresponding synchronization task
    sync_task_id: String,

    // upload, update and delete
    action: String,

    // source_platform: fromAWS, fromGeneralS3, fromAzure, fromGoogle, fromAlibaba etc.
    source_platform: String,

    // used when source_platform === fromGoogle
    source_project_id: String,

    // used when source_platform === fromGoogle
    source_credentials: String,

    // used when source_platform === fromAzure
    source_connection_string: String,

    // used when source_platform === fromAzure
    source_container: String,

    // used when source_platform !== fromAWS
    source_endpoint: String,

    // used when source_platform === fromAWS
    source_region: String,

    // bucket name of the source object
    source_bucket: String,

    // source object's key
    source_obj_key: String,

    // source login key id
    source_key_id: String,

    // source login key secret
    source_key_secret: String,

    // size of the object to migrate, for folders, size == 0 byte.
    size: Number,

    // status: "NOT_STARTED", "IN_PROGRESS", "ERROR", "COMPLETED", "PENDING-TERMINATION", "TERMINATED"
    status: String,

    // bytes migrated to the server
    bytes_migrated: Number,

    // destination bucket name
    destination_bucket: String,

    // destination key, calculated by destination path + source key
    destination_key: String,

    // destination region of lyve cloud
    destination_region: String,

    // destination login key id
    destination_key_id: String,

    // destination login key secret
    destination_key_secret: String,

    // multipart upload Id
    multi_part_upload_id: String,

    // multipart upload parts
    partitions: [PartitionSchema],

    // migration logs
    logs: [LogSchema]
}, {timestamps: {createdAt: "created_at", updatedAt: "updated_at"}});


module.exports = SynchronizationJobSchema;