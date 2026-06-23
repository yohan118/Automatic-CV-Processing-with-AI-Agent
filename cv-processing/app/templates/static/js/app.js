/**
 * Automatic CV Processing System v7 — Frontend
 * Shows CrossLang dictionary score + TF-IDF.
 * Matched keywords now show both JD term and CV term.
 * Per-user authentication and data isolation.
 */

/* ---------- LOGOUT ---------- */
async function doLogout() {
    try {
        await fetch('/api/auth/logout', { method: 'POST' });
    } catch(e) {}
    window.location.href = '/login';
}

let activeJobId = null;
let selectedFiles = [];

document.addEventListener('DOMContentLoaded', () => {

    const uploadArea = document.getElementById('upload-area');
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.style.borderColor = 'var(--color-primary)';
    });
    uploadArea.addEventListener('dragleave', () => {
        uploadArea.style.borderColor = '';
    });
    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.style.borderColor = '';
        addFiles(Array.from(e.dataTransfer.files));
    });
});

function notify(message, type) {
    type = type || 'info';
    var el = document.createElement('div');
    el.className = 'toast ' + type;
    el.textContent = message;
    document.body.appendChild(el);
    setTimeout(function() { el.remove(); }, 4000);
}

/* ===== JOB DESCRIPTIONS ===== */

async function createJobDescription() {
    var title = document.getElementById('jd-title').value.trim();
    var text = document.getElementById('jd-text').value.trim();

    if (!title) { notify('Please enter a job title.', 'error'); return; }
    if (!text) { notify('Please enter the job description text.', 'error'); return; }

    var btn = document.getElementById('btn-create-jd');
    btn.disabled = true;
    btn.textContent = 'Creating...';

    try {
        var res = await fetch('/api/jobs', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title: title, original_text: text }),
        });
        if (!res.ok) throw new Error((await res.json()).detail || 'Failed');

        var job = await res.json();
        selectJob(job.id, job.title);
        notify('Job description created successfully.', 'success');
    } catch (e) {
        notify(e.message, 'error');
    } finally {
        btn.disabled = false;
        btn.textContent = 'Create Job Description';
    }
}

function selectJob(jobId, jobTitle) {
    activeJobId = jobId;
    document.getElementById('active-jd').classList.remove('hidden');
    document.getElementById('active-jd-title').textContent = jobTitle;
    document.getElementById('active-jd-id').textContent = jobId;
    loadResults();
}

async function deleteJob(jobId) {
    if (!confirm('Delete this job and all associated CVs?')) return;
    try {
        await fetch('/api/jobs/' + jobId, { method: 'DELETE' });
        if (activeJobId === jobId) {
            activeJobId = null;
            document.getElementById('active-jd').classList.add('hidden');
        }
        document.getElementById('results-list').innerHTML = '';
        document.getElementById('results-summary').classList.add('hidden');
        document.getElementById('export-bar').classList.add('hidden');
        notify('Job deleted.', 'success');
    } catch (e) {
        notify('Failed to delete.', 'error');
    }
}

/* ===== FILE UPLOAD ===== */

function handleFileSelect(event) {
    addFiles(Array.from(event.target.files));
    event.target.value = '';
}

function addFiles(files) {
    for (var i = 0; i < files.length; i++) {
        var f = files[i];
        var ext = f.name.split('.').pop().toLowerCase();
        if (ext !== 'pdf' && ext !== 'docx') {
            notify('"' + f.name + '" is not supported. Use PDF or DOCX.', 'error');
            continue;
        }
        if (f.size > 10 * 1024 * 1024) {
            notify('"' + f.name + '" exceeds 10 MB limit.', 'error');
            continue;
        }
        selectedFiles.push(f);
    }
    renderFileList();
}

function removeFile(index) {
    selectedFiles.splice(index, 1);
    renderFileList();
}

