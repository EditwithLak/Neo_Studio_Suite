function recentKindToSearchKind(kind, name='') {
  if (kind === 'prompt') return ['prompts', ''];
  if (kind === 'caption') return ['captions', ''];
  if (kind === 'character') return ['characters', ''];
  if (kind === 'metadata') return ['metadata_records', ''];
  if (kind === 'bundle') return ['bundles', ''];
  if (kind === 'prompt_preset') return ['presets', `prompt:${name}`];
  if (kind === 'caption_preset') return ['presets', `caption:${name}`];
  return ['', ''];
}

function renderRecentItemsGroup(title, items) {
  const group = document.createElement('div');
  group.className = 'recent-group';
  group.innerHTML = `<h4>${escapeHtml(title)} <span class="kbd">${items.length}</span></h4>`;
  items.forEach(item => {
    const row = document.createElement('div');
    row.className = 'recent-item';
    const meta = [item.category || '', item.group || '', item.updated_at ? String(item.updated_at).replace('T', ' ') : '', item.usage_count ? `used ${item.usage_count}` : ''].filter(Boolean).join(' · ');
    row.innerHTML = `
      <div>
        <div class="recent-item-title">${escapeHtml(item.favorite ? `★ ${item.name || '(untitled)'}` : (item.name || '(untitled)'))}</div>
        <div class="recent-item-meta">${escapeHtml(meta || item.kind || '')}</div>
      </div>
      <button class="btn" type="button" data-recent-open="${item.kind}" data-recent-id="${escapeHtml(item.id || '')}" data-recent-name="${escapeHtml(item.name || '')}">Open</button>
    `;
    group.appendChild(row);
  });
  return group;
}

async function refreshRecentItems() {
  const wrap = $('recent-items-grid');
  if (!wrap) return;
  try {
    const data = await safeFetchJson('/api/recent-items?limit=6');
    const groups = [
      ['Recent prompts', data.items?.prompts || []],
      ['Recent captions', data.items?.captions || []],
      ['Recent characters', data.items?.characters || []],
      ['Recent bundles', data.items?.bundles || []],
      ['Recent prompt presets', data.items?.prompt_presets || []],
      ['Recent caption presets', data.items?.caption_presets || []],
      ['Recovered metadata', data.items?.metadata || []],
    ];
    wrap.innerHTML = '';
    let total = 0;
    groups.forEach(([label, items]) => {
      if (!items.length) return;
      total += items.length;
      wrap.appendChild(renderRecentItemsGroup(label, items));
    });
    if (!total) {
      wrap.innerHTML = '<div class="card-lite"><div class="muted">No recent items yet.</div></div>';
    }
    setStatus('recent-items-status', total ? `${total} recent item(s) ready.` : 'No recent items yet.');
  } catch (e) {
    setStatus('recent-items-status', e.message, 'error');
  }
}

