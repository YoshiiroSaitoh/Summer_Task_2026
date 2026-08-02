import { useCallback, useEffect, useMemo, useState } from 'react';
import {
  addExperimentRunProbe,
  completeExperiment,
  createExperiment,
  createExperimentRun,
  deleteExperiment,
  deleteProbe,
  endExperimentRun,
  getCurrentExperimentRun,
  getExperiment,
  listExperimentRunProbes,
  listExperimentRuns,
  listExperiments,
  listProbes,
  reopenExperiment,
  startExperiment,
  startExperimentRun,
} from './api';
import type { Experiment, ExperimentRun, ExperimentRunProbe, Probe } from './types';

type AppPage = { kind: 'list' } | { kind: 'detail'; experimentId: number } | { kind: 'probes' };

const grafanaBaseUrl = import.meta.env.VITE_GRAFANA_BASE_URL ?? 'http://experiment.local:3000';

function grafanaRunUrl(experimentId: number, runId: number): string {
  const params = new URLSearchParams({
    orgId: '1',
    'var-experiment_id': String(experimentId),
    'var-run_id': String(runId),
    'var-probe_id': 'All',
  });
  return `${grafanaBaseUrl}/d/temperature-logs/temperature-logs?${params.toString()}`;
}

const navItems = [
  { label: '実験一覧', path: '/' },
  { label: 'プローブ管理', path: '/probes' },
] as const;

function isActivePath(page: AppPage, path: string): boolean {
  if (path === '/') return page.kind === 'list';
  if (path === '/probes') return page.kind === 'probes';
  return page.kind === 'detail' && path === `/experiments/${page.experimentId}`;
}

function readPageFromLocation(): AppPage {
  if (window.location.pathname === '/probes') return { kind: 'probes' };
  const match = window.location.pathname.match(/^\/experiments\/(\d+)\/?$/);
  return match ? { kind: 'detail', experimentId: Number(match[1]) } : { kind: 'list' };
}

function formatDateTime(value: string | null | undefined): string {
  return value ? new Date(value).toLocaleString('ja-JP') : '-';
}

function statusLabel(status: string): string {
  return {
    planned: '予定',
    running: '実行中',
    completed: '完了',
    archived: 'アーカイブ',
    finished: '完了',
  }[status] ?? status;
}

function pageTitle(page: AppPage, experiment?: Experiment | null): string {
  if (page.kind === 'list') return '実験計画';
  if (page.kind === 'probes') return 'プローブ管理';
  return experiment?.name ?? '実験詳細';
}

function pageLead(page: AppPage): string {
  if (page.kind === 'list') {
    return '実験の計画、詳細、プローブ割り当てをまとめて扱います。';
  }
  if (page.kind === 'probes') {
    return '登録済みプローブを確認し、不要なものを削除できます。';
  }
  return '実験の状態遷移、回ごとの測定、プローブ割り当てを行います。';
}

