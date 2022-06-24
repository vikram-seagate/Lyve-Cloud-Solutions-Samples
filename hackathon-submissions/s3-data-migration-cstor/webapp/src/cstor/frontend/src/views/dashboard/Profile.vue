<template>
  <div class="dashboard-profile">
    <div class="hero is-info">
      <div class="hero-body has-text-centered">
        <h1 class="title">Profile</h1>
      </div>
    </div>
    <!-- End of Hero -->
    <section class="section">
      <button @click="logout()" class="button is-danger">Log out</button>
    </section>
  </div>
</template>
<script>
import axios from "axios";

export default {
  methods: {
    logout() {
      this.$store.commit("removeToken");
      axios.defaults.headers.common["Authorization"] = "";
      localStorage.removeItem("token");
      this.$router.push("/");
    },
  },
};
</script>
