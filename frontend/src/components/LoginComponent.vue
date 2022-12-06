<script setup lang="ts">
import { ref } from "vue";
import { useUserStore } from "@/stores/user";
import { apiClient } from "@/utils/api-client";
import ListItem from "@/components/ListItem.vue";
const userStore = useUserStore();
const login_email_address = ref("");
const login_password = ref("");
const login_error_message = ref("");

function do_login() {
  apiClient
    .post("login", {
      email: login_email_address.value,
      password: login_password.value,
    })
    .then((response) => {
      login_error_message.value = "";
      userStore.user = response.data.user;
      userStore.token = response.data.access_token;
    })
    .catch((error) => {
      login_error_message.value = `Login failed: ${error.response.data}`;
      userStore.user = null;
      userStore.token = "";
    });
}
</script>

<template>
  <ListItem title="Login" icon="bi-person">
    <p>Log in with the email address and password you used to sign up:</p>
    <form @submit.prevent="do_login">
      <table>
        <tr>
          <td style="text-align: right">Email:</td>
          <td>
            <input
              v-model="login_email_address"
              placeholder="your.name@uni-heidelberg.de"
              maxlength="256"
            />
          </td>
        </tr>
        <tr>
          <td style="text-align: right">Password:</td>
          <td>
            <input v-model="login_password" type="password" maxlength="256" />
          </td>
        </tr>
        <tr>
          <td></td>
          <td style="font-style: italic">{{ login_error_message }}</td>
        </tr>
        <tr>
          <td></td>
          <td>
            <input type="submit" />
          </td>
        </tr>
      </table>
    </form>
  </ListItem>
</template>
