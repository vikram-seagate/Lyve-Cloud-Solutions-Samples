<template>
  <div class="landing-login">
    <div class="hero is-info">
      <div class="hero-body has-text-centered">
        <h1 class="title">Create Bucket</h1>
      </div>
    </div>
    <!-- End of Hero -->
    <section class="section">
      <div class="container">
        <div class="column is-6 is-offset-3">
          <form v-on:submit.prevent="submitForm">
            <div class="field">
              <label>Connection</label>
              <div class="control">
                <div class="select">
                  <select v-model="v$.cloud_provider_id.$model">
                    <option disabled value="">Select One</option>
                    <option
                      v-for="conn in connList"
                      :key="conn.id"
                      :value="conn.id"
                    >
                      {{ conn.name }}
                    </option>
                    <!--
                    <option disabled value="">Select One</option>
                    <option value="AWS">AWS</option>
                    <option value="LYC">LyveCloud</option>
                    -->
                  </select>
                </div>
              </div>
							<template v-if="v$.cloud_provider_id.$errors.length">
								<p
									class="help is-danger"
									v-for="error of v$.cloud_provider_id.$errors"
									:key="error.$uid"
								>
									{{ error.$message }}
								</p>
              </template>
            </div>
            <!-- End of Connection Field -->
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
              <label>Cloud Region</label>
              <div class="control">
                <input type="text" class="input" v-model="v$.cloud_region.$model"/>
              </div>
							<template v-if="v$.cloud_region.$errors.length">
								<p
									class="help is-danger"
									v-for="error of v$.cloud_region.$errors"
									:key="error.$uid"
								>
									{{ error.$message }}
								</p>
              </template>
            </div>
            <!-- End of Cloud Region Field -->
            <div class="field">
              <div class="control">
                <button class="button is-dark">Create</button>
              </div>
            </div>
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
  computed: {
    reqBucketListStatus() {
      return this.$store.getters["bucket/reqBucketListStatus"];
    },
    connList() {
      return this.$store.getters["bucket/connList"];
    },
  },
  data() {
    return {
      cloud_provider_id: "",
      name: "",
      description: "",
      cloud_region: "",
    };
  },
  methods: {
    async submitForm() {
      const isFormCorrect = await this.v$.$validate();
      if (!isFormCorrect) return;
      // Create new connection
      const sendData = {
       cloud_provider_id: this.cloud_provider_id,
       name: this.name,
       description: this.description,
       cloud_region: this.cloud_region,
      };
      try {
        const createResp = await axios.post("/api/v1/cloud/buckets/", sendData);
        console.log(createResp);
        this.$router.push("/dashboard/buckets")
      } catch (error) {
        if (error) {
          console.error(error);
        }
      }
    },
  },
  async mounted() {
    this.$store.dispatch("bucket/getConnections");
  },
  validations() {
    return {
      cloud_provider_id: { required },
      name: { required },
      description: { },
      cloud_region: { },
    };
  },
}
</script>
