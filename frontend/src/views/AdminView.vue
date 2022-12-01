<script setup lang="ts">
import ListItem from "@/components/ListItem.vue";
import { ref, computed } from "vue";
import type { Sample, User, Settings } from "@/utils/types";
import {
  apiClient,
  download_zipsamples,
  download_reference_sequence,
  download_result,
} from "@/utils/api-client";

function generate_api_token() {
  apiClient.get("admin/token").then((response) => {
    navigator.clipboard
      .writeText(response.data.access_token)
      .then(() => {
        console.log("API token copied to clipboard");
      })
      .catch(() => {
        console.log("Failed to copy API token to clipboard");
      });
  });
}

const current_samples = ref([] as Sample[]);
const previous_samples = ref([] as Sample[]);

apiClient.get("admin/samples").then((response) => {
  current_samples.value = response.data.current_samples;
  previous_samples.value = response.data.previous_samples;
});

const users = ref([] as User[]);
apiClient.get("admin/users").then((response) => {
  users.value = response.data.users;
});

const settings = ref({} as Settings);
const days = [1, 2, 3, 4, 5, 6, 7];
const last_submission_day = ref(1);
const new_running_option = ref("");
const settings_message = ref("");
apiClient.get("admin/settings").then((response) => {
  settings.value = response.data;
  last_submission_day.value = settings.value.last_submission_day;
});

function add_running_option() {
  settings.value.running_options.push(new_running_option.value);
  new_running_option.value = "";
}

function remove_running_option(option: string) {
  settings.value.running_options = settings.value.running_options.filter(
    (t) => t !== option
  );
}

function update_n_rows(event: Event) {
  const target = event.target as HTMLInputElement;
  settings.value.plate_n_rows = Number(target.value);
}

function update_n_cols(event: Event) {
  const target = event.target as HTMLInputElement;
  settings.value.plate_n_cols = Number(target.value);
}

const plate_range_string = computed(() => {
  return `A1 ... ${String.fromCharCode(settings.value.plate_n_rows + 64)}${
    settings.value.plate_n_cols
  }`;
});

function save_settings() {
  settings.value.last_submission_day = Number(last_submission_day.value);
  apiClient
    .post("admin/settings", settings.value)
    .then((response) => {
      settings_message.value = response.data.message;
    })
    .catch((error) => {
      settings_message.value = error.response.data.message;
    });
}

const upload_result_message = ref("");

function upload_result(event: Event) {
  const target = event.target as HTMLInputElement;
  if (target.files != null && target.files.length > 0) {
    let formData = new FormData();
    formData.append("file", target.files[0]);
    apiClient
      .post("admin/result", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      })
      .then((response) => {
        upload_result_message.value = response.data.message;
      })
      .catch((error) => {
        upload_result_message.value = error.response.data.message;
      });
  }
}
</script>

<template>
  <main>
    <ListItem title="Samples this week" icon="bi-gear">
      <p>{{ current_samples.length }} samples have been requested so far:</p>
      <table class="zebra">
        <tr>
          <th>Date</th>
          <th>Primary Key</th>
          <th>Email</th>
          <th>Sample Name</th>
          <th>Running Option</th>
          <th>Reference Sequence</th>
        </tr>
        <tr v-for="sample in current_samples" :key="sample.id">
          <td>{{ new Date(sample["date"]).toLocaleDateString("en-CA") }}</td>
          <td>{{ sample["primary_key"] }}</td>
          <td>{{ sample["email"] }}</td>
          <td>{{ sample["name"] }}</td>
          <td>{{ sample["running_option"] }}</td>
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
      <p>
        <a href="" @click.prevent="download_zipsamples()">
          Download as zipfile
        </a>
      </p>
    </ListItem>
    <ListItem title="Upload result" icon="bi-gear">
      <p>Upload a result zipfile:</p>
      <p><input type="file" name="file" @change="upload_result($event)" /></p>
      <p style="font-style: italic">
        {{ upload_result_message }}
      </p>
    </ListItem>
    <ListItem title="Generate API Token" icon="bi-gear">
      <p>
        Here you can generate an admin API token to interact programmatically
        with the backend. Note this token should be kept secret! It is valid for
        6 months, then you will need to generate a new one.
      </p>
      <p>
        <button @click="generate_api_token">
          Generate API Token and copy to clipboard
        </button>
      </p>
    </ListItem>
    <ListItem title="Settings" icon="bi-gear">
      <table>
        <tr>
          <td>Plate num rows:</td>
          <td>
            <input
              type="number"
              min="1"
              :value="settings.plate_n_rows"
              @change="update_n_rows"
            />
          </td>
        </tr>
        <tr>
          <td>Plate num cols:</td>
          <td>
            <input
              type="number"
              min="1"
              :value="settings.plate_n_cols"
              @change="update_n_cols"
            />
          </td>
        </tr>
        <tr>
          <td>Plate indices:</td>
          <td>{{ plate_range_string }}</td>
        </tr>
        <tr>
          <td>Running options:</td>
          <td>
            <ul>
              <li v-for="option in settings.running_options">
                {{ option }}
                <button @click="remove_running_option(option)">x</button>
              </li>
              <li>
                <form @submit.prevent="add_running_option">
                  <input v-model="new_running_option" maxlength="256" />
                  <button>add</button>
                </form>
              </li>
            </ul>
          </td>
        </tr>
        <tr>
          <td>Last submission day (1=mon):</td>
          <td>
            <select v-model="last_submission_day">
              <option v-for="day in days">{{ day }}</option>
            </select>
          </td>
        </tr>
        <tr>
          <td></td>
          <td>
            <button @click="save_settings">Save Settings</button>
          </td>
        </tr>
      </table>
      <p style="font-style: italic">
        {{ settings_message }}
      </p>
    </ListItem>
    <ListItem title="Previous samples" icon="bi-gear">
      <table class="zebra">
        <tr>
          <th>Date</th>
          <th>Primary Key</th>
          <th>Email</th>
          <th>Sample Name</th>
          <th>Running Option</th>
          <th>Reference Sequence</th>
          <th>Results</th>
        </tr>
        <tr v-for="sample in previous_samples" :key="sample.id">
          <td>{{ new Date(sample["date"]).toLocaleDateString("en-CA") }}</td>
          <td>{{ sample["primary_key"] }}</td>
          <td>{{ sample["email"] }}</td>
          <td>{{ sample["name"] }}</td>
          <td>{{ sample["running_option"] }}</td>
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
    </ListItem>
    <ListItem title="Users" icon="bi-gear">
      <p>{{ users.length }} registered users:</p>
      <table class="zebra">
        <tr>
          <th>Id</th>
          <th>Email</th>
          <th>Activated</th>
          <th>Admin</th>
        </tr>
        <tr v-for="user in users" :key="user.id">
          <td>{{ user["id"] }}</td>
          <td>{{ user["email"] }}</td>
          <td>{{ user["activated"] }}</td>
          <td>{{ user["is_admin"] }}</td>
        </tr>
      </table>
    </ListItem>
  </main>
</template>