function renderFileList() {
    var container = document.getElementById('file-list');
    var btn = document.getElementById('btn-process');

    if (selectedFiles.length === 0) {
        container.classList.add('hidden');
        btn.classList.add('hidden');
        return;
    }
    container.classList.remove('hidden');
    btn.classList.remove('hidden');

    var html = '';
    for (var i = 0; i < selectedFiles.length; i++) {
        var f = selectedFiles[i];
        html += '<div class="file-item">';
        html += '<span class="file-item-name">' + f.name + '</span>';
        html += '<span class="file-item-size">' + (f.size / 1024).toFixed(1) + ' KB</span>';
        html += '<span class="file-item-remove" onclick="removeFile(' + i + ')">x</span>';
        html += '</div>';
    }
    container.innerHTML = html;
}

/* ===== PROCESSING ===== */

async function processAllCVs() {
    if (!activeJobId) { notify('Select a job description first.', 'error'); return; }
    if (selectedFiles.length === 0) { notify('Upload at least one CV file.', 'error'); return; }

    var btn = document.getElementById('btn-process');
    btn.disabled = true;
    btn.textContent = 'Processing...';

    var progressContainer = document.getElementById('progress-container');
    var progressFill = document.getElementById('progress-fill');
    var progressText = document.getElementById('progress-text');
    progressContainer.classList.remove('hidden');

    var total = selectedFiles.length;
    var completed = 0;

    for (var i = 0; i < selectedFiles.length; i++) {
        var file = selectedFiles[i];
        progressText.textContent = 'Processing ' + file.name + ' (' + (completed + 1) + '/' + total + ')...';
        progressFill.style.width = (completed / total * 100) + '%';

        try {
            var formData = new FormData();
            formData.append('file', file);
            var res = await fetch('/api/jobs/' + activeJobId + '/cvs', {
                method: 'POST',
                body: formData,
            });
            if (!res.ok) {
                var err = await res.json();
                notify('Error with ' + file.name + ': ' + err.detail, 'error');
            }
        } catch (e) {
            notify('Error with ' + file.name + ': ' + e.message, 'error');
        }
        completed++;
        progressFill.style.width = (completed / total * 100) + '%';
    }

    progressText.textContent = 'Done. Processed ' + completed + ' of ' + total + ' CVs.';
    btn.disabled = false;
    btn.textContent = 'Process All CVs';
    selectedFiles = [];
    renderFileList();
    loadResults();
    notify(completed + ' CVs processed.', 'success');
    setTimeout(function() { progressContainer.classList.add('hidden'); }, 3000);
}

/* ===== RESULTS ===== */

