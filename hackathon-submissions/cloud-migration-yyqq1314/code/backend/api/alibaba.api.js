const OSS = require("ali-oss");

function AlibabaProxyExecute(region, accessKeyId, accessKeySecret, cmd, params, bucket) {
    let client;
    if (bucket) {
        client = new OSS({
            region,
            accessKeyId,
            accessKeySecret,
            bucket
        });
    } else {
        client = new OSS({
            region,
            accessKeyId,
            accessKeySecret,
        });
    }

    return new Promise(async (resolve, reject) => {
        try {
            let result;
            if (params) {
                result = client[cmd](...params);
            } else {
                result = client[cmd]();
            }
            resolve(result);
        } catch (e) {
            reject(e);
        }
    });
}

module.exports = {
    AlibabaProxyExecute
};