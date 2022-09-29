import axios from "axios";
import {serverURL} from "./common";

export const apiAWSS3ProxyExecute = (data) => {
    console.log(data);
    return axios.post(`${serverURL}/aws/proxy-execute`, data);
};

export const apiAWSListS3AllObjects = async (Bucket, credentials) => {
    return new Promise(async (resolve, reject) => {
        let token = undefined;
        let objectList = [];
        try {
            do {
                const res = await apiAWSS3ProxyExecute({
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

export const apiAWSStartMigration = () => {
    return axios.post(`${serverURL}/aws/migration-tasks/start`);
};