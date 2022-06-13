import {Button, Form, Input} from "antd";
import {formLayout, formTailLayout} from "../../../common/forms";

function GeneralS3CredentialForm({form, onSubmit}) {
    return <Form {...formLayout}
                 form={form}
                 name="control-hooks"
                 onFinish={onSubmit}
                 initialValues={{}}>
        <Form.Item name="endpoint" label="EndPoint" rules={[{required: true}]}>
            <Input/>
        </Form.Item>

        <Form.Item name="accessKeyId" label="Key ID" rules={[{required: true}]}>
            <Input type={"password"}/>
            {/*<Input/>*/}
        </Form.Item>

        <Form.Item name="accessKeySecret" label="Key Secret" rules={[{required: true}]}>
            <Input type={"password"}/>
            {/*<Input/>*/}
        </Form.Item>

        <Form.Item {...formTailLayout}>
            <Button type="primary" htmlType="submit">
                Submit
            </Button>
        </Form.Item>
    </Form>;
}

export default GeneralS3CredentialForm;