import { ref } from "vue";
import { defineStore } from "pinia";

export const useSamplesStore = defineStore("samples", () => {
  const max_samples = 96;
  const row_labels = ["A", "B", "C", "D", "E", "F", "G", "H"];
  const n_columns = max_samples / row_labels.length;
  const samples = ref([] as object[]);
  function remaining() {
    return max_samples - samples.value.length;
  }
  function get(name: string) {
    const id = samples.value.length;
    // i_label = Math.floor(id/n_columns)id
    samples.value.push({"name": name});
    return samples.value.length;
  }

  return { samples, remaining, get };
});