async function loadResults() {
    if (!activeJobId) return;

    try {
        var summaryRes = await fetch('/api/jobs/' + activeJobId + '/results/summary');
        var summary = await summaryRes.json();
        var summaryContainer = document.getElementById('results-summary');

        if (summary.total_cvs > 0) {
            summaryContainer.classList.remove('hidden');
            document.getElementById('export-bar').classList.remove('hidden');
            summaryContainer.innerHTML =
                '<div class="summary-item"><div class="summary-number">' + summary.total_cvs + '</div><div class="summary-label">Total CVs</div></div>' +
                '<div class="summary-item"><div class="summary-number">' + summary.completed + '</div><div class="summary-label">Processed</div></div>' +
                '<div class="summary-item"><div class="summary-number">' + (summary.highest_score * 100).toFixed(1) + '%</div><div class="summary-label">Best Match</div></div>' +
                '<div class="summary-item"><div class="summary-number">' + (summary.average_score * 100).toFixed(1) + '%</div><div class="summary-label">Average</div></div>';
        } else {
            document.getElementById('export-bar').classList.add('hidden');
        }

        var rankedRes = await fetch('/api/jobs/' + activeJobId + '/results');
        var ranked = await rankedRes.json();
        var resultsList = document.getElementById('results-list');

        if (ranked.total_cvs === 0) {
            resultsList.innerHTML = '<div class="empty-state"><svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" opacity="0.3"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14,2 14,8 20,8"/></svg><p>No results yet. Upload CVs to begin.</p></div>';
            return;
        }

        var html = '';
        for (var i = 0; i < ranked.ranked_cvs.length; i++) {
            var cv = ranked.ranked_cvs[i];
            var scoreClass = getScoreClass(cv.similarity_label);
            var rankClass = cv.rank <= 3 ? 'rank-' + cv.rank : 'rank-other';

            // Show matched keywords with both JD and CV terms
            var keywords = '';
            var kwList = cv.matched_keywords.slice(0, 6);
            for (var k = 0; k < kwList.length; k++) {
                var kw = kwList[k];
                var label = kw.keyword;
                if (kw.cv_term && kw.cv_term !== kw.keyword) {
                    label = kw.cv_term + ' = ' + kw.keyword;
                }
                keywords += '<span class="kw-tag">' + label + '</span>';
            }

            var parsedTags = '';
            if (cv.parsed_degree) {
                parsedTags += '<span class="parsed-tag degree">' + cv.parsed_degree + '</span>';
            }
            if (cv.parsed_name) {
                parsedTags += '<span class="parsed-tag">' + cv.parsed_name + '</span>';
            }

            html += '<div class="result-card">';
            html += '<div class="result-top-row">';
            html += '<div class="rank-num ' + rankClass + '">' + cv.rank + '</div>';
            html += '<div class="result-info">';
            html += '<div class="result-filename">' + cv.filename + '</div>';
            html += '<div class="result-meta-line">';
            html += (cv.detected_language || 'Unknown') + ' &middot; ';
            if (cv.matching_method === 'claude_api') {
                html += '<span class="method-badge claude-badge">Claude Sonnet</span> &middot; ';
                html += 'Claude: ' + (cv.claude_score * 100).toFixed(1) + '% &middot; ';
                html += 'TF-IDF: ' + (cv.tfidf_score * 100).toFixed(1) + '%';
            } else {
                html += cv.matched_keyword_count + ' dictionary matches &middot; ';
                html += 'CrossLang: ' + (cv.crosslang_score * 100).toFixed(1) + '% &middot; ';
                html += 'TF-IDF: ' + (cv.tfidf_score * 100).toFixed(1) + '%';
            }
            html += '</div>';

            if (cv.claude_summary) {
                html += '<div class="claude-summary">' + cv.claude_summary + '</div>';
            }

            html += '<div class="result-actions">';
            if (cv.status === 'cleaned') {
                html += '<span class="cleaned-badge">Files Cleared</span>';
            } else {
                html += '<button class="btn-preview" onclick="event.stopPropagation();showCVDetail(' + activeJobId + ',' + cv.cv_id + ')">Details</button>';
                html += '<button class="btn-preview" onclick="event.stopPropagation();previewFile(' + activeJobId + ',' + cv.cv_id + ')">Preview File</button>';
            }
            html += '</div>';

            if (parsedTags) {
                html += '<div class="result-parsed">' + parsedTags + '</div>';
            }
            html += '</div>';

            html += '<div class="result-score-box">';
            html += '<div class="score-value ' + scoreClass + '">' + cv.similarity_percentage.toFixed(1) + '%</div>';
            html += '<div class="score-label-text ' + scoreClass + '">' + cv.similarity_label + '</div>';
            html += '</div></div>';

            if (keywords) {
                html += '<div class="result-keywords">' + keywords + '</div>';
            }
            html += '</div>';
        }
        resultsList.innerHTML = html;

        // Update privacy button state
        var privBtn = document.getElementById('btn-privacy');
        var anyCleaned = ranked.ranked_cvs.some(function(cv) { return cv.status === 'cleaned'; });
        if (anyCleaned) {
            privBtn.disabled = true;
            privBtn.textContent = 'Files Cleared';
            privBtn.style.background = '#f0fdf4';
            privBtn.style.borderColor = '#bbf7d0';
            privBtn.style.color = '#16a34a';
        } else {
            privBtn.disabled = false;
            privBtn.textContent = 'Clear CV Files';
            privBtn.style.background = '';
            privBtn.style.borderColor = '';
            privBtn.style.color = '';
        }

    } catch (e) {
        console.error('Failed to load results:', e);
    }
}

