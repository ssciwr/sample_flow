<script setup lang="ts">
import Item from "@/components/ListItem.vue";
import { ref, computed } from "vue";
import { useUserStore } from "@/stores/user";
import apiClient from "@/api-client";

const user = useUserStore();

const login_email_address = ref("");
const login_password = ref("");
const login_error_message = ref("");

function validate_email(email: string) {
  var re = /\S+@((\S*heidelberg)|embl|dkfz)\.de$/;
  return re.test(email);
}

function validate_password(password: string) {
  // at least 8 chars, including lower-case, upper-case, number
  var re = /^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9]).{8,}$/;
  return re.test(password);
}

const signup_email_address = ref("");
const signup_email_address_message = computed(() => {
  if (validate_email(signup_email_address.value)) {
    return "";
} else {
  return "Please use a heidelberg, dkfz or embl email address.";
}});
const signup_password = ref("");
const signup_password_message = computed(() => {
  if (validate_password(signup_password.value)) {
    return "";
  } else {
    return "Password needs at least 8 chars, including lower-case, upper-case and a number.";
  }});

const signup_error_message = ref("");

function do_login() {
  apiClient
    .post("login", {
      email: login_email_address.value,
      password: login_password.value,
    })
    .then((response) => {
      console.log("Login successful");
      login_error_message.value = "";
      user.email = login_email_address.value;
      user.token = response.data.access_token;
    })
    .catch((error) => {
      login_error_message.value = `Login failed: ${error.response.data}`;
    });
}

function do_signup() {
  apiClient
      .post("signup", {
        email: signup_email_address.value,
        password: signup_password.value,
      })
      .then((response) => {
        console.log("Signup successful");
        signup_error_message.value = "Signup successful, you can now login!";
        // todo: email activation step
      })
      .catch((error) => {
        signup_error_message.value = `Signup failed: ${error.response.data}`;
      });
}
</script>

<template>
  <main>
    <Item>
      <template #icon>
        <i class="bi-person"></i>
      </template>
      <template #heading>My account</template>
      <template v-if="user.email.length > 0">
        <p>You are currently logged in as:</p>
        <p class="purple">{{ user.email }}</p>
        <p>
          <button
            @click="
              user.email = '';
              login_email_address = '';
              user.token = '';
            "
          >
            Logout
          </button>
        </p>
      </template>
      <template v-else>
        <p>Log in with the email address and password you used to sign up:</p>
        <p>Email:
          <input
            v-model="login_email_address"
            placeholder="your.name@uni-heidelberg.de"
          />
        </p>
        <p>Password:
          <input v-model="login_password" type="password" />
        </p>
        <p>{{ login_error_message }}</p>
        <p>
          <button @click="do_login">Login</button>
        </p>
      </template>
    </Item>
    <Item v-if="user.email.length === 0">
      <template #icon>
        <i class="bi-person-plus"></i>
      </template>
      <template #heading>Sign up</template>
        <p>If you don't yet have an account, you can create one by entering your Heidelberg Uni, EMBL or DKFZ email address and choosing a password:</p>
        <p>Email:
          <input
              v-model="signup_email_address"
              placeholder="your.name@uni-heidelberg.de"
              :title=signup_email_address_message
          />
        </p>
        <p>Password:
          <input v-model="signup_password" type="password" placeholder="password"               :title=signup_password_message
          />
        </p>
        <p>{{ signup_error_message }}</p>
        <p>
          <button @click="do_signup" :disabled="signup_email_address_message.length + signup_password_message.length > 0">Sign up</button>
        </p>
      </Item>
  </main>
</template>
