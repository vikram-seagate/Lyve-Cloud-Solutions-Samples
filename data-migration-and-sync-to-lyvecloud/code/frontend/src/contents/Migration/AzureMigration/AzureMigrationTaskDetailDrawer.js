import {Descriptions, Drawer, Empty, List} from "antd";
import moment from "moment";

function AzureMigrationTaskDetailDrawer({taskToView, setTaskToView}) {
    let drawerBody = <Empty description={"No task to view"}></Empty>;

    if (taskToView) {
        const {
            source_container,
            source_obj_key,
            destination_region,
            destination_bucket,
            destination_key,
            status,
            size,
            bytes_migrated
        } = taskToView;

        drawerBody = <div>
            <Descriptions title={"Migration Task Details"} bordered>
                <Descriptions.Item label={"Source Container"}>{source_container}</Descriptions.Item>
                <Descriptions.Item label={"Source Object Key"} span={2}>{source_obj_key}</Descriptions.Item>
                <Descriptions.Item label={"Lyve Cloud Region"}>{destination_region}</Descriptions.Item>
                <Descriptions.Item label={"Destination Bucket"} span={2}>{destination_bucket}</Descriptions.Item>
                <Descriptions.Item label={"Destination Folder"} span={3}>{destination_key}</Descriptions.Item>
                <Descriptions.Item label={"status"}>{status}</Descriptions.Item>
                <Descriptions.Item label={"size"}>{size}</Descriptions.Item>
                <Descriptions.Item label={"bytes_migrated"}>{bytes_migrated}</Descriptions.Item>
            </Descriptions>

            <div className="ant-descriptions-title" style={{margin: "20px 0"}}>Logs</div>

            <List
                bordered
                pagination={{
                    showSizeChanger: false,
                    pageSize: 10,
                }}
                dataSource={taskToView.logs}
                renderItem={log => {
                    if (log.type === "auto" || log.severity === "info") {
                        const content = JSON.parse(log.content);
                        return <List.Item>
                            <List.Item.Meta
                                title={`${moment(log.created_at).calendar()} - Database Log`}
                                description={
                                    <ul>
                                        {Object.entries(content).map(([field, values]) => {
                                            if (field === "partition") {
                                                return <li key={field}>{field}: {values}</li>;
                                            }
                                            return <li key={field}><strong>{field}</strong>: {values[0]}=>{values[1]}
                                            </li>;
                                        })}
                                    </ul>
                                }
                            />
                        </List.Item>;
                    }
                    return <List.Item>
                        <List.Item.Meta
                            title={`${moment(log.created_at).calendar()} - Worker Log - Severity: ${log.severity}`}
                            description={log.content}
                        />
                        {log.trace}
                    </List.Item>;
                }}
            />
        </div>;
    }

    return <Drawer title="Task Detail Panel" placement="right" onClose={() => setTaskToView(null)} visible={taskToView}
                   width={800}>
        {drawerBody}
    </Drawer>;
}

export default AzureMigrationTaskDetailDrawer;