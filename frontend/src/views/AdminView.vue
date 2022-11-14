<script setup lang="ts">
import Item from "@/components/ListItem.vue";
import { ref, computed } from "vue";
import type { Sample, User, Settings } from "@/utils/types";
import {
  apiClient,
  download_zipsamples,
  download_reference_sequence,
} from "@/utils/api-client";

const current_samples = ref([] as Sample[]);
const previous_samples = ref([] as Sample[]);

apiClient.get("admin/allsamples").then((response) => {
  current_samples.value = response.data.current_samples;
  previous_samples.value = response.data.previous_samples;
});

const users = ref([] as User[]);
apiClient.get("admin/allusers").then((response) => {
  users.value = response.data.users;
});

const settings = ref({} as Settings);
const settings_message = ref("");
apiClient.get("admin/settings").then((response) => {
  settings.value = response.data;
});

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
  apiClient
    .post("admin/settings", settings.value)
    .then((response) => {
      settings_message.value = response.data.message;
    })
    .catch((error) => {
      settings_message.value = error.response.data.message;
    });
}
</script>

<template>
  <main>
    <Item>
      <template #icon>
        <i class="bi-gear"></i>
      </template>
      <template #heading>Samples this week</template>
      <p>{{ current_samples.length }} samples have been requested so far:</p>
      <table class="zebra">
        <tr>
          <th>Date</th>
          <th>Primary Key</th>
          <th>Email</th>
          <th>Sample Name</th>
          <th>Reference Sequence</th>
        </tr>
        <tr v-for="sample in current_samples" :key="sample.id">
          <td>{{ new Date(sample["date"]).toLocaleDateString("en-CA") }}</td>
          <td>{{ sample["primary_key"] }}</td>
          <td>{{ sample["email"] }}</td>
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
      <p>
        <a href="" @click.prevent="download_zipsamples()">
          Download as zipfile
        </a>
      </p>
    </Item>
    <Item>
      <template #icon>
        <i class="bi-gear"></i>
      </template>
      <template #heading>Settings</template>
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
          <td></td>
          <td>
            <button @click="save_settings">Save Settings</button>
          </td>
        </tr>
      </table>
      <p style="font-style: italic">
        {{ settings_message }}
      </p>
    </Item>
    <Item>
      <template #icon>
        <i class="bi-gear"></i>
      </template>
      <template #heading>Previous samples</template>
      <table class="zebra">
        <tr>
          <th>Date</th>
          <th>Primary Key</th>
          <th>Email</th>
          <th>Sample Name</th>
          <th>Reference Sequence</th>
        </tr>
        <tr v-for="sample in previous_samples" :key="sample.id">
          <td>{{ new Date(sample["date"]).toLocaleDateString("en-CA") }}</td>
          <td>{{ sample["primary_key"] }}</td>
          <td>{{ sample["email"] }}</td>
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
    </Item>
    <Item>
      <template #icon>
        <i class="bi-gear"></i>
      </template>
      <template #heading>Users</template>
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
    </Item>
  </main>
</template>
