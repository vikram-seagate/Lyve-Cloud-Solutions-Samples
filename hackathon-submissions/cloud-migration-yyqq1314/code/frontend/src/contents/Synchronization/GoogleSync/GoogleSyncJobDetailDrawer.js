import {Descriptions, Drawer, Empty, List} from "antd";
import moment from "moment";

function GoogleSyncJobDetailDrawer({jobToView, setJobToView}) {

    let drawerBody = <Empty description={"No job to view"}></Empty>;

    if (jobToView) {

        const {
            source_project_id,
            source_bucket,
            source_obj_key,
            destination_region,
            destination_bucket,
            status,
            size,
            bytes_migrated
        } = jobToView;

        drawerBody = <div>
            <Descriptions title={"Synchronization Job Details"} bordered>
                <Descriptions.Item label={"Source Project ID"}>{source_project_id}</Descriptions.Item>
                <Descriptions.Item label={"Source Bucket"} span={2}>{source_bucket}</Descriptions.Item>
                <Descriptions.Item label={"Lyve Cloud Region"}>{destination_region}</Descriptions.Item>
                <Descriptions.Item label={"Destination Bucket"} span={2}>{destination_bucket}</Descriptions.Item>
                <Descriptions.Item label={"Source Object Key"} span={3}>{source_obj_key}</Descriptions.Item>
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
                dataSource={jobToView.logs}
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

    return <Drawer title="Job Detail Panel" placement="right" onClose={() => setJobToView(null)} visible={jobToView}
                   width={800}>
        {drawerBody}
    </Drawer>;
}

export default GoogleSyncJobDetailDrawer;