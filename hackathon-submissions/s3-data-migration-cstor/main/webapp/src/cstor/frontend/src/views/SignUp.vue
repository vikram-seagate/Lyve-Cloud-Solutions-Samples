<template>
  <div class="landing-signup">
    <div class="hero is-info">
      <div class="hero-body has-text-centered">
        <h1 class="title">Sign Up</h1>
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
              <label>Repeat Password</label>
              <div class="control">
                <input type="password" class="input" v-model="v$.password_repeat.$model"/>
              </div>
							<template v-if="v$.password_repeat.$errors.length">
								<p
									class="help is-danger"
									v-for="error of v$.password_repeat.$errors"
									:key="error.$uid"
								>
									{{ error.$message }}
								</p>
              </template>
            </div>
            <!-- End of Repeat Password Field -->
            <div class="field">
              <div class="control">
                <button class="button is-dark">Sign Up</button>
              </div>
            </div>
            <!-- End of Sign Up Button -->
            <hr />

            Or <router-link to="/login">Login</router-link>
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
import { toast as superToast } from 'bulma-toast'

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
      password_repeat: "",
    };
  },
  methods: {
    async submitForm() {
      const isFormCorrect = await this.v$.$validate();
      if (!isFormCorrect) return;
      // Sign up with Django
      const signupData = {
         username: this.username,
         password: this.password,
      };
      try {
        let signUpResp = await axios.post("/api/v1/users/", signupData);
        superToast({
          message: `Signup Success!`,
          type: "is-success",
        });
        this.$router.push("/login");
      } catch (error) {
        if (error) {
          if (error.response.data) {
            for (const [fieldName, fieldMsg] of Object.entries(error.response.data)) {
              superToast({
                message: `Signup Failed: ${fieldMsg}`,
                type: "is-danger",
                dismissible: true,
                duration: 4000,
              });
            }
          }
        }
      }
    },
  },
  validations() {
    return {
      username: { required, email },
      password: { required },
      password_repeat: {
        required,
        sameAsPassword: sameAs(this.password),
        minLength: minLength(8),
		    containsUppercase: (value) => {
          return /[A-Z]/.test(value);
        },
				containsLowercase: (value) => {
					return /[a-z]/.test(value);
				},
				containsNumber: (value) => {
					return /[0-9]/.test(value);
				},
				containsSpecial: (value) => {
					return /[#?!@$%^&*-]/.test(value)
				}
      },
    };
  },
}
</script>
