const express = require("express");
const router = express.Router();

router.get("/new-migration-task-to-run", async (req, res) => {
    try {
        const result = await req.mongoDAO.getMigrationTaskToRun();
        res.json(result);
    } catch (e) {
        console.log(e.toString());
        res.status(400).send({message: e.toString()});
    }
});

router.get("/new-sync-job-to-run", async (req, res) => {
    try {
        const result = await req.mongoDAO.getSyncJobToRun();
        res.json(result);
    } catch (e) {
        console.log(e.toString());
        res.status(400).send({message: e.toString()});
    }
});

module.exports = router;