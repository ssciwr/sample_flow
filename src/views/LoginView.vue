<script setup lang="ts">
import Item from "@/components/ListItem.vue";
import { useUserStore } from "@/stores/user";
const user = useUserStore();
let email_address = "";
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
              email_address = '';
            "
          >
            Logout
          </button>
        </p>
      </template>
      <template v-else>
        <p>Log in with your email address:</p>
        <p>
          <input
            v-model="email_address"
            placeholder="your.name@uni-heidelberg.de"
          />
        </p>
        <p><button @click="user.email = email_address">Login</button></p>
      </template>
    </Item>
  </main>
</template>
