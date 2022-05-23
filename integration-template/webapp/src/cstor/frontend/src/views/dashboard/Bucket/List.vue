<template>
  <div class="dashboard-profile">
    <div class="hero is-info">
      <div class="hero-body has-text-centered">
        <h1 class="title">Buckets</h1>
      </div>
    </div>
    <!-- End of Hero -->
    <section class="section">
      <div class="container">
        <router-link to="/dashboard/buckets/create">
          <button class="button is-dark">Create</button>
        </router-link>
        <div class="card-wrapper">
          <div
            class="card"
            v-for="bucket in api_data"
            :key="bucket.id"
          >
            <div class="card-content">
              <p class="subtitle is-6">{{ bucket.cloud_provider.name }}</p>
              <p class="title is-4">{{ bucket.name }}</p>
              <p class="title is-6">{{ bucket.cloud_region }}</p>
              <router-link :to="{ 'name': 'db-buckets-detail', params: { id: bucket.id }}">
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
      api_data: [],
    };
  },
  async mounted() {
    try {
      const apiResp = await axios.get("/api/v1/cloud/buckets/");
      this.api_data = apiResp.data;
    } catch (error) {
      if (error) {
        console.error(error);
      }
    }
  },
};
</script>
