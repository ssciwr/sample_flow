import { ref } from "vue";
import { defineStore } from "pinia";

export const useUserStore = defineStore("user", () => {
  const email = ref("");
  const token = ref("");
  return { email, token };
});
