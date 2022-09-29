import {formLayout, formTailLayout} from "./forms";
import {Button, Form, Input, Select} from "antd";
import LyveCloudRegions from "./LyveCloudRegions";

const {Option} = Select;

function LyveCredentialForm({form, onSubmit}) {
    return <Form {...formLayout}
                 form={form}
                 name="control-hooks"
                 onFinish={onSubmit}
                 initialValues={{}}>

        <Form.Item name="region" label="Region" rules={[{required: true}]}>
            <Select
                placeholder="Select the region of the Object Storage Service to connect"
                allowClear>
                {LyveCloudRegions.map(regionItem => <Option key={regionItem.id}
                                                            value={regionItem.id}>{regionItem.region} ({regionItem.id})</Option>)}
            </Select>
        </Form.Item>

        <Form.Item name="accessKeyId" label="Key ID">
            {/*<Input/>*/}
            <Input type={"password"}/>
        </Form.Item>

        <Form.Item name="accessKeySecret" label="Key Secret">
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

export default LyveCredentialForm;