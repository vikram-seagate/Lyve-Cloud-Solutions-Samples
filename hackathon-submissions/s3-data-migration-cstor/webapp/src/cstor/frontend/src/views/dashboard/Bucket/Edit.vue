<template>
  <div class="dashboard-profile">
    <div class="hero is-info">
      <div class="hero-body has-text-centered">
        <h1 class="title">Bucket Detail</h1>
      </div>
    </div>
    <!-- End of Hero -->
    <section class="section">
      <div class="container">
        <div class="column is-6 is-offset-3">
          <div class="form">
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
              <div class="control">
                <div class="level">
                  <div class="level-left">
                    <div class="level-item">
                      <button
                        class="button is-dark"
                        @click="updateObj"
                      >
                        Update
                      </button>
                    </div>
                  </div>
                  <!-- End of Level Left -->
                  <div class="level-right">
                    <div class="level-item">
                      <button
                        class="button is-danger"
                        @click="deleteObj"
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                  <!-- End of Level Right -->
                </div>
                <!-- End of Level -->
              </div>
            </div>
            <!-- End of Buttons Field -->
          </div>
        </div>
      </div>
      <!-- End of Container -->
    </section>
    <!-- End of Section -->
  </div>
</template>
<script>
import axios from "axios";
import useVuelidate from "@vuelidate/core";
import { required } from "@vuelidate/validators";
import { mapGetters } from "vuex";

export default {
  data() {
    return {
      name: "",
      description: "",
      cloud_region: "",
    };
  },
  computed: {
  },
  methods: {
    async updateObj(evt) {
      const id = this.$route.params.id;
      const isFormCorrect = await this.v$.$validate();
      if (!isFormCorrect) return;
      // Create new connection
      const patchData = {
         name: this.name,
         description: this.description,
         cloud_region: this.cloud_region,
      };
      if (this.cloud_secret_key != "") {
        patchData.cloud_secret_key = this.cloud_secret_key;
      }
      try {
        const patchResp = await axios.patch(`/api/v1/cloud/buckets/${id}/`, patchData);
        console.log(patchResp);
      } catch (error) {
        if (error) {
          console.error(error);
        }
      }
    },
    async deleteObj(evt) {
      const id = this.$route.params.id;
      try {
        const deleteResp = await axios.delete(`/api/v1/cloud/buckets/${id}/`);
        this.$router.push("/dashboard/buckets")
      } catch (error) {
        if (error) {
          console.error(error);
        }
      }
    },
  },
  setup() {
    return {
      v$: useVuelidate({ $lazy: true, $autoDirty: true }),
    };
  },
  async mounted() {
    const id = this.$route.params.id;
    try {
      const connResp = await axios.get(`/api/v1/cloud/buckets/${id}/`);
      this.name = connResp.data.name;
      this.description = connResp.data.description;
      this.cloud_region = connResp.data.cloud_name;
    } catch (error) {
      if (error) {
        console.error(error);
      }
    }
  },
  validations() {
    return {
      name: { required },
      description: { },
      cloud_region: { },
    };
  },
};
</script>
