import BucketTable from "../../../common/BucketTable";
import {Empty, Form, notification} from "antd";
import React, {useState} from "react";
import {apiCreateSynchronizationTask} from "../../../api/common";
import {encryptWithAES} from "../../../common/Encryption";
import PassphraseFormModal from "../../Migration/GeneralS3Migration/PassphraseFormModal";
import SyncConfigForm from "../../../common/SyncConfigForm";
import SyncDestinationSelection from "../../../common/SyncDestinationSelection";
import {apiAzureProxyExecute} from "../../../api/azure";
import AzureCredentialForm from "../../Migration/AzureMigration/AzureCredentialForm";

function AzureBucketSynchronizationForm() {
    const [azureCredentialForm] = Form.useForm();
    const [lyveCredentialForm] = Form.useForm();
    const [syncConfigForm] = Form.useForm();
    const [sourceContainers, setSourceContainers] = useState([]);
    const [currentSourceContainer, setCurrentSourceContainer] = useState(null);
    const [lyveBuckets, setLyveBuckets] = useState([]);
    const [currentLyveBucket, setCurrentLyveBucket] = useState(null);

    const onAzureSignIn = () => {
        apiAzureProxyExecute({
            cmd: "listContainers", ...azureCredentialForm.getFieldsValue(),
        }).then(res => {
            console.log(res);
            res.data.forEach(container => {
                container.key = container.name;
            });
            setSourceContainers(res.data);
        }).catch(e => {
            if (e?.response?.data?.message) {
                notification["error"]({
                    message: e.response.data.message, description: "",
                });
            }
        });
    };

    const onSubmit = (passphrase) => {
        const configs = syncConfigForm.getFieldsValue();
        console.log(configs, passphrase);

        const sourceFormData = azureCredentialForm.getFieldsValue();
        const lyveFormData = lyveCredentialForm.getFieldsValue();

        const task = {
            ...configs,
            source_platform: "fromAzure",
            source_connection_string: encryptWithAES(passphrase, sourceFormData.connection_string),
            source_container: currentSourceContainer.name,
            status: "ACTIVE",
            destination_region: lyveFormData.region,
            destination_bucket: currentLyveBucket.name,
            destination_key_id: encryptWithAES(passphrase, lyveFormData.accessKeyId),
            destination_key_secret: encryptWithAES(passphrase, lyveFormData.accessKeySecret),
        };

        apiCreateSynchronizationTask(task).then(res => {
            console.log(res);
            setCurrentLyveBucket(null);
            setCurrentSourceContainer(null);
            notification["success"]({
                message: "synchronization task created.", description: "", placement: "bottomRight"
            });
        }).catch(e => {
            if (e?.response?.data?.message) {
                notification["error"]({
                    message: e.response.data.message, description: "",
                });
            }
        });
    };

    return <div>
        <h1>Source Bucket Selection</h1>
        <div>
            <div style={{display: "flex", justifyContent: "space-between"}}>
                <div style={{width: "48%"}}>
                    <h1>Credentials</h1>
                    <div>
                        <AzureCredentialForm form={azureCredentialForm} onSubmit={onAzureSignIn}/>
                    </div>
                </div>
                <div style={{width: "48%"}}>
                    <h1 style={{marginBottom: "1rem"}}>Bucket Table</h1>
                    {sourceContainers.length > 0 &&
                        <BucketTable selectedBuckets={currentSourceContainer ? [currentSourceContainer] : []}
                                     buckets={sourceContainers} selectBucket={setCurrentSourceContainer}/>}
                    {sourceContainers.length === 0 && <Empty description={"No buckets available"}/>}
                </div>
            </div>
        </div>

        <h1>Destination Bucket Selection</h1>
        <SyncDestinationSelection lyveBuckets={lyveBuckets}
                                  currentLyveBucket={currentLyveBucket}
                                  lyveCredentialForm={lyveCredentialForm} setCurrentLyveBucket={setCurrentLyveBucket}
                                  setLyveBuckets={setLyveBuckets}/>

        <h1>Synchronization Configuration</h1>
        <SyncConfigForm form={syncConfigForm}/>

        <PassphraseFormModal disabled={!currentSourceContainer || !currentLyveBucket} onSubmit={onSubmit}
                             buttonText={"Create Synchronization Tasks"}/>
    </div>;
}

export default AzureBucketSynchronizationForm;