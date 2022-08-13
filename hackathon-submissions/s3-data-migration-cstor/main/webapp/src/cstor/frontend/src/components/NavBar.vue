<template>
  <nav class="navbar is-info" role="navigation" aria-label="main navigation" style="min-height: 5rem;">
    <div class="navbar-brand">
      <a class="navbar-item is-size-4" href="/">cstor</a>
    </div>
    <div id="navbar-item" class="navbar-menu">
      <div class="navbar-start">
        <template v-if="isLoggedIn === false">
          <a class="navbar-item">Home</a>
          <a class="navbar-item">About</a>
        </template>
        <template v-else="">
          <a class="navbar-item" href="/dashboard/migrations">
            Migrations
          </a>
          <a class="navbar-item" href="/dashboard/buckets">
            Bucket
          </a>
          <a class="navbar-item" href="/dashboard/connection">
            Connection
          </a>
        </template>
      </div>
      <div class="navbar-end">
        <div class="navbar-item" v-if="isLoggedIn === false">
          <div class="buttons">
            <a class="button is-primary" href="/sign-up"><strong>Sign Up</strong></a>
            <a class="button is-light" href="/login"><strong>Login</strong></a>
          </div>
        </div>
        <div class="navbar-item" v-else="">
          <div class="buttons">
            <a class="button is-primary" href="/dashboard/profile"><strong>Profile</strong></a>
          </div>
        </div>
      </div>
    </div>
  </nav>
</template>

<script>
import axios from "axios";
import NavBar from "@/components/NavBar";
import Footer from "@/components/Footer";

export default {
  data() {
    return {
      isLoggedIn: false,
    };
  },
  async mounted() {
    this.$store.commit("initStore");
    const token = this.$store.state.user.token;

    if (token) {
      this.isLoggedIn = true;
    }
  },
};
</script>
