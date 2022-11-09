<script setup lang="ts">
import { computed, ref } from "vue";
import Item from "@/components/ListItem.vue";
import { apiClient, download_reference_sequence } from "@/api-client";
import type { Sample } from "@/types";
const new_sample_name = ref("");
const selected_file = ref(null as null | Blob);

function on_file_changed(event: Event) {
  const target = event.target as HTMLInputElement;
  if (target.files != null && target.files.length > 0) {
    selected_file.value = target.files[0];
  } else {
    selected_file.value = null;
  }
  if (
    selected_file.value != null &&
    selected_file.value.size > 1024 * 1024 * 4
  ) {
    window.alert(
      "File is too large: maximum reference sequence file size is 4MB"
    );
  }
}

function duplicate_sample_name(sample_name: string) {
  return current_samples.value.some((e) => e.name === sample_name);
}

function invalid_sample_name(sample_name: string) {
  // only alphanumeric characters or underscores
  const re = /^([A-Za-z0-9_]+)$/;
  return !re.test(sample_name);
}

const new_sample_name_message = computed(() => {
  if (duplicate_sample_name(new_sample_name.value)) {
    return "Sample name already used";
  } else if (invalid_sample_name(new_sample_name.value)) {
    return "Only alphanumeric characters and underscores allowed";
  } else {
    return "";
  }
});

const current_samples = ref([] as Sample[]);
const previous_samples = ref([] as Sample[]);

apiClient
  .get("samples")
  .then((response) => {
    current_samples.value = response.data.current_samples;
    previous_samples.value = response.data.previous_samples;
  })
  .catch((error) => {
    console.log(error);
  });

function add_sample() {
  let formData = new FormData();
  formData.append("name", new_sample_name.value);
  if (selected_file.value !== null) {
    formData.append("file", selected_file.value);
  }
  apiClient
    .post("addsample", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    })
    .then((response) => {
      current_samples.value.push(response.data.sample);
    });
  new_sample_name.value = "";
  selected_file.value = null;
}
</script>
<template>
  <main>
    <Item>
      <template #icon>
        <i class="bi-clipboard-data"></i>
      </template>
      <template #heading>My samples</template>
      <template v-if="current_samples.length > 0">
        <p>Your samples for this week:</p>
        <table class="zebra">
          <tr>
            <th>Primary Key</th>
            <th>Sample Name</th>
            <th>Reference Sequence</th>
          </tr>
          <tr v-for="sample in current_samples" :key="sample.id">
            <td>{{ sample["primary_key"] }}</td>
            <td>{{ sample["name"] }}</td>
            <td>
              <template v-if="sample['reference_sequence_description']">
                <a
                  href=""
                  @click.prevent="
                    download_reference_sequence(sample['primary_key'])
                  "
                >
                  {{ sample["reference_sequence_description"] }}
                </a>
              </template>
              <template v-else> - </template>
            </td>
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
      <p>
        To submit a new sample, enter a sample name, and optionally upload a
        fasta file containing a reference sequence:
      </p>
      <table>
        <tr>
          <td style="text-align: right">Sample name:</td>
          <td>
            <input
              v-model="new_sample_name"
              placeholder="pXYZ_ABC_c1"
              maxlength="128"
              :title="new_sample_name_message"
            />
          </td>
          <td style="font-style: italic">
            <template v-if="new_sample_name">
              {{ new_sample_name_message }}
            </template>
          </td>
        </tr>
        <tr>
          <td style="text-align: right">Reference sequence (optional):</td>
          <td>
            <input
              type="file"
              name="file"
              @change="on_file_changed($event)"
              title="Optionally upload a fasta file reference sequence"
            />
          </td>
        </tr>
        <tr>
          <td></td>
          <td>
            <button
              @click="add_sample"
              :disabled="new_sample_name_message.length > 0"
              :title="new_sample_name_message"
            >
              Request Sample
            </button>
          </td>
        </tr>
      </table>
    </Item>
    <Item>
      <template #icon>
        <i class="bi-clipboard-data"></i>
      </template>
      <template #heading>Results</template>
      <template v-if="previous_samples.length > 0">
        <p>Results from your previous samples:</p>
        <table class="zebra">
          <tr>
            <th>Date</th>
            <th>Primary Key</th>
            <th>Sample Name</th>
            <th>Reference Sequence</th>
          </tr>
          <tr v-for="sample in previous_samples" :key="sample.id">
            <td>{{ new Date(sample["date"]).toLocaleDateString("en-CA") }}</td>
            <td>{{ sample["primary_key"] }}</td>
            <td>{{ sample["name"] }}</td>
            <td>
              <template v-if="sample['reference_sequence_description']">
                <a
                  href=""
                  @click.prevent="
                    download_reference_sequence(sample['primary_key'])
                  "
                >
                  {{ sample["reference_sequence_description"] }}
                </a>
              </template>
              <template v-else> - </template>
            </td>
          </tr>
        </table>
      </template>
      <template v-else>
        <p>No previous samples.</p>
      </template>
    </Item>
  </main>
</template>
