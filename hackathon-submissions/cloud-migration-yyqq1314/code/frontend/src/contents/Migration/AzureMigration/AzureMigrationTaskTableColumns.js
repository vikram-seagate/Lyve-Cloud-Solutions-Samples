import moment from "moment";
import {Button, message, Popconfirm, Progress, Space, Tag, Tooltip} from "antd";
import {MULTI_PART_SIZE} from "../../../common/MultiPart";
import {DeleteOutlined, MonitorOutlined, RedoOutlined, StopOutlined} from "@ant-design/icons";
import {apiDeleteMigrationTask, apiRerunMigrationTask, apiUpdateMigrationTaskProgress} from "../../../api/common";

const azureMigrationTaskTableColumns = (setTaskToView) => [{
    title: "Updated At",
    dataIndex: "updated_at",
    sorter: (a, b) => Date.parse(a.updated_at) - Date.parse(b.updated_at),
    render: utcString => moment(utcString).calendar()
}, {
    title: "Source Container", dataIndex: "source_container", key: "source_container",
}, {
    title: "Source Object", dataIndex: "source_obj_key", key: "source_obj_key",
}, {
    title: "Destination Bucket", dataIndex: "destination_bucket", key: "destination_bucket",
}, {
    title: "Destination Folder", key: "destination_key", dataIndex: "destination_key",
}, {
    title: "Progress", key: "status", dataIndex: "status", render: (status, task) => {
        if (status === "NOT_STARTED" && task.bytes_migrated === 0) {
            return <Tag color={"geekblue"}>Not Started</Tag>;
        } else if (status === "NOT_STARTED" && task.bytes_migrated > 0) {
            return <Progress percent={Math.floor(task.bytes_migrated / task.size * 100)} status={"normal"}/>;
        } else if (status === "ERROR") {
            return <Tag color={"red"}>Error</Tag>;
        } else if (status === "COMPLETED") {
            return <Tag color={"green"}>Completed</Tag>;
        } else if (status === "IN_PROGRESS") {
            return <Progress percent={Math.floor(task.bytes_migrated / task.size * 100)} status={"active"}/>;
        } else if (status === "PENDING-TERMINATION") {
            return <Tag color={"gray"}>Pending Termination</Tag>;
        } else if (status === "TERMINATED") {
            return <Tag color={"gray"}>Terminated</Tag>;
        } else {
            return <Tag color={"gray"}>Unknown State</Tag>;
        }
    }
}, {
    title: "Action", key: "action", dataIndex: "status", render: (status, task) => {
        const allowRerun = task.status === "COMPLETED" || task.status === "TERMINATED";
        const allowDelete = task.status !== "IN_PROGRESS";
        const allowTerminate = task.status === "IN_PROGRESS" && task.size > MULTI_PART_SIZE;

        return <Space size="small">
            <Tooltip title={"Click to view task details"}>
                <Button type={"link"} icon={<MonitorOutlined/>} onClick={() => setTaskToView(task)}></Button>
            </Tooltip>
            <Tooltip title={allowRerun ? "Rerun" : "only completed or terminated tasks allowed to rerun"}>
                <Popconfirm
                    disabled={!allowRerun}
                    title="Are you sure to rerun this task? (All logs cleared)"
                    onConfirm={() => {
                        apiRerunMigrationTask(task._id).then(() => {
                            message.success("Rerun task submitted");
                        });
                    }}
                    okText="Yes"
                    cancelText="No">
                    <Button type={"link"} icon={<RedoOutlined/>} disabled={!allowRerun}></Button>
                </Popconfirm>
            </Tooltip>
            <Tooltip title={allowTerminate ? "Terminate" : "Task is not running."}>
                <Popconfirm
                    disabled={!allowTerminate}
                    title="Are you sure to terminate this task?"
                    onConfirm={() => {
                        apiUpdateMigrationTaskProgress(task._id, {status: "PENDING-TERMINATION"}).then(() => {
                            message.success("Task status set to pending termination");
                        });
                    }}
                    okText="Yes"
                    cancelText="No">
                    <Button type={"link"} danger icon={<StopOutlined/>} disabled={!allowTerminate}/>
                </Popconfirm>
            </Tooltip>
            <Tooltip title={allowDelete ? "Delete" : "Running task cannot be deleted."}>
                <Popconfirm
                    disabled={!allowDelete}
                    title="Are you sure to delete this task?"
                    onConfirm={() => {
                        apiDeleteMigrationTask(task._id).then(() => {
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
},];

export default azureMigrationTaskTableColumns;