<script setup lang="ts">
import Item from "@/components/ListItem.vue";
import DocumentationIcon from "@/components/icons/IconDocumentation.vue";
import CommunityIcon from "@/components/icons/IconCommunity.vue";
import { useSamplesStore } from "@/stores/samples";
const samples = useSamplesStore();
</script>

<template>
  <main>
    <Item>
      <template #icon>
        <DocumentationIcon />
      </template>
      <template #heading>About</template>
      <p>
        The CircuitSEQ project is a trial service offering sequencing of DNA
        samples.
      </p>
      <ul>
        <li>Samples must be submitted by Wednesday each week.</li>
        <li>Results will be available on Friday.</li>
        <li>
          Remaining available samples this week: {{ samples.num_remaining() }}.
        </li>
      </ul>
    </Item>
    <Item>
      <template #icon>
        <CommunityIcon />
      </template>
      <template #heading>Feedback</template>
      Questions or feedback about this service are welcome at
      <a href="mailto:email@address.com">email@address.com</a>
    </Item>
  </main>
</template>
