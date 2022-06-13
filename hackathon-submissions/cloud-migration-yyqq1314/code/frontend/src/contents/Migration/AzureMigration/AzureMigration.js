import {Divider, Form, notification, Switch, Tabs} from "antd";
import {useEffect, useState} from "react";
import BucketTable from "../../../common/BucketTable";
import {mainContentHeight} from "../../../common/style";
import AzureMigrationProgressMonitor from "./AzureMigrationProgressMonitor";
import S3BucketObjectsTable from "../../../common/S3BucketObjectsTable";
import AzureCredentialForm from "./AzureCredentialForm";
import {apiCreateMigrationTasks, apiFetchMigrationTasks} from "../../../api/common";
import {encryptWithAES} from "../../../common/Encryption";
import {MULTI_PART_SIZE} from "../../../common/MultiPart";
import LyveDestinationSelection from "../../../common/LyveDestinationSelection";
import {apiAzureProxyExecute} from "../../../api/azure";

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

function AzureMigration() {
    const [azureCredentialForm] = Form.useForm();
    const [tasks, setTasks] = useState([]);
    const [containers, setContainers] = useState([]);
    const [currentContainer, selectContainer] = useState(null);
    const [containerBlobs, setContainerBlobs] = useState([]);
    const [selectedObjects, setSelectedObjects] = useState([]);
    const [bucketObjectLoading, setBucketObjectLoading] = useState(false);
    const [liveMonitorInterval, setLiveMonitorInterval] = useState(null);

    const loadTasks = () => {
        apiFetchMigrationTasks("fromAzure")
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
        if (currentContainer) {
            setBucketObjectLoading(true);
            apiAzureProxyExecute({
                cmd: "listBlobsFlat",
                ...azureCredentialForm.getFieldsValue(),
                container: currentContainer.name,
            })
                .then((res) => {
                    console.log(res);
                    res.data.forEach(blob => {
                        blob.key = blob.name;
                        blob.Size = blob.properties.contentLength;
                        blob.LastModified = blob.properties.lastModified;
                    });
                    setContainerBlobs(res.data);
                })
                .catch(e => {
                    console.error(e);
                    notification["error"]({
                        message: e.response.data.message, description: "",
                    });
                }).finally(() => {
                setBucketObjectLoading(false);
            });
        }
    }, [currentContainer]);

    const onSubmit = () => {
        apiAzureProxyExecute({
            cmd: "listContainers", ...azureCredentialForm.getFieldsValue(),
        }).then(res => {
            console.log(res);
            res.data.forEach(container => {
                container.key = container.name;
            });
            setContainers(res.data);
        }).catch(e => {
            if (e?.response?.data?.message) {
                notification["error"]({
                    message: e.response.data.message, description: "",
                });
            }
        });
    };

    const createMigrationTask = (destinationData, passphrase) => {
        const {connection_string} = azureCredentialForm.getFieldsValue();

        const migrationTasks = selectedObjects.map(objectToMigrate => {

            const migrationTask = {
                ...destinationData,
                size: objectToMigrate.Size,
                source_platform: "fromAzure",
                source_obj_key: objectToMigrate.key,
                source_container: currentContainer.name,
                source_connection_string: encryptWithAES(passphrase, connection_string),
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
            <h1>Azure Cloud Data Migration Dashboard</h1>
            <div>
                <Switch checkedChildren="Refresh" unCheckedChildren="Refresh"
                        onClick={onEnableLiveMonitor}/>
            </div>
        </div>

        <Tabs defaultActiveKey="monitor">
            <TabPane tab="Progress Monitor" key="monitor">
                <AzureMigrationProgressMonitor tasks={tasks} setTasks={setTasks}/>
            </TabPane>
            <TabPane tab="Azure Source Data" key="source">
                <div>
                    <div style={{display: "flex", justifyContent: "space-between"}}>
                        <div style={{width: "48%"}}>
                            <h1>Credentials</h1>
                            <div style={styles.formContainer}>
                                <AzureCredentialForm form={azureCredentialForm} onSubmit={onSubmit}/>
                            </div>
                        </div>
                        <div style={{width: "48%"}}>
                            <h1 style={{marginBottom: "1rem"}}>Bucket Table</h1>
                            <BucketTable buckets={containers} selectBucket={selectContainer}
                                         selectedBuckets={currentContainer ? [currentContainer] : []}/>
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

export default AzureMigration;