import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";
import store from "./store";

// Add Axios Library
import axios from "axios";

import wsService from "./services/wsservice";

// Default Django Local Development
//axios.defaults.baseURL = "http://127.0.0.1:8000";
// axios.defaults.baseURL = "http://128.199.125.233:8000";
const API_URL = process.env.VUE_APP_WEB_API ? process.env.VUE_APP_WEB_API : "http://127.0.0.1:8080"
const API_WS = process.env.VUE_APP_WEB_WS ? process.env.VUE_APP_WEB_WS : "ws://127.0.0.1:8080/ws/"
axios.defaults.baseURL = API_URL;

createApp(App)
  .use(store)
  .use(router, axios)
  .use(
    wsService,
    {
      store,
      //url: "ws://128.199.125.233:8000/ws/",
      url: API_WS,
    })
  .mount("#app");
