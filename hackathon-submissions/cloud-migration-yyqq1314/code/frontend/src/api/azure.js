import axios from "axios";
import {serverURL} from "./common";

export const apiAzureProxyExecute = (data) => {
    return axios.post(`${serverURL}/azure/proxy-execute`, data);
};
