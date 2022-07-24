import {Empty, Spin, Tree} from "antd";
import {useState} from "react";
import {DownOutlined, FolderOutlined} from "@ant-design/icons";

function findChildren(folderObjects, parentObject) {
    // no children for non-folder objects
    if (!parentObject.name.endsWith("/")) {
        // console.log(`${parentObject.name} not ending with /. returning []`);
        return [];
    }

    return folderObjects.filter(object => {
        if (object.name === parentObject.name) {
            return false;
        }
        if (!object.name.startsWith(parentObject.name)) {
            return false;
        }
        const childrenNameRemaining = object.name.replace(parentObject.name, "");
        // console.log(`children name remaining: ${childrenNameRemaining}`);
        const split = childrenNameRemaining.split("/");
        if (childrenNameRemaining.endsWith("/") && split.length === 2 && split[1].length === 0) {
            // console.log(`found child folder: ${childrenNameRemaining}`);
            return true;
        }
        if (!childrenNameRemaining.includes("/")) {
            // console.log(`found child item: ${childrenNameRemaining}`);
            return true;
        }
        return false;
    }).map(object => {
        return {
            ...object,
            key: object.name,
            title: object.name.replace(parentObject.name, ""),
            icon: <FolderOutlined />,
            children: findChildren(folderObjects, object)
        };
    });
}

function formatTreeData(bucketObjects) {
    const folderObjects = bucketObjects.filter(object => object.name.endsWith("/"));

    const treeItems = folderObjects
        .filter(object => {
            const split = object.name.split("/");
            return (object.name.endsWith("/") && split.length === 2 && split[1].length === 0);
        }).map(object => {
            return {
                ...object, key: object.name, title: object.name,
                icon: <FolderOutlined />,
                children: findChildren(folderObjects, object)
            };
        });

    return [
        {
            key: "/", title: "/", children: treeItems, icon: <FolderOutlined />
        }
    ];
}

function DestinationFolderTree({
                                   currentBucket,
                                   bucketObjects,
                                   destinationFolder,
                                   setDestinationFolder,
                                   loading = false
                               }) {
    const [expandedKeys, setExpandedKeys] = useState([]);
    const [autoExpandParent, setAutoExpandParent] = useState(true);

    const onExpand = (expandedKeysValue) => {
        console.log("onExpand", expandedKeysValue);
        // if not set autoExpandParent to false, if children expanded, parent can not collapse.
        // or, you can remove all expanded children keys.

        setExpandedKeys(expandedKeysValue);
        setAutoExpandParent(false);
    };

    const onSelect = (destinationFolder, info) => {
        console.log("onSelect", info);
        console.log(destinationFolder);
        setDestinationFolder(destinationFolder);
    };

    if (!currentBucket || !bucketObjects) {
        return <Empty description={"No objects found"}/>;
    }

    if (loading) {
        return <div style={{width: "100%", textAlign: "center", marginTop: "5rem"}}>
            <Spin tip={"Loading objects ..."}/>
        </div>;
    }

    return <Tree
        showIcon
        switcherIcon={<DownOutlined />}
        onExpand={onExpand}
        expandedKeys={expandedKeys}
        autoExpandParent={autoExpandParent}
        onSelect={onSelect}
        selectedKeys={destinationFolder}
        treeData={formatTreeData(bucketObjects)}
    />;
}

export default DestinationFolderTree;