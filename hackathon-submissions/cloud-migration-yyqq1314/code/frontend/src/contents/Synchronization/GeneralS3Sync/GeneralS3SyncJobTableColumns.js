import moment from "moment";
import {Button, Progress, Space, Tag, Tooltip} from "antd";
import {MonitorOutlined,} from "@ant-design/icons";

const syncJobTaskColumns = (setTaskToView) => [{
    title: "Updated At",
    dataIndex: "updated_at",
    sorter: (a, b) => Date.parse(a.updated_at) - Date.parse(b.updated_at),
    render: utcString => moment(utcString).calendar()
}, {
    title: "Source Endpoint", dataIndex: "source_endpoint", key: "source_endpoint",
}, {
    title: "Source Bucket", dataIndex: "source_bucket", key: "source_bucket",
}, {
    title: "Destination Bucket", dataIndex: "destination_bucket", key: "destination_bucket",
}, {
    title: "Object", dataIndex: "source_obj_key", key: "source_obj_key",
}, {
    title: "Action", dataIndex: "action", key: "action",
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
    title: "Action", key: "actions", dataIndex: "status", render: (status, task) => {
        return <Space size="small">
            <Tooltip title={"Click to view task details"}>
                <Button type={"link"} icon={<MonitorOutlined/>} onClick={() => setTaskToView(task)}></Button>
            </Tooltip>
        </Space>;
    },
}];

export default syncJobTaskColumns;