function getScoreClass(label) {
    if (label === 'Excellent Match') return 'score-excellent';
    if (label === 'Good Match') return 'score-good';
    if (label === 'Fair Match') return 'score-fair';
    if (label === 'Weak Match') return 'score-weak';
    return 'score-poor';
}

/* ===== CV DETAIL MODAL ===== */

async function showCVDetail(jobId, cvId) {
    try {
        var res = await fetch('/api/jobs/' + jobId + '/cvs/' + cvId);
        var cv = await res.json();

        // Matched keywords with cross-language details
        var matchedKw = '';
        var mkw = cv.matched_keywords || [];
        for (var i = 0; i < mkw.length; i++) {
            var kw = mkw[i];
            var label = kw.keyword;
            if (kw.cv_term && kw.cv_term !== kw.keyword) {
                label = kw.cv_term + ' → ' + kw.keyword;
            }
            var cat = kw.category ? ' [' + kw.category + ']' : '';
            matchedKw += '<span class="detail-kw">' + label + cat + '</span> ';
        }

        var allKw = '';
        var akw = (cv.extracted_keywords || []).slice(0, 20);
        for (var i = 0; i < akw.length; i++) {
            allKw += '<span class="detail-kw all">' + akw[i].keyword + '</span> ';
        }

        var skills = '';
        var sk = cv.parsed_skills || [];
        for (var i = 0; i < sk.length; i++) {
            skills += '<span class="detail-kw">' + sk[i] + '</span> ';
        }

        var rawPreview = cv.raw_text ? cv.raw_text.substring(0, 1200) : 'N/A';
        if (cv.raw_text && cv.raw_text.length > 1200) rawPreview += '...';

        var transPreview = '';
        if (cv.detected_language !== 'ckb' && cv.translated_text) {
            transPreview = cv.translated_text.substring(0, 1200);
            if (cv.translated_text.length > 1200) transPreview += '...';
        }

        var body = '';
        body += '<h2 style="font-size:1.1rem;margin-bottom:20px;">' + cv.filename + '</h2>';

        // Scores — now shows CrossLang instead of Semantic
        body += '<div class="detail-block"><div class="detail-label">Scoring Breakdown</div>';
        body += '<div class="detail-scores">';
        body += '<div class="detail-score-item"><div class="detail-score-number">' + (cv.crosslang_score * 100).toFixed(1) + '%</div><div class="detail-score-label">Dictionary Match (70%)</div></div>';
        body += '<div class="detail-score-item"><div class="detail-score-number">' + (cv.similarity_score * 100).toFixed(1) + '%</div><div class="detail-score-label">TF-IDF Score (30%)</div></div>';
        body += '<div class="detail-score-item"><div class="detail-score-number" style="color:var(--color-success)">' + cv.similarity_percentage.toFixed(1) + '%</div><div class="detail-score-label">Combined Score</div></div>';
        body += '</div></div>';

        // Parsed info
        body += '<div class="detail-block"><div class="detail-label">Parsed Information</div>';
        body += '<div class="detail-parsed-grid">';
        body += '<div class="parsed-field"><div class="parsed-field-label">Name</div><div class="parsed-field-value">' + (cv.parsed_name || 'Not detected') + '</div></div>';
        body += '<div class="parsed-field"><div class="parsed-field-label">Email</div><div class="parsed-field-value">' + (cv.parsed_email || 'Not detected') + '</div></div>';
        body += '<div class="parsed-field"><div class="parsed-field-label">Phone</div><div class="parsed-field-value">' + (cv.parsed_phone || 'Not detected') + '</div></div>';
        body += '<div class="parsed-field"><div class="parsed-field-label">Degree</div><div class="parsed-field-value" style="font-weight:600;color:var(--color-warning)">' + (cv.parsed_degree || 'Not detected') + '</div></div>';
        body += '</div></div>';

        if (skills) {
            body += '<div class="detail-block"><div class="detail-label">Detected Skills</div>';
            body += '<div class="detail-keywords-wrap">' + skills + '</div></div>';
        }

        body += '<div class="detail-block"><div class="detail-label">Cross-Language Dictionary Matches (' + mkw.length + ')</div>';
        body += '<div class="detail-keywords-wrap">' + (matchedKw || '<span style="color:var(--color-text-muted);font-size:0.85rem;">No matches found</span>') + '</div></div>';

        body += '<div class="detail-block"><div class="detail-label">All Extracted Keywords</div>';
        body += '<div class="detail-keywords-wrap">' + (allKw || '<span style="color:var(--color-text-muted);font-size:0.85rem;">None</span>') + '</div></div>';

        body += '<div class="detail-block"><div class="detail-label">Raw Extracted Text</div>';
        body += '<div class="detail-text-box">' + rawPreview + '</div></div>';

        if (transPreview) {
            body += '<div class="detail-block"><div class="detail-label">Translated Text — Approximate (Kurdish Sorani)</div>';
            body += '<div class="detail-text-box">' + transPreview + '</div></div>';
        }

        body += '<div class="detail-block"><div class="detail-label">Pipeline Status</div>';
        body += '<div class="detail-value">Language: ' + cv.detected_language + ' | Status: ' + cv.status;
        if (cv.error_message) body += ' | Error: ' + cv.error_message;
        body += '</div></div>';

        document.getElementById('modal-body').innerHTML = body;
        document.getElementById('cv-modal').classList.remove('hidden');
    } catch (e) {
        notify('Failed to load CV details.', 'error');
    }
}

