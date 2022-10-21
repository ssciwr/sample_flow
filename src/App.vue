<script setup lang="ts">
import { RouterLink, RouterView } from "vue-router";
import { ref } from "vue";
import TitleItem from "./components/TitleComponent.vue";
import { useUserStore } from "@/stores/user";
const user = useUserStore();
let login_title = ref("Login");
if (user.email.length > 0) {
  login_title.value = user.email;
}
</script>

<template>
  <header>
    <div class="wrapper">
      <TitleItem />
      <nav>
        <RouterLink to="/">About</RouterLink>
        <RouterLink to="/samples">My samples</RouterLink>
        <RouterLink to="/login">{{
          user.email.length > 0 ? user.email : "Login"
        }}</RouterLink>
        <RouterLink to="/admin">Admin</RouterLink>
      </nav>
    </div>
  </header>

  <RouterView />
</template>

<style scoped>
header {
  line-height: 1.5;
  max-height: 100vh;
}

nav {
  width: 100%;
  font-size: 16px;
  text-align: center;
  margin-top: 2rem;
  margin-bottom: 2rem;
}

nav a.router-link-exact-active {
  color: var(--color-text);
}

nav a.router-link-exact-active:hover {
  background-color: transparent;
}

nav a {
  display: inline-block;
  padding: 0 1rem;
  border-left: 1px solid var(--color-border);
}

nav a:first-of-type {
  border: 0;
}
</style>
