const express = require("express");
const {GeneralS3ProxyExecute} = require("../api/generals3.api");
const router = express.Router();

router.post("/proxy-execute", async (req, res) => {
    try {
        const result = await GeneralS3ProxyExecute(req.body.endpoint, req.body.accessKeyId, req.body.accessKeySecret, req.body.cmd, req.body.params);
        console.log(result);
        res.json(result);
    } catch (e) {
        res.status(400).send({message: e.toString()});
    }
});

module.exports = router;