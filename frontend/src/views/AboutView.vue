<script setup lang="ts">
import Item from "@/components/ListItem.vue";
import { ref } from "vue";
import { apiClient } from "@/utils/api-client";
const remaining = ref(0);
apiClient
  .get("remaining")
  .then((response) => {
    console.log(response);
    remaining.value = response.data.remaining;
  })
  .catch((error) => {
    console.log("Could not connect to server");
  });
</script>

<template>
  <main>
    <Item>
      <template #icon>
        <i class="bi-lightbulb"></i>
      </template>
      <template #heading>About</template>
      <p>
        The CircuitSEQ project is a trial service offering sequencing of DNA
        samples.
      </p>
      <ul>
        <li>Samples must be submitted by Wednesday each week.</li>
        <li>Results will be available on Friday.</li>
        <li>Remaining available samples this week: {{ remaining }}.</li>
      </ul>
    </Item>
    <Item>
      <template #icon>
        <i class="bi-chat"></i>
      </template>
      <template #heading>Feedback</template>
      Questions or feedback about this service are welcome at
      <a href="mailto:e.green@dkfz.de?subject=circuitSEQ">e.green@dkfz.de</a>
    </Item>
    <Item>
      <template #icon>
        <i class="bi-book"></i>
      </template>
      <template #heading>References</template>
      This software implements a variant of the Circuit-seq method published by
      the McKenna lab:
      <a href="https://pubs.acs.org/doi/pdf/10.1021/acssynbio.2c00126"
        >ACS Synth. Biol. 2022, 11, 2238−2246</a
      >
    </Item>
    <Item>
      <template #icon>
        <i class="bi-info-circle"></i>
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
