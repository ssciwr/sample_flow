<script setup lang="ts">
import Item from "@/components/ListItem.vue";
import IconLightbulb from "@/components/icons/IconLightbulb.vue";
import IconInfo from "@/components/icons/IconInfo.vue";
import IconChat from "@/components/icons/IconChat.vue";
import { useSamplesStore } from "@/stores/samples";
const samples = useSamplesStore();
</script>

<template>
  <main>
    <Item>
      <template #icon>
        <IconLightbulb />
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
        <IconChat />
      </template>
      <template #heading>Feedback</template>
      Questions or feedback about this service are welcome at
      <a href="mailto:e.green@dkfz.de?subject=circuitSEQ">e.green@dkfz.de</a>
    </Item>
    <Item>
      <template #icon>
        <IconInfo />
      </template>
      <template #heading>Funding</template>
      This work was funded by the
      <a href="https://www.health-life-sciences.de/?lang=de"
        >Heidelberg Mannheim Life Sciences alliance</a
      >
      through an 'Explore!Tech' grant awarded to Drs Ed Green, Liam Keegan and
      Kim Remans.
    </Item>
  </main>
</template>
