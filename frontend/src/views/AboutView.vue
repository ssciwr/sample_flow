<script setup lang="ts">
import ListItem from "@/components/ListItem.vue";
import { ref } from "vue";
import { apiClient } from "@/utils/api-client";
const remaining = ref(0);
const remaining_message = ref("");
apiClient
  .get("remaining")
  .then((response) => {
    remaining.value = response.data.remaining;
    remaining_message.value = response.data.message;
  })
  .catch((error) => {
    console.log("Could not connect to server");
  });
</script>

<template>
  <main>
    <ListItem title="About" icon="bi-lightbulb">
      <p>
        The CircuitSEQ project is a trial service offering sequencing of DNA
        samples.
      </p>
      <ul>
        <li>Samples must be submitted by Wednesday each week</li>
        <ul>
          <li>via a letter box at H2.06.053.</li>
          <li>in eppendorf 1.5 ml microtubes.</li>
          <li>
            with a concentration between 143 ng/μl (at least 7 μl sample) and
            1000 ng/μl (at least 1 μl sample).
          </li>
        </ul>
        <li>Results will be available on Friday.</li>
        <template v-if="remaining_message">
          <li>{{ remaining_message }} Please try again on Monday.</li>
        </template>
        <template v-else>
          <li>Remaining available samples this week: {{ remaining }}.</li>
        </template>
      </ul>
    </ListItem>
    <ListItem title="Feedback" icon="bi-chat">
      Questions or feedback about this service are welcome at
      <a href="mailto:e.green@dkfz.de?subject=circuitSEQ">e.green@dkfz.de</a>
    </ListItem>
    <ListItem title="References" icon="bi-book">
      <p>
        This software implements a variant of the Circuit-seq method published
        by the McKenna lab:
        <a href="https://pubs.acs.org/doi/pdf/10.1021/acssynbio.2c00126"
          >ACS Synth. Biol. 2022, 11, 2238−2246</a
        >.
      </p>
      <p>
        The <a href="https://github.com/ssciwr/circuit_seq">web service</a> was
        developed by the
        <a href="https://ssc.iwr.uni-heidelberg.de/"
          >Scientific Software Center</a
        >
        of Heidelberg University.
      </p>
    </ListItem>
    <ListItem title="Funding" icon="bi-info-circle">
      This work was funded by the
      <a href="https://www.health-life-sciences.de/?lang=de"
        >Heidelberg Mannheim Life Sciences alliance</a
      >
      through an 'Explore!Tech' grant awarded to Drs Ed Green, Liam Keegan and
      Kim Remans.
    </ListItem>
  </main>
</template>
