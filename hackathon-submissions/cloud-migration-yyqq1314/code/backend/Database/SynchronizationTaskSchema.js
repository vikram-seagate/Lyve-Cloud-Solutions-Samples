const mongoose = require("mongoose");

const LogSchema = require("./LogSchema");

const SynchronizationTaskSchema = new mongoose.Schema({
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

    // source login key id
    source_key_id: String,

    // source login key secret
    source_key_secret: String,

    // status: "ACTIVE", "DISABLED", "ERROR"
    status: String,

    // destination bucket name
    destination_bucket: String,

    // destination region of lyve cloud
    destination_region: String,

    // destination login key id
    destination_key_id: String,

    // destination login key secret
    destination_key_secret: String,

    // Modified Before (If set, only synchronize files modified before the time)
    sync_before: String,

    // Modified After (If set, only synchronize files modified after the time)
    sync_after: String,

    // Enable Upload (If checked, the tool is allowed to upload new files to Lyve Cloud Bucket)
    enable_upload: Boolean,

    // Enable Delete (If checked, the tool is allowed to delete files that are not existing in the source bucket)
    enable_delete: Boolean,

    // Enable Update (If checked, the tool is allowed to override Lyve bucket files based on the updated file from the source bucket)
    enable_update: Boolean,

    // synchronization frequency
    frequency: {
        unit: String, value: Number
    },

    // latest synchronization datetime
    last_sync_time: String,

    // next scheduled sync time
    scheduled_sync_time: String,

    // synchronization logs
    logs: [LogSchema]
}, {timestamps: {createdAt: "created_at", updatedAt: "updated_at"}});

module.exports = SynchronizationTaskSchema;