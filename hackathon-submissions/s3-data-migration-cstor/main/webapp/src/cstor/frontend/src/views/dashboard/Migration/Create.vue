<template>
  <div class="landing-login">
    <div class="hero is-info">
      <div class="hero-body has-text-centered">
        <h1 class="title">Create Migration</h1>
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
              <label>Source Bucket</label>
              <div class="control">
                <div class="select">
                  <select v-model="v$.src_bucket_id.$model">
                    <option disabled value="">Select One</option>
                    <option
                      v-for="bucket in bucketListSrc"
                      :key="bucket.id"
                      :value="bucket.id"
                    >
                      {{ bucket.name }}
                    </option>
                  </select>
                </div>
              </div>
							<template v-if="v$.src_bucket_id.$errors.length">
								<p
									class="help is-danger"
									v-for="error of v$.src_bucket_id.$errors"
									:key="error.$uid"
								>
									{{ error.$message }}
								</p>
              </template>
            </div>
            <!-- End of Src Bucket Id -->
            <div class="field">
              <label>Source Prefix</label>
              <div class="control">
                <input type="text" class="input" v-model="v$.src_prefix.$model"/>
              </div>
							<template v-if="v$.src_prefix.$errors.length">
								<p
									class="help is-danger"
									v-for="error of v$.src_prefix.$errors"
									:key="error.$uid"
								>
									{{ error.$message }}
								</p>
              </template>
            </div>
            <!-- End of Src Prefix Field -->
            <div class="field">
              <label>Destination Bucket</label>
              <div class="control">
                <div class="select">
                  <select v-model="v$.dest_bucket_id.$model">
                    <option disabled value="">Select One</option>
                    <option
                      v-for="bucket in bucketListDest"
                      :key="bucket.id"
                      :value="bucket.id"
                    >
                      {{ bucket.name }}
                    </option>
                  </select>
                </div>
              </div>
							<template v-if="v$.dest_bucket_id.$errors.length">
								<p
									class="help is-danger"
									v-for="error of v$.dest_bucket_id.$errors"
									:key="error.$uid"
								>
									{{ error.$message }}
								</p>
              </template>
            </div>
            <!-- End of Dest Bucket Id -->
            <div class="field">
              <label>Destination Prefix</label>
              <div class="control">
                <input type="text" class="input" v-model="v$.dest_prefix.$model"/>
              </div>
							<template v-if="v$.dest_prefix.$errors.length">
								<p
									class="help is-danger"
									v-for="error of v$.dest_prefix.$errors"
									:key="error.$uid"
								>
									{{ error.$message }}
								</p>
              </template>
            </div>
            <!-- End of Dest Prefix Field -->
            <div class="field">
              <label>Description</label>
              <div class="control">
                <textarea class="textarea" v-model="v$.description.$model"/>
              </div>
            </div>
            <hr />
            <div class="field">
              <label>Size GTE</label>
              <div class="control">
                <input type="text" class="input" v-model="v$.filter_size_gte.$model"/>
              </div>
              <template v-if="v$.filter_size_gte.$errors.length">
                <p
                  class="help is-danger"
                  v-for="error of v$.filter_size_gte.$errors"
                  :key="error.$uid"
                >
                  {{ error.$message }}
                </p>
              </template>
            </div>
            <!-- End of Size GTE Field -->
            <div class="field">
              <label>Size LTE</label>
              <div class="control">
                <input type="text" class="input" v-model="v$.filter_size_lte.$model"/>
              </div>
              <template v-if="v$.filter_size_lte.$errors.length">
                <p
                  class="help is-danger"
                  v-for="error of v$.filter_size_lte.$errors"
                  :key="error.$uid"
                >
                  {{ error.$message }}
                </p>
              </template>
            </div>
            <!-- End of Size LTE Field -->
            <!-- End of Description Field -->
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
import { required, not, sameAs, integer, between } from "@vuelidate/validators";
export default {
  setup() {
    return {
      v$: useVuelidate({ $lazy: true, $autoDirty: true }),
    };
  },
  computed: {
    bucketListSrc() {
      // return this.$store.getters["migration/buckets"];
      const bucketList = this.$store.getters["migration/buckets"];
      return bucketList;
    },
    bucketListDest() {
      const bucketList = this.$store.getters["migration/buckets"];
      return bucketList;
    },
  },
  data() {
    return {
      name: "",
      src_bucket_id: "",
      src_prefix: "",
      dest_bucket_id: "",
      dest_prefix: "",
      description: "",
      filter_size_gte: 0,
      filter_size_lte: 0,
    };
  },
  methods: {
    async submitForm() {
      const isFormCorrect = await this.v$.$validate();
      if (!isFormCorrect) return;
      // Create new connection
      const sendData = {
        // 
        src_bucket_id: this.src_bucket_id,
        src_prefix: this.src_prefix,
        dest_bucket_id: this.dest_bucket_id,
        dest_prefix: this.dest_prefix,
        name: this.name,
        description: this.description,
      };
      if (this.filter_size_gte !== 0) {
        sendData.filter_size_gte = this.filter_size_gte;
      }
      if (this.filter_size_lte !== 0) {
        sendData.filter_size_lte = this.filter_size_lte;
      }
      try {
        console.log(sendData);
        const createResp = await axios.post("/api/v1/cloud/migrations/", sendData);
        console.log(createResp);
        this.$router.push("/dashboard/migrations")
      } catch (error) {
        if (error) {
          console.error(error);
        }
      }
    },
  },
  async mounted() {
    this.$store.dispatch("migration/getBucketList");
  },
  validations() {
    return {
      src_bucket_id: { required },
      src_prefix: {},
      // Cannot be the same as src
      dest_bucket_id: {
        required,
        not: not(sameAs("src_bucket_id"))
      },
      dest_prefix: {},
      name: { required },
      description: { },
      filter_size_gte: {
        integer,
        betweenVal: between(0, 1024*1024*5),
      },
      filter_size_lte: {
        integer,
        betweenVal: between(0, 1024*1024*5),
      },
    };
  },
};
</script>
