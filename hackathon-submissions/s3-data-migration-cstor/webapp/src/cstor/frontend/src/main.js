import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";
import store from "./store";

// Add Axios Library
import axios from "axios";

import wsService from "./services/wsservice";

// Default Django Local Development
//axios.defaults.baseURL = "http://127.0.0.1:8000";
axios.defaults.baseURL = "http://128.199.125.233:8000";

createApp(App)
  .use(store)
  .use(router, axios)
  .use(
    wsService,
    {
      store,
      url: "ws://128.199.125.233:8000/ws/",
    })
  .mount("#app");
