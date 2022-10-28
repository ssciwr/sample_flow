<script setup lang="ts">
import Item from "@/components/ListItem.vue";
import { ref } from 'vue'
import type { Sample, User } from "@/types";
import apiClient from "@/api-client";

const samples = ref([] as Sample[]);
apiClient.get("allsamples").then((response) => {
  console.log(response);
  samples.value = response.data.samples;
});

const users = ref([] as User[]);
apiClient.get("allusers").then((response) => {
  console.log(response);
  users.value = response.data.users;
});

</script>

<template>
  <main>
    <p>(Normally this page would only be accessible to admin users)</p>
    <Item>
      <template #icon>
        <i class="bi-gear"></i>
      </template>
      <template #heading>Samples</template>
      <p>{{ samples.length }} samples have been requested so far:</p>
      <table>
        <tr>
          <th>Primary Key</th>
          <th>Email</th>
          <th>Sample Name</th>
          <th>Requested on</th>
        </tr>
        <tr v-for="sample in samples" :key="sample.id">
          <td>{{ sample["primary_key"] }}</td>
          <td>{{ sample["email"] }}</td>
          <td>{{ sample["name"] }}</td>
          <!--          <td>{{ sample["date"].toUTCString() }}</td>-->
        </tr>
      </table>
    </Item>
    <Item>
      <template #icon>
        <i class="bi-gear"></i>
      </template>
      <template #heading>Users</template>
      <p>(Normally this page only be accessible to admin users)</p>
      <p>{{ users.length }} registered users:</p>
      <table>
        <tr>
          <th>Id</th>
          <th>Email</th>
          <th>Activated</th>
        </tr>
        <tr v-for="user in users" :key="user.id">
          <td>{{ user["id"] }}</td>
          <td>{{ user["email"] }}</td>
          <td>{{ user["activated"] }}</td>
        </tr>
      </table>
    </Item>
  </main>
</template>
