<template>
  <div class="landing-login">
    <div class="hero is-info">
      <div class="hero-body has-text-centered">
        <h1 class="title">Create Connection</h1>
      </div>
    </div>
    <!-- End of Hero -->
    <section class="section">
      <div class="container">
        <div class="column is-6 is-offset-3">
          <form v-on:submit.prevent="submitForm">
            <div class="field">
              <label>Name</label>
              <div class="control">
                <input type="text" class="input" v-model="v$.name.$model"/>
              </div>
							<template v-if="v$.name.$errors.length">
								<p
									class="help is-danger"
									v-for="error of v$.name.$errors"
									:key="error.$uid"
								>
									{{ error.$message }}
								</p>
              </template>
            </div>
            <!-- End of Name Field -->
            <div class="field">
              <label>Description</label>
              <div class="control">
                <textarea class="textarea" v-model="v$.description.$model"/>
              </div>
            </div>
            <!-- End of Description Field -->
            <div class="field">
              <label>Cloud Provider</label>
              <div class="control">
                <div class="select">
                  <select v-model="v$.cloud_name.$model">
                    <option disabled value="">Select One</option>
                    <option value="AWS">AWS</option>
                    <option value="LYC">LyveCloud</option>
                  </select>
                </div>
              </div>
							<template v-if="v$.cloud_name.$errors.length">
								<p
									class="help is-danger"
									v-for="error of v$.cloud_name.$errors"
									:key="error.$uid"
								>
									{{ error.$message }}
								</p>
              </template>
            </div>
            <!-- End of Cloud Name Field -->
            <div class="field">
              <label>Cloud Access Key</label>
              <div class="control">
                <input type="text" class="input" v-model="v$.cloud_access_key.$model"/>
              </div>
							<template v-if="v$.cloud_access_key.$errors.length">
								<p
									class="help is-danger"
									v-for="error of v$.cloud_access_key.$errors"
									:key="error.$uid"
								>
									{{ error.$message }}
								</p>
              </template>
            </div>
            <!-- End of Cloud Access Key Field -->
            <div class="field">
              <label>Cloud Secret Key</label>
              <div class="control">
                <input type="password" class="input" v-model="v$.cloud_secret_key.$model"/>
              </div>
							<template v-if="v$.cloud_secret_key.$errors.length">
								<p
									class="help is-danger"
									v-for="error of v$.cloud_secret_key.$errors"
									:key="error.$uid"
								>
									{{ error.$message }}
								</p>
              </template>
            </div>
            <!-- End of Cloud Secret Key Field -->
            <div class="field">
              <label>Cloud Endpoint</label>
              <div class="control">
                <input type="text" class="input" v-model="v$.cloud_endpoint.$model"/>
              </div>
							<template v-if="v$.cloud_endpoint.$errors.length">
								<p
									class="help is-danger"
									v-for="error of v$.cloud_endpoint.$errors"
									:key="error.$uid"
								>
									{{ error.$message }}
								</p>
              </template>
            </div>
            <div class="field">
              <div class="control">
                <button class="button is-dark">Create</button>
              </div>
            </div>
            <!-- End of Cloud Endpoint Field -->
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
import { required } from "@vuelidate/validators";
export default {
  setup() {
    return {
      v$: useVuelidate({ $lazy: true, $autoDirty: true }),
    };
  },
  data() {
    return {
      name: "",
      description: "",
      cloud_name: "",
      cloud_access_key: "",
      cloud_secret_key: "",
      cloud_endpoint: "",
    };
  },
  methods: {
    async submitForm() {
      const isFormCorrect = await this.v$.$validate();
      if (!isFormCorrect) return;
      // Create new connection
      const sendData = {
         name: this.name,
         description: this.description,
         cloud_name: this.cloud_name,
         cloud_access_key: this.cloud_access_key,
         cloud_secret_key: this.cloud_secret_key,
         cloud_endpoint: this.cloud_endpoint,
      };
      try {
        const createResp = await axios.post("/api/v1/cloud/connections/", sendData);
        console.log(createResp);
        this.$router.push("/dashboard/connection")
      } catch (error) {
        if (error) {
          console.error(error);
        }
      }
    },
  },
  validations() {
    return {
      name: { required },
      description: { },
      cloud_name: { required },
      cloud_access_key: { required },
      cloud_secret_key: { required },
      cloud_endpoint: { },
    };
  },
}
</script>
