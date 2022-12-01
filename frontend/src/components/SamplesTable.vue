<script setup lang="ts">
import {
  download_reference_sequence,
  download_result,
} from "@/utils/api-client";
import type { Sample } from "@/utils/types";

defineProps<{
  samples: Sample[];
}>();
</script>

<template>
  <table class="zebra">
    <tr>
      <th>Primary Key</th>
      <th>Sample Name</th>
      <th>Running Option</th>
      <th>Reference Sequence</th>
      <th>Results</th>
    </tr>
    <tr v-for="sample in samples" :key="sample.id">
      <td>{{ sample["primary_key"] }}</td>
      <td>{{ sample["name"] }}</td>
      <td>{{ sample["running_option"] }}</td>
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
