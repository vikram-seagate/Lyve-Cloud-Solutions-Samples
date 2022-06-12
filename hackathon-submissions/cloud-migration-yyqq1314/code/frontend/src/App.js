import "./App.css";
import {Layout, Menu} from "antd";
import {
    CloudDownloadOutlined,
    CloudServerOutlined,
    CoffeeOutlined,
    FieldTimeOutlined,
    RetweetOutlined,
} from "@ant-design/icons";
import Introduction from "./contents/Introduction";
import {useState} from "react";
import GeneralS3Migration from "./contents/Migration/GeneralS3Migration/GeneralS3Migration";
import GeneralS3Synchronization from "./contents/Synchronization/GeneralS3Sync/GeneralS3Synchronization";
import AlibabaMigration from "./contents/Migration/AlibabaMigration/AlibabaMigration";
import AzureMigration from "./contents/Migration/AzureMigration/AzureMigration";
import GoogleMigration from "./contents/Migration/GoogleMigration/GoogleMigration";
import AlibabaSynchronization from "./contents/Synchronization/AlibabaSync/AlibabaSynchronization";
import AzureSynchronization from "./contents/Synchronization/AzureSync/AzureSynchronization";
import GoogleSynchronization from "./contents/Synchronization/GoogleSync/GoogleSynchronization";

const {Header, Footer, Sider, Content} = Layout;

const styles = {
    title: {
        color: "white", textAlign: "center"
    }
};

function App() {
    const [menuKey, setMenuKey] = useState("Intro");

    const menuItems = [
        {label: "Introduction", key: "Intro", icon: <CoffeeOutlined/>},
        {
            label: "Migration",
            key: "migration-sources",
            icon: <CloudServerOutlined/>,
            children: [
                {
                    label: "General S3",
                    key: "General S3 Migration",
                    icon: <CloudDownloadOutlined/>
                },
                {
                    label: "Alibaba",
                    key: "Alibaba",
                    icon: <CloudDownloadOutlined/>
                },
                {label: "Azure", key: "Azure", icon: <CloudDownloadOutlined/>},
                {label: "Google", key: "Google", icon: <CloudDownloadOutlined/>}
            ],
        },
        {
            label: "Bucket Sync",
            icon: <FieldTimeOutlined/>,
            key: "synchronization-sources",
            children: [
                {
                    label: "General S3",
                    key: "General S3 Sync",
                    icon: <RetweetOutlined/>
                },
                {
                    label: "Alibaba",
                    key: "Alibaba Sync",
                    icon: <RetweetOutlined/>
                },
                {
                    label: "Azure",
                    key: "Azure Sync",
                    icon: <RetweetOutlined/>
                },
                {
                    label: "Google",
                    key: "Google Sync",
                    icon: <RetweetOutlined/>
                }
            ]
        }
    ];

    return <Layout>
        <Header>
            <h1 style={styles.title}>
                Lyve Hackathon - CloudMigration
            </h1>
        </Header>
        <Layout>
            <Sider>
                <Menu
                    defaultSelectedKeys={[menuKey]}
                    selectedKeys={[menuKey]}
                    defaultOpenKeys={["migration-sources", "synchronization-sources"]}
                    onClick={({key}) => setMenuKey(key)}
                    mode="inline"
                    items={menuItems}
                    theme="dark">
                </Menu>
            </Sider>
            <Content>
                {menuKey === "Intro" && <Introduction/>}
                {menuKey === "General S3 Migration" && <GeneralS3Migration/>}
                {menuKey === "General S3 Sync" && <GeneralS3Synchronization/>}
                {menuKey === "Alibaba Sync" && <AlibabaSynchronization/>}
                {menuKey === "Azure Sync" && <AzureSynchronization/>}
                {menuKey === "Google Sync" && <GoogleSynchronization/>}
                {menuKey === "Alibaba" && <AlibabaMigration/>}
                {menuKey === "Azure" && <AzureMigration/>}
                {menuKey === "Google" && <GoogleMigration/>}
            </Content>
        </Layout>
        <Footer>
            <div style={{textAlign: "center"}}>
                Team - YYQQ1314 @ yun005 [at] e [dot] ntu [dot] edu [dot] sg
            </div>
        </Footer>
    </Layout>;
}

export default App;
