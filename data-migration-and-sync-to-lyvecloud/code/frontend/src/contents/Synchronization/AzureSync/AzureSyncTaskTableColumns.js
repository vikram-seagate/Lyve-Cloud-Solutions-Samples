import moment from "moment";
import {Button, message, Popconfirm, Space, Tooltip} from "antd";
import {
    DeleteOutlined,
    MonitorOutlined,
    PauseCircleOutlined,
    PlayCircleOutlined,
} from "@ant-design/icons";
import {
    apiDeleteSyncTask,
    apiEnableSyncTask,
    apiPauseSyncTask,
} from "../../../api/common";

const syncJobTableColumns = (setTaskToView) => [{
    title: "Latest Sync Time",
    dataIndex: "last_sync_time",
    key: "last_sync_time",
    sorter: (a, b) => Date.parse(a.last_sync_time) - Date.parse(b.last_sync_time),
    render: utcString => moment(utcString).calendar()
}, {
    title: "Scheduled Sync Time",
    dataIndex: "scheduled_sync_time",
    key: "scheduled_sync_time",
    sorter: (a, b) => Date.parse(a.scheduled_sync_time) - Date.parse(b.scheduled_sync_time),
    render: utcString => utcString ? moment(utcString).calendar() : "-"
},  {
    title: "Source Container", dataIndex: "source_container", key: "source_container",
}, {
    title: "Lyve Region", dataIndex: "destination_region", key: "destination_region",
}, {
    title: "Destination Bucket", dataIndex: "destination_bucket", key: "destination_bucket",
}, {
    title: "Status", dataIndex: "status", key: "status"
}, {
    title: "Action", key: "action", dataIndex: "status", render: (status, task) => {
        // sync task status: "ACTIVE", "PAUSED". there is no PENDING-PAUSE
        const allowEnable = task.status === "PAUSED";
        const allowDelete = task.status === "PAUSED" || task.status === "ERROR";
        const allowPause = task.status === "ACTIVE";

        return <Space size="small">
            <Tooltip title={"Click to view task details"}>
                <Button type={"link"} icon={<MonitorOutlined/>} onClick={() => setTaskToView(task)}></Button>
            </Tooltip>
            <Tooltip title={allowEnable ? "Enable" : "Only paused tasks allowed to be set active again"}>
                <Popconfirm
                    disabled={!allowEnable}
                    title="Are you sure to start this task again? (All logs cleared)"
                    onConfirm={() => {
                        apiEnableSyncTask(task._id).then(() => {
                            message.success("Enable task submitted");
                        });
                    }}
                    okText="Yes"
                    cancelText="No">
                    <Button type={"link"} icon={<PlayCircleOutlined/>} disabled={!allowEnable}></Button>
                </Popconfirm>
            </Tooltip>
            <Tooltip title={allowPause ? "Pause" : "Task is not active."}>
                <Popconfirm
                    disabled={!allowPause}
                    title="Are you sure to pause this task?"
                    onConfirm={() => {
                        apiPauseSyncTask(task._id).then(() => {
                            message.success("Pause task submitted");
                        });
                    }}
                    okText="Yes"
                    cancelText="No">
                    <Button type={"link"} danger icon={<PauseCircleOutlined/>} disabled={!allowPause}/>
                </Popconfirm>
            </Tooltip>
            <Tooltip title={allowDelete ? "Delete" : "Please pause the task first."}>
                <Popconfirm
                    disabled={!allowDelete}
                    title="Are you sure to delete this task? All the corresponding jobs will be deleted as well."
                    onConfirm={() => {
                        apiDeleteSyncTask(task._id).then(() => {
                            message.success("Task deleted");
                        });
                    }}
                    okText="Yes"
                    cancelText="No">
                    <Button type={"link"} danger icon={<DeleteOutlined/>} disabled={!allowDelete}/>
                </Popconfirm>
            </Tooltip>
        </Space>;
    },
}];

export default syncJobTableColumns;