function closeModal() {
    document.getElementById('cv-modal').classList.add('hidden');
}

/* ===== FILE PREVIEW ===== */

function previewFile(jobId, cvId) {
    var url = '/api/jobs/' + jobId + '/cvs/' + cvId + '/preview';
    document.getElementById('preview-iframe').src = url;
    document.getElementById('preview-modal').classList.remove('hidden');
}

function closePreview() {
    document.getElementById('preview-modal').classList.add('hidden');
    document.getElementById('preview-iframe').src = '';
}

/* ===== EXPORT ===== */

function exportPDF() {
    if (!activeJobId) { notify('No job selected.', 'error'); return; }
    window.open('/api/jobs/' + activeJobId + '/export/pdf', '_blank');
}

function exportExcel() {
    if (!activeJobId) { notify('No job selected.', 'error'); return; }
    window.open('/api/jobs/' + activeJobId + '/export/excel', '_blank');
}

/* ===== PRIVACY CLEANUP ===== */
async function privacyCleanup() {
    if (!activeJobId) { notify('No job selected.', 'error'); return; }

    var confirmed = confirm(
        'Privacy Cleanup\n\n' +
        'This will permanently delete:\n' +
        '• All uploaded CV files from the server\n' +
        '• Personal data (names, emails, phone numbers)\n' +
        '• Raw and translated text content\n\n' +
        'Rankings and scores will be preserved.\n\n' +
        'This action cannot be undone. Continue?'
    );
    if (!confirmed) return;

    var btn = document.getElementById('btn-privacy');
    btn.disabled = true;
    btn.textContent = 'Cleaning...';

    try {
        var res = await fetch('/api/jobs/' + activeJobId + '/privacy-cleanup', {
            method: 'POST',
        });
        if (!res.ok) throw new Error((await res.json()).detail || 'Failed');

        var data = await res.json();
        notify(data.message, 'success');

        btn.textContent = 'Files Cleared';
        btn.style.background = '#f0fdf4';
        btn.style.borderColor = '#bbf7d0';
        btn.style.color = '#16a34a';

        loadResults();
    } catch (e) {
        notify(e.message, 'error');
        btn.disabled = false;
        btn.textContent = 'Clear CV Files';
    }
}

/* ===== KEYBOARD ===== */
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        closeModal();
        closePreview();
    }
});
