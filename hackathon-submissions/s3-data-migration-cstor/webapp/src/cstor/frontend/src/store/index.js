import { createStore } from "vuex";
import bucket from "./modules/bucket";
import migration from "./modules/migration";

export default createStore({
  state: {
    // Signed-in user information
    user: {
      token: "",
      isAuthenticated: false,
    },
  },
  getters: {},
  mutations: {
    initStore(state) {
      if (localStorage.getItem("token")) {
        state.user.token = localStorage.getItem("token");
        state.user.isAuthenticated = true;
      } else {
        state.user.token = "";
        state.user.isAuthenticated = false;
      }
    },
    setToken(state, token) {
      state.user.token = token;
      state.user.isAuthenticated = true;
    },
    removeToken(state) {
      state.user.token = "";
      state.user.isAuthenticated = false;
    },
  },
  actions: {},
  modules: {
    bucket,
    migration,
  },
});
