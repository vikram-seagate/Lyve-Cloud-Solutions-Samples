const express = require("express");
const router = express.Router();

// source_platform needs to be set in query_params
router.get("/", async (req, res) => {
    try {
        const result = await req.mongoDAO.getSynchronizationJobsByPlatform(req.query.source_platform);
        res.json(result);
    } catch (e) {
        console.log(e.toString());
        res.status(400).send({message: e.toString()});
    }
});

router.put("/:id", async (req, res) => {
    try {
        const result = await req.mongoDAO.updateSynchronizationJobProgress(req.params.id, req.body);
        res.json(result);
    } catch (e) {
        console.log(e.toString());
        res.status(400).send({message: e.toString()});
    }
});

router.post("/:id/logs", async (req, res) => {
    try {
        const result = await req.mongoDAO.addSynchronizationJobLog(req.params.id, req.body);
        res.json(result);
    } catch (e) {
        console.log(e.toString());
        res.status(400).send({message: e.toString()});
    }
});

// return axios.put(`http://${process.env.BACKEND_IP}:10086/migration-tasks/${id}/partitions/${partitionIndex}`, data);
router.put("/:id/partitions/:partitionIndex", async (req, res) => {
    try {
        const result = await req.mongoDAO.updateSynchronizationJobPartition(req.params.id, req.params.partitionIndex, req.body);
        res.json(result);
    } catch (e) {
        console.log(e.toString());
        res.status(400).send({message: e.toString()});
    }
});

module.exports = router;