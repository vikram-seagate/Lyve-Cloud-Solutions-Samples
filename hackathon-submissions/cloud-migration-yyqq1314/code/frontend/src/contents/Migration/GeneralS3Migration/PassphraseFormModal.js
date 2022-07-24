import React, {useState} from "react";
import {Button, Modal, Form, Input} from "antd";

const PassphraseModal = ({visible, onConfirm, onCancel}) => {
    const [form] = Form.useForm();
    return <Modal
        visible={visible}
        title="Enter passphrase to protect your credentials"
        okText="Submit"
        cancelText="Cancel"
        onCancel={onCancel}
        onOk={() => {
            form
                .validateFields()
                .then(({passphrase}) => {
                    form.resetFields();
                    onConfirm(passphrase);
                })
                .catch((info) => {
                    console.log("Validate Failed:", info);
                });
        }}>
        <p>Use this passphrase when you set up every migration worker.</p>
        <Form
            form={form}
            layout="horizontal"
            name="passphrase-form"
            initialValues={{
                passphrase: "123",
            }}>
            <Form.Item
                name="passphrase"
                label="Passphrase"
                rules={[{
                    required: true, message: "Passphrase is required!",
                },]}>
                <Input/>
                {/*<Input type={"password"}/>*/}
            </Form.Item>
        </Form>
    </Modal>;
};

const PassphraseFormModal = ({disabled, onSubmit, buttonText = "Create Migration Tasks"}) => {
    const [visible, setVisible] = useState(false);

    const onConfirm = (passphrase) => {
        onSubmit(passphrase);
        setVisible(false);
    };

    return <div>
        <Button
            type="primary"
            disabled={disabled}
            onClick={() => {
                setVisible(true);
            }}>
            {buttonText}
        </Button>
        <PassphraseModal
            visible={visible}
            onConfirm={onConfirm}
            onCancel={() => {
                setVisible(false);
            }}
        />
    </div>;
};

export default PassphraseFormModal;