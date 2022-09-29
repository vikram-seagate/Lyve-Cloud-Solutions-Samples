const mongoose = require("mongoose");

const PartitionSchema = new mongoose.Schema({
    start: Number, end: Number, PartNumber: Number, ETag: String,
}, {timestamps: {createdAt: "created_at", updatedAt: "updated_at"}});

module.exports = PartitionSchema;