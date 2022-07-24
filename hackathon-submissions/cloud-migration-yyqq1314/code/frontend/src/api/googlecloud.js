import axios from "axios";
import {serverURL} from "./common";

export const apiGoogleCloudStorageConnect = (data) => {
    return axios.post(`${serverURL}/google/connect`, data);
};

export const apiGoogleProxyExecute = (data) => {
    return axios.post(`${serverURL}/google/proxy-execute`, data);
};

export const apiGoogleCloudStorageBucketOperationProxyExecute = (data) => {
    return axios.post(`${serverURL}/google/bucket-operation-proxy-execute`, data);
};

