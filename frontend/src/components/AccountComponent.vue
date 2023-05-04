<script setup lang="ts">
import { ref, computed } from "vue";
import { apiClient } from "@/utils/api-client";
import { validate_password } from "@/utils/validation";
import { useUserStore } from "@/stores/user";
import ListItem from "@/components/ListItem.vue";
const userStore = useUserStore();
const current_email = ref("");
if (userStore.user) {
  current_email.value = userStore.user.email;
}
const current_password = ref("");
const new_password = ref("");
const new_password_message = computed(() => {
  if (
    new_password.value.length === 0 ||
    validate_password(new_password.value)
  ) {
    return "";
  } else {
    return "At least 8 characters, including lower-case, upper-case and a number.";
  }
});
const new_password2 = ref("");
const new_password2_message = computed(() => {
  if (new_password.value == new_password2.value) {
    return "";
  } else {
    return "New passwords don't match";
  }
});
const response_message = ref("");

function do_change_password() {
  apiClient
    .post("change_password", {
      current_password: current_password.value,
      new_password: new_password.value,
    })
    .then((response) => {
      response_message.value = response.data.message;
    })
    .catch((error) => {
      response_message.value = error.response.data.message;
    });
}
</script>

<template v-if="userStore.user != null">
  <ListItem title="My account" icon="bi-person">
    <p>You are currently logged in as:</p>
    <p class="purple">{{ current_email }}</p>
    <p>
      <button
        @click="
          userStore.user = null;
          userStore.token = '';
        "
      >
        Logout
      </button>
    </p>
  </ListItem>
  <ListItem title="Change password" icon="bi-key">
    <form @submit.prevent="do_change_password">
      <table>
        <tr>
          <td style="text-align: right">Current Password:</td>
          <td>
            <input
              v-model="current_password"
              type="password"
              placeholder="current password"
              maxlength="256"
            />
          </td>
        </tr>
        <tr>
          <td style="text-align: right">New Password:</td>
          <td>
            <input
              v-model="new_password"
              type="password"
              placeholder="new password"
              :title="new_password_message"
              maxlength="256"
            />
          </td>
          <td style="font-style: italic">{{ new_password_message }}</td>
        </tr>
        <tr>
          <td style="text-align: right">Confirm New Password:</td>
          <td>
            <input
              v-model="new_password2"
              type="password"
              placeholder="new password"
              :title="new_password2_message"
              maxlength="256"
            />
          </td>
          <td style="font-style: italic">{{ new_password2_message }}</td>
        </tr>
        <tr>
          <td></td>
          <td>
            <input
              type="submit"
              :title="new_password_message + ' ' + new_password2_message"
              :disabled="
                current_password.length === 0 ||
                new_password.length === 0 ||
                new_password2.length === 0 ||
                new_password_message.length + new_password2_message.length > 0
              "
            />
          </td>
        </tr>
      </table>
    </form>
    <p style="font-style: italic">
      {{ response_message }}
    </p>
  </ListItem>
</template>
