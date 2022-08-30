<template>
  <div class="dashboard-profile">
    <div class="hero is-info">
      <div class="hero-body has-text-centered">
        <h1 class="title">Connection Detail</h1>
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
                    <div class="level-item">
                      <button
                        class="button is-primary"
                        @click="scanBucket"
                      >
                        Scan Bucket
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
            <template v-if="reqBucketListStatus !== 'waiting'">
              <div class="box">
                Scanning Buckets <span class="tag is-info is-uppercase"> {{ reqBucketListStatus }}</span>
              </div>
            </template>
            <template v-if="candidateList.length > 0">
              <table class="table">
                <thead>
                  <th>Name</th>
                  <th>Creation Date</th>
                  <th>Action</th>
                </thead>
                <tbody>
                  <tr
                    v-for="candidate in candidateList"
                    :key="candidate.Name"
                  >
                    <td>{{ candidate.Name }}</td>
                    <td>{{ candidate.CreationDate }}</td>
                    <td>
                      <label class="checkbox">
                        <input type="checkbox" @click="selectCandidate(candidate.Name)">
                      </label>
                    </td>
                  </tr>
                </tbody>
                <div class="level">
                  <div class="level-right">
                    <div class="level-item">
                      <button
                        class="button is-success"
                        @click="createBuckets"
                      >
                        Create
                      </button>
                    </div>
                  </div>
                  <!-- End of Level Right -->
                </div>
                <!-- End of Level -->
              </table>
            </template>
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
      cloud_name: "",
      cloud_access_key: "",
      cloud_secret_key: "",
      cloud_endpoint: "",
      candidateSelected: [],
    };
  },
  computed: {
    reqBucketListStatus() {
      return this.$store.getters["bucket/reqBucketListStatus"];
    },
    candidateList() {
      return this.$store.getters["bucket/candidateList"];
    },
  },
  methods: {
    async createBuckets(evt) {
      const cloud_provider_id = this.$route.params.id;
      // Create Buckets
      let idx = 0;
      while(idx < this.candidateSelected.length) {
        const postData = {
          name: this.candidateSelected[idx],
          cloud_provider_id,
        };
        console.log(`postData: ${postData}`);
        const postResp = await axios.post(`/api/v1/cloud/buckets/`, postData);
        console.log(`postResp: ${postResp}`);
        idx += 1;
      }
    },
    async updateObj(evt) {
      const id = this.$route.params.id;
      const isFormCorrect = await this.v$.$validate();
      if (!isFormCorrect) return;
      // Create new connection
      const patchData = {
         name: this.name,
         description: this.description,
         cloud_name: this.cloud_name,
         cloud_access_key: this.cloud_access_key,
         cloud_endpoint: this.cloud_endpoint,
      };
      if (this.cloud_secret_key != "") {
        patchData.cloud_secret_key = this.cloud_secret_key;
      }
      try {
        const patchResp = await axios.patch(`/api/v1/cloud/connections/${id}/`, patchData);
        console.log(patchResp);
      } catch (error) {
        if (error) {
          console.error(error);
        }
      }
    },
    selectCandidate(name) {
      let candidateIdx = this.candidateSelected.indexOf(name);
      if (candidateIdx === -1) {
        this.candidateSelected.push(name);
        return;
      }
      this.candidateSelected.splice(candidateIdx, 1);
    },
    async scanBucket(evt) {
      const id = this.$route.params.id;
      try {
        const patchData = {
          action: "list_buckets",
        };
        await axios.patch(`/api/v1/cloud/connections/${id}/`, patchData);
        this.$store.commit("bucket/setReqBucketListStatus", { req_status: "pending" });
      } catch (error) {
        if (error) {
          console.error(error);
        }
      }
    },
    async deleteObj(evt) {
      const id = this.$route.params.id;
      try {
        const deleteResp = await axios.delete(`/api/v1/cloud/connections/${id}/`);
        this.$router.push("/dashboard/connection")
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
      const connResp = await axios.get(`/api/v1/cloud/connections/${id}/`);
      this.name = connResp.data.name;
      this.description = connResp.data.description;
      this.cloud_name = connResp.data.cloud_name;
      this.cloud_access_key = connResp.data.cloud_access_key;
      this.cloud_secret_key = "";
      this.cloud_endpoint = connResp.data.cloud_endpoint;
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
      cloud_name: { required },
      cloud_access_key: { required },
      cloud_secret_key: { },
      cloud_endpoint: { },
    };
  },
};
</script>