export default function App() {
  const [page, setPage] = useState<AppPage>(() => readPageFromLocation());
  const [menuOpen, setMenuOpen] = useState(false);
  const [experiments, setExperiments] = useState<Experiment[]>([]);
  const [detailExperiment, setDetailExperiment] = useState<Experiment | null>(null);
  const [runs, setRuns] = useState<ExperimentRun[]>([]);
  const [currentRun, setCurrentRun] = useState<ExperimentRun | null>(null);
  const [selectedRunId, setSelectedRunId] = useState<number | null>(null);
  const [assignments, setAssignments] = useState<ExperimentRunProbe[]>([]);
  const [registeredProbes, setRegisteredProbes] = useState<Probe[]>([]);
  const [selectedProbeId, setSelectedProbeId] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [newExperimentName, setNewExperimentName] = useState('');
  const [newExperimentDescription, setNewExperimentDescription] = useState('');
  const [newRunLabel, setNewRunLabel] = useState('');
  const [newProbeId, setNewProbeId] = useState('');
  const [newProbeRole, setNewProbeRole] = useState('');

  const selectedExperiment = useMemo(() => {
    if (page.kind !== 'detail') return null;
    return detailExperiment ?? experiments.find((experiment) => experiment.id === page.experimentId) ?? null;
  }, [detailExperiment, experiments, page]);

  const refreshDetail = useCallback(async (experimentId: number) => {
    const [detail, runItems, activeRun, probeItems] = await Promise.all([
      getExperiment(experimentId),
      listExperimentRuns(experimentId),
      getCurrentExperimentRun(experimentId).catch(() => null),
      listProbes(),
    ]);
    const selectedId = activeRun?.id ?? runItems.at(-1)?.id ?? null;
    const assignmentItems = selectedId === null
      ? []
      : await listExperimentRunProbes(experimentId, selectedId);
    setDetailExperiment(detail);
    setRuns(runItems);
    setAssignments(assignmentItems);
    setCurrentRun(activeRun);
    setSelectedRunId(selectedId);
    setRegisteredProbes(probeItems);
  }, []);

  const refreshPage = useCallback(
    async (nextPage: AppPage) => {
      setLoading(true);
      setError(null);
      try {
        const experimentItems = await listExperiments();
        setExperiments(experimentItems);
        if (nextPage.kind === 'detail') {
          await refreshDetail(nextPage.experimentId);
        } else {
          setDetailExperiment(null);
          setRuns([]);
          setCurrentRun(null);
          setSelectedRunId(null);
          setAssignments([]);
          if (nextPage.kind === 'probes') {
            const probeItems = await listProbes();
            setRegisteredProbes(probeItems);
          }
        }
      } catch (cause) {
        setError(cause instanceof Error ? cause.message : 'データの取得に失敗しました。');
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
    const onPopState = () => setPage(readPageFromLocation());
    window.addEventListener('popstate', onPopState);
    return () => window.removeEventListener('popstate', onPopState);
  }, []);

  function navigate(path: string) {
    window.history.pushState({}, '', path);
    setPage(readPageFromLocation());
    setMenuOpen(false);
  }

  async function perform(action: () => Promise<unknown>, failureMessage: string) {
    setLoading(true);
    setError(null);
    try {
      await action();
      await refreshPage(page);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : failureMessage);
      setLoading(false);
    }
  }

  async function handleCreateExperiment() {
    const name = newExperimentName.trim();
    if (!name) {
      setError('実験名を入力してください。');
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const created = await createExperiment({
        name,
        description: newExperimentDescription.trim() || null,
      });
      setNewExperimentName('');
      setNewExperimentDescription('');
      navigate(`/experiments/${created.id}`);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : '実験の作成に失敗しました。');
      setLoading(false);
    }
  }

  async function handleCreateRun() {
    if (page.kind !== 'detail') return;
    const label = newRunLabel.trim();
    if (!label) {
      setError('測定回のラベルを入力してください。');
      return;
    }
    await perform(async () => {
      await createExperimentRun(page.experimentId, { label });
      setNewRunLabel('');
    }, '測定回の作成に失敗しました。');
  }

  async function handleStartRun() {
    if (page.kind !== 'detail' || selectedRunId === null) return;
    await perform(
      () => startExperimentRun(page.experimentId, selectedRunId),
      '測定回の開始に失敗しました。',
    );
  }

  async function handleAddProbe() {
    if (page.kind !== 'detail' || selectedRunId === null) return;
    const probeId = newProbeId.trim();
    const role = newProbeRole.trim();
    if (!probeId || !role) {
      setError('プローブIDと役割を入力してください。');
      return;
    }
    await perform(async () => {
      await addExperimentRunProbe(page.experimentId, selectedRunId, { probe_id: probeId, role });
      setNewProbeId('');
      setNewProbeRole('');
    }, 'プローブの割り当てに失敗しました。');
  }

  async function handleSelectRun(runId: number) {
    if (page.kind !== 'detail') return;
    setSelectedRunId(runId);
    setLoading(true);
    setError(null);
    try {
      setAssignments(await listExperimentRunProbes(page.experimentId, runId));
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : '測定回の割り当てを取得できませんでした。');
    } finally {
      setLoading(false);
    }
  }

  const experimentRunning = selectedExperiment?.status === 'running';
  const experimentCompleted = selectedExperiment?.status === 'completed' || selectedExperiment?.status === 'finished';
  const selectedRun = runs.find((run) => run.id === selectedRunId) ?? null;

  return (
    <main className="app-shell">
      <header className="topbar">
        <div className="topbar-brand">
          <button
            type="button"
            className="icon-button"
            aria-label="メニューを開く"
            aria-expanded={menuOpen}
            onClick={() => setMenuOpen((current) => !current)}
          >
            <span />
            <span />
            <span />
          </button>
          <div>
            <p className="eyebrow">Summer Task 2026</p>
            <h1>{pageTitle(page, selectedExperiment)}</h1>
          </div>
        </div>

        <div className="topbar-actions">
          <button type="button" className="button secondary" onClick={() => navigate('/')} disabled={loading}>
            実験一覧
          </button>
          <button type="button" className="button secondary" onClick={() => navigate('/probes')} disabled={loading}>
            プローブ管理
          </button>
          <button type="button" className="button secondary" onClick={() => void refreshPage(page)} disabled={loading}>
            更新
          </button>
        </div>
      </header>

      <div className={`drawer-backdrop ${menuOpen ? 'open' : ''}`} onClick={() => setMenuOpen(false)} />
      <aside className={`drawer ${menuOpen ? 'open' : ''}`} aria-label="メインメニュー">
        <div className="drawer-header">
          <div>
            <p className="eyebrow">Navigation</p>
            <strong>メニュー</strong>
          </div>
          <button type="button" className="icon-button close-button" aria-label="メニューを閉じる" onClick={() => setMenuOpen(false)}>
            ×
          </button>
        </div>
        <nav className="drawer-nav">
          {navItems.map((item) => (
            <button
              key={item.path}
              type="button"
              className={`drawer-link ${isActivePath(page, item.path) ? 'active' : ''}`}
              onClick={() => navigate(item.path)}
            >
              {item.label}
            </button>
          ))}
          {page.kind === 'detail' && (
            <button
              type="button"
              className={`drawer-link ${isActivePath(page, `/experiments/${page.experimentId}`) ? 'active' : ''}`}
              onClick={() => navigate(`/experiments/${page.experimentId}`)}
            >
              実験詳細
            </button>
          )}
        </nav>
      </aside>

      <section className="hero-copy">
        <p className="lead">{pageLead(page)}</p>
      </section>

      {error && <section className="banner error">{error}</section>}

      {page.kind === 'list' && (
        <>
          <section className="card plan-card">
            <div className="section-heading">
              <div>
                <span className="step-number">1</span>
                <div>
                  <h2>新しい実験を計画</h2>
                  <p>測定を始める前に、目的と条件を登録します。</p>
                </div>
              </div>
            </div>

            <div className="form-grid plan-form">
              <label>
                実験名
                <input
                  value={newExperimentName}
                  onChange={(event) => setNewExperimentName(event.target.value)}
                  placeholder="例：100gの水による温度比較"
                />
              </label>
              <label>
                目的・条件
                <textarea
                  value={newExperimentDescription}
                  onChange={(event) => setNewExperimentDescription(event.target.value)}
                  placeholder="何を、どの条件で比較するか"
                />
              </label>
            </div>

            <button type="button" className="button" onClick={() => void handleCreateExperiment()} disabled={loading}>
              実験計画を作成
            </button>
          </section>

          <section className="card">
            <div className="card-header">
              <h2>実験一覧</h2>
              <span className="badge">{experiments.length}件</span>
            </div>
            <div className="experiment-list">
              {experiments.length === 0 ? (
                <div className="empty-state">実験計画はまだありません。</div>
              ) : (
                experiments.map((experiment) => (
                  <button
                    key={experiment.id}
                    type="button"
                    className="experiment-row"
                    onClick={() => navigate(`/experiments/${experiment.id}`)}
                  >
                    <span className={`status-dot status-${experiment.status}`} />
                    <span className="experiment-main">
                      <strong>{experiment.name}</strong>
                      <small>{experiment.description || '説明なし'}</small>
                    </span>
                    <span className={`badge status-${experiment.status}`}>{statusLabel(experiment.status)}</span>
                    <span className="row-arrow">›</span>
                  </button>
                ))
              )}
            </div>
          </section>
        </>
      )}

      {page.kind === 'detail' && selectedExperiment && (
        <>
          <section className="lifecycle" aria-label="実験の状態">
            {[
              { key: 'planned', label: '計画' },
              { key: 'running', label: '実行中' },
              { key: 'completed', label: '完了' },
            ].map((item, index) => {
              const currentIndex = selectedExperiment.status === 'planned' ? 0 : experimentRunning ? 1 : 2;
              return (
                <div
                  key={item.key}
                  className={`lifecycle-step ${index === currentIndex ? 'current' : ''} ${index < currentIndex ? 'done' : ''}`}
                >
                  <span>{index < currentIndex ? '✓' : index + 1}</span>
                  <strong>{item.label}</strong>
                </div>
              );
            })}
          </section>

          <section className="detail-grid">
            <article className="card">
              <div className="card-header">
                <h2>実験詳細</h2>
                <span className={`badge status-${selectedExperiment.status}`}>{statusLabel(selectedExperiment.status)}</span>
              </div>
              <dl className="summary">
                <div>
                  <dt>ID</dt>
                  <dd>#{selectedExperiment.id}</dd>
                </div>
                <div>
                  <dt>測定回数</dt>
                  <dd>{runs.length}回</dd>
                </div>
                <div className="summary-wide">
                  <dt>目的・条件</dt>
                  <dd>{selectedExperiment.description || '未設定'}</dd>
                </div>
                <div>
                  <dt>開始</dt>
                  <dd>{formatDateTime(selectedExperiment.started_at)}</dd>
                </div>
                <div>
                  <dt>完了</dt>
                  <dd>{formatDateTime(selectedExperiment.completed_at)}</dd>
                </div>
              </dl>
            </article>

            <article className="card action-card">
              <h2>実験操作</h2>
              {selectedExperiment.status === 'planned' && (
                <>
                  <p>測定回とプローブ割り当てを計画してから、実験を開始できます。</p>
                  <button type="button" className="button" onClick={() => void perform(() => startExperiment(selectedExperiment.id), '実験の開始に失敗しました。')} disabled={loading}>
                    実験を開始
                  </button>
                </>
              )}
              {experimentRunning && (
                <>
                  <p>{currentRun ? '測定中の回を終了してから、実験全体を終了してください。' : '測定回を開始するか、すべての測定が済んだら実験を終了できます。'}</p>
                  <button
                    type="button"
                    className="button success"
                    onClick={() => void perform(() => completeExperiment(selectedExperiment.id), '実験の完了に失敗しました。')}
                    disabled={loading || Boolean(currentRun)}
                  >
                    実験を終了
                  </button>
                </>
              )}
              {experimentCompleted && (
                <>
                  <p>追加測定が必要な場合は、完了済みの実験を再開できます。</p>
                  <button type="button" className="button" onClick={() => void perform(() => reopenExperiment(selectedExperiment.id), '実験の再開に失敗しました。')} disabled={loading}>
                    実験を再開
                  </button>
                </>
              )}
              <button
                type="button"
                className="text-button danger"
                onClick={() => void perform(() => deleteExperiment(selectedExperiment.id), '実験のアーカイブに失敗しました。')}
                disabled={loading || experimentRunning}
              >
                実験をアーカイブ
              </button>
            </article>
          </section>

          <section className="card">
            <div className="section-heading">
              <div>
                <span className="step-number">2</span>
                <div>
                  <h2>測定回のプローブ割り当て</h2>
                  <p>{selectedRun ? `「${selectedRun.label}」で使うプローブと役割です。` : '先に測定回を作成してください。'}</p>
                </div>
              </div>
              <span className="badge">{assignments.length}件</span>
            </div>

            {!selectedRun && (
              <div className="start-measurement">
                <input
                  value={newRunLabel}
                  onChange={(event) => setNewRunLabel(event.target.value)}
                  placeholder={`例：baseline-${runs.length + 1}`}
                />
                <button type="button" className="button" onClick={() => void handleCreateRun()} disabled={loading}>
                  測定回を計画
                </button>
              </div>
            )}

            <div className="probe-grid">
              {assignments.length === 0 ? (
                <div className="empty-state">まだプローブ割り当てはありません。</div>
              ) : (
                assignments.map((probe) => (
                  <div className="probe-tile" key={probe.id}>
                    <span className="probe-state" />
                    <div>
                      <strong>{probe.role}</strong>
                      <small>{probe.probe_id}</small>
                    </div>
                    <span className="muted">この測定回</span>
                  </div>
                ))
              )}
            </div>

            {selectedRun && !selectedRun.started_at && (
              <div className="inline-form">
                <select value={newProbeId} onChange={(event) => setNewProbeId(event.target.value)}>
                  <option value="">プローブを選択</option>
                  {registeredProbes.map((probe) => (
                    <option key={probe.probe_id} value={probe.probe_id}>
                      {probe.probe_id}
                    </option>
                  ))}
                </select>
                <input value={newProbeRole} onChange={(event) => setNewProbeRole(event.target.value)} placeholder="main / backup / room" />
                <button type="button" className="button secondary" onClick={() => void handleAddProbe()} disabled={loading}>
                  割り当て追加
                </button>
              </div>
            )}
          </section>

          <section className="card measurement-card">
            <div className="section-heading">
              <div>
                <span className="step-number">3</span>
                <div>
                  <h2>測定回</h2>
                  <p>回ごとに開始・終了を繰り返し、グラフを重ねられるようにします。</p>
                </div>
              </div>
              <span className={`badge ${currentRun ? 'status-running' : ''}`}>{currentRun ? '測定中' : `${runs.length}回`}</span>
            </div>

            {currentRun ? (
                <div className="active-measurement">
                  <div className="pulse" />
                  <div>
                    <span>測定中</span>
                    <h3>{currentRun.label}</h3>
                    <p>開始: {formatDateTime(currentRun.started_at)}</p>
                  </div>
                  <button
                    type="button"
                    className="button danger-button"
                    onClick={() => void perform(() => endExperimentRun(selectedExperiment.id, currentRun.id), '測定回の終了に失敗しました。')}
                    disabled={loading}
                  >
                    測定回を終了
                  </button>
                </div>
              ) : (
                <>
                <div className="start-measurement">
                  <input
                    value={newRunLabel}
                    onChange={(event) => setNewRunLabel(event.target.value)}
                    placeholder={`例：baseline-${runs.length + 1}`}
                  />
                  <button type="button" className="button" onClick={() => void handleCreateRun()} disabled={loading}>
                    測定回を計画
                  </button>
                </div>
                {experimentRunning && selectedRun && !selectedRun.started_at && (
                  <button
                    type="button"
                    className="button success"
                    onClick={() => void handleStartRun()}
                    disabled={loading || assignments.length === 0}
                  >
                    選択中の測定回を開始
                  </button>
                )}
                {!experimentRunning && (
                  <div className="empty-state">実験開始後、計画済みの測定回を開始できます。</div>
                )}
                </>
              )}

            <div className="run-history">
              <h3>履歴</h3>
              {runs.length === 0 ? (
                <div className="empty-state">まだ測定回はありません。</div>
              ) : (
                runs.map((run, index) => (
                  <div
                    className={`run-row ${run.id === selectedRunId ? 'active' : ''}`}
                    key={run.id}
                  >
                    <span className="run-index">{index + 1}</span>
                    <button type="button" className="run-select-button" onClick={() => void handleSelectRun(run.id)}>
                      <strong>{run.label}</strong>
                      <small>
                        {run.started_at ? `${formatDateTime(run.started_at)} / ${formatDateTime(run.ended_at)}` : '開始前・プローブ割り当て可能'}
                      </small>
                    </button>
                    <span className={`badge ${run.ended_at ? 'status-completed' : run.started_at ? 'status-running' : 'status-planned'}`}>
                      {run.ended_at ? '終了' : run.started_at ? '測定中' : '予定'}
                    </span>
                    {run.started_at && (
                      <a
                        className="grafana-link"
                        href={grafanaRunUrl(selectedExperiment.id, run.id)}
                        target="_blank"
                        rel="noreferrer"
                      >
                        Grafanaで結果を見る
                      </a>
                    )}
                  </div>
                ))
              )}
            </div>
          </section>
        </>
      )}

      {page.kind === 'probes' && (
        <section className="card">
          <div className="card-header">
            <h2>プローブ一覧</h2>
            <span className="badge">{registeredProbes.length}件</span>
          </div>
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th />
                  <th>プローブID</th>
                  <th>作成日時</th>
                  <th>更新日時</th>
                </tr>
              </thead>
              <tbody>
                {registeredProbes.map((probe) => (
                  <tr key={probe.probe_id} className={selectedProbeId === probe.probe_id ? 'selected' : ''}>
                    <td>
                      <input type="radio" checked={selectedProbeId === probe.probe_id} onChange={() => setSelectedProbeId(probe.probe_id)} />
                    </td>
                    <td>
                      <strong>{probe.probe_id}</strong>
                    </td>
                    <td>{formatDateTime(probe.created_at)}</td>
                    <td>{formatDateTime(probe.updated_at)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <button
            type="button"
            className="text-button danger"
            onClick={() => selectedProbeId && void perform(() => deleteProbe(selectedProbeId), 'プローブの削除に失敗しました。')}
            disabled={!selectedProbeId || loading}
          >
            選択したプローブを削除
          </button>
        </section>
      )}
    </main>
  );
}
