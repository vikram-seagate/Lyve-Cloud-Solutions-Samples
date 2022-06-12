import {Button, Input, Space} from "antd";
import {SearchOutlined} from "@ant-design/icons";
import moment from "moment";

export function getColumnSearchProps(dataIndex) {
    return ({
        filterDropdown: ({setSelectedKeys, selectedKeys, confirm, clearFilters}) => (
            <div style={{padding: 8}}>
                <Input
                    autoFocus
                    placeholder={`Search ${dataIndex}`}
                    value={selectedKeys[0]}
                    onChange={e => setSelectedKeys(e.target.value ? [e.target.value] : [])}
                    onPressEnter={confirm}
                    style={{width: 188, marginBottom: 8, display: "block"}}/>
                <Space>
                    <Button
                        type="primary"
                        onClick={confirm}
                        icon={<SearchOutlined/>}
                        size="small"
                        style={{width: 90}}>
                        Search
                    </Button>
                    <Button onClick={clearFilters} size="small" style={{width: 90}}>
                        Reset
                    </Button>
                    <Button
                        type="link"
                        size="small"
                        onClick={() => {
                            confirm({closeDropdown: false});
                        }}>
                        Filter
                    </Button>
                </Space>
            </div>
        ),
        filterIcon: filtered => <SearchOutlined style={{color: filtered ? "#1890ff" : undefined}}/>,
        onFilter: (value, record) =>
            record[dataIndex]
                ? record[dataIndex].toString().toLowerCase().includes(value.toLowerCase())
                : ""
    });
}

export function checkPossibleDisconnectedTask(task) {
    if (task.status !== "IN_PROGRESS") {
        return false;
    }

    return moment().subtract(1, "hours").isAfter(task.updated_at);
}