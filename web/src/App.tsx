import { useCallback, useEffect, useMemo, useState } from 'react';
import {
  addExperimentProbe,
  completeExperiment,
  createExperiment,
  createExperimentRun,
  deleteExperiment,
  deleteProbe,
  endExperimentRun,
  getCurrentExperimentRun,
  getExperiment,
  listExperimentProbes,
  listExperimentRuns,
  listExperiments,
  listProbes,
  reopenExperiment,
  startExperiment,
} from './api';
import type { Experiment, ExperimentProbe, ExperimentRun, Probe } from './types';

type AppPage = { kind: 'list' } | { kind: 'detail'; experimentId: number } | { kind: 'probes' };

function formatDateTime(value: string | null | undefined): string {
  return value ? new Date(value).toLocaleString('ja-JP') : '—';
}

function statusLabel(status: string): string {
  return {
    planned: '計画中',
    running: '実施中',
    completed: '完了',
    finished: '完了',
    archived: 'アーカイブ',
  }[status] ?? status;
}

function readPageFromLocation(): AppPage {
  if (window.location.pathname === '/probes') return { kind: 'probes' };
  const match = window.location.pathname.match(/^\/experiments\/(\d+)\/?$/);
  return match ? { kind: 'detail', experimentId: Number(match[1]) } : { kind: 'list' };
}

export default function App() {
  const [page, setPage] = useState<AppPage>(() => readPageFromLocation());
  const [experiments, setExperiments] = useState<Experiment[]>([]);
  const [detailExperiment, setDetailExperiment] = useState<Experiment | null>(null);
  const [runs, setRuns] = useState<ExperimentRun[]>([]);
  const [currentRun, setCurrentRun] = useState<ExperimentRun | null>(null);
  const [assignments, setAssignments] = useState<ExperimentProbe[]>([]);
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
    return detailExperiment ?? experiments.find((item) => item.id === page.experimentId) ?? null;
  }, [detailExperiment, experiments, page]);

  const refreshDetail = useCallback(async (experimentId: number) => {
    const [detail, runItems, assignmentItems, activeRun, probeItems] = await Promise.all([
      getExperiment(experimentId),
      listExperimentRuns(experimentId),
      listExperimentProbes(experimentId),
      getCurrentExperimentRun(experimentId).catch(() => null),
      listProbes(),
    ]);
    setDetailExperiment(detail);
    setRuns(runItems);
    setAssignments(assignmentItems);
    setCurrentRun(activeRun);
    setRegisteredProbes(probeItems);
  }, []);

  const refreshPage = useCallback(async (nextPage: AppPage) => {
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
        setAssignments([]);
        if (nextPage.kind === 'probes') {
          const probeItems = await listProbes();
          setRegisteredProbes(probeItems);
        }
      }
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : 'データを読み込めませんでした。');
    } finally {
      setLoading(false);
    }
  }, [refreshDetail]);

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
      setError(cause instanceof Error ? cause.message : '実験計画を作成できませんでした。');
      setLoading(false);
    }
  }

  async function handleCreateRun() {
    if (page.kind !== 'detail') return;
    const label = newRunLabel.trim();
    if (!label) {
      setError('測定名を入力してください。');
      return;
    }
    await perform(async () => {
      await createExperimentRun(page.experimentId, { label });
      setNewRunLabel('');
    }, '測定を開始できませんでした。');
  }

  async function handleAddProbe() {
    if (page.kind !== 'detail') return;
    const probeId = newProbeId.trim();
    const role = newProbeRole.trim();
    if (!probeId || !role) {
      setError('プローブと測定場所・役割を入力してください。');
      return;
    }
    await perform(async () => {
      await addExperimentProbe(page.experimentId, { probe_id: probeId, role });
      setNewProbeId('');
      setNewProbeRole('');
    }, 'プローブを割り当てられませんでした。');
  }

  const experimentRunning = selectedExperiment?.status === 'running';
  const experimentCompleted = selectedExperiment?.status === 'completed' || selectedExperiment?.status === 'finished';

  return (
    <main className="app">
      <header className="hero">
        <div>
          <p className="eyebrow">Summer Task 2026</p>
          <h1>{page.kind === 'list' ? '実験計画' : page.kind === 'probes' ? 'プローブ管理' : selectedExperiment?.name ?? '実験詳細'}</h1>
          <p className="lead">
            {page.kind === 'list'
              ? '先に実験の目的と条件を計画し、その実験の中で測定を必要な回数だけ実施します。'
              : page.kind === 'probes'
                ? '受信したプローブの登録状況を管理します。'
                : '実験全体の進行と、個々の測定の開始・終了を分けて管理します。'}
          </p>
        </div>
        <nav className="page-actions" aria-label="ページ操作">
          {page.kind !== 'list' && <button className="button secondary" onClick={() => navigate('/')}>実験一覧</button>}
          {page.kind !== 'probes' && <button className="button secondary" onClick={() => navigate('/probes')}>プローブ管理</button>}
          <button className="button secondary" onClick={() => void refreshPage(page)} disabled={loading}>更新</button>
        </nav>
      </header>

      {error && <section className="banner error">{error}</section>}

      {page.kind === 'list' && (
        <>
          <section className="card plan-card">
            <div className="section-heading">
              <div><span className="step-number">1</span><div><h2>新しい実験を計画</h2><p>測定を始める前に、目的と条件を登録します。</p></div></div>
            </div>
            <div className="form-grid plan-form">
              <label>実験名<input value={newExperimentName} onChange={(event) => setNewExperimentName(event.target.value)} placeholder="例：100gの水による温度比較" /></label>
              <label>目的・条件<textarea value={newExperimentDescription} onChange={(event) => setNewExperimentDescription(event.target.value)} placeholder="何を、どの条件で比較するか" /></label>
            </div>
            <button className="button" onClick={() => void handleCreateExperiment()} disabled={loading}>実験計画を作成</button>
          </section>

          <section className="card">
            <div className="card-header"><h2>実験一覧</h2><span className="badge">{experiments.length}件</span></div>
            <div className="experiment-list">
              {experiments.length === 0 ? <div className="empty-state">実験計画はまだありません。</div> : experiments.map((experiment) => (
                <button key={experiment.id} className="experiment-row" onClick={() => navigate(`/experiments/${experiment.id}`)}>
                  <span className={`status-dot status-${experiment.status}`} />
                  <span className="experiment-main"><strong>{experiment.name}</strong><small>{experiment.description || '説明なし'}</small></span>
                  <span className={`badge status-${experiment.status}`}>{statusLabel(experiment.status)}</span>
                  <span className="row-arrow">›</span>
                </button>
              ))}
            </div>
          </section>
        </>
      )}

      {page.kind === 'detail' && selectedExperiment && (
        <>
          <section className="lifecycle" aria-label="実験の進行状況">
            {[
              ['planned', '1', '計画・準備'],
              ['running', '2', '実験実施'],
              ['completed', '3', '実験完了'],
            ].map(([status, number, label]) => {
              const currentIndex = selectedExperiment.status === 'planned' ? 0 : experimentRunning ? 1 : 2;
              const itemIndex = Number(number) - 1;
              return <div key={status} className={`lifecycle-step ${itemIndex === currentIndex ? 'current' : ''} ${itemIndex < currentIndex ? 'done' : ''}`}><span>{itemIndex < currentIndex ? '✓' : number}</span><strong>{label}</strong></div>;
            })}
          </section>

          <section className="detail-grid">
            <article className="card">
              <div className="card-header"><h2>実験計画</h2><span className={`badge status-${selectedExperiment.status}`}>{statusLabel(selectedExperiment.status)}</span></div>
              <dl className="summary">
                <div><dt>実験ID</dt><dd>#{selectedExperiment.id}</dd></div>
                <div><dt>測定回数</dt><dd>{runs.length}回</dd></div>
                <div className="summary-wide"><dt>目的・条件</dt><dd>{selectedExperiment.description || '未入力'}</dd></div>
                <div><dt>実験開始</dt><dd>{formatDateTime(selectedExperiment.started_at)}</dd></div>
                <div><dt>実験完了</dt><dd>{formatDateTime(selectedExperiment.completed_at)}</dd></div>
              </dl>
            </article>

            <article className="card action-card">
              <h2>実験全体の操作</h2>
              {selectedExperiment.status === 'planned' && <>
                <p>準備ができたら実験を開始します。測定は開始後に個別に行います。</p>
                <button className="button" onClick={() => void perform(() => startExperiment(selectedExperiment.id), '実験を開始できませんでした。')} disabled={loading}>実験を開始</button>
              </>}
              {experimentRunning && <>
                <p>{currentRun ? '実施中の測定を終了してから、実験全体を完了してください。' : '必要な測定がすべて終わったら、実験全体を完了します。'}</p>
                <button className="button success" onClick={() => void perform(() => completeExperiment(selectedExperiment.id), '実験を完了できませんでした。')} disabled={loading || Boolean(currentRun)}>実験を完了</button>
              </>}
              {experimentCompleted && <>
                <p>追加の測定が必要な場合は実験を再開できます。</p>
                <button className="button" onClick={() => void perform(() => reopenExperiment(selectedExperiment.id), '実験を再開できませんでした。')} disabled={loading}>実験を再開</button>
              </>}
              <button className="text-button danger" onClick={() => void perform(() => deleteExperiment(selectedExperiment.id), 'アーカイブできませんでした。')} disabled={loading || experimentRunning}>実験をアーカイブ</button>
            </article>
          </section>

          <section className="card">
            <div className="section-heading">
              <div><span className="step-number">1</span><div><h2>プローブを準備</h2><p>この実験で使うプローブと測定場所・役割を設定します。</p></div></div>
              <span className="badge">{assignments.length}本</span>
            </div>
            <div className="probe-grid">
              {assignments.map((probe) => <div className="probe-tile" key={probe.id}><span className={probe.valid_to ? 'probe-state inactive' : 'probe-state'} /><div><strong>{probe.role}</strong><small>{probe.probe_id}</small></div><span className="muted">{probe.valid_to ? '終了' : '有効'}</span></div>)}
            </div>
            {!experimentCompleted && (
              <div className="inline-form">
                <select value={newProbeId} onChange={(event) => setNewProbeId(event.target.value)}>
                  <option value="">プローブを選択</option>
                  {registeredProbes.map((probe) => <option key={probe.probe_id} value={probe.probe_id}>{probe.probe_id}</option>)}
                </select>
                <input value={newProbeRole} onChange={(event) => setNewProbeRole(event.target.value)} placeholder="測定場所・役割（例：冷蔵庫）" />
                <button className="button secondary" onClick={() => void handleAddProbe()} disabled={loading}>割り当てる</button>
              </div>
            )}
          </section>

          <section className="card measurement-card">
            <div className="section-heading">
              <div><span className="step-number">2</span><div><h2>測定を実施</h2><p>1つの実験で、条件を揃えた測定を何回でも実施できます。</p></div></div>
              <span className={`badge ${currentRun ? 'status-running' : ''}`}>{currentRun ? '測定中' : `${runs.length}回実施`}</span>
            </div>

            {experimentRunning ? currentRun ? (
              <div className="active-measurement">
                <div className="pulse" /><div><span>測定中</span><h3>{currentRun.label}</h3><p>開始：{formatDateTime(currentRun.started_at)}</p></div>
                <button className="button danger-button" onClick={() => void perform(() => endExperimentRun(selectedExperiment.id, currentRun.id), '測定を終了できませんでした。')} disabled={loading}>この測定を終了</button>
              </div>
            ) : (
              <div className="start-measurement">
                <input value={newRunLabel} onChange={(event) => setNewRunLabel(event.target.value)} placeholder={`例：測定 ${runs.length + 1}回目`} />
                <button className="button" onClick={() => void handleCreateRun()} disabled={loading}>新しい測定を開始</button>
              </div>
            ) : <div className="empty-state">測定を始めるには、先に実験全体を開始してください。</div>}

            <div className="run-history">
              <h3>測定履歴</h3>
              {runs.length === 0 ? <div className="empty-state">測定履歴はまだありません。</div> : runs.map((run, index) => (
                <div className={`run-row ${run.id === currentRun?.id ? 'active' : ''}`} key={run.id}>
                  <span className="run-index">{index + 1}</span>
                  <div><strong>{run.label}</strong><small>{formatDateTime(run.started_at)} → {formatDateTime(run.ended_at)}</small></div>
                  <span className={`badge ${run.ended_at ? 'status-completed' : 'status-running'}`}>{run.ended_at ? '終了' : '測定中'}</span>
                </div>
              ))}
            </div>
          </section>
        </>
      )}

      {page.kind === 'probes' && (
        <section className="card">
          <div className="card-header"><h2>登録済みプローブ</h2><span className="badge">{registeredProbes.length}本</span></div>
          <div className="table-wrap"><table><thead><tr><th /><th>プローブID</th><th>初回受信</th><th>最終受信</th></tr></thead><tbody>
            {registeredProbes.map((probe) => <tr key={probe.probe_id} className={selectedProbeId === probe.probe_id ? 'selected' : ''}><td><input type="radio" checked={selectedProbeId === probe.probe_id} onChange={() => setSelectedProbeId(probe.probe_id)} /></td><td><strong>{probe.probe_id}</strong></td><td>{formatDateTime(probe.created_at)}</td><td>{formatDateTime(probe.updated_at)}</td></tr>)}
          </tbody></table></div>
          <button className="text-button danger" onClick={() => selectedProbeId && void perform(() => deleteProbe(selectedProbeId), '削除できませんでした。')} disabled={!selectedProbeId || loading}>選択したプローブを削除</button>
        </section>
      )}
    </main>
  );
}
