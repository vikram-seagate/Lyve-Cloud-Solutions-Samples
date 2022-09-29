const express = require("express");
const {AlibabaProxyExecute} = require("../api/alibaba.api");
const router = express.Router();

router.post("/proxy-execute", async (req, res) => {
    try {
        const result = await AlibabaProxyExecute(req.body.region, req.body.accessKeyId, req.body.accessKeySecret, req.body.cmd, req.body.params, req.body.bucket);
        console.log(result);
        res.json(result);
    } catch (e) {
        res.status(400).send({message: e.toString()});
    }
});

module.exports = router;