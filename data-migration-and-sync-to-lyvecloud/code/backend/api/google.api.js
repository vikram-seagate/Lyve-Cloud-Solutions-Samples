const {Storage} = require("@google-cloud/storage");

function GoogleProxyExecute(credentials, cmd, params, projectId, bucket, file) {
    let client = new Storage({
        projectId, credentials
    });

    // change to bucket client
    if (bucket) {
        client = client.bucket(bucket);
        if (file) {
            client = client.file(file);
        }
    }

    if (cmd === "createReadStream") {
        return new Promise((resolve, reject) => {
            const data = [];
            const readStream = params ? client.createReadStream(...params) : client.createReadStream();

            readStream
                .on("data", (chunk) => {
                    data.push(chunk);
                })
                .on("end", () => {
                    resolve({Body: Buffer.concat(data)});
                })
                .on("error", (e) => {
                    reject(e);
                });
        });
    }

    return new Promise(((resolve, reject) => {
        if (params) {
            client[cmd](...params, (err, data) => {
                if (err) {
                    reject(err);
                } else {
                    resolve(data);
                }
            });
        } else {
            client[cmd]((err, data) => {
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
    GoogleProxyExecute
};