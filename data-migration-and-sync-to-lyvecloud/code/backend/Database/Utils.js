const CryptoJS = require("crypto-js");

const {AlibabaProxyExecute} = require("../api/alibaba.api");
const {LyveProxyExecute} = require("../api/lyve.api");
const {GeneralS3ProxyExecute} = require("../api/generals3.api");

function encryptWithAES(passphrase, text) {
    return CryptoJS.AES.encrypt(text, passphrase).toString();
}

function decryptWithAES(passphrase, ciphertext) {
    if (ciphertext) {
        const bytes = CryptoJS.AES.decrypt(ciphertext, passphrase);
        return bytes.toString(CryptoJS.enc.Utf8);
    } else {
        return null;
    }
}

function getPassphraseFromEnv() {
    return process.env.PASSPHRASE;
}

async function getGeneralS3AllObjectsInBucket(Bucket, endpoint, accessKeyId, accessKeySecret) {
    return new Promise(async (resolve, reject) => {
        let token = undefined;
        let objectList = [];
        try {
            do {
                const params = {
                    Bucket,
                    ContinuationToken: token
                };
                const data = await GeneralS3ProxyExecute(
                    endpoint,
                    accessKeyId,
                    accessKeySecret,
                    "listObjectsV2",
                    params
                );
                token = data.NextContinuationToken;
                objectList = objectList.concat(data.Contents);
            } while (token !== undefined);
            resolve(objectList);
        } catch (e) {
            reject(e);
        }
    });
}

async function getAlibabaAllObjectsInBucket(bucket, region, accessKeyId, accessKeySecret) {
    return new Promise(async (resolve, reject) => {
        let continuationToken = undefined;
        let objectList = [];
        try {
            do {
                const params = [
                    {
                        "continuation-token": continuationToken
                    }
                ];
                const res = await AlibabaProxyExecute(region, accessKeyId, accessKeySecret, "listV2", params, bucket);
                continuationToken = res.nextContinuationToken;
                objectList = objectList.concat(res.objects);
            } while (continuationToken);
            resolve(objectList);
        } catch (e) {
            reject(e);
        }
    });
}

async function getLyveS3AllObjectsInBucket(Bucket, region, accessKeyId, accessKeySecret) {
    return new Promise(async (resolve, reject) => {
        let token = undefined;
        let objectList = [];
        try {
            do {
                const data = await LyveProxyExecute(
                    region,
                    accessKeyId,
                    accessKeySecret,
                    "listObjectsV2",
                    {
                        Bucket,
                        ContinuationToken: token
                    });
                token = data.NextContinuationToken;
                objectList = objectList.concat(data.Contents);
            } while (token !== undefined);
            resolve(objectList);
        } catch (e) {
            reject(e);
        }
    });
}

const MULTI_PART_SIZE = 5 * 1e7;

module.exports = {
    encryptWithAES,
    decryptWithAES,
    getPassphraseFromEnv,
    getGeneralS3AllObjectsInBucket,
    getLyveS3AllObjectsInBucket,
    getAlibabaAllObjectsInBucket,
    MULTI_PART_SIZE
};

