const express = require("express");
const {AzureProxyExecute} = require("../api/azure.api");
const router = express.Router();

router.post("/proxy-execute", async (req, res) => {
    try {
        const result = await AzureProxyExecute(req.body.connection_string, req.body.cmd, req.body.params, req.body.container);
        console.log(result);
        res.json(result);
    } catch (e) {
        res.status(400).send({message: e.toString()});
    }
});


module.exports = router;