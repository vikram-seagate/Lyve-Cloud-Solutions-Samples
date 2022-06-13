import {Divider, Form, notification, Switch, Tabs} from "antd";
import {useEffect, useState} from "react";
import BucketTable from "../../../common/BucketTable";
import {mainContentHeight} from "../../../common/style";
import GoogleMigrationProgressMonitor from "./GoogleMigrationProgressMonitor";
import S3BucketObjectsTable from "../../../common/S3BucketObjectsTable";
import GoogleCredentialForm from "./GoogleCredentialForm";
import {apiCreateMigrationTasks, apiFetchMigrationTasks} from "../../../api/common";
import {encryptWithAES} from "../../../common/Encryption";
import {MULTI_PART_SIZE} from "../../../common/MultiPart";
import LyveDestinationSelection from "../../../common/LyveDestinationSelection";
import {apiGoogleProxyExecute} from "../../../api/googlecloud";

const {TabPane} = Tabs;

const styles = {
    pageContainer: {
        padding: "3rem", height: mainContentHeight, overflowY: "auto"
    }, formContainer: {}, bucketContainer: {
        display: "flex", flexWrap: "wrap"
    }, bucketCard: {
        padding: "1rem", margin: "1rem 1rem 0 0", border: "1px solid rgba(0, 0, 0, 0.1)", cursor: "pointer"
    }
};

function GoogleMigration() {
    const [googleCredentialForm] = Form.useForm();
    const [tasks, setTasks] = useState([]);
    const [buckets, setBuckets] = useState([]);
    const [currentBucket, selectBucket] = useState(null);
    const [containerBlobs, setContainerBlobs] = useState([]);
    const [selectedObjects, setSelectedObjects] = useState([]);
    const [bucketObjectLoading, setBucketObjectLoading] = useState(false);
    const [liveMonitorInterval, setLiveMonitorInterval] = useState(null);

    const loadTasks = () => {
        apiFetchMigrationTasks("fromGoogle")
            .then(res => {
                console.log(res.data);
                res.data.forEach(task => task.key = task._id);
                setTasks(res.data);
            }).catch(e => {
            notification["error"]({
                message: e.response.data.message, description: "",
            });
        });
    };

    useEffect(() => {
        loadTasks();
        return () => {
            clearInterval(liveMonitorInterval);
        };
    }, []);

    useEffect(() => {
        if (!currentBucket) {
            return;
        }

        setBucketObjectLoading(true);
        apiGoogleProxyExecute({
            cmd: "getFiles",
            bucket: currentBucket.name,
            ...googleCredentialForm.getFieldsValue(),
        }).then((res) => {
            console.log(res);
            res.data.forEach(obj => {
                obj.key = obj.name;
                obj.Key = obj.name;
                obj.Size = +obj.metadata.size;
                obj.LastModified = obj.metadata.updated;
            });
            setContainerBlobs(res.data);
        }).catch(e => {
            console.error(e);
            notification["error"]({
                message: e.response.data.message,
                description: "",
            });
        }).finally(() => {
            setBucketObjectLoading(false);
        });
    }, [currentBucket]);

    const onSubmit = () => {
        console.log(googleCredentialForm.getFieldsValue());

        apiGoogleProxyExecute({
            cmd: "getBuckets", ...googleCredentialForm.getFieldsValue(),
        }).then(res => {
            console.log(res);
            res.data.forEach(bucket => {
                bucket.key = bucket.name;
            });
            setBuckets(res.data);
        }).catch(e => {
            if (e?.response?.data?.message) {
                notification["error"]({
                    message: e.response.data.message, description: "",
                });
            }
        });
    };

    const createMigrationTask = (destinationData, passphrase) => {
        const {projectId, credentials} = googleCredentialForm.getFieldsValue();

        const migrationTasks = selectedObjects.map(objectToMigrate => {
            const migrationTask = {
                ...destinationData,
                size: objectToMigrate.Size,
                source_platform: "fromGoogle",
                source_obj_key: objectToMigrate.key,
                source_bucket: currentBucket.name,
                source_project_id: projectId,
                source_credentials: encryptWithAES(passphrase, JSON.stringify(credentials))
            };

            if (objectToMigrate.Size > MULTI_PART_SIZE) {
                // requires multi-part upload
                const partitionCount = Math.ceil(objectToMigrate.Size / MULTI_PART_SIZE);
                migrationTask.partitions = [];
                for (let i = 0; i < partitionCount; i++) {
                    const start = i * MULTI_PART_SIZE;
                    migrationTask.partitions.push({
                        start,
                        end: start + Math.min(objectToMigrate.Size - start, MULTI_PART_SIZE) - 1,
                        PartNumber: i + 1,
                    });
                }
            }

            return migrationTask;
        });

        console.log(migrationTasks);

        apiCreateMigrationTasks(migrationTasks)
            .then(res => {
                console.log(res.data);
                notification["success"]({
                    message: "migration tasks created.", description: "", placement: "bottomRight"
                });
            }).catch(e => {
            console.error(e);
            notification["error"]({
                message: e.response.data.message, description: "",
            });
        });
    };

    const onEnableLiveMonitor = (checked) => {
        console.log(checked);
        clearInterval(liveMonitorInterval);
        if (checked) {
            setLiveMonitorInterval(setInterval(() => {
                loadTasks();
            }, 5000));
        } else {
            setLiveMonitorInterval(null);
        }
    };

    return <div style={styles.pageContainer}>
        <div style={{display: "flex", justifyContent: "space-between"}}>
            <h1>Google Cloud Data Migration Dashboard</h1>
            <div>
                <Switch checkedChildren="Refresh" unCheckedChildren="Refresh"
                        onClick={onEnableLiveMonitor}/>
            </div>
        </div>

        <Tabs defaultActiveKey="monitor">
            <TabPane tab="Progress Monitor" key="monitor">
                <GoogleMigrationProgressMonitor tasks={tasks} setTasks={setTasks}/>
            </TabPane>
            <TabPane tab="Google Source Data" key="source">
                <div>
                    <div style={{display: "flex", justifyContent: "space-between"}}>
                        <div style={{width: "48%"}}>
                            <h1>Credentials</h1>
                            <div style={styles.formContainer}>
                                <GoogleCredentialForm form={googleCredentialForm} onSubmit={onSubmit}/>
                            </div>
                        </div>
                        <div style={{width: "48%"}}>
                            <h1 style={{marginBottom: "1rem"}}>Bucket Table</h1>
                            <BucketTable buckets={buckets} selectBucket={selectBucket}
                                         selectedBuckets={currentBucket ? [currentBucket] : []}/>
                        </div>
                    </div>
                </div>
                <Divider/>
                <div>
                    <S3BucketObjectsTable bucketObjects={containerBlobs}
                                          selectedObjects={selectedObjects}
                                          bucketObjectLoading={bucketObjectLoading}
                                          setSelectedObjects={setSelectedObjects}/>
                </div>
            </TabPane>
            <TabPane tab="Lyve Destination" key="destination" disabled={selectedObjects.length === 0}>
                <LyveDestinationSelection objectsToMigrate={selectedObjects} createMigrationTask={createMigrationTask}/>
            </TabPane>
        </Tabs>

    </div>;
}

export default GoogleMigration;