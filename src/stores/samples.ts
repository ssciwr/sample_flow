import { ref } from "vue";
import { defineStore } from "pinia";
import type { Sample } from "@/types";

export const useSamplesStore = defineStore("samples", () => {
  const week = 1;
  const max_samples = 96;
  const row_labels = ["A", "B", "C", "D", "E", "F", "G", "H"];
  const n_columns = max_samples / row_labels.length;
  console.assert(Number.isInteger(n_columns));
  const samples = ref([] as Sample[]);
  function get_label(index: number) {
    console.assert(Number.isInteger(index));
    const i_row = Math.floor(index / n_columns);
    const i_col = index % n_columns;
    const col_label = (i_col + 1).toString();
    return row_labels[i_row] + col_label;
  }
  function get_primary_key(week: number, label: string) {
    console.assert(Number.isInteger(week));
    return week.toString() + "_" + label;
  }
  function num_remaining() {
    return max_samples - samples.value.length;
  }
  function get_samples(email: string) {
    return samples.value.filter((s) => s["email"] == email);
  }
  function add_sample(sample_name: string, email: string) {
    const index = samples.value.length;
    const label = get_label(index);
    const primary_key = get_primary_key(week, label);
    samples.value.push({
      index: index,
      label: label,
      primary_key: primary_key,
      name: sample_name,
      email: email,
      date: new Date(),
    });
    return samples.value.length;
  }
  return { samples, add_sample, num_remaining, get_samples };
});
