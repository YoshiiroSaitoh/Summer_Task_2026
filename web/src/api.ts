import type { ErrorResponse, Experiment, ExperimentProbe, ExperimentRun, Probe } from './types';

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8080';

async function requestJson<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${apiBaseUrl}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(init?.headers ?? {}),
    },
    ...init,
  });

  if (!response.ok) {
    let message = `${response.status} ${response.statusText}`;
    try {
      const payload = (await response.json()) as ErrorResponse;
      if (payload.message) {
        message = payload.message;
      }
    } catch {
      // ignore parse failures
    }
    throw new Error(message);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return (await response.json()) as T;
}

export interface CreateExperimentPayload {
  name: string;
}

export interface CreateRunPayload {
  label: string;
}

export interface CreateProbePayload {
  probe_id: string;
  role: string;
  valid_from?: string | null;
  valid_to?: string | null;
}

export function listExperiments(): Promise<Experiment[]> {
  return requestJson<Experiment[]>('/experiments');
}

export function listProbes(): Promise<Probe[]> {
  return requestJson<Probe[]>('/probes');
}

export function deleteProbe(probeId: string): Promise<void> {
  return requestJson<void>(`/probes/${encodeURIComponent(probeId)}`, {
    method: 'DELETE',
  });
}

export function getExperiment(experimentId: number): Promise<Experiment> {
  return requestJson<Experiment>(`/experiments/${experimentId}`);
}

export function createExperiment(payload: CreateExperimentPayload): Promise<Experiment> {
  return requestJson<Experiment>('/experiments', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function getCurrentExperiment(): Promise<Experiment> {
  return requestJson<Experiment>('/experiments/current');
}

export function startExperiment(experimentId: number): Promise<Experiment> {
  return requestJson<Experiment>(`/experiments/${experimentId}/start`, {
    method: 'POST',
  });
}

export function endExperiment(experimentId: number): Promise<Experiment> {
  return requestJson<Experiment>(`/experiments/${experimentId}/end`, {
    method: 'POST',
  });
}

export function listExperimentRuns(experimentId: number): Promise<ExperimentRun[]> {
  return requestJson<ExperimentRun[]>(`/experiments/${experimentId}/runs`);
}

export function createExperimentRun(experimentId: number, payload: CreateRunPayload): Promise<ExperimentRun> {
  return requestJson<ExperimentRun>(`/experiments/${experimentId}/runs`, {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function getCurrentExperimentRun(experimentId: number): Promise<ExperimentRun> {
  return requestJson<ExperimentRun>(`/experiments/${experimentId}/runs/current`);
}

export function endExperimentRun(experimentId: number, runId: number): Promise<ExperimentRun> {
  return requestJson<ExperimentRun>(`/experiments/${experimentId}/runs/${runId}/end`, {
    method: 'POST',
  });
}

export function listExperimentProbes(experimentId: number): Promise<ExperimentProbe[]> {
  return requestJson<ExperimentProbe[]>(`/experiments/${experimentId}/probes`);
}

export function addExperimentProbe(experimentId: number, payload: CreateProbePayload): Promise<ExperimentProbe> {
  return requestJson<ExperimentProbe>(`/experiments/${experimentId}/probes`, {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}
