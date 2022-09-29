const express = require("express");
const router = express.Router();

// task's source_platform and progress should be set correctly
router.post("/", async (req, res) => {
    try {
        const result = req.mongoDAO.createMigrationTasks(req.body);
        if (result) {
            res.json(req.body);
        } else {
            res.status(400).send({message: "Something went wrong"});
        }
    } catch (e) {
        console.log(e.toString());
        res.status(400).send({message: e.toString()});
    }
});

// source_platform needs to be set in query_params
router.get("/", async (req, res) => {
    try {
        const result = await req.mongoDAO.getMigrationTasksByPlatform(req.query.source_platform);
        res.json(result);
    } catch (e) {
        console.log(e.toString());
        res.status(400).send({message: e.toString()});
    }
});

router.put("/:id", async (req, res) => {
    try {
        const result = await req.mongoDAO.updateMigrationTaskProgress(req.params.id, req.body);
        res.json(result);
    } catch (e) {
        console.log(e.toString());
        res.status(400).send({message: e.toString()});
    }
});

router.delete("/:id", async (req, res) => {
    try {
        const result = await req.mongoDAO.deleteMigrationTask(req.params.id);
        res.json(result);
    } catch (e) {
        console.log(e.toString());
        res.status(400).send({message: e.toString()});
    }
});

router.post("/:id/logs", async (req, res) => {
    try {
        const result = await req.mongoDAO.addMigrationTaskLog(req.params.id, req.body);
        res.json(result);
    } catch (e) {
        console.log(e.toString());
        res.status(400).send({message: e.toString()});
    }
});

router.post("/:id/rerun", async (req, res) => {
    try {
        const result = await req.mongoDAO.rerunMigrationTask(req.params.id);
        res.json(result);
    } catch (e) {
        console.log(e.toString());
        res.status(400).send({message: e.toString()});
    }
});

// return axios.put(`http://${process.env.BACKEND_IP}:10086/migration-tasks/${id}/partitions/${partitionIndex}`, data);
router.put("/:id/partitions/:partitionIndex", async (req, res) => {
    try {
        const result = await req.mongoDAO.updateMigrationTaskPartition(req.params.id, req.params.partitionIndex, req.body);
        res.json(result);
    } catch (e) {
        console.log(e.toString());
        res.status(400).send({message: e.toString()});
    }
});

module.exports = router;