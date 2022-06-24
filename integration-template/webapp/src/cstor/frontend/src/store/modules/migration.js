// Initial State
import axios from "axios";

const state = () => ({
  buckets: [], // List of buckets
  migrations: [], // List of migrations
  migrationDetail: {}, // Migration Detail
});

// getters

const getters = {
  buckets: (state) => state.buckets,
  migrations: (state) => state.migrations,
  migrationDetail: (state) => (id) => {
    if (state.migrationDetail.hasOwnProperty(id)) {
      return state.migrationDetail[id];
    }
    return {
      name: "",
      src_bucket: {
        name: "",
      },
      dest_bucket: {
        name: "",
      },
      status: 2,
      total_count: "0",
      total_size: "0",
      success_count: "0",
      success_size: "0",
      fail_count: "0",
      fail_size: "0",
      progress_count: "0",
      progress_size: "0",
    };
  }
};

// mutations

const mutations = {
  setBuckets(state, { data }) {
    state.buckets = data;
  },
  setMigrations(state, { data }) {
    state.migrations = data;
  },

  updateMigrationDetail(state, { id, data }) {
    state.migrationDetail = {
       ...state.migrationDetail,
       [id]: data,
    };
  },
  patchMigrationDetail(state, { id, data }) {
    const curState = state.migrationDetail[id];
    if (typeof curState !== "undefined") {
      const newState = {
        ...curState,
        ...data,
      };
      state.migrationDetail = {
         ...state.migrationDetail,
         [id]: newState,
      };
    }
  },
};

// actions

const actions = {
  async getBucketList ({ commit }) {
    try {
      const apiResp = await axios.get("/api/v1/cloud/buckets/");
      console.log(apiResp);
      commit("setBuckets", { data: apiResp.data });
    
    } catch (error) {
      console.error(error);
    }
  },
  async getMigrationList ({ commit }) {
    try {
      const apiResp = await axios.get("/api/v1/cloud/migrations/");
      console.log(apiResp);
      commit("setMigrations", { data: apiResp.data });
    
    } catch (error) {
      console.error(error);
    }
  },
  async getMigrationDet({ commit }, { id }) {
    console.log("running getMigrationDet");
    try {
      const apiResp = await axios.get(`/api/v1/cloud/migrations/${id}/`);
      console.log(apiResp);
      commit("updateMigrationDetail", { id, data: apiResp.data });
    
    } catch (error) {
      console.error(error);
    }
  },
  async startMigration({ commit }, { id }) {
    try {
      const apiResp = await axios.patch(`/api/v1/cloud/migrations/${id}/`, {
        action: "migration_start",
      });
    } catch (error) {
      console.error(error);
    }
  },
  async pauseMigration({ commit }, { id }) {
    try {
      const apiResp = await axios.patch(`/api/v1/cloud/migrations/${id}/`, {
        action: "migration_pause",
      });
    } catch (error) {
      console.error(error);
    }
  },
};

export default {
  namespaced: true,
  state,
  actions,
  getters,
  mutations,
};
