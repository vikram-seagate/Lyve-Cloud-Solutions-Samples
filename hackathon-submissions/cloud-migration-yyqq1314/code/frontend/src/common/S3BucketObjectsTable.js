import {Form, Input, Table, DatePicker, InputNumber} from "antd";
import prettyBytes from "pretty-bytes";
import moment from "moment";
import {useState} from "react";

function filterObjects(filter, bucketObjects) {
    return bucketObjects.filter(object => {
        if (filter.name !== null && filter.name !== undefined && filter.name.length > 0) {
            if (!object.key.toLowerCase().toLowerCase().includes(filter.name.toLowerCase())) {
                return false;
            }
        }

        if (filter.size_min !== null && filter.size_min !== undefined && filter.size_min > 0) {
            if (object.Size < filter.size_min) {
                return false;
            }
        }

        if (filter.size_max !== null && filter.size_max !== undefined) {
            if (object.Size > filter.size_max) {
                return false;
            }
        }

        if (filter.time_before !== null && filter.time_before !== undefined) {
            if (filter.time_before.isBefore(object.LastModified)) {
                return false;
            }
        }

        if (filter.time_after !== null && filter.time_after !== undefined) {
            if (filter.time_after.isAfter(object.LastModified)) {
                return false;
            }
        }

        return true;
    });
}

function S3BucketObjectsTable({bucketObjects, selectedObjects, setSelectedObjects, bucketObjectLoading}) {
    const [filterForm] = Form.useForm();
    const [filters, setFilters] = useState({});

    const onFilterValueChange = () => {
        console.log(filterForm.getFieldsValue());
        setFilters(filterForm.getFieldsValue());
    };

    const columns = [{
        title: "Name",
        dataIndex: "name",
        // ...getColumnSearchProps("name"),
        sorter: (a, b) => a.name.localeCompare(b.name),
    }, {
        title: "Size", dataIndex: "Size", render: size => prettyBytes(size), sorter: (a, b) => a.Size - b.Size,
    }, {
        title: "Last Modified",
        dataIndex: "LastModified",
        sorter: (a, b) => Date.parse(a.LastModified) - Date.parse(b.LastModified),
        render: utcString => moment(utcString).calendar()
    }];

    const rowSelection = {
        onChange: (selectedRowKeys, selectedRows) => {
            console.log(`selectedRowKeys: ${selectedRowKeys}`, "selectedRows: ", selectedRows);
            setSelectedObjects(selectedRows);
        }, selectedRowKeys: selectedObjects.map(obj => obj.key),
    };

    return <div>
        <div style={{display: "flex", justifyContent: "space-between"}}>
            <div style={{display: "flex", alignItems: "center"}}>
                <h1>Object Table</h1>
            </div>
            <p>{selectedObjects.length} objects selected, in
                total {prettyBytes(selectedObjects.reduce((sum, object) => sum + object.Size, 0))}.</p>
        </div>
        <div style={{marginBottom: "1rem"}}>
            <Form
                layout={"inline"}
                form={filterForm}
                initialValues={{name: "", size_max: null, modify_range: null}}
                onValuesChange={onFilterValueChange}>
                <Form.Item label="Name contains" name={"name"}>
                    <Input placeholder=""/>
                </Form.Item>
                <Form.Item label="Size >= (Bytes)" style={{marginRight: 0}}>
                    <Form.Item
                        name="size_min">
                        <InputNumber min={0}/>
                    </Form.Item>
                </Form.Item>
                <Form.Item label="Size <= (Bytes)">
                    <Form.Item
                        name="size_max">
                        <InputNumber min={0}/>
                    </Form.Item>
                </Form.Item>
                <Form.Item name="time_before" label="Before Time:">
                    <DatePicker showTime/>
                </Form.Item>
                <Form.Item name="time_after" label="After Time:">
                    <DatePicker showTime/>
                </Form.Item>
            </Form>
        </div>
        <Table size={"small"}
               pagination={{position: ["bottomLeft"], defaultPageSize: 100}}
               loading={bucketObjectLoading}
               columns={columns}
               dataSource={filterObjects(filters, bucketObjects)}
               rowSelection={rowSelection}/>
    </div>;
}

export default S3BucketObjectsTable;