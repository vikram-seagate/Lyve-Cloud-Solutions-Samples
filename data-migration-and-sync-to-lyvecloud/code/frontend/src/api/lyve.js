import axios from "axios";
import {serverURL} from "./common";

export const apiLyveS3ProxyExecute = (data) => {
    return axios.post(`${serverURL}/lyve/proxy-execute`, data);
};

export const apiLyveListS3AllObjects = async (Bucket, credentials) => {
    return new Promise(async (resolve, reject) => {
        let token = undefined;
        let objectList = [];
        try {
            do {
                const res = await apiLyveS3ProxyExecute({
                    cmd: "listObjectsV2",
                    params: {
                        Bucket,
                        ContinuationToken: token
                    },
                    ...credentials,
                });
                token = res.data.NextContinuationToken;
                objectList = objectList.concat(res.data.Contents);
            } while (token !== undefined);
            resolve(objectList);
        } catch (e) {
            reject(e);
        }
    });
};