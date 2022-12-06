<script setup lang="ts">
import { ref, computed } from "vue";
import { apiClient } from "@/utils/api-client";
import { validate_email, validate_password } from "@/utils/validation";
import ListItem from "@/components/ListItem.vue";
const signup_email_address = ref("");
const signup_email_address_message = computed(() => {
  if (validate_email(signup_email_address.value)) {
    return "";
  } else {
    return "Please use a uni-heidelberg, dkfz or embl email address.";
  }
});
const signup_password = ref("");
const signup_password_message = computed(() => {
  if (validate_password(signup_password.value)) {
    return "";
  } else {
    return "At least 8 characters, including lower-case, upper-case and a number.";
  }
});
const signup_response_message = ref("");

function do_signup() {
  apiClient
    .post("signup", {
      email: signup_email_address.value,
      password: signup_password.value,
    })
    .then((response) => {
      signup_response_message.value = response.data.message;
    })
    .catch((error) => {
      signup_response_message.value = error.response.data.message;
    });
}
</script>

<template>
  <ListItem title="Sign up" icon="bi-person-plus">
    <p>
      If you don't yet have an account, you can create one by entering your
      Heidelberg Uni, EMBL or DKFZ email address and choosing a password:
    </p>
    <form @submit.prevent="do_signup">
      <table>
        <tr>
          <td style="text-align: right">Email:</td>
          <td>
            <input
              v-model="signup_email_address"
              placeholder="your.name@uni-heidelberg.de"
              :title="signup_email_address_message"
              maxlength="256"
            />
          </td>
          <td style="font-style: italic">
            {{ signup_email_address_message }}
          </td>
        </tr>
        <tr>
          <td style="text-align: right">Password:</td>
          <td>
            <input
              v-model="signup_password"
              type="password"
              placeholder="password"
              :title="signup_password_message"
              maxlength="256"
            />
          </td>
          <td style="font-style: italic">{{ signup_password_message }}</td>
        </tr>
        <tr>
          <td></td>
          <td>
            <input
              type="submit"
              :title="
                signup_email_address_message + ' ' + signup_password_message
              "
              :disabled="
                signup_email_address_message.length +
                  signup_password_message.length >
                0
              "
            />
          </td>
        </tr>
      </table>
    </form>
    <p style="font-style: italic">
      {{ signup_response_message }}
    </p>
  </ListItem>
</template>
