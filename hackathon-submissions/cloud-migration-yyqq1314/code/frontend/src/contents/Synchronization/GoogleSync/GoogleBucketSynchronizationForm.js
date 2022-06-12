import BucketTable from "../../../common/BucketTable";
import {Empty, Form, notification} from "antd";
import React, {useState} from "react";
import {apiCreateSynchronizationTask} from "../../../api/common";
import {encryptWithAES} from "../../../common/Encryption";
import PassphraseFormModal from "../../Migration/GeneralS3Migration/PassphraseFormModal";
import SyncConfigForm from "../../../common/SyncConfigForm";
import SyncDestinationSelection from "../../../common/SyncDestinationSelection";
import GoogleCredentialForm from "../../Migration/GoogleMigration/GoogleCredentialForm";
import {apiGoogleProxyExecute} from "../../../api/googlecloud";

function GoogleBucketSynchronizationForm() {
    const [googleCredentialForm] = Form.useForm();
    const [lyveCredentialForm] = Form.useForm();
    const [syncConfigForm] = Form.useForm();
    const [sourceBuckets, setSourceBuckets] = useState([]);
    const [currentSourceBucket, setCurrentSourceBucket1] = useState(null);
    const [lyveBuckets, setLyveBuckets] = useState([]);
    const [currentLyveBucket, setCurrentLyveBucket] = useState(null);

    const onGoogleSignIn = () => {
        apiGoogleProxyExecute({
            cmd: "getBuckets", ...googleCredentialForm.getFieldsValue(),
        }).then(res => {
            console.log(res);
            res.data.forEach(bucket => {
                bucket.key = bucket.name;
            });
            setSourceBuckets(res.data);
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

        const sourceFormData = googleCredentialForm.getFieldsValue();
        const lyveFormData = lyveCredentialForm.getFieldsValue();

        const task = {
            ...configs,
            source_platform: "fromGoogle",
            source_project_id: sourceFormData.projectId,
            source_credentials: encryptWithAES(passphrase, JSON.stringify(sourceFormData.credentials)),
            source_bucket: currentSourceBucket.name,
            status: "ACTIVE",
            destination_region: lyveFormData.region,
            destination_bucket: currentLyveBucket.name,
            destination_key_id: encryptWithAES(passphrase, lyveFormData.accessKeyId),
            destination_key_secret: encryptWithAES(passphrase, lyveFormData.accessKeySecret),
        };

        apiCreateSynchronizationTask(task).then(res => {
            console.log(res);
            setCurrentLyveBucket(null);
            setCurrentSourceBucket1(null);
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
                        <GoogleCredentialForm form={googleCredentialForm} onSubmit={onGoogleSignIn}/>
                    </div>
                </div>
                <div style={{width: "48%"}}>
                    <h1 style={{marginBottom: "1rem"}}>Bucket Table</h1>
                    {sourceBuckets.length > 0 &&
                        <BucketTable selectedBuckets={currentSourceBucket ? [currentSourceBucket] : []}
                                     buckets={sourceBuckets} selectBucket={setCurrentSourceBucket1}/>}
                    {sourceBuckets.length === 0 && <Empty description={"No buckets available"}/>}
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

        <PassphraseFormModal disabled={!currentSourceBucket || !currentLyveBucket} onSubmit={onSubmit}
                             buttonText={"Create Synchronization Tasks"}/>
    </div>;
}

export default GoogleBucketSynchronizationForm;