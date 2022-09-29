import {
    Table, Form, Checkbox, Input, InputNumber, DatePicker, Divider,
} from "antd";

import {useState} from "react";
import syncTaskTableColumns from "./AzureSyncTaskTableColumns";
import syncJobTableColumns from "./AzureSyncJobTableColumns";
import AzureSyncJobDetailDrawer from "./AzureSyncJobDetailDrawer";
import AzureSyncTaskDetailDrawer from "./AzureSyncTaskDetailDrawer";
import {checkPossibleDisconnectedTask} from "../../../common/TableUtil";

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
            if (filter.disconnected && !checkPossibleDisconnectedTask(task)) {
                return false;
            }
        }

        return true;
    });
}

function AzureSynchronizationProgressMonitor({syncTasks, syncJobs}) {
    const [filterForm] = Form.useForm();
    const [taskToView, setTaskToView] = useState(null);
    const [jobToView, setJobToView] = useState(null);
    const [filters, setFilters] = useState({});

    const onFilterValueChange = () => {
        console.log(filterForm.getFieldsValue());
        setFilters(filterForm.getFieldsValue());
    };

    return <div>
        <h3>Synchronization Configs</h3>
        <Table dataSource={syncTasks} columns={syncTaskTableColumns(setTaskToView)} size={"small"}
               pagination={{position: ["bottomLeft"], defaultPageSize: 100}}/>

        <Divider/>
        <h3>Synchronization Jobs</h3>
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
        <Table dataSource={filterTasks(filters, syncJobs)} columns={syncJobTableColumns(setJobToView)} size={"small"}
               pagination={{position: ["bottomLeft"], defaultPageSize: 100}}/>
        <AzureSyncTaskDetailDrawer setTaskToView={setTaskToView} taskToView={taskToView}/>
        <AzureSyncJobDetailDrawer setJobToView={setJobToView} jobToView={jobToView}/>
    </div>;
}

export default AzureSynchronizationProgressMonitor;