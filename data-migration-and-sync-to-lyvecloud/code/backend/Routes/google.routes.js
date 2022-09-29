const express = require("express");
const {GoogleProxyExecute} = require("../api/google.api");
const router = express.Router();

router.post("/proxy-execute", async (req, res) => {
    try {
        const result = await GoogleProxyExecute(req.body.credentials, req.body.cmd, req.body.params, req.body.projectId, req.body.bucket, req.body.file,);
        console.log(result);
        res.json(result);
    } catch (e) {
        res.status(400).send(`cmd: ${req.body.cmd} failed with params: ${JSON.stringify(req.body.params)}`);
    }
});

module.exports = router;