document.addEventListener('DOMContentLoaded', () => {
  refreshCategoryList(initialCategories);
  fillCategorySelect('prompt-category', initialCategories, initialLastPromptCategory);
  fillCategorySelect('caption-category', initialCategories, initialLastCaptionCategory);
  fillCategorySelect('batch-category', initialCategories, initialLastCaptionCategory);
  fillCategorySelect('saved-prompt-category', initialPromptCategoryList, initialLastPromptCategory);
  fillCategorySelect('caption-browser-category', ['all', ...initialCategories.filter(x => x !== 'all')], 'all');
  fillCategorySelect('component-browser-category', ['all', ...initialCategories.filter(x => x !== 'all')], 'all');
  fillCategorySelect('caption-editor-category', initialCategories, initialLastCaptionCategory);
  fillCategorySelect('metadata-save-category', initialCategories, initialLastPromptCategory);
  fillSavedPromptEntries(initialPromptEntries || [], '');
  fillSavedCharacterEntries(initialCharacterEntries || [], '');
  populatePresetSelect('prompt-preset', promptPresets, initialLastPromptPreset);
  populatePresetSelect('caption-preset', captionPresets, initialLastCaptionPreset);
  applyPromptPreset($('prompt-preset').value, false);
  applyCaptionPreset($('caption-preset').value, false);
  refreshPromptPresetAux($('prompt-preset').value);
  refreshCaptionPresetAux($('caption-preset').value);
  toggleBatchMode();
  if (typeof syncDatasetPreparationControls === 'function') syncDatasetPreparationControls();
  renderVariationInputs();
  syncPromptOutputVisibility();
  resetBatchDisplay();
  resetTimer('prompt-elapsed');
  resetTimer('caption-elapsed');
  resetTimer('character-elapsed');
  refreshCaptionBrowser();
  refreshComponentBrowser();
  applyCaptionModeDefaults(true);
  refreshRecentItems();
  if (typeof initializeStudioAccordions === 'function') initializeStudioAccordions();
  refreshRecentBatchJobs();
  const batchAccordion = document.querySelector('[data-accordion-id="caption-batch-captioning"]');
  if (batchAccordion) batchAccordion.addEventListener('toggle', () => { if (batchAccordion.open) refreshRecentBatchJobs(); });
  if ($('saved-bundle-id') || $('bundle-name')) {
    fillBundleEntries(initialBundleEntries || [], '');
    refreshBundleSupportData();
  }

  document.querySelectorAll('.tabbar button').forEach(btn => btn.addEventListener('click', () => switchTab(btn.dataset.tab)));
  ['prompt-idea','prompt-output','caption-output','character-content'].forEach(id => $(id).addEventListener('input', () => { updateCounter(id, `${id}-counter`); if (id === 'prompt-output') $('prompt-raw').value = $('prompt-output').value || ''; }));
  updateCounter('prompt-idea','prompt-idea-counter');
  updateCounter('prompt-output','prompt-output-counter');
  updateCounter('caption-output','caption-output-counter');
  updateCounter('character-content','character-content-counter');

  $('prompt-preset').addEventListener('change', e => applyPromptPreset(e.target.value));
  $('caption-preset').addEventListener('change', e => applyCaptionPreset(e.target.value));
  $('prompt-preset-recent').addEventListener('change', e => { if (e.target.value) { $('prompt-preset').value = e.target.value; applyPromptPreset(e.target.value); } });
  $('caption-preset-recent').addEventListener('change', e => { if (e.target.value) { $('caption-preset').value = e.target.value; applyCaptionPreset(e.target.value); } });
  $('saved-prompt-category').addEventListener('change', refreshSavedPromptNames);
  $('batch-mode').addEventListener('change', () => { toggleBatchMode(); refreshRecentBatchJobs(); });
  ['batch-dataset-caption-images','batch-dataset-save-txt','batch-dataset-rename-images'].forEach(id => $(id)?.addEventListener('change', () => syncDatasetPreparationControls()));
  ['batch-dataset-prefix','batch-dataset-pattern','batch-number-start','batch-dataset-number-padding'].forEach(id => $(id)?.addEventListener('input', () => updateDatasetPreparationPreview()));
  $('prompt-enable-variations').addEventListener('change', renderVariationInputs);
  $('prompt-variation-count').addEventListener('input', renderVariationInputs);
  $('saved-character-name').addEventListener('change', loadSavedCharacter);
  $('global-search-query').addEventListener('keydown', e => { if (e.key === 'Enter') runGlobalSearch(); });
  ['caption-browser-query','caption-browser-model','caption-browser-style'].forEach(id => $(id).addEventListener('input', () => scheduleCaptionBrowserRefresh(true)));
  ['caption-browser-date-from','caption-browser-date-to'].forEach(id => $(id).addEventListener('change', () => refreshCaptionBrowser({ resetPage:true })));
  $('caption-browser-category').addEventListener('change', () => refreshCaptionBrowser({ resetPage:true }));
  $('caption-browser-component').addEventListener('change', () => refreshCaptionBrowser({ resetPage:true }));
  $('caption-browser-sort').addEventListener('change', () => refreshCaptionBrowser({ resetPage:true }));
  $('caption-browser-page-size').addEventListener('change', () => refreshCaptionBrowser({ resetPage:true }));
  ['component-browser-query','component-browser-type'].forEach(id => $(id).addEventListener('change', refreshComponentBrowser));
  $('component-browser-category').addEventListener('change', refreshComponentBrowser);
  $('caption-mode').addEventListener('change', () => applyCaptionModeDefaults());
  if ($('caption-detail-level')) $('caption-detail-level').addEventListener('change', () => refreshCaptionGuidance());
  $('caption-component-type').addEventListener('change', () => { captionAutoComponentValue = $('caption-component-type').value || ''; $('caption-save-component-type').value = $('caption-component-type').value || ''; });
  $('caption-save-component-type').addEventListener('change', () => { captionAutoComponentValue = $('caption-save-component-type').value || captionAutoComponentValue; });

  $('caption-image').addEventListener('change', e => {
    const file = e.target.files[0];
    if (!file) return;
    setCaptionPreviewFile(file);
  });
  $('caption-preview-wrap').addEventListener('mousedown', startCaptionCropDrag);
  window.addEventListener('mousemove', moveCaptionCropDrag);
  window.addEventListener('mouseup', endCaptionCropDrag);
  window.addEventListener('resize', updateCaptionCropOverlay);
  applyCaptionModeDefaults();
  if (typeof refreshCaptionGuidance === 'function') refreshCaptionGuidance();

  $('btn-generate-prompt').addEventListener('click', generatePrompt);
  $('btn-cancel-prompt-run').addEventListener('click', () => { if (promptAbortController) promptAbortController.abort(); });
  $('btn-continue-prompt').addEventListener('click', continuePrompt);
  $('btn-save-prompt-preset').addEventListener('click', () => savePromptPreset(false));
  $('btn-update-prompt-preset').addEventListener('click', () => savePromptPreset(true));
  $('btn-delete-prompt-preset').addEventListener('click', deletePromptPreset);
  $('btn-toggle-prompt-preset-favorite').addEventListener('click', togglePromptPresetFavorite);
  $('btn-duplicate-prompt-preset').addEventListener('click', duplicatePromptPreset);
  $('btn-compare-prompt-preset').addEventListener('click', comparePromptPresets);
  $('btn-export-prompt-preset').addEventListener('click', exportSinglePromptPreset);
  $('btn-save-prompt').addEventListener('click', savePromptEntry);
  if ($('btn-pull-current-to-bundle')) $('btn-pull-current-to-bundle').addEventListener('click', pullCurrentPromptIntoBundle);
  if ($('btn-save-bundle')) $('btn-save-bundle').addEventListener('click', saveBundleRecord);
  if ($('btn-update-bundle')) $('btn-update-bundle').addEventListener('click', updateBundleRecord);
  if ($('btn-refresh-bundles')) $('btn-refresh-bundles').addEventListener('click', () => refreshBundleRecords($('saved-bundle-id')?.value || loadedBundleId || ''));
  if ($('btn-load-bundle')) $('btn-load-bundle').addEventListener('click', loadSelectedBundle);
  if ($('btn-apply-bundle-workspace')) $('btn-apply-bundle-workspace').addEventListener('click', async () => { await loadSelectedBundle(); const rec = await safeFetchJson(`/api/bundle-record?bundle_id=${encodeURIComponent(loadedBundleId || $('saved-bundle-id')?.value || '')}`); applyBundleToWorkspace(rec.record || {}); });
  if ($('btn-duplicate-bundle')) $('btn-duplicate-bundle').addEventListener('click', duplicateSelectedBundle);
  if ($('btn-delete-bundle')) $('btn-delete-bundle').addEventListener('click', deleteSelectedBundle);
  $('btn-load-prompt').addEventListener('click', loadSavedPrompt);
  $('btn-update-loaded').addEventListener('click', updateLoadedPrompt);
  $('btn-delete-loaded').addEventListener('click', deleteLoadedPrompt);
  $('btn-improve-loaded').addEventListener('click', improveLoadedPrompt);
  $('btn-copy-prompt').addEventListener('click', () => copyText('prompt-output', 'prompt-run-status'));
  $('btn-analyze-prompt').addEventListener('click', () => runPromptQA('manual'));
  $('prompt-output').addEventListener('input', () => { updateCounter('prompt-output','prompt-output-counter'); schedulePromptQAAuto(); });
  $('prompt-qa-auto').addEventListener('change', () => { if ($('prompt-qa-auto').checked) schedulePromptQAAuto(); else setStatus('prompt-qa-status', 'Auto-run disabled.'); });
  $('btn-clear-prompt').addEventListener('click', () => { promptSingleOutputForcedVisible = false; $('prompt-idea').value=''; $('prompt-output').value=''; $('prompt-raw').value=''; renderVariationResults([]); syncPromptOutputVisibility(); updateCounter('prompt-idea','prompt-idea-counter'); updateCounter('prompt-output','prompt-output-counter'); $('prompt-qa-summary').textContent = 'Run Prompt QA to catch messy structure before you save or send the prompt.'; $('prompt-qa-stats').innerHTML=''; $('prompt-qa-list').innerHTML=''; setStatus('prompt-qa-status',''); });
  $('prompt-variation-results').addEventListener('click', async (e) => {
    const loadBtn = e.target.closest('[data-variation-load]');
    const copyBtn = e.target.closest('[data-variation-copy]');
    if (loadBtn) {
      const item = variationResultsState[Number(loadBtn.dataset.variationLoad || -1)];
      if (!item) return;
      $('prompt-output').value = item.prompt || '';
      $('prompt-raw').value = item.prompt || '';
      currentPromptFinishReason = item.finish_reason || '';
      $('prompt-finish-reason').textContent = `finish: ${currentPromptFinishReason || 'stop'}`;
      promptSingleOutputForcedVisible = true;
      syncPromptOutputVisibility();
      updateCounter('prompt-output', 'prompt-output-counter');
      maybeRunPromptQA('auto');
      setStatus('prompt-run-status', 'Selected variation moved into final output.');
    }
    if (copyBtn) {
      const item = variationResultsState[Number(copyBtn.dataset.variationCopy || -1)];
      if (!item) return;
      try { await navigator.clipboard.writeText(item.prompt || ''); setStatus('prompt-run-status', 'Variation copied to clipboard.'); } catch (_) { setStatus('prompt-run-status', 'Copy failed.', 'error'); }
    }
  });

  $('btn-dedupe-tags').addEventListener('click', () => {
    $('prompt-output').value = uniqueTags($('prompt-output').value || '');
    updateCounter('prompt-output','prompt-output-counter');
    maybeRunPromptQA('auto');
    setStatus('prompt-qa-status', 'Duplicate tags removed.');
  });
  $('btn-sort-tags').addEventListener('click', () => runImprove('Sort tags by importance'));
  $('btn-shorten-prompt').addEventListener('click', () => runImprove('Tighten / shorten'));
  $('btn-expand-prompt').addEventListener('click', () => runImprove('Expand details'));
  $('btn-fix-contradictions').addEventListener('click', () => runImprove('Fix contradictions'));
  $('btn-convert-style').addEventListener('click', () => {
    const src = $('prompt-output').value || '';
    const mode = (src.includes(',') && src.split(',').length >= 4) ? 'Convert to descriptive prose' : 'Convert to SD tags';
    runImprove(mode);
  });

  $('btn-caption-image').addEventListener('click', () => captionImage(false));
  $('btn-caption-selected-area').addEventListener('click', () => captionImage(true));
  $('btn-reset-caption-crop').addEventListener('click', resetCaptionCrop);
  $('btn-use-auto-caption-crop').addEventListener('click', useAutoCaptionCrop);
  $('btn-load-character').addEventListener('click', loadSavedCharacter);
  $('btn-save-character').addEventListener('click', saveCharacter);
  $('btn-delete-character').addEventListener('click', deleteCharacter);
  $('btn-improve-character').addEventListener('click', improveCharacter);
  $('btn-character-to-idea').addEventListener('click', () => { $('prompt-idea').value = $('character-content').value || ''; updateCounter('prompt-idea','prompt-idea-counter'); setStatus('character-status', 'Character copied into prompt idea.'); });
  $('btn-save-caption-preset').addEventListener('click', () => saveCaptionPreset(false));
  $('btn-update-caption-preset').addEventListener('click', () => saveCaptionPreset(true));
  $('btn-delete-caption-preset').addEventListener('click', deleteCaptionPreset);
  $('btn-toggle-caption-preset-favorite').addEventListener('click', toggleCaptionPresetFavorite);
  $('btn-duplicate-caption-preset').addEventListener('click', duplicateCaptionPreset);
  $('btn-compare-caption-preset').addEventListener('click', compareCaptionPresets);
  $('btn-export-caption-preset').addEventListener('click', exportSingleCaptionPreset);
  $('btn-save-caption').addEventListener('click', saveCaptionEntry);
  $('btn-copy-caption').addEventListener('click', () => copyText('caption-output', 'caption-run-status'));
  $('btn-clear-caption').addEventListener('click', () => { $('caption-output').value=''; $('caption-notes').value=''; updateCounter('caption-output','caption-output-counter'); setWarning('caption-warning',''); setStatus('caption-run-status',''); });

  $('btn-refresh-caption-browser').addEventListener('click', () => refreshCaptionBrowser({ resetPage:false }));
  $('btn-refresh-components').addEventListener('click', refreshComponentBrowser);
  $('btn-clear-components').addEventListener('click', () => { $('component-browser-query').value=''; $('component-browser-type').value=''; fillCategorySelect('component-browser-category', ['all', ...initialCategories.filter(x => x !== 'all')], 'all'); refreshComponentBrowser(); });
  $('btn-build-component-draft').addEventListener('click', buildComponentDraftFromSelection);
  $('btn-send-component-draft').addEventListener('click', sendComponentDraftToPromptStudio);
  $('btn-clear-component-selection').addEventListener('click', clearComponentSelection);
  $('btn-clear-caption-browser').addEventListener('click', () => {
    $('caption-browser-query').value = '';
    $('caption-browser-model').value = '';
    $('caption-browser-style').value = '';
    $('caption-browser-date-from').value = '';
    $('caption-browser-date-to').value = '';
    $('caption-browser-component').value = '';
    if (typeof resetCaptionBrowserControls === 'function') resetCaptionBrowserControls();
    fillCategorySelect('caption-browser-category', ['all', ...initialCategories.filter(x => x !== 'all')], 'all');
    refreshCaptionBrowser({ resetPage:true });
  });
  $('btn-caption-browser-prev').addEventListener('click', () => changeCaptionBrowserPage(-1));
  $('btn-caption-browser-next').addEventListener('click', () => changeCaptionBrowserPage(1));
  $('caption-browser-grid').addEventListener('click', async (e) => {
    const editBtn = e.target.closest('[data-caption-edit]');
    const previewBtn = e.target.closest('[data-caption-preview]');
    const sendBtn = e.target.closest('[data-caption-send]');
    if (editBtn) await loadCaptionRecord(editBtn.dataset.captionEdit);
    if (previewBtn) openLightbox(previewBtn.dataset.captionPreview);
    if (sendBtn) { await loadCaptionRecord(sendBtn.dataset.captionSend); sendCaptionEditorToPrompt(); }
  });
  $('component-browser-list').addEventListener('change', e => {
    const box = e.target.closest('[data-component-id]');
    if (!box) return;
    const id = box.getAttribute('data-component-id');
    if (box.checked) captionSelectedComponentIds.add(id); else captionSelectedComponentIds.delete(id);
  });
  $('btn-preview-caption-image').addEventListener('click', () => openLightbox($('caption-editor-image-url').value || ''));
  $('btn-send-caption-to-prompt').addEventListener('click', sendCaptionEditorToPrompt);
  $('btn-caption-to-prompt').addEventListener('click', captionEditorToPromptRecord);
  $('btn-update-caption-record').addEventListener('click', updateCaptionRecord);
  $('btn-delete-caption-record').addEventListener('click', deleteCaptionRecord);

  $('btn-run-global-search').addEventListener('click', runGlobalSearch);
  $('btn-clear-global-search').addEventListener('click', clearGlobalSearchResults);
  $('global-search-results').addEventListener('click', async (e) => {
    const btn = e.target.closest('[data-search-open]');
    if (!btn) return;
    await openSearchResult(btn.dataset.searchOpen, btn.dataset.searchId, btn.dataset.searchName);
  });
  $('recent-items-grid').addEventListener('click', async (e) => {
    const btn = e.target.closest('[data-recent-open]');
    if (!btn) return;
    const [kind, id] = recentKindToSearchKind(btn.dataset.recentOpen, btn.dataset.recentName || '');
    if (!kind) return;
    await openSearchResult(kind, id || btn.dataset.recentId || '', btn.dataset.recentName || '');
  });
  $('btn-refresh-recent-items').addEventListener('click', refreshRecentItems);

  $('btn-batch-preview').addEventListener('click', previewBatch);
  $('btn-run-batch').addEventListener('click', runBatchCaption);
  $('btn-batch-cancel').addEventListener('click', cancelBatchCaption);
  $('btn-batch-resume').addEventListener('click', resumeBatchCaption);
  $('btn-batch-retry').addEventListener('click', retryFailedBatchCaption);
  $('btn-batch-export-log').addEventListener('click', exportBatchLog);
  $('btn-batch-cancel-post-action').addEventListener('click', cancelBatchPostAction);
  if ($('btn-interrupted-batch-resume')) $('btn-interrupted-batch-resume').addEventListener('click', () => handleInterruptedBatchAction('resume'));
  if ($('btn-interrupted-batch-start-fresh')) $('btn-interrupted-batch-start-fresh').addEventListener('click', () => handleInterruptedBatchAction('start_fresh'));
  if ($('btn-interrupted-batch-open-log')) $('btn-interrupted-batch-open-log').addEventListener('click', () => handleInterruptedBatchAction('open_log'));
  if ($('btn-interrupted-batch-cancel')) $('btn-interrupted-batch-cancel').addEventListener('click', () => handleInterruptedBatchAction('cancel'));
  $('batch-session-select').addEventListener('change', async e => {
    if (!e.target.value) return;
    currentBatchJobId = e.target.value;
    await pollBatchStatus();
  });
  $('btn-batch-input-folder').addEventListener('click', () => browseForFolder('batch-folder'));
  $('btn-batch-output-folder').addEventListener('click', () => browseForFolder('batch-output-folder'));
  $('btn-save-settings').addEventListener('click', saveSettings);
  $('btn-export-presets').addEventListener('click', exportPresets);
  $('btn-import-presets').addEventListener('click', importPresets);
  $('btn-export-library').addEventListener('click', exportLibraryPack);
  $('btn-import-library').addEventListener('click', importLibraryPack);

  if (typeof populateLibraryExportCategories === 'function') populateLibraryExportCategories(initialCategories);
  if ($('library-export-full-snapshot')) {
    $('library-export-full-snapshot').addEventListener('change', e => {
      const disabled = !!e.target.checked;
      ['library-export-prompts','library-export-captions','library-export-characters','library-export-presets','library-export-categories','library-export-metadata','library-export-bundles','library-export-categories-select'].forEach(id => {
        if ($(id)) $(id).disabled = disabled;
      });
    });
  }

  $('btn-close-lightbox').addEventListener('click', closeLightbox);
  $('image-lightbox').addEventListener('click', e => { if (e.target.id === 'image-lightbox') closeLightbox(); });
  document.addEventListener('keydown', e => { if (e.key === 'Escape') closeLightbox(); });
});
