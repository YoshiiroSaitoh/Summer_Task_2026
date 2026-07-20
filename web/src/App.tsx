import { useCallback, useEffect, useMemo, useState } from 'react';
import {
  addExperimentProbe,
  createExperiment,
  createExperimentRun,
  deleteProbe,
  endExperiment,
  endExperimentRun,
  getCurrentExperimentRun,
  getExperiment,
  listExperimentProbes,
  listExperimentRuns,
  listExperiments,
  listProbes,
  startExperiment,
} from './api';
import type { Experiment, ExperimentProbe, ExperimentRun, Probe } from './types';

type AppPage = { kind: 'list' } | { kind: 'detail'; experimentId: number } | { kind: 'probes' };

function formatDateTime(value: string | null | undefined): string {
  if (!value) {
    return '-';
  }
  return new Date(value).toLocaleString('ja-JP');
}

function statusLabel(status: string): string {
  switch (status) {
    case 'planned':
      return 'Planned';
    case 'running':
      return 'Running';
    case 'finished':
      return 'Finished';
    default:
      return status;
  }
}

function readPageFromLocation(): AppPage {
  if (window.location.pathname === '/probes') {
    return { kind: 'probes' };
  }

  const match = window.location.pathname.match(/^\/experiments\/(\d+)\/?$/);
  if (match) {
    return { kind: 'detail', experimentId: Number(match[1]) };
  }

  return { kind: 'list' };
}

function buildExperimentPath(experimentId: number): string {
  return `/experiments/${experimentId}`;
}

