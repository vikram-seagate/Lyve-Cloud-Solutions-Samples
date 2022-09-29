const AWS = require("aws-sdk");

function LyveProxyExecute(region, accessKeyId, accessKeySecret, cmd, params) {
    const s3 = new AWS.S3({
        endpoint: `https://s3.${region}.lyvecloud.seagate.com`,
        apiVersion: "2006-03-01",
        region: region,
        accessKeyId: accessKeyId,
        secretAccessKey: accessKeySecret
    });

    return new Promise(((resolve, reject) => {
        if (params) {
            s3[cmd](params, (err, data) => {
                if (err) {
                    reject(err);
                } else {
                    resolve(data);
                }
            });
        } else {
            s3[cmd]((err, data) => {
                if (err) {
                    reject(err);
                } else {
                    resolve(data);
                }
            });
        }
    }));
}

module.exports = {
    LyveProxyExecute
};