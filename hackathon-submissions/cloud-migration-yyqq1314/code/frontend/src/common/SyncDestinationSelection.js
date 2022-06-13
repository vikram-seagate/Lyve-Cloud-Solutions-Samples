import LyveCredentialForm from "./LyveCredentialForm";
import {apiLyveS3ProxyExecute} from "../api/lyve";
import {Empty, notification} from "antd";
import BucketTable from "./BucketTable";

function SyncDestinationSelection({
                                      lyveCredentialForm,
                                      setLyveBuckets,
                                      lyveBuckets,
                                      currentLyveBucket,
                                      setCurrentLyveBucket
                                  }) {
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
        }).catch(e => {
            if (e?.response?.data?.message) {
                notification["error"]({
                    message: e.response.data.message, description: "",
                });
            }
        });
    };

    return <div>
        <div style={{display: "flex", justifyContent: "space-between"}}>
            <div style={{width: "48%"}}>
                <h1>Credentials</h1>
                <div>
                    <LyveCredentialForm form={lyveCredentialForm} onSubmit={onLyveSignIn}/>
                </div>
            </div>
            <div style={{width: "48%"}}>
                <h1 style={{marginBottom: "1rem"}}>Bucket Table</h1>
                {lyveBuckets.length > 0 && <BucketTable buckets={lyveBuckets} selectBucket={setCurrentLyveBucket}
                                                        selectedBuckets={currentLyveBucket ? [currentLyveBucket] : []}/>}
                {lyveBuckets.length === 0 && <Empty description={"No buckets available"}/>}
            </div>
        </div>
    </div>;
}

export default SyncDestinationSelection;