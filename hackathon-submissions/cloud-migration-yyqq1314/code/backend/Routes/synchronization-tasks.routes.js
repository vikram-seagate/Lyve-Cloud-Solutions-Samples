const express = require("express");
const router = express.Router();

router.post("/", async (req, res) => {
    try {
        const newTask = await req.syncTaskManager.createSyncTask(req.body);
        if (newTask) {
            res.json(newTask);
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
        const result = await req.mongoDAO.getSynchronizationTasksByPlatform(req.query.source_platform);
        res.json(result);
    } catch (e) {
        console.log(e.toString());
        res.status(400).send({message: e.toString()});
    }
});

router.put("/:id", async (req, res) => {
    try {
        const result = await req.mongoDAO.updateSynchronizationTaskProgress(req.params.id, req.body);
        res.json(result);
    } catch (e) {
        console.log(e.toString());
        res.status(400).send({message: e.toString()});
    }
});

router.delete("/:id", async (req, res) => {
    try {
        const result = await req.syncTaskManager.deleteSyncTask(req.params.id);
        res.json(result);
    } catch (e) {
        console.log(e.toString());
        res.status(400).send({message: e.toString()});
    }
});

router.post("/:id/logs", async (req, res) => {
    try {
        const result = await req.mongoDAO.addSynchronizationTaskLog(req.params.id, req.body);
        res.json(result);
    } catch (e) {
        console.log(e.toString());
        res.status(400).send({message: e.toString()});
    }
});

router.post("/:id/enable", async (req, res) => {
    try {
        const result = await req.syncTaskManager.enableSyncTask(req.params.id);
        res.json(result);
    } catch (e) {
        console.log(e.toString());
        res.status(400).send({message: e.toString()});
    }
});

router.post("/:id/pause", async (req, res) => {
    try {
        const result = await req.syncTaskManager.pauseSyncTask(req.params.id);
        res.json(result);
    } catch (e) {
        console.log(e.toString());
        res.status(400).send({message: e.toString()});
    }
});

module.exports = router;