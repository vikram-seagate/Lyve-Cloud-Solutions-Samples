import {Descriptions, Drawer, Empty, List} from "antd";
import moment from "moment";

function GoogleSyncTaskDetailDrawer({taskToView, setTaskToView}) {
    let drawerBody = <Empty description={"No task to view"}></Empty>;

    if (taskToView) {
        const {
            source_project_id,
            source_bucket,
            destination_region,
            destination_bucket,
            status,
            enable_upload,
            enable_update,
            enable_delete
        } = taskToView;

        drawerBody = <div>
            <Descriptions title={"Synchronization Task Details"} bordered>
                <Descriptions.Item label={"Project ID"}>{source_project_id}</Descriptions.Item>
                <Descriptions.Item label={"Source Container"} span={2}>{source_bucket}</Descriptions.Item>
                <Descriptions.Item label={"Lyve Cloud Region"}>{destination_region}</Descriptions.Item>
                <Descriptions.Item label={"Destination Bucket"} span={2}>{destination_bucket}</Descriptions.Item>
                <Descriptions.Item label={"Enable Upload"}>{enable_upload ? "✔" : "-"}</Descriptions.Item>
                <Descriptions.Item label={"Enable Update"}>{enable_update ? "✔" : "-"}</Descriptions.Item>
                <Descriptions.Item label={"Enable Delete"}>{enable_delete ? "✔" : "-"}</Descriptions.Item>
                <Descriptions.Item label={"status"}>{status}</Descriptions.Item>
            </Descriptions>

            <div className="ant-descriptions-title" style={{margin: "20px 0"}}>Logs</div>

            <List
                bordered
                dataSource={taskToView.logs}
                pagination={{
                    showSizeChanger: false,
                    pageSize: 10,
                }}
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

export default GoogleSyncTaskDetailDrawer;