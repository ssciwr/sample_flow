<script setup lang="ts">
import Item from "@/components/ListItem.vue";
import { ref } from "vue";
import { apiClient } from "@/utils/api-client";
const props = defineProps({ activation_token: String });

const status_message = ref("");
const message = ref("");
const icon_name = ref("bi-person-exclamation");

apiClient
  .get(`activate/${props.activation_token}`)
  .then((response) => {
    console.log(response);
    message.value = response.data.message;
    icon_name.value = "bi-person-check";
    status_message.value = "Successful";
  })
  .catch((error) => {
    if (error.response != null) {
      message.value = error.response.data.message;
    } else {
      message.value = "Cannot connect to server.";
    }
    icon_name.value = "bi-person-exclamation";
    status_message.value = "Failed";
  });
</script>

<template>
  <main>
    <Item>
      <template #icon>
        <p><i :class="icon_name"></i></p>
      </template>
      <template #heading>Account Activation {{ status_message }}</template>
      <p>{{ message }}</p>
      <p>Go to <RouterLink to="/login">login / signup</RouterLink> page.</p>
    </Item>
  </main>
</template>
