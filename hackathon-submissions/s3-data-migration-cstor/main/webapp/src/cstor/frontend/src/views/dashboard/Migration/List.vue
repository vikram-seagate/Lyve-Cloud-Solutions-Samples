<template>
  <div class="dashboard-profile">
    <div class="hero is-info">
      <div class="hero-body has-text-centered">
        <h1 class="title">Migrations</h1>
      </div>
    </div>
    <!-- End of Hero -->
    <section class="section">
      <div class="container">
        <router-link to="/dashboard/migrations/create">
          <button class="button is-dark">Create</button>
        </router-link>
        <hr />
        <div class="card-wrapper-migration">
          <div
            class="card"
            v-for="migration in migrationList"
            :key="migration.id"
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
                      <router-link :to="{ 'name': 'db-migrations-detail', params: { id: migration.id }}">
                        <button class="button is-dark is-small">View</button>
                      </router-link>
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
      </div>
    </section>
    <!-- End of Section -->
  </div>
</template>
<script>
export default {
  data() {
    return {};
  },
  computed: {
    migrationList() {
      return this.$store.getters["migration/migrations"];
    },
  },
  async mounted() {
    this.$store.dispatch("migration/getMigrationList");
  },
};
</script>
