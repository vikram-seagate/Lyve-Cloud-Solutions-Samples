const mongoose = require("mongoose");

const LogSchema = new mongoose.Schema({
    type: String,   // auto, manual
    severity: String, // info, warning, error
    content: String, // main body of the log
    trace: String, // debug code trace of the exception
}, {timestamps: {createdAt: "created_at", updatedAt: "updated_at"}});

module.exports = LogSchema;