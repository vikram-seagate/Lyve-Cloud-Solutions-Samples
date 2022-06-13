import axios from "axios";
import {serverURL} from "./common";

export const apiGeneralS3ProxyExecute = (data) => {
    return axios.post(`${serverURL}/general-s3/proxy-execute`, data);
};

export const apiGeneralListS3AllObjects = async (Bucket, credentials) => {
    return new Promise(async (resolve, reject) => {
        let token = undefined;
        let objectList = [];
        try {
            do {
                const res = await apiGeneralS3ProxyExecute({
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

export const apiGeneralS3StartMigration = () => {
    return axios.post(`${serverURL}/general-s3/migration-tasks/start`);
};