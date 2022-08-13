// src/services/wsservice.js

export default {
  install: (app, options) => {
    // let ws = new WebSocket(options.url);
    let ws = null;
    let reconnInterval = options.reconnectInterval || 1000;
    const store = options.store;
    app.config.globalProperties.$wsConnect = (token) => {
      ws = new WebSocket(`${options.url}${token}/`);

      ws.onopen = () => {
        // Restart Reconn Interval
        reconnInterval = options.reconnectInterval || 1000;
      };

      ws.onmessage = (evt) => {
        // Message from WS Server
        console.log(evt.data);
        const mesg = JSON.parse(evt.data);
        if (mesg["mesg_type"] === "respListBuckets") {
          if (mesg["status"] == "success") {
            store.commit("bucket/setReqBucketListStatus", { req_status: "success" }); 
            store.commit("bucket/setCandidateList", { data: mesg["data"] });
          }
        }
        if (mesg["mesg_type"] === "migrationProgress") {
          if (mesg["status"] == "progress") {
            let migrationId = mesg["data"]["id"];
            let migrationData = mesg["data"]["progress"];
            // store.commit("bucket/setReqBucketListStatus", { req_status: "success" }); 
            // store.commit("bucket/setCandidateList", { data: mesg["data"] });
            store.commit("migration/patchMigrationDetail", { id: migrationId, data: migrationData });
          }
        }
      };

      ws.onclose = (evt) => {
        if (evt.code !== 1000) {
          // Attempt to reconnect
          let maxReconnInterval = options.maxReconnectInterval || 3000;
          setTimeout(() => {
            if (reconnInterval < maxReconnInterval) {
              reconnInterval += 1000;
            }
            app.config.globalProperties.$wsConnect(token);
          }, reconnInterval);
        }
      };
    };

    app.config.globalProperties.$wsDisconnect = () => {
      ws.close();
    };

    app.config.globalProperties.$wsSend = (data) => {
      ws.send(JSON.stringify(data));
    };
  },
};
