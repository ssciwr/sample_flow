<script setup lang="ts">
import { ref } from "vue";
import Item from "@/components/ListItem.vue";
import IconData from "@/components/icons/IconData.vue";
import IconPlus from "@/components/icons/IconPlus.vue";
import { useSamplesStore } from "@/stores/samples";
import { useUserStore } from "@/stores/user";
const samples = useSamplesStore();
const user = useUserStore();
const new_sample_name = ref("");

function add() {
  samples.add_sample(new_sample_name.value, user.email);
  new_sample_name.value = "";
}
</script>

<template>
  <main>
    <Item>
      <template #icon>
        <IconData />
      </template>
      <template #heading>My samples</template>
      <template v-if="samples.get_samples(user.email).length > 0">
        <p>Your samples for this week:</p>
        <table>
          <tr>
            <th>Primary Key</th>
            <th>Sample Name</th>
          </tr>
          <tr
            v-for="sample in samples.get_samples(user.email)"
            :key="sample.index"
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
        <IconPlus />
      </template>
      <template #heading>Submit a sample</template>
      <p>To submit a new sample, enter a sample name:</p>
      <input v-model="new_sample_name" placeholder="sample name" />
      <button @click="add">Request Sample</button>
    </Item>
  </main>
</template>
