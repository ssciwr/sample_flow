<script setup lang="ts">
import Item from "@/components/ListItem.vue";
import DocumentationIcon from "@/components/icons/IconDocumentation.vue";
import { useSamplesStore } from "@/stores/samples";
const samples = useSamplesStore();
</script>

<template>
  <main>
    <Item>
      <template #icon>
        <DocumentationIcon />
      </template>
      <template #heading>This week</template>
      <p>{{ samples.samples.length }} samples have been requested so far:</p>
      <table>
        <tr>
          <th>Primary Key</th>
          <th>Email</th>
          <th>Sample Name</th>
          <th>Requested on</th>
        </tr>
        <tr v-for="sample in samples.samples" :key="sample.index">
          <td>{{ sample["primary_key"] }}</td>
          <td>{{ sample["email"] }}</td>
          <td>{{ sample["name"] }}</td>
          <td>{{ sample["date"].toUTCString() }}</td>
        </tr>
      </table>
    </Item>
  </main>
</template>
