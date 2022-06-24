<template>
  <div class="landing-login">
    <div class="hero is-info">
      <div class="hero-body has-text-centered">
        <h1 class="title">Login</h1>
      </div>
    </div>
    <!-- End of Hero -->
    <section class="section">
      <div class="container">
        <div class="column is-6 is-offset-3">
          <form v-on:submit.prevent="submitForm">
            <div class="field">
              <label>Email</label>
              <div class="control">
                <input type="email" class="input" v-model="v$.username.$model"/>
              </div>
							<template v-if="v$.username.$errors.length">
								<p
									class="help is-danger"
									v-for="error of v$.username.$errors"
									:key="error.$uid"
								>
									{{ error.$message }}
								</p>
              </template>

            </div>
            <!-- End of Email Field -->
            <div class="field">
              <label>Password</label>
              <div class="control">
                <input type="password" class="input" v-model="v$.password.$model"/>
              </div>
							<template v-if="v$.password.$errors.length">
								<p
									class="help is-danger"
									v-for="error of v$.password.$errors"
									:key="error.$uid"
								>
									{{ error.$message }}
								</p>
              </template>
            </div>
            <!-- End of Password Field -->
            <div class="field">
              <div class="control">
                <button class="button is-dark">Login</button>
              </div>
            </div>
            <!-- End of Sign Up Button -->
            <hr />

            Or <router-link to="/sign-up">Sign Up</router-link>
          </form>
        </div>
      </div>
      <!-- End of Container -->
    </section>
  </div>
</template>
<script>
import axios from "axios";
import useVuelidate from "@vuelidate/core";
import { required, email, sameAs, minLength } from "@vuelidate/validators";
export default {
  setup() {
    return {
      v$: useVuelidate({ $lazy: true, $autoDirty: true }),
    };
  },
  data() {
    return {
      username: "",
      password: "",
    };
  },
  methods: {
    async submitForm() {
      const isFormCorrect = await this.v$.$validate();
      if (!isFormCorrect) return;
      // Login with Django
      const loginData = {
         username: this.username,
         password: this.password,
      };
      try {
        const loginResp = await axios.post("/api/v1/token/login", loginData);
        const token = loginResp.data.auth_token;
        // Save authorized token
        this.$store.commit("setToken", token);
        axios.defaults.headers.common["Authorization"] = `Token ${token}`;
        localStorage.setItem("token", token);
        this.$router.push("/dashboard/profile");
        this.$wsConnect(token);
      } catch (error) {
        if (error) {
          console.error(error);
        }
      }
    },
  },
  validations() {
    return {
      username: { required, email },
      password: { required },
    };
  },
}
</script>