export default function App() {
  const [page, setPage] = useState<AppPage>(() => readPageFromLocation());
  const [experiments, setExperiments] = useState<Experiment[]>([]);
  const [detailExperiment, setDetailExperiment] = useState<Experiment | null>(null);
  const [runs, setRuns] = useState<ExperimentRun[]>([]);
  const [currentRun, setCurrentRun] = useState<ExperimentRun | null>(null);
  const [probes, setProbes] = useState<ExperimentProbe[]>([]);
  const [managedProbes, setManagedProbes] = useState<Probe[]>([]);
  const [selectedProbeId, setSelectedProbeId] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [newExperimentName, setNewExperimentName] = useState('');
  const [newRunLabel, setNewRunLabel] = useState('');
  const [newProbeId, setNewProbeId] = useState('');
  const [newProbeRole, setNewProbeRole] = useState('main');
  const [newProbeValidFrom, setNewProbeValidFrom] = useState('');
  const [newProbeValidTo, setNewProbeValidTo] = useState('');

  const selectedExperiment = useMemo(() => {
    if (page.kind !== 'detail') {
      return null;
    }
    return detailExperiment ?? experiments.find((experiment) => experiment.id === page.experimentId) ?? null;
  }, [detailExperiment, experiments, page]);

  const refreshDetail = useCallback(async (experimentId: number) => {
    const [detail, runItems, probeItems, activeRun] = await Promise.all([
      getExperiment(experimentId),
      listExperimentRuns(experimentId),
      listExperimentProbes(experimentId),
      getCurrentExperimentRun(experimentId).catch(() => null),
    ]);

    setDetailExperiment(detail);
    setRuns(runItems);
    setProbes(probeItems);
    setCurrentRun(activeRun);
  }, []);

  const refreshPage = useCallback(
    async (nextPage: AppPage) => {
      setLoading(true);
      setError(null);
      try {
        const [experimentItems, managedProbeItems] = await Promise.all([
          listExperiments(),
          nextPage.kind === 'probes' ? listProbes() : Promise.resolve([] as Probe[]),
        ]);
        setExperiments(experimentItems);
        setManagedProbes(managedProbeItems);
        if (nextPage.kind === 'detail') {
          await refreshDetail(nextPage.experimentId);
        } else {
          setDetailExperiment(null);
          setRuns([]);
          setCurrentRun(null);
          setProbes([]);
        }
        if (nextPage.kind === 'probes') {
          setSelectedProbeId((current) =>
            managedProbeItems.some((probe) => probe.probe_id === current) ? current : '',
          );
        } else {
          setSelectedProbeId('');
        }
      } catch (cause) {
        setError(cause instanceof Error ? cause.message : 'Failed to load data.');
      } finally {
        setLoading(false);
      }
    },
    [refreshDetail],
  );

  useEffect(() => {
    void refreshPage(page);
  }, [page, refreshPage]);

  useEffect(() => {
    const handlePopState = () => {
      setPage(readPageFromLocation());
    };

    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  }, []);

  function navigateTo(path: string) {
    if (window.location.pathname !== path) {
      window.history.pushState({}, '', path);
    }
    setPage(readPageFromLocation());
  }

  async function handleCreateExperiment() {
    const name = newExperimentName.trim();
    if (!name) {
      setError('Enter an experiment name.');
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const created = await createExperiment({ name });
      setNewExperimentName('');
      navigateTo(buildExperimentPath(created.id));
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : 'Failed to create experiment.');
      setLoading(false);
    }
  }

  async function handleStartExperiment(experimentId: number) {
    setLoading(true);
    setError(null);
    try {
      await startExperiment(experimentId);
      await refreshPage(page);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : 'Failed to start experiment.');
      setLoading(false);
    }
  }

  async function handleEndExperiment(experimentId: number) {
    setLoading(true);
    setError(null);
    try {
      await endExperiment(experimentId);
      await refreshPage(page);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : 'Failed to end experiment.');
      setLoading(false);
    }
  }

  async function handleCreateRun() {
    if (page.kind !== 'detail') {
      return;
    }

    const label = newRunLabel.trim();
    if (!label) {
      setError('Enter a run label.');
      return;
    }

    setLoading(true);
    setError(null);
    try {
      await createExperimentRun(page.experimentId, { label });
      setNewRunLabel('');
      await refreshPage(page);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : 'Failed to create run.');
      setLoading(false);
    }
  }

  async function handleEndRun(runId: number) {
    if (page.kind !== 'detail') {
      return;
    }

    setLoading(true);
    setError(null);
    try {
      await endExperimentRun(page.experimentId, runId);
      await refreshPage(page);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : 'Failed to end run.');
      setLoading(false);
    }
  }

  async function handleAddProbe() {
    if (page.kind !== 'detail') {
      return;
    }

    const probeId = newProbeId.trim();
    const role = newProbeRole.trim();
    if (!probeId || !role) {
      setError('Enter probe_id and role.');
      return;
    }

    setLoading(true);
    setError(null);
    try {
      await addExperimentProbe(page.experimentId, {
        probe_id: probeId,
        role,
        valid_from: newProbeValidFrom ? new Date(newProbeValidFrom).toISOString() : null,
        valid_to: newProbeValidTo ? new Date(newProbeValidTo).toISOString() : null,
      });
      setNewProbeId('');
      setNewProbeRole('main');
      setNewProbeValidFrom('');
      setNewProbeValidTo('');
      await refreshPage(page);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : 'Failed to add probe assignment.');
      setLoading(false);
    }
  }

  async function handleDeleteProbe() {
    if (page.kind !== 'probes' || !selectedProbeId) {
      return;
    }

    setLoading(true);
    setError(null);
    try {
      await deleteProbe(selectedProbeId);
      await refreshPage(page);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : 'Failed to delete probe.');
      setLoading(false);
    }
  }

  const listSummary = experiments.length === 0 ? 'No experiments yet' : `${experiments.length} items`;

  return (
    <main className="app">
      <header className="hero">
        <div>
          <p className="eyebrow">Summer Task 2026</p>
          <h1>
            {page.kind === 'detail' ? 'Experiment Detail' : page.kind === 'probes' ? 'Probe Management' : 'Experiment List'}
          </h1>
          <p className="lead">
            {page.kind === 'detail'
              ? 'Probe assignments and runs are managed per experiment.'
              : page.kind === 'probes'
                ? 'Incoming measurements register probes automatically. Select one and soft-delete it from this list.'
                : 'Create experiments and jump to the detail page to manage probes and runs.'}
          </p>
        </div>
        <div className="page-actions">
          {page.kind === 'probes' ? (
            <button className="button secondary" onClick={() => navigateTo('/')} disabled={loading}>
              Back to experiments
            </button>
          ) : (
            <button className="button secondary" onClick={() => navigateTo('/probes')} disabled={loading}>
              Probe Management
            </button>
          )}
          {page.kind === 'detail' ? (
            <button className="button secondary" onClick={() => navigateTo('/')} disabled={loading}>
              Back to list
            </button>
          ) : null}
          <button className="button secondary" onClick={() => void refreshPage(page)} disabled={loading}>
            Reload
          </button>
        </div>
      </header>

      {error ? <section className="banner error">{error}</section> : null}

      {page.kind === 'list' ? (
        <>
          <section className="grid">
            <article className="card">
              <div className="card-header">
                <h2>Create Experiment</h2>
              </div>
              <div className="form-row">
                <input
                  value={newExperimentName}
                  onChange={(event) => setNewExperimentName(event.target.value)}
                  placeholder="Example: 2026-07 cooling test"
                />
                <button className="button" onClick={() => void handleCreateExperiment()} disabled={loading}>
                  Create
                </button>
              </div>
            </article>
          </section>

          <section className="grid wide">
            <article className="card">
              <div className="card-header">
                <h2>Experiments</h2>
                <span className="badge">{listSummary}</span>
              </div>
              <div className="table-wrap">
                <table>
                  <thead>
                    <tr>
                      <th>ID</th>
                      <th>Name</th>
                      <th>Status</th>
                      <th>Started</th>
                      <th>Ended</th>
                      <th />
                    </tr>
                  </thead>
                  <tbody>
                    {experiments.map((experiment) => (
                      <tr key={experiment.id}>
                        <td>{experiment.id}</td>
                        <td>{experiment.name}</td>
                        <td>
                          <span className={`badge status-${experiment.status}`}>{statusLabel(experiment.status)}</span>
                        </td>
                        <td>{formatDateTime(experiment.started_at)}</td>
                        <td>{formatDateTime(experiment.ended_at)}</td>
                        <td className="actions">
                          <button className="link" onClick={() => navigateTo(buildExperimentPath(experiment.id))}>
                            Open
                          </button>
                          <button className="link" onClick={() => void handleStartExperiment(experiment.id)} disabled={loading}>
                            Start
                          </button>
                          <button className="link" onClick={() => void handleEndExperiment(experiment.id)} disabled={loading}>
                            End
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </article>
          </section>
        </>
      ) : null}

      {page.kind === 'probes' ? (
        <section className="grid wide">
          <article className="card">
            <div className="card-header">
              <h2>Probe Registry</h2>
              <div className="card-tools">
                <span className="badge">{managedProbes.length} items</span>
                <button className="button secondary" onClick={() => void handleDeleteProbe()} disabled={!selectedProbeId || loading}>
                  Delete
                </button>
              </div>
            </div>
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th />
                    <th>Probe ID</th>
                    <th>First Seen</th>
                    <th>Last Seen</th>
                  </tr>
                </thead>
                <tbody>
                  {managedProbes.length === 0 ? (
                    <tr>
                      <td colSpan={4}>
                        <div className="empty-state">No probes yet. Sending temperature data will register them here.</div>
                      </td>
                    </tr>
                  ) : (
                    managedProbes.map((probe) => {
                      const isSelected = selectedProbeId === probe.probe_id;
                      return (
                        <tr key={probe.probe_id} className={isSelected ? 'selected' : undefined}>
                          <td className="radio-cell">
                            <input
                              type="radio"
                              name="selected-probe"
                              checked={isSelected}
                              onChange={() => setSelectedProbeId(probe.probe_id)}
                            />
                          </td>
                          <td>
                            <strong>{probe.probe_id}</strong>
                          </td>
                          <td>{formatDateTime(probe.created_at)}</td>
                          <td>{formatDateTime(probe.updated_at)}</td>
                        </tr>
                      );
                    })
                  )}
                </tbody>
              </table>
            </div>
          </article>
        </section>
      ) : null}

      {page.kind === 'detail' ? (
        <>
          <section className="grid">
            <article className="card">
              <div className="card-header">
                <h2>Selected Experiment</h2>
                <span className={`badge status-${selectedExperiment?.status ?? 'planned'}`}>
                  {selectedExperiment ? statusLabel(selectedExperiment.status) : 'Unselected'}
                </span>
              </div>
              <dl className="summary">
                <div>
                  <dt>ID</dt>
                  <dd>{selectedExperiment?.id ?? page.experimentId}</dd>
                </div>
                <div>
                  <dt>Name</dt>
                  <dd>{selectedExperiment?.name ?? '-'}</dd>
                </div>
                <div>
                  <dt>Started</dt>
                  <dd>{formatDateTime(selectedExperiment?.started_at)}</dd>
                </div>
                <div>
                  <dt>Ended</dt>
                  <dd>{formatDateTime(selectedExperiment?.ended_at)}</dd>
                </div>
              </dl>
            </article>

            <article className="card">
              <div className="card-header">
                <h2>Experiment Actions</h2>
              </div>
              <div className="stack compact">
                <button className="button" onClick={() => void handleStartExperiment(page.experimentId)} disabled={loading}>
                  Start Experiment
                </button>
                <button className="button secondary" onClick={() => void handleEndExperiment(page.experimentId)} disabled={loading}>
                  End Experiment
                </button>
              </div>
            </article>
          </section>

          <section className="grid">
            <article className="card">
              <div className="card-header">
                <h2>Probe List</h2>
                <span className="badge">{probes.length} items</span>
              </div>
              <div className="stack">
                {probes.length === 0 ? (
                  <div className="empty-state">No probe assignments yet.</div>
                ) : (
                  probes.map((probe) => (
                    <div key={probe.id} className="probe-item">
                      <div>
                        <strong>{probe.probe_id}</strong>
                        <div className="muted">{probe.role}</div>
                      </div>
                      <div className="muted">
                        {formatDateTime(probe.valid_from)} / {formatDateTime(probe.valid_to)}
                      </div>
                    </div>
                  ))
                )}
              </div>
            </article>

            <article className="card">
              <div className="card-header">
                <h2>Assign Probe</h2>
              </div>
              <div className="form-grid">
                <input value={newProbeId} onChange={(event) => setNewProbeId(event.target.value)} placeholder="probe_id" />
                <input value={newProbeRole} onChange={(event) => setNewProbeRole(event.target.value)} placeholder="role" />
                <input
                  type="datetime-local"
                  value={newProbeValidFrom}
                  onChange={(event) => setNewProbeValidFrom(event.target.value)}
                />
                <input
                  type="datetime-local"
                  value={newProbeValidTo}
                  onChange={(event) => setNewProbeValidTo(event.target.value)}
                />
              </div>
              <div className="form-row">
                <button className="button" onClick={() => void handleAddProbe()} disabled={loading}>
                  Add Assignment
                </button>
              </div>
            </article>
          </section>

          <section className="grid wide">
            <article className="card">
              <div className="card-header">
                <h2>Runs</h2>
                <span className="badge">{currentRun ? 'Active' : 'Idle'}</span>
              </div>
              <div className="form-row">
                <input
                  value={newRunLabel}
                  onChange={(event) => setNewRunLabel(event.target.value)}
                  placeholder="Example: baseline / after_5min"
                />
                <button className="button" onClick={() => void handleCreateRun()} disabled={loading}>
                  Add Run
                </button>
              </div>
              <div className="stack">
                {runs.length === 0 ? (
                  <div className="empty-state">No runs yet.</div>
                ) : (
                  runs.map((run) => (
                    <div key={run.id} className={`run-item ${run.id === currentRun?.id ? 'active' : ''}`}>
                      <div>
                        <strong>{run.label}</strong>
                        <div className="muted">
                          Started: {formatDateTime(run.started_at)} / Ended: {formatDateTime(run.ended_at)}
                        </div>
                      </div>
                      <div className="run-meta">
                        <span>run #{run.id}</span>
                        <button className="link" onClick={() => void handleEndRun(run.id)} disabled={loading}>
                          End
                        </button>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </article>
          </section>
        </>
      ) : null}

      {page.kind !== 'probes' ? (
        <section className="card">
          <div className="card-header">
            <h2>Operational Note</h2>
          </div>
          <p className="muted">
            Temperature logs include experiment ID, run ID, and elapsed seconds, so Grafana can use
            <code>v_temperature_logs_grafana</code> for per-experiment charts.
          </p>
        </section>
      ) : null}
    </main>
  );
}
