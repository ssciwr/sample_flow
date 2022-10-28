<script setup lang="ts">
import { ref } from "vue";
import Item from "@/components/ListItem.vue";
import apiClient from "@/api-client";
import type { Sample } from "@/types";
const new_sample_name = ref("");
const samples = ref([] as Sample[]);

  apiClient.get("samples").then((response) => {
    samples.value = response.data.samples;
  }).catch((error) => {
    console.log(error);
  });

function add_sample() {
  apiClient
    .post("addsample", {
      name: new_sample_name.value,
    })
    .then((response) => {
      console.log(response);
      samples.value.push(response.data.sample)
    });
  new_sample_name.value = "";
}

</script>

<template>
  <main>
    <Item>
      <template #icon>
        <i class="bi-clipboard-data"></i>
      </template>
      <template #heading>My samples</template>
      <template v-if="samples.length > 0">
        <p>Your samples for this week:</p>
        <table>
          <tr>
            <th>Primary Key</th>
            <th>Sample Name</th>
          </tr>
          <tr
            v-for="sample in samples"
            :key="sample.id"
          >
            <td>{{ sample["primary_key"] }}</td>
            <td>{{ sample["name"] }}</td>
          </tr>
        </table>
      </template>
      <template v-else>
        <p>You don't have any samples this week.</p>
      </template>
    </Item>
    <Item>
      <template #icon>
        <i class="bi-clipboard-plus"></i>
      </template>
      <template #heading>Submit a sample</template>
      <p>To submit a new sample, enter a sample name:</p>
      <input v-model="new_sample_name" placeholder="sample name" />
      <button @click="add_sample">Request Sample</button>
    </Item>
  </main>
</template>
