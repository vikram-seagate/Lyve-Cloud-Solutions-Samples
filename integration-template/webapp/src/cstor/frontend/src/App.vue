<template>
  <div> <!-- Template Single Root -->
    <NavBar />
    <router-view />
    <Footer />
  </div>
</template>

<style lang="scss">
@import "../node_modules/bulma";

.card-wrapper {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px,1fr));
  grid-gap: 0.5em;
}

.card-wrapper-migration {
  display: grid;
  width: 100%;
}
</style>
<script>
import axios from "axios";
import NavBar from "@/components/NavBar";
import Footer from "@/components/Footer";

export default {
  name: "App",
  components: {
    NavBar,
    Footer,
  },
  beforeCreate() {
    this.$store.commit("initStore");
    const token = this.$store.state.user.token;

    if (token) {
      axios.defaults.headers.common["Authorization"] = `Token ${token}`;
      this.$wsConnect(token);
    } else {
      axios.defaults.headers.common["Authorization"] = "";
    }
  },
};
</script>
