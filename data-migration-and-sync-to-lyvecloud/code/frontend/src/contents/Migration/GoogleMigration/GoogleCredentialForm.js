import {Button, Form, Input, Upload} from "antd";
import {formLayout, formTailLayout} from "../../../common/forms";
import {UploadOutlined} from "@ant-design/icons";

const normFile = (e) => {
    if (Array.isArray(e)) {
        return e;
    }
    return e && e.fileList;
};

function GoogleCredentialForm({form, onSubmit}) {
    const beforeUpload = (file, fileList) => {
        console.log(file, fileList);
        const reader = new FileReader();

        reader.onload = (e) => {
            const {project_id, private_key, client_email} = JSON.parse(e.target.result);
            form.setFieldsValue({
                projectId: project_id,
                credentials: {
                    private_key,
                    client_email
                }
            });
        };
        reader.readAsText(file);
        return false;
    };

    return <Form {...formLayout}
                 form={form}
                 name="control-hooks"
                 onFinish={onSubmit}
                 initialValues={{}}>

        <Form.Item
            name="key_file"
            label="Upload"
            valuePropName="fileList"
            getValueFromEvent={normFile}>
            <Upload name="key_file_upload" beforeUpload={beforeUpload} maxCount={1}
                    accept={".json,application/json,application/JSON"}>
                <Button icon={<UploadOutlined/>}>Click to select the KeyFile</Button>
            </Upload>
        </Form.Item>

        <Form.Item name="projectId" label="Project ID" rules={[{required: true}]}>
            <Input/>
        </Form.Item>

        <Form.Item name={["credentials", "client_email"]} label="Client Email" rules={[{required: true}]}>
            {/*<Input/>*/}
            <Input type={"password"}/>
        </Form.Item>

        <Form.Item name={["credentials", "private_key"]} label="Private Key" rules={[{required: true}]}>
            {/*<Input/>*/}
            <Input type={"password"}/>
        </Form.Item>

        <Form.Item {...formTailLayout}>
            <Button type="primary" htmlType="submit">
                Submit
            </Button>
        </Form.Item>
    </Form>;
}

export default GoogleCredentialForm;