import BucketTable from "../../../common/BucketTable";
import {Empty, Form, notification} from "antd";
import React, {useState} from "react";
import {apiAlibabaProxyExecute} from "../../../api/alicloud";
import {apiCreateSynchronizationTask} from "../../../api/common";
import {encryptWithAES} from "../../../common/Encryption";
import PassphraseFormModal from "../../Migration/GeneralS3Migration/PassphraseFormModal";
import AlibabaCredentialForm from "../../../common/AlibabaCredentialForm";
import SyncConfigForm from "../../../common/SyncConfigForm";
import SyncDestinationSelection from "../../../common/SyncDestinationSelection";

function AlibabaBucketSynchronizationForm() {
    const [alibabaCredentialForm] = Form.useForm();
    const [lyveCredentialForm] = Form.useForm();
    const [syncConfigForm] = Form.useForm();
    const [sourceBuckets, setSourceBuckets] = useState([]);
    const [currentSourceBucket, setCurrentSourceBucket] = useState(null);
    const [lyveBuckets, setLyveBuckets] = useState([]);
    const [currentLyveBucket, setCurrentLyveBucket] = useState(null);

    const onAlibabaSignIn = () => {
        apiAlibabaProxyExecute({
            cmd: "listBuckets", ...alibabaCredentialForm.getFieldsValue(),
        }).then(res => {
            console.log(res);
            res.data.buckets.forEach(bucket => {
                bucket.key = bucket.name;
            });
            setSourceBuckets(res.data.buckets);
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

        const sourceFormData = alibabaCredentialForm.getFieldsValue();
        const lyveFormData = lyveCredentialForm.getFieldsValue();

        const task = {
            ...configs,
            source_platform: "fromAlibaba",
            source_region: sourceFormData.region,
            source_bucket: currentSourceBucket.name,
            source_key_id: encryptWithAES(passphrase, sourceFormData.accessKeyId),
            source_key_secret: encryptWithAES(passphrase, sourceFormData.accessKeySecret),
            status: "ACTIVE",
            destination_region: lyveFormData.region,
            destination_bucket: currentLyveBucket.name,
            destination_key_id: encryptWithAES(passphrase, lyveFormData.accessKeyId),
            destination_key_secret: encryptWithAES(passphrase, lyveFormData.accessKeySecret),
        };

        apiCreateSynchronizationTask(task).then(res => {
            console.log(res);
            setCurrentLyveBucket(null);
            setCurrentSourceBucket(null);
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
                        <AlibabaCredentialForm form={alibabaCredentialForm} onSubmit={onAlibabaSignIn}/>
                    </div>
                </div>
                <div style={{width: "48%"}}>
                    <h1 style={{marginBottom: "1rem"}}>Bucket Table</h1>
                    {sourceBuckets.length > 0 &&
                        <BucketTable selectedBuckets={currentSourceBucket ? [currentSourceBucket] : []}
                                     buckets={sourceBuckets} selectBucket={setCurrentSourceBucket}/>}
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

        <PassphraseFormModal disabled={!currentSourceBucket || !currentLyveBucket} onSubmit={onSubmit} buttonText={"Create Synchronization Tasks"}/>
    </div>;
}

export default AlibabaBucketSynchronizationForm;