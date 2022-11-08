export type Sample = {
  id: number;
  // label: string;
  primary_key: string;
  name: string;
  email: string;
  reference_sequence_description: string | null;
  date: string;
};

export type User = {
  id: number;
  email: string;
  activated: boolean;
  is_admin: boolean;
};

export type Settings = {
  plate_n_rows: number;
  plate_n_cols: number;
};
