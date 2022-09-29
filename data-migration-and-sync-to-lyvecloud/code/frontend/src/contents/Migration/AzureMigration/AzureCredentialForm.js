import {Button, Form, Input} from "antd";
import {formLayout, formTailLayout} from "../../../common/forms";

function AzureCredentialForm({form, onSubmit}) {
    return <Form {...formLayout}
                 form={form}
                 name="control-hooks"
                 onFinish={onSubmit}
                 initialValues={{}}>

        <Form.Item name="connection_string" label="Connection String" rules={[{required: true}]}>
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

export default AzureCredentialForm;