import {notification, Switch, Tabs} from "antd";
import {useEffect, useState} from "react";
import {mainContentHeight} from "../../../common/style";
import {apiFetchSynchronizationJobs, apiFetchSynchronizationTasks} from "../../../api/common";
import AzureBucketSynchronizationForm from "./AzureBucketSynchronizationForm";
import AzureSynchronizationProgressMonitor from "./AzureSynchronizationProgressMonitor";

const {TabPane} = Tabs;

const styles = {
    pageContainer: {
        padding: "3rem", height: mainContentHeight, overflowY: "auto"
    },
    formContainer: {},
    bucketContainer: {
        display: "flex", flexWrap: "wrap"
    },
    bucketCard: {
        padding: "1rem", margin: "1rem 1rem 0 0", border: "1px solid rgba(0, 0, 0, 0.1)", cursor: "pointer"
    }
};

function AzureSynchronization() {
    const [syncTasks, setSyncTasks] = useState([]);
    const [syncJobs, setSyncJobs] = useState([]);
    const [liveMonitorInterval, setLiveMonitorInterval] = useState(null);

    const loadTasks = () => {
        apiFetchSynchronizationTasks("fromAzure")
            .then(res => {
                console.log(res.data);
                res.data.forEach(task => task.key = task._id);
                setSyncTasks(res.data);
            }).catch(e => {
            notification["error"]({
                message: e.response.data.message, description: "",
            });
        });

        apiFetchSynchronizationJobs("fromAzure")
            .then(res => {
                console.log(res.data);
                res.data.forEach(job => job.key = job._id);
                setSyncJobs(res.data);
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
            <h1>Azure Container → Lyve Bucket Synchronization Dashboard
            </h1>
            <div>
                <Switch checkedChildren="Refresh" unCheckedChildren="Refresh"
                        onClick={onEnableLiveMonitor}/>
            </div>
        </div>

        <Tabs defaultActiveKey="monitor">
            <TabPane tab="Progress Monitor" key="monitor">
                <AzureSynchronizationProgressMonitor syncTasks={syncTasks}
                                                     setSyncTasks={setSyncTasks}
                                                     syncJobs={syncJobs}
                                                     setSyncJobs={setSyncJobs}/>
            </TabPane>
            <TabPane tab="Synchronization Configuration">
                <AzureBucketSynchronizationForm/>
            </TabPane>
        </Tabs>
    </div>;
}

export default AzureSynchronization;