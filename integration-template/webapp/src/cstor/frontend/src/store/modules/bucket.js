// Initial State
import axios from "axios";

const state = () => ({
  candidates: [], // List of buckets returned by list_buckets
  req_bucket_list_status: "waiting", // one of waiting, pending, success, failed
  connections: [] // List of connections 
});

// getters

const getters = {
  candidateList: (state) => state.candidates,
  reqBucketListStatus: (state) => state.req_bucket_list_status,
  connList: (state) => state.connections,
};

// mutations

const mutations = {
  setReqBucketListStatus(state, { req_status }) {
    state.req_bucket_list_status = req_status;
  },
  setCandidateList(state, { data }) {
    state.candidates = data.Buckets;
  },
  setConnList(state, { data }) {
    state.connections = data;
  },
};

// actions

const actions = {
  async getConnections ({ commit }) {
    try {
      const apiResp = await axios.get("/api/v1/cloud/connections/");
      console.log(apiResp);
      // const apiData = apiResp.data;
      commit("setConnList", { data: apiResp.data });
    
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
