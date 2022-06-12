import {DatePicker, Form, Input, InputNumber, Select, Switch} from "antd";
import React from "react";

function SyncConfigForm({form}) {
    return <Form
        form={form}
        layout="vertical"
        initialValues={{
            enable_upload: true,
            enable_delete: false,
            enable_update: true,
            frequency: {
                value: 1, unit: "hours"
            }
        }}>
        <Form.Item label="Synchronization Frequency">
            <Input.Group compact>
                <Form.Item
                    name={["frequency", "value"]}
                    noStyle
                    rules={[{required: true, message: "Synchronization Frequency is required"}]}>
                    <InputNumber min={1}/>
                </Form.Item>
                <Form.Item
                    name={["frequency", "unit"]}
                    noStyle>
                    <Select>
                        <Select.Option value="minutes">Minutes</Select.Option>
                        <Select.Option value="hours">Hour</Select.Option>
                        <Select.Option value="days">Day</Select.Option>
                        <Select.Option value="weeks">Week</Select.Option>
                    </Select>
                </Form.Item>
            </Input.Group>
        </Form.Item>
        <Form.Item
            label="Modified Before (If set, only synchronize files modified before the time)"
            name={"sync_before"}>
            <DatePicker showTime/>
        </Form.Item>
        <Form.Item
            label="Modified After (If set, only synchronize files modified after the time)"
            name={"sync_after"}>
            <DatePicker showTime/>
        </Form.Item>
        <Form.Item label="Enable Upload (If checked, the tool is allowed to upload new files to Lyve Cloud Bucket)"
                   valuePropName="checked" name={"enable_upload"}>
            <Switch/>
        </Form.Item>
        <Form.Item
            label="Enable Delete (If checked, the tool is allowed to delete files that are not existing in the source bucket)"
            valuePropName="checked" name={"enable_delete"}>
            <Switch/>
        </Form.Item>
        <Form.Item
            label="Enable Update (If checked, the tool is allowed to override Lyve bucket files based on the updated file from the source bucket)"
            valuePropName="checked" name={"enable_update"}>
            <Switch/>
        </Form.Item>
    </Form>;
}

export default SyncConfigForm;