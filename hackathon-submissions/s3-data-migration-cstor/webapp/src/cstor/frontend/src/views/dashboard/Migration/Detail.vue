<template>
  <div class="dashboard-profile">
    <div class="hero is-info">
      <div class="hero-body has-text-centered">
        <h1 class="title">Migration Detail</h1>
      </div>
    </div>
    <!-- End of Hero -->
    <section class="section">
      <div class="container">
        <div
          class="card"
        >
          <div class="card-content">
            <nav class="level">
              <div class="level-left">
                <div class="level-item">
                  <div>
                    <p class="heading">Source Bucket</p>
                    <p class="title is-5">{{ migration.src_bucket.name }}</p>
                  </div>
                </div>
                <!-- End of Level Item -->
                <div class="level-item">
                  <div>
                    <p class="heading">Destination Bucket</p>
                    <p class="title is-5">{{ migration.dest_bucket.name }}</p>
                  </div>
                </div>
                <!-- End of Level Item -->
                <div class="level-item">
                  <div>
                    <p class="heading">Name</p>
                    <p class="title is-5">{{ migration.name }}</p>
                  </div>
                </div>
                <!-- End of Level Item -->
                <div class="level-item">
                  <div>
                    <p class="heading">Status</p>
                    <!-- <p class="title is-5">{{ migration.status }}</p> -->
                    <p class="title is-5">
                      <span v-if="migration.status == 0" class="tag is-light">SCANNING</span>
                      <span v-if="migration.status == 2" class="tag is-link">PAUSED</span>
                      <span v-if="migration.status == 1" class="tag is-warning">RUNNING</span>
                      <span v-if="migration.status == 3" class="tag is-success">SUCCESS</span>
                    </p>
                  </div>
                </div>
                <!-- End of Level Item -->
                <div class="level-item">
                  <div>
                    <p class="heading">Total Size</p>
                    <p class="title is-5">{{ totalSize }}</p>
                  </div>
                </div>
                <!-- End of Level Item -->
                <div class="level-item">
                  <div>
                    <p class="heading">In Progress Size</p>
                    <p class="title is-5">{{ progressSize }}</p>
                  </div>
                </div>
                <!-- End of Level Item -->
                <div class="level-item">
                  <div>
                    <p class="heading">Success Size</p>
                    <p class="title is-5">{{ successSize }}</p>
                  </div>
                </div>
                <!-- End of Level Item -->
                <div class="level-item">
                  <div>
                    <p class="heading">Failed Size</p>
                    <p class="title is-5">{{ failSize }}</p>
                  </div>
                </div>
                <!-- End of Level Item -->
                <div class="level-item">
                  <div>
                    <p class="heading">Progress</p>
                    <p class="title is-5">
                      <progress class="progress" :value="migration.success_count" :max="migration.total_count" />
                    </p>
                  </div>
                </div>
                <!-- End of Level Item -->
              </div>
              <!-- End of Level Left -->
              <div class="level-right">
                <div class="level-item">
                  <div>
                    <button
                        v-if="migration.status === 2"
                        class="button is-success"
                        @click="migration_start"
                    >
                        Start
                    </button>
                    <button
                        v-if="migration.status === 1"
                        class="button is-info"
                        @click="migration_pause"
                    >
                        Pause
                    </button>
                  </div>
                </div>

              </div>
              <!-- End of Level Right -->
            </nav>
            <!-- End of Level -->
            <!-- <p class="title is-4">{{ migration.name }}</p> -->
            <!--
            <router-link :to="{ 'name': 'db-buckets-detail', params: { id: bucket.id }}">
              <button class="button is-dark is-small">Edit</button>
            </router-link>
            -->
          </div>
        </div>
        <!-- End of Card -->
      </div>
      <!-- End of Container -->
    </section>
    <!-- End of Section -->
  </div>
</template>
<script>
import axios from "axios";

const mbyte = 1024 * 1024;
const gbyte = 1024 * mbyte;

export default {
  data() {
    return {
    };
  },
  computed: {
    migration() {
      return this.$store.getters["migration/migrationDetail"](this.$route.params.id);
    },
    totalSize() {
      // Total Size in Appropiate Units
      return this.size_scale(this.migration.total_size);
    },
    progressSize() {
      // Total Size in Appropiate Units
      return this.size_scale(this.migration.progress_size);
    },
    successSize() {
      // Total Size in Appropiate Units
      return this.size_scale(this.migration.success_size);
    },
    failSize() {
      // Total Size in Appropiate Units
      return this.size_scale(this.migration.fail_size);
    },
  },
  methods: {
    size_scale(raw_size) {
      const size_in_mb = parseFloat(raw_size / mbyte).toFixed(2);
      if (size_in_mb > 2000) {
        const size_in_gb = (size_in_mb / 1024 ).toFixed(2);
        return `${size_in_gb} GB`;
      }
      return `${size_in_mb} MB`;
    },
    migration_start() {
      const id = this.$route.params.id;
      this.$store.dispatch("migration/startMigration", { id });
    },
    migration_pause() {
      const id = this.$route.params.id;
      this.$store.dispatch("migration/pauseMigration", { id });
    },
  },
  async mounted() {
    console.log("Mounting...");
    const id = this.$route.params.id;
    console.log(`ID: ${id}`);
    this.$store.dispatch("migration/getMigrationDet", { id });
  },
};
</script>
