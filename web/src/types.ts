export type ExperimentStatus = 'planned' | 'running' | 'completed' | 'archived' | 'finished';

export interface Experiment {
  id: number;
  name: string;
  description: string | null;
  status: ExperimentStatus;
  started_at: string | null;
  ended_at: string | null;
  completed_at: string | null;
  archived_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface ExperimentRun {
  id: number;
  experiment_id: number;
  label: string;
  started_at: string | null;
  ended_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface ExperimentRunProbe {
  id: number;
  experiment_run_id: number;
  probe_id: string;
  role: string;
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
