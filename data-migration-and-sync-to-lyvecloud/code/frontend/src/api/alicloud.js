import axios from "axios";
import {serverURL} from "./common";

export const apiAlibabaProxyExecute = (data) => {
    return axios.post(`${serverURL}/alibaba-cloud/proxy-execute`, data);
};

export const apiAlibabaListBucketAllObjects = async (bucket, alibabaCredentialForm) => {
    return new Promise(async (resolve, reject) => {
        let continuationToken = undefined;
        let objectList = [];
        try {
            do {
                const data = {
                    cmd: "listV2",
                    ...alibabaCredentialForm.getFieldsValue(),
                    bucket,
                    params: [
                        {
                            "continuation-token": continuationToken
                        }
                    ]
                };
                const res = await apiAlibabaProxyExecute(data);
                continuationToken = res.data.nextContinuationToken;
                objectList = objectList.concat(res.data.objects);
            } while (continuationToken);
            resolve(objectList);
        } catch (e) {
            reject(e);
        }
    });
};
