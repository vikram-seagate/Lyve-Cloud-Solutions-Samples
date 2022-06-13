import {Button, Form, Input, Select} from "antd";
import {formLayout, formTailLayout} from "./forms";
import ALIBABA_CLOUD_REGIONS from "../contents/Migration/AlibabaMigration/AlibabaRegions";

function AlibabaCredentialForm({form, onSubmit}) {
    return <Form {...formLayout}
                 form={form}
                 name="control-hooks"
                 onFinish={onSubmit}
                 initialValues={{}}>

        <Form.Item name="region" label="Region" rules={[{required: true}]}>
            <Select
                placeholder="Select the region of the Object Storage Service to connect"
                allowClear>
                {ALIBABA_CLOUD_REGIONS.map(regionItem =>
                    <Select.Option key={regionItem.id}
                                   value={regionItem.id}>{regionItem.region} ({regionItem.id})</Select.Option>)}
            </Select>
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

export default AlibabaCredentialForm;