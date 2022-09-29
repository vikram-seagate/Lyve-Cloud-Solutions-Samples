import React, {useEffect, useState} from "react";
import {Divider, Empty, Form, notification} from "antd";
import {apiLyveListS3AllObjects, apiLyveS3ProxyExecute} from "../api/lyve";
import BucketTable from "./BucketTable";
import DestinationFolderTree from "./DestinationFolderTree";
import LyveCredentialForm from "./LyveCredentialForm";
import prettyBytes from "pretty-bytes";
import PassphraseFormModal from "../contents/Migration/GeneralS3Migration/PassphraseFormModal";
import {encryptWithAES} from "./Encryption";

const LyveDestinationSelection = ({objectsToMigrate, createMigrationTask}) => {
    const [lyveCredentialForm] = Form.useForm();
    const [lyveBuckets, setLyveBuckets] = useState([]);
    const [destinationBucket, setDestinationBucket] = useState(null);
    const [destinationBucketObjects, setDestinationBucketObjects] = useState([]);
    const [destinationFolder, setDestinationFolder] = useState([]);
    const [bucketObjectLoading, setBucketObjectLoading] = useState(false);

    useEffect(() => {
        if (destinationBucket) {
            setBucketObjectLoading(true);
            apiLyveListS3AllObjects(destinationBucket.name, lyveCredentialForm.getFieldsValue())
                .then(res => {
                    console.log(res);
                    res.forEach(content => {
                        content.name = content.Key;
                        content.key = content.Key;
                    });
                    setDestinationBucketObjects(res);
                    setDestinationFolder([]);
                })
                .catch(e => {
                    notification["error"]({
                        message: e.response.data.message, description: "",
                    });
                })
                .finally(() => {
                    setBucketObjectLoading(false);
                });
        }
    }, [destinationBucket]);

    const onLyveSignIn = () => {
        apiLyveS3ProxyExecute({
            cmd: "listBuckets", ...lyveCredentialForm.getFieldsValue(),
        }).then(res => {
            console.log(res);
            res.data.Buckets.forEach(bucket => {
                bucket.key = bucket.Name;
                bucket.name = bucket.Name;
                bucket.creationDate = bucket.CreationDate;
            });
            setLyveBuckets(res.data.Buckets);
            setDestinationFolder([]);
        }).catch(e => {
            if (e?.response?.data?.message) {
                notification["error"]({
                    message: e.response.data.message, description: "",
                });
            }
        });
    };

    const onCreateMigrationTask = (passphrase) => {
        const {region, accessKeyId, accessKeySecret} = lyveCredentialForm.getFieldsValue();

        createMigrationTask({
            destination_region: region,
            destination_key_id: encryptWithAES(passphrase, accessKeyId),
            destination_key_secret: encryptWithAES(passphrase, accessKeySecret),
            destination_key: destinationFolder[0],
            destination_bucket: destinationBucket.name,
        }, passphrase);
        setDestinationFolder([]);
    };

    return <div>
        <h2>Files to migrate</h2>
        <p>{objectsToMigrate.length} objects to migrate, in
            total {prettyBytes(objectsToMigrate.reduce((sum, object) => sum + object.Size, 0))}.</p>
        <ul>
            {objectsToMigrate.slice(0, 10).map(obj => <li key={obj.key}>{obj.key}</li>)}
            {objectsToMigrate.length > 10 && <li>...</li>}
        </ul>
        <Divider/>
        <h2>Select Destination</h2>
        <p>Lyve Credentials</p>
        <LyveCredentialForm form={lyveCredentialForm} onSubmit={onLyveSignIn}/>

        <div style={{display: "flex", justifyContent: "space-between"}}>
            <div style={{width: "48%"}}>
                <h1 style={{marginBottom: "1rem"}}>Bucket Table</h1>
                {lyveBuckets.length > 0 && <BucketTable buckets={lyveBuckets}
                                                        currentBucket={destinationBucket}
                                                        selectedBuckets={destinationBucket ? [destinationBucket] : []}
                                                        disabled={bucketObjectLoading}
                                                        selectBucket={setDestinationBucket}/>}
                {lyveBuckets.length === 0 && <Empty description={"No buckets available"}/>}
            </div>
            <div style={{width: "48%"}}>
                {destinationBucket && <>
                    <div style={{display: "flex", justifyContent: "space-between"}}>
                        <h1 style={{marginBottom: "1rem"}}>Bucket Object List</h1>
                        {destinationFolder.length === 0 && <h3>Destination Not Selected.</h3>}
                        {destinationFolder.length > 0 && <h3>Destination Selected: {destinationFolder[0]}</h3>}
                    </div>
                    <DestinationFolderTree currentBucket={destinationBucket}
                                           bucketObjects={destinationBucketObjects}
                                           destinationFolder={destinationFolder}
                                           setDestinationFolder={setDestinationFolder}
                                           loading={bucketObjectLoading}
                    />
                </>}
            </div>
        </div>
        <Divider/>
        <PassphraseFormModal disabled={destinationFolder.length === 0} onSubmit={onCreateMigrationTask}/>
        {/*<Button disabled={destinationFolder.length === 0} type={"primary"}*/}
        {/*        onClick={onCreateMigrationTask}>*/}
        {/*    Create Migration Tasks*/}
        {/*</Button>*/}
    </div>;
};

export default LyveDestinationSelection;