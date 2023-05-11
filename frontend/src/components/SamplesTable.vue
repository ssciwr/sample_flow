<script setup lang="ts">
import {
  download_reference_sequence,
  download_result,
} from "@/utils/api-client";
import type { Sample } from "@/utils/types";
import BarCode from "@/components/BarCode.vue";

defineProps<{
  samples: Sample[];
  show_email: boolean;
}>();
</script>

<template>
  <table class="zebra" aria-label="Samples">
    <tr>
      <th>Primary Key</th>
      <th v-if="show_email">Email</th>
      <th>Sample Name</th>
      <th>Running Option</th>
      <th>Concentration</th>
      <th>Reference Sequence</th>
      <th>Results</th>
    </tr>
    <tr v-for="sample in samples" :key="sample.id">
      <td>
        <template v-if="show_email">{{ sample["primary_key"] }}</template>
        <template v-else>
          <BarCode :value="sample['primary_key']"></BarCode>
        </template>
      </td>
      <td v-if="show_email">{{ sample["email"] }}</td>
      <td>{{ sample["name"] }}</td>
      <td>{{ sample["running_option"] }}</td>
      <td>{{ sample["concentration"] }} ng/μl</td>
      <td>
        <template v-if="sample['reference_sequence_description']">
          <a
            href=""
            @click.prevent="download_reference_sequence(sample['primary_key'])"
          >
            {{ sample["reference_sequence_description"] }}
          </a>
        </template>
        <template v-else> - </template>
      </td>
      <td>
        <template
          v-if="
            !(
              sample.has_results_fasta ||
              sample.has_results_gbk ||
              sample.has_results_zip
            )
          "
        >
          -
        </template>
        <template v-else>
          <template v-if="sample.has_results_fasta">
            <a
              href=""
              @click.prevent="download_result(sample.primary_key, 'fasta')"
              >fasta</a
            >
            |
          </template>
          <template v-if="sample.has_results_gbk">
            <a
              href=""
              @click.prevent="download_result(sample.primary_key, 'gbk')"
              >gbk</a
            >
            |
          </template>
          <template v-if="sample.has_results_zip">
            <a
              href=""
              @click.prevent="download_result(sample.primary_key, 'zip')"
              >zip</a
            >
          </template>
        </template>
      </td>
    </tr>
  </table>
</template>
