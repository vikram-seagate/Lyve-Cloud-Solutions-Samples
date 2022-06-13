import {
    Button,
    Card,
    Divider,
    Popconfirm,
    Progress,
    Space,
    Table,
    Tag,
    Tooltip,
    message,
    Form,
    Input,
    InputNumber,
    DatePicker, Checkbox
} from "antd";
import prettyBytes from "pretty-bytes";
import {DeleteOutlined, MonitorOutlined, RedoOutlined, StopOutlined} from "@ant-design/icons";
import moment from "moment";
import {useEffect, useState} from "react";
import {apiDeleteMigrationTask, apiRerunMigrationTask, apiUpdateMigrationTaskProgress} from "../../../api/common";
import {MULTI_PART_SIZE} from "../../../common/MultiPart";
import AlibabaMigrationTaskDetailDrawer from "./AlibabaMigrationTaskDetailDrawer";
import alibabaMigrationTaskTableColumns from "./AlibabaMigrationTaskTableColumns";

const styles = {
    cardContainer: {
        display: "flex",
    }, card: {
        margin: "0 0.25rem", flex: "1"
    }, cardValue: {
        fontSize: "1.5rem", textAlign: "center"
    }
};

function sumBytesMigrated(tasks) {
    return tasks.reduce((size, task) => size + Math.max(task.bytes_migrated, 0), 0);
}

function checkPossibleDisconnection(task) {
    if (task.status !== "IN_PROGRESS") {
        return false;
    }

    return moment().subtract(1, "hours").isAfter(task.updated_at);
}

function filterTasks(filter, tasks) {
    return tasks.filter(task => {
        if (filter.name !== null && filter.name !== undefined && filter.name.length > 0) {
            if (!task.source_obj_key.toLowerCase().toLowerCase().includes(filter.name.toLowerCase())) {
                return false;
            }
        }

        if (filter.size_min !== null && filter.size_min !== undefined && filter.size_min > 0) {
            if (task.size < filter.size_min) {
                return false;
            }
        }

        if (filter.size_max !== null && filter.size_max !== undefined) {
            if (task.size > filter.size_max) {
                return false;
            }
        }

        if (filter.update_time_before !== null && filter.update_time_before !== undefined) {
            if (filter.update_time_before.isBefore(task.updated_at)) {
                return false;
            }
        }

        if (filter.update_time_after !== null && filter.update_time_after !== undefined) {
            if (filter.update_time_after.isAfter(task.updated_at)) {
                return false;
            }
        }

        if (filter.disconnected !== null && filter.disconnected !== undefined) {
            if (filter.disconnected && !checkPossibleDisconnection(task)) {
                return false;
            }
        }

        return true;
    });
}

function AlibabaMigrationProgressMonitor({tasks}) {
    const [filterForm] = Form.useForm();
    const [lastMigratedSize, setLastMigratedSize] = useState(sumBytesMigrated(tasks));
    const [migrationSpeed, setMigrationSpeed] = useState(0);
    const [lastUpdateTime, setLastUpdateTime] = useState(null);
    const [taskToView, setTaskToView] = useState(null);
    const [filters, setFilters] = useState({});

    const onFilterValueChange = () => {
        console.log(filterForm.getFieldsValue());
        setFilters(filterForm.getFieldsValue());
    };

    useEffect(() => {
        if (!tasks || tasks.length === 0) {
            return;
        }

        if (lastUpdateTime === null) {
            setLastUpdateTime(Date.now() / 1000);
            setLastMigratedSize(sumBytesMigrated(tasks));
            return;
        }

        const newBytesMigrated = sumBytesMigrated(tasks);
        const newTime = Date.now() / 1000;
        const timeGap = newTime - lastUpdateTime;
        setMigrationSpeed(Math.max((newBytesMigrated - lastMigratedSize) / timeGap, 0));
        setLastMigratedSize(newBytesMigrated);
        setLastUpdateTime(newTime);
    }, [tasks]);

    return <div>
        <div style={styles.cardContainer}>
            <Card style={styles.card} title={"Not Started"}>
                <div style={styles.cardValue}>{tasks.filter(task => task.status === "NOT_STARTED").length}</div>
            </Card>
            <Card style={styles.card} title={"In Progress"}>
                <div
                    style={styles.cardValue}>{tasks.filter(task => task.status === "IN_PROGRESS").length}</div>
            </Card>
            <Card style={styles.card} title={"Completed"}>
                <div style={styles.cardValue}>{tasks.filter(task => task.status === "COMPLETED").length}</div>
            </Card>
            <Card style={styles.card} title={"Terminated"}>
                <div style={styles.cardValue}>{tasks.filter(task => task.status === "TERMINATED").length}</div>
            </Card>
            <Card style={styles.card} title={"Migrated Size"}>
                <div
                    style={styles.cardValue}>{prettyBytes(sumBytesMigrated(tasks))} / {prettyBytes(tasks.reduce((size, task) => size + task.size, 0))}</div>
            </Card>
            <Card style={styles.card} title={"Migrated Speed"}>
                <div
                    style={styles.cardValue}>{prettyBytes(migrationSpeed)} / s
                </div>
            </Card>
            <Card style={styles.card} title={"Error"}>
                <div style={styles.cardValue}>{tasks.filter(task => task.status === "ERROR").length}</div>
            </Card>
        </div>
        <Divider/>
        <div style={{marginBottom: "1rem"}}>
            <Form
                layout={"inline"}
                form={filterForm}
                initialValues={{name: "", size_max: null, modify_range: null}}
                onValuesChange={onFilterValueChange}>
                <Form.Item
                    name="disconnected"
                    valuePropName="checked">
                    <Checkbox>Disconnected</Checkbox>
                </Form.Item>
                <Form.Item label="Object key Contains" name={"name"}>
                    <Input placeholder=""/>
                </Form.Item>
                <Form.Item label="Size >= (B)" style={{marginRight: 0}}>
                    <Form.Item
                        name="size_min">
                        <InputNumber min={0}/>
                    </Form.Item>
                </Form.Item>
                <Form.Item label="Size <= (B)">
                    <Form.Item
                        name="size_max">
                        <InputNumber min={0}/>
                    </Form.Item>
                </Form.Item>
                <Form.Item name="update_time_before" label="Before Time:">
                    <DatePicker showTime/>
                </Form.Item>
                <Form.Item name="update_time_after" label="After Time:">
                    <DatePicker showTime/>
                </Form.Item>
            </Form>
        </div>
        <Table dataSource={filterTasks(filters, tasks)} columns={alibabaMigrationTaskTableColumns(setTaskToView)}
               size={"small"}
               pagination={{position: ["bottomLeft"], defaultPageSize: 100}}/>
        <AlibabaMigrationTaskDetailDrawer setTaskToView={setTaskToView} taskToView={taskToView}/>
    </div>;
}

export default AlibabaMigrationProgressMonitor;