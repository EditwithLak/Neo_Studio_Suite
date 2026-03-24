function resetBatchDisplay() {
  $('batch-progress-fill').style.width = '0%';
  $('batch-progress-text').textContent = 'Processing 0 / 0';
  $('batch-elapsed-total').textContent = 'Batch total: 00:00';
  $('batch-elapsed-current').textContent = 'Current file: 00:00';
  if ($('batch-eta')) $('batch-eta').textContent = 'ETA: —';
  $('batch-current-file').textContent = 'Current file: —';
  $('batch-counts').textContent = 'Success: 0 · Failed: 0 · Skipped: 0';
  if ($('batch-duplicate-summary')) $('batch-duplicate-summary').textContent = 'Duplicates: 0';
  if ($('batch-post-action-status')) $('batch-post-action-status').textContent = 'Post-task action: none';
}

function refreshBatchSessionOptions(jobs, selected='') {
  const sel = $('batch-session-select');
  if (!sel) return;
  const items = Array.isArray(jobs) ? jobs : [];
  sel.innerHTML = '';
  const first = document.createElement('option');
  first.value = '';
  first.textContent = '—';
  sel.appendChild(first);
  items.forEach(job => {
    const opt = document.createElement('option');
    opt.value = job.job_id || '';
    const folder = job.folder_path || 'Unknown folder';
    opt.textContent = `${job.status || 'saved'} · ${folder} · ${job.processed || 0}/${job.total_items || 0}`;
    if ((job.job_id || '') === selected) opt.selected = true;
    sel.appendChild(opt);
  });
}

function updateBatchActionButtons(data) {
  const status = data?.status || '';
  const running = status === 'running' || status === 'queued' || status === 'cancelling';
  if ($('btn-batch-cancel')) $('btn-batch-cancel').disabled = !running;
  if ($('btn-run-batch')) $('btn-run-batch').disabled = running;
  const hasFailed = Array.isArray(data?.failed_items) && data.failed_items.length > 0;
  if ($('btn-batch-retry')) $('btn-batch-retry').disabled = !currentBatchJobId || !hasFailed;
  const hasRemaining = Number(data?.remaining_items_count || 0) > 0 || status === 'cancelled';
  if ($('btn-batch-resume')) $('btn-batch-resume').disabled = !currentBatchJobId || !hasRemaining;
  const canCancelPost = Number(data?.post_action_seconds_left || 0) > 0;
  if ($('btn-batch-cancel-post-action')) $('btn-batch-cancel-post-action').disabled = !canCancelPost;
}

function updateBatchDisplay(data) {
  const pct = Math.max(0, Math.min(100, Number(data.progress_percent || 0)));
  $('batch-progress-fill').style.width = `${pct}%`;
  $('batch-progress-text').textContent = `Processing ${data.current_index || 0} / ${data.total_items || 0}`;
  $('batch-elapsed-total').textContent = `Batch total: ${formatElapsed(data.elapsed_total_seconds || 0)}`;
  $('batch-elapsed-current').textContent = `Current file: ${formatElapsed(data.elapsed_current_seconds || 0)}`;
  if ($('batch-eta')) {
    const eta = Number(data.eta_seconds || 0);
    $('batch-eta').textContent = eta > 0 ? `ETA: ${formatElapsed(eta)}` : 'ETA: —';
  }
  $('batch-current-file').textContent = `Current file: ${data.current_item_name || '—'}`;
  $('batch-counts').textContent = `Success: ${data.saved || 0} · Failed: ${data.errors || 0} · Skipped: ${data.skipped || 0}`;
  if ($('batch-duplicate-summary')) $('batch-duplicate-summary').textContent = `Duplicates: ${data.duplicates || 0}`;
  let postActionText = `Post-task action: ${data.post_action || 'none'}`;
  if (Number(data.post_action_seconds_left || 0) > 0) {
    postActionText += ` · ${data.post_action_status || 'countdown'} in ${data.post_action_seconds_left}s`;
  } else if (data.post_action_status && data.post_action_status !== 'idle') {
    postActionText += ` · ${data.post_action_status}`;
  }
  if ($('batch-post-action-status')) $('batch-post-action-status').textContent = postActionText;
  const lines = [];
  if (data.message) lines.push(data.message);
  if (data.duplicate_lines?.length) {
    lines.push('');
    lines.push('Duplicate summary');
    data.duplicate_lines.forEach(x => lines.push(x));
  }
  (data.detail_lines || []).forEach(x => lines.push(x));
  if (data.error_lines?.length) {
    lines.push('');
    lines.push('Errors');
    data.error_lines.forEach(x => lines.push(x));
  }
  $('batch-log').value = lines.join('\n');
  refreshBatchSessionOptions(data.recent_jobs || [], data.job_id || currentBatchJobId || '');
  updateBatchActionButtons(data);
}

function stopBatchPolling() {
  if (batchPollHandle) {
    clearInterval(batchPollHandle);
    batchPollHandle = null;
  }
}

async function refreshRecentBatchJobs() {
  try {
    const data = await safeFetchJson('/api/caption-batch-recent');
    refreshBatchSessionOptions(data.jobs || [], currentBatchJobId || '');
  } catch (_e) {}
}

async function pollBatchStatus() {
  if (!currentBatchJobId) return;
  try {
    const data = await safeFetchJson(`/api/caption-batch-status?job_id=${encodeURIComponent(currentBatchJobId)}`);
    updateBatchDisplay(data);
    setStatus('batch-status', data.message || data.summary || 'Batch running...');
    if (data.status === 'completed' || data.status === 'failed' || data.status === 'cancelled') {
      stopBatchPolling();
      setBusy('btn-run-batch', false);
      if (data.stats) updateStats(data.stats);
      if (data.categories) fillCategorySelect('batch-category', data.categories, resolveCategory('batch-category','batch-category-new'));
    }
  } catch (e) {
    stopBatchPolling();
    setBusy('btn-run-batch', false);
    setStatus('batch-status', e.message, 'error');
  }
}
