export type ExperimentStatus = 'planned' | 'running' | 'finished';

export interface Experiment {
  id: number;
  name: string;
  status: ExperimentStatus;
  started_at: string | null;
  ended_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface ExperimentRun {
  id: number;
  experiment_id: number;
  label: string;
  started_at: string;
  ended_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface ExperimentProbe {
  id: number;
  experiment_id: number;
  probe_id: string;
  role: string;
  valid_from: string | null;
  valid_to: string | null;
  created_at: string;
  updated_at: string;
}

export interface Probe {
  id: number;
  probe_id: string;
  deleted_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface TemperatureLog {
  id: number;
  experiment_id: number | null;
  experiment_run_id: number | null;
  probe_id: string;
  recorded_at: string;
  elapsed_seconds: number | null;
  temperature: number;
}

export interface ErrorResponse {
  message?: string;
}
