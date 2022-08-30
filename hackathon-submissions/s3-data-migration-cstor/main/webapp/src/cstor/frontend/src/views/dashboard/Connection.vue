<template>
  <div class="dashboard-profile">
    <div class="hero is-info">
      <div class="hero-body has-text-centered">
        <h1 class="title">Connection</h1>
      </div>
    </div>
    <!-- End of Hero -->
    <section class="section">
      <div class="container">
        <router-link to="/dashboard/connection/create">
          <button class="button is-dark">Create</button>
        </router-link>
        <div class="card-wrapper">
          <div
            class="card"
            v-for="conn in connections"
            :key="conn.id"
          >
            <div class="card-content">
              <p class="subtitle is-6">{{ conn.cloud_name }}</p>
              <p class="title is-4">{{ conn.name }}</p>
              <router-link :to="{ 'name': 'dashboard-conn-detail', params: { id: conn.id }}">
                <button class="button is-dark is-small">Edit</button>
              </router-link>
            </div>
          </div>
          <!-- End of Card -->
        </div>
      </div>
    </section>
    <!-- End of Section -->
  </div>
</template>
<script>
import axios from "axios";

export default {
  data() {
    return {
      connections: [],
    };
  },
  async mounted() {
    try {
      const connResp = await axios.get("/api/v1/cloud/connections/");
      this.connections = connResp.data;
    } catch (error) {
      if (error) {
        console.error(error);
      }
    }
  },
};
</script>
