import {Table} from "antd";

const columns = [
    {
        title: "Name",
        dataIndex: "name",
    }
];

function BucketTable({buckets, selectBucket, disabled, selectedBuckets}) {
    return <Table
        size={"small"}
        style={{marginRight: "2rem"}}

        rowSelection={{
            type: "radio",
            onChange: (selectedRowKeys, selectedRows) => {
                selectBucket(selectedRows[0]);
            },
            getCheckboxProps: () => ({
                disabled
            }),
            selectedRowKeys: selectedBuckets.map(bucket => bucket.key)
        }}
        columns={columns}
        dataSource={buckets}
    />;
}

export default BucketTable;