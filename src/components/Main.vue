<script setup lang="ts">
import Item from "./Item.vue";
import DocumentationIcon from "./icons/IconDocumentation.vue";
import ToolingIcon from "./icons/IconTooling.vue";
import CommunityIcon from "./icons/IconCommunity.vue";
import {useSamplesStore} from "@/stores/samples";
const samples = useSamplesStore();

function gets(){
  samples.get("OK");
}

</script>

<template>
  <Item>
    <template #icon>
      <DocumentationIcon />
    </template>
    <template #heading>About</template>
    The CircuitSEQ project is a trial service offering sequencing of DNA samples.
  </Item>

  <Item>
    <template #icon>
      <ToolingIcon />
    </template>
    <template #heading>Submit a sample</template>
    <p>Remaining samples this week: {{samples.remaining()}}</p>
    <ul><li>get a code</li></ul>
    <button @click="gets">Request Sample</button>
  </Item>
  <Item>
    <template #icon>
      <CommunityIcon />
    </template>
    <template #heading>Feedback</template>
    Questions or feedback about this service are welcome.
  </Item>
</template>
