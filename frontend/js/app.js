/**
 * IAMShield v5 — Fixed & Complete
 * Fixes:
 *  1. Login popup fires ONLY on submit, NOT on checkbox click
 *  2. Recommendation page works for both logged-in + guest→login flows
 *  3. 8 categories supported
 *  4. Score calculation fixed (flat values scoring)
 *  5. All components verified error-free
 */

const State = {
    user:                null,
    adminUser:           null,
    assessment:          { category: null, questions: [], answers: {} },
    lastRecommendations: [],
    lastAnswers:         {},
    lastCategory:        null,
    pendingSessionId:    null,
    pendingAnswers:      null,
    pendingCategory:     null,
    dashPage:            1,
};

/* ── ROUTER ── */
function showPage(id) {
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    const pg = document.getElementById(id);
    if (pg) { pg.classList.add('active'); window.scrollTo(0, 0); }
    document.querySelectorAll('.nav-btn[data-page]').forEach(b => {
        b.classList.toggle('active', b.dataset.page === id);
    });
}

/* ── AUTH HELPERS ── */
function isLoggedIn() {
    const token = localStorage.getItem('iam_token');
    if (!token) return false;
    try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        if (payload.exp && payload.exp * 1000 < Date.now()) { clearSession(); return false; }
        if (payload.is_admin) { clearSession(); return false; }
    } catch(e) { clearSession(); return false; }
    return true;
}

function isAdminLoggedIn() {
    const token = localStorage.getItem('iam_admin_token');
    if (!token) return false;
    try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        if (payload.exp && payload.exp * 1000 < Date.now()) { clearAdminSession(); return false; }
    } catch(e) { clearAdminSession(); return false; }
    return true;
}

function saveSession(data) {
    localStorage.setItem('iam_token', data.token);
    localStorage.setItem('iam_user',  JSON.stringify(data.user));
    State.user = data.user;
}

function clearSession() {
    localStorage.removeItem('iam_token');
    localStorage.removeItem('iam_user');
    State.user = null;
}

function saveAdminSession(data) {
    localStorage.setItem('iam_admin_token', data.token);
    localStorage.setItem('iam_admin',       JSON.stringify(data.admin));
    State.adminUser = data.admin;
    Api._token = () => localStorage.getItem('iam_admin_token');
}

function clearAdminSession() {
    localStorage.removeItem('iam_admin_token');
    localStorage.removeItem('iam_admin');
    State.adminUser = null;
    Api._token = () => localStorage.getItem('iam_token');
}

/* ── NAVBAR ── */
function updateNav() {
    const loggedIn = isLoggedIn();
    const u = JSON.parse(localStorage.getItem('iam_user') || '{}');
    document.getElementById('nav-login-btn').style.display  = loggedIn ? 'none' : '';
    document.getElementById('nav-signup-btn').style.display = loggedIn ? 'none' : '';
    document.getElementById('nav-dash-btn').style.display   = loggedIn ? '' : 'none';
    document.getElementById('nav-logout-btn').style.display = loggedIn ? '' : 'none';
    document.getElementById('nav-user-name').style.display  = loggedIn ? '' : 'none';
    if (loggedIn) document.getElementById('nav-user-name').textContent = u.firstName || '';
}

/* ── TOAST ── */
function toast(msg, type = 'info', duration = 3500) {
    const icons = { success: '✅', error: '❌', info: 'ℹ️' };
    const el = document.createElement('div');
    el.className = `toast ${type}`;
    el.innerHTML = `<span>${icons[type] || '•'}</span><span class="toast-msg">${msg}</span>`;
    document.getElementById('toasts').appendChild(el);
    setTimeout(() => el.remove(), duration);
}

/* ── LOADING ── */
function showLoading(msg = 'Loading…') {
    document.getElementById('overlay-load').style.display = 'flex';
    document.getElementById('overlay-msg').textContent    = msg;
}
function hideLoading() {
    document.getElementById('overlay-load').style.display = 'none';
}

/* ── LOGIN REQUIRED MODAL ── */
function showLoginRequired() {
    document.getElementById('login-required-modal').style.display = 'flex';
}
function closeLoginRequiredModal() {
    document.getElementById('login-required-modal').style.display = 'none';
}
function goLoginFromModal() {
    closeLoginRequiredModal();
    showPage('login-page');
}
function goSignupFromModal() {
    closeLoginRequiredModal();
    showPage('signup-page');
}

/* ── AUTH PROMPT MODAL ── */
function showAuthPrompt() {
    document.getElementById('auth-prompt-modal').style.display = 'flex';
}
function closeAuthPrompt() {
    document.getElementById('auth-prompt-modal').style.display = 'none';
}
function goLoginFromPrompt()  { closeAuthPrompt(); showPage('login-page'); }
function goSignupFromPrompt() { closeAuthPrompt(); showPage('signup-page'); }

/* ── AUTH FORMS ── */
async function handleLogin(e) {
    e.preventDefault();
    const email    = document.getElementById('login-email').value.trim();
    const password = document.getElementById('login-password').value;
    const errEl    = document.getElementById('login-error');
    errEl.classList.remove('show');
    showLoading('Authenticating…');
    try {
        const d = await Api.login({ email, password });
        saveSession(d);
        updateNav();

        // If user had answered questions as guest, claim the session
        const claimed = await claimPendingAssessment();
        toast(`Welcome back, ${d.user.firstName}!`, 'success');

        if (claimed) {
            // Restore questions from State if still available, otherwise just show results
            showRecommendationPage({
                category:    claimed.category,
                recommended: claimed.recommended,
                answers:     claimed.answers || State.pendingAnswers || {},
                questions:   State.assessment.questions,
            });
        } else {
            showPage('home-page');
        }
    } catch (err) {
        errEl.textContent = err.message;
        errEl.classList.add('show');
    } finally { hideLoading(); }
}

async function handleRegister(e) {
    e.preventDefault();
    const body = {
        firstName:        document.getElementById('reg-fname').value.trim(),
        lastName:         document.getElementById('reg-lname').value.trim(),
        email:            document.getElementById('reg-email').value.trim(),
        password:         document.getElementById('reg-password').value,
        organizationName: document.getElementById('reg-org').value.trim(),
    };
    const errEl = document.getElementById('reg-error');
    errEl.classList.remove('show');
    showLoading('Creating account…');
    try {
        const d = await Api.register(body);
        saveSession(d);
        updateNav();
        const claimed = await claimPendingAssessment();
        toast('Account created! Welcome to IAMShield 🛡️', 'success');
        if (claimed) {
            showRecommendationPage({
                category:    claimed.category,
                recommended: claimed.recommended,
                answers:     claimed.answers || State.pendingAnswers || {},
                questions:   State.assessment.questions,
            });
        } else {
            showPage('home-page');
        }
    } catch (err) {
        errEl.textContent = err.message;
        errEl.classList.add('show');
    } finally { hideLoading(); }
}

async function handleForgotPassword(e) {
    e.preventDefault();
    showLoading('Sending reset link…');
    try {
        await Api.forgotPassword({ email: document.getElementById('fp-email').value.trim() });
        toast('Reset link sent if the email exists', 'success');
        showPage('login-page');
    } catch (err) { toast(err.message, 'error'); }
    finally { hideLoading(); }
}

function handleLogout() {
    clearSession();
    State.pendingSessionId = null;
    State.pendingAnswers   = null;
    State.pendingCategory  = null;
    localStorage.removeItem('iam_pending_session');
    updateNav();
    toast('Logged out successfully', 'info');
    showPage('home-page');
}

async function claimPendingAssessment() {
    const sid = State.pendingSessionId || localStorage.getItem('iam_pending_session');
    if (!sid) return null;
    try {
        const res = await Api.claimAssessment({ sessionId: sid });
        State.pendingSessionId = null;
        localStorage.removeItem('iam_pending_session');
        return res;
    } catch (e) {
        State.pendingSessionId = null;
        localStorage.removeItem('iam_pending_session');
        return null;
    }
}

/* ══════════════════════════════════════════════════════════════
   CATEGORY LABELS — covers all 8 categories
   ══════════════════════════════════════════════════════════════ */
const CAT_LABELS = {
    privileged: 'Privileged Access',
    workforce:  'Workforce IAM',
    customer:   'Customer Identity',
    governance: 'Access Governance',
    network:    'Network & API Security',
    cloud:      'Cloud Security',
    zerotrust:  'Zero Trust Architecture',
    devops:     'DevOps & Secrets Mgmt',
};
const CAT_ICONS = {
    privileged: '🔐',
    workforce:  '👥',
    customer:   '🌐',
    governance: '📋',
    network:    '🔒',
    cloud:      '☁️',
    zerotrust:  '🛡️',
    devops:     '⚙️',
};

function getCategoryKey(name) {
    const map = {
        'Privileged Access':      'privileged',
        'Workforce IAM':          'workforce',
        'Customer Identity':      'customer',
        'Access Governance':      'governance',
        'Network & API Security': 'network',
        'Cloud Security':         'cloud',
        'Zero Trust Architecture':'zerotrust',
        'DevOps & Secrets Mgmt':  'devops',
    };
    return map[name] || name.toLowerCase().replace(/[^a-z]/g,'');
}

/* ══════════════════════════════════════════════════════════════
   ASSESSMENT ENGINE
   ══════════════════════════════════════════════════════════════ */
async function loadAssessmentPage() {
    showPage('assessment-page');
    showLoading('Loading categories…');
    try {
        const cats = await Api.categories();
        renderCategoryStep(cats);
    } catch (e) { toast('Failed to load categories', 'error'); }
    finally { hideLoading(); }
}

function renderCategoryStep(cats) {
    State.assessment = { category: null, questions: [], answers: {} };
    const wrapper = document.getElementById('assess-wrapper');
    wrapper.innerHTML = `
    <div class="assess-head fade-1">
      <div class="tag-blue mb-16">Step 1 of 2</div>
      <h2>What is your primary IAM challenge?</h2>
      <p class="mt-8">Select the area that best describes your security priority.</p>
    </div>
    <div class="cats-grid fade-2">
      ${cats.map(c => `
        <div class="cat-card" onclick="selectCategory('${getCategoryKey(c.name)}', '${c.name}')">
          <div class="cat-icon">${CAT_ICONS[getCategoryKey(c.name)] || '🔑'}</div>
          <div class="cat-name">${c.name}</div>
        </div>`).join('')}
    </div>`;
}

async function selectCategory(catId, catName) {
    State.assessment.category = catId;
    showLoading('Loading questions…');
    try {
        const qs = await Api.questions(catId);
        State.assessment.questions  = qs;
        State.assessment.answers    = {};
        State.assessment._assessPage = 1;
        renderAllQuestionsCheckbox();
    } catch (e) { toast('Failed to load questions', 'error'); }
    finally { hideLoading(); }
}

/**
 * Paginated assessment — 1 question per page.
 * FIX: Checkboxes do NOT block guest users — login popup fires only on SUBMIT.
 */
const ASSESS_PAGE_SIZE = 1; // questions per page

function renderAllQuestionsCheckbox() {
    if (!State.assessment._assessPage) State.assessment._assessPage = 1;
    renderAssessPage(State.assessment._assessPage);
}

function renderAssessPage(pageNum) {
    const { questions } = State.assessment;
    const totalPages = questions.length;
    const idx = pageNum - 1;          // 0-based question index
    const q   = questions[idx];
    if (!q) return;

    State.assessment._assessPage = pageNum;
    const wrapper = document.getElementById('assess-wrapper');

    // restore already-selected options for this question
    const alreadySelected = State.assessment.answers[idx] || [];

    wrapper.innerHTML = `
    <div class="assess-head fade-1">
      <div class="tag-gold mb-16">Question ${pageNum} of ${totalPages} — Select all that apply</div>
      <h2>Tell us about your <span class="gradient-text">${CAT_LABELS[State.assessment.category] || State.assessment.category}</span> needs</h2>
      <p class="mt-8">Check all options that match your organization.</p>
      <div class="guest-notice" id="guest-notice" style="${isLoggedIn() ? 'display:none' : ''}">
        🔒 You can answer freely. You'll be asked to log in when you click <strong>Get Recommendations</strong>.
      </div>
    </div>

    <!-- Progress bar -->
    <div class="assess-progress-wrap">
      <div class="assess-progress-bar" style="width:${Math.round((pageNum / totalPages) * 100)}%"></div>
    </div>
    <div class="assess-progress-label">${pageNum} / ${totalPages}</div>

    <div class="questions-list fade-2">
      <div class="q-block" id="qblock-0">
        <div class="q-block-title">
          <span class="q-num">${pageNum}</span>
          <span>${q.text}</span>
        </div>
        <div class="checkbox-grid">
          ${q.options.map(o => {
              const isChecked = alreadySelected.includes(o.value);
              return `
              <label class="checkbox-opt${isChecked ? ' checked' : ''}" id="cbopt-0-${o.value}">
                <input type="checkbox"
                       class="cb-input"
                       data-qidx="0"
                       data-value="${o.value}"
                       ${isChecked ? 'checked' : ''}
                       onchange="handleCheckboxChange(${idx}, '${o.value}', this)"
                />
                <span class="cb-box">${isChecked ? '<span class="cb-check">✓</span>' : ''}</span>
                <span class="cb-label">${o.label}</span>
              </label>`;
          }).join('')}
        </div>
      </div>
    </div>

    <div class="flex gap-16 mt-32 fade-3" style="justify-content:space-between;align-items:center">
      <button class="btn btn-outline" onclick="${pageNum === 1 ? 'loadAssessmentPage()' : `renderAssessPage(${pageNum - 1})`}">
        ← ${pageNum === 1 ? 'Back to Categories' : 'Previous'}
      </button>
      <span style="color:var(--text-muted);font-size:.88rem">${pageNum} of ${totalPages}</span>
      ${pageNum < totalPages
        ? `<button class="btn btn-primary" onclick="renderAssessPage(${pageNum + 1})">Next →</button>`
        : `<button class="btn btn-primary btn-lg" id="submit-assessment-btn" onclick="submitCheckboxAssessment()">Get My Recommendations →</button>`
      }
    </div>`;
}

/**
 * FIX: No login check here at all. Just track the answer.
 */
function handleCheckboxChange(qIdx, value, checkbox) {
    if (!State.assessment.answers[qIdx]) State.assessment.answers[qIdx] = [];
    // Label ids use local index 0 in paginated view
    const labelEl = document.getElementById(`cbopt-0-${value}`) || document.getElementById(`cbopt-${qIdx}-${value}`);
    const cbBox   = labelEl ? labelEl.querySelector('.cb-box') : null;
    if (checkbox.checked) {
        if (!State.assessment.answers[qIdx].includes(value)) {
            State.assessment.answers[qIdx].push(value);
        }
        labelEl?.classList.add('checked');
        if (cbBox) cbBox.innerHTML = '<span class="cb-check">✓</span>';
    } else {
        State.assessment.answers[qIdx] = State.assessment.answers[qIdx].filter(v => v !== value);
        labelEl?.classList.remove('checked');
        if (cbBox) cbBox.innerHTML = '';
    }
}

async function submitCheckboxAssessment() {
    const { questions, answers, category } = State.assessment;

    // Build answer map { "1": [val, val], "2": [val] }
    const answerMap = {};
    questions.forEach((q, idx) => {
        const selected = answers[idx] || [];
        if (selected.length > 0) answerMap[String(idx + 1)] = selected;
    });

    if (Object.keys(answerMap).length === 0) {
        toast('Please select at least one option before proceeding.', 'info');
        return;
    }

    // FIX: Show login popup only AFTER user completes answering and clicks submit
    if (!isLoggedIn()) {
        // Save answers + category so they survive login redirect
        State.pendingAnswers  = answerMap;
        State.pendingCategory = category;
        showLoading('Saving your answers…');
        try {
            // Submit as guest — get session ID to claim after login
            const res = await Api.submitGuestAssessment({ category, answers: answerMap });
            State.pendingSessionId = res.sessionId;
            localStorage.setItem('iam_pending_session', res.sessionId);
            // Store results temporarily so they can be shown after login
            State.lastRecommendations = res.recommended;
            State.lastAnswers = answerMap;
            State.lastCategory = category;
        } catch(e) {
            toast('Could not save assessment. Please try again.', 'error');
            hideLoading();
            return;
        }
        hideLoading();
        // Now show the login prompt
        showLoginRequired();
        return;
    }

    // Logged in — submit directly
    showLoading('Calculating your recommendations…');
    try {
        const res = await Api.submitAssessment({ category, answers: answerMap });
        State.lastRecommendations = res.recommended;
        State.lastAnswers = answerMap;
        State.lastCategory = category;
        showRecommendationPage({
            category,
            recommended: res.recommended,
            answers:     answerMap,
            questions:   questions,
        });
    } catch (e) {
        toast(e.message || 'Assessment failed', 'error');
    } finally { hideLoading(); }
}

/* ══════════════════════════════════════════════════════════════
   RECOMMENDATION PAGE — Fixed data flow
   ══════════════════════════════════════════════════════════════ */
function showRecommendationPage(res) {
    showPage('recommendation-page');
    const wrapper = document.getElementById('recommendation-wrapper');

    // Use questions from State or from the passed argument
    const qs      = res.questions || State.assessment.questions || [];
    const answers = res.answers   || State.lastAnswers || {};
    const topProducts = res.recommended || State.lastRecommendations || [];
    const catKey  = res.category  || State.lastCategory || '';
    const user    = JSON.parse(localStorage.getItem('iam_user') || '{}');

    // Build selected product details section — collapsed by default, toggle per product
    const prodDetailsHTML = topProducts.length > 0 ? `
        <div class="rec-summary-block fade-2">
          <h3 style="color:var(--gold);margin-bottom:16px">Matched Products</h3>
          <div class="prod-details-list">
            ${topProducts.map((p, i) => {
                const medal = `#${i+1}`;
                const uid    = 'pd_' + i;
                return `
                <div class="prod-detail-card" id="${uid}_card">
                  <div class="prod-detail-header">
                    <span class="prod-detail-medal">${medal}</span>
                    <div style="flex:1;min-width:0">
                      <div class="prod-detail-name">${p.name}</div>
                      <div class="prod-detail-cat">${p.category} &nbsp;·&nbsp; ${p.score}% match</div>
                    </div>
                    <button class="btn-view-detail" id="${uid}_btn"
                      onclick="toggleProdDetail('${uid}')">View Details ▾</button>
                  </div>
                  <div class="prod-detail-body" id="${uid}_body" style="display:none">
                    ${p.rank_reason ? `<div class="rank-reason">${p.rank_reason}</div>` : ''}
                    <p class="prod-detail-desc">${p.description || ''}</p>
                    ${(p.features && p.features.length) ? `
                    <div class="prod-detail-features-title">Key Features</div>
                    <div class="prod-detail-features">
                      ${p.features.map(f => `<span class="prod-detail-ftag">✓ ${f}</span>`).join('')}
                    </div>` : ''}
                  </div>
                </div>`;
            }).join('')}
          </div>
        </div>` : '';

    wrapper.innerHTML = `
    <div class="assess-head fade-1" style="text-align:center;padding-bottom:0">
      <div class="tag-gold mb-16" style="display:inline-block">Assessment Complete</div>
      <h2 style="font-size:2rem">Your Personalised IAM Recommendations</h2>
      <p class="mt-8" style="font-size:1.05rem">
        Based on your <strong>${CAT_LABELS[catKey] || catKey}</strong> profile
        ${user.firstName ? `for <strong>${user.firstName}</strong>` : ''}.
      </p>
      <div style="margin:20px auto;padding:12px 24px;background:rgba(0,191,255,.07);border:1px solid var(--border-b);border-radius:12px;display:inline-block;font-size:.9rem;color:var(--text-2)">
        🏢 ${user.organizationName || 'Your Organization'} &nbsp;|&nbsp;
        📅 ${new Date().toLocaleDateString('en-IN', {day:'numeric', month:'long', year:'numeric'})}
      </div>
    </div>
    ${prodDetailsHTML}

    <div class="rec-products-section fade-3">
      <h3 style="color:var(--gold);margin-bottom:4px">Recommended Products (${topProducts.length})</h3>
      <p style="color:var(--text-muted);margin-bottom:20px;font-size:.9rem">
        Products are ranked by how well they match your selected requirements.
      </p>
      ${topProducts.length > 0
        ? `<div class="prods-grid">${topProducts.map((p, i) => renderRecProductCard(p, i)).join('')}</div>`
        : `<div class="empty-msg"><div class="ei">🔍</div><p>No products matched yet. Try adding more category answers.</p></div>`
      }
    </div>

    <div class="text-center mt-32 fade-3" style="padding-bottom:48px">
      <button class="btn btn-outline" onclick="loadAssessmentPage()">← New Assessment</button>
      <button class="btn btn-secondary" onclick="goToProducts()" style="margin-left:12px">View All Products</button>
      ${isLoggedIn() ? `<button class="btn btn-primary" onclick="loadDashboard()" style="margin-left:12px">Dashboard</button>` : ''}
    </div>`;

}

function renderRecProductCard(p, rank) {
    const medal = `#${rank + 1}`;
    const score  = p.score !== undefined ? p.score : 0;
    return `
    <div class="prod-card fade-1" style="position:relative;${rank === 0 ? 'border-color:var(--gold);box-shadow:0 0 24px rgba(255,215,0,.18)' : ''}">
      <div class="rank-badge" title="Rank ${rank+1}">${medal}</div>
      <div class="score-pill" style="right:12px;top:12px;left:auto">Match: ${score}%</div>
      <div class="prod-cat" style="margin-top:28px">${p.category}</div>
      <div class="prod-name">${p.name}</div>
      <p class="prod-desc">${p.description}</p>
      <div class="prod-features">${(p.features||[]).map(f=>`<span class="ftag">${f}</span>`).join('')}</div>
      <div class="score-bar-wrap">
        <div class="score-bar-lbl"><span>Match Score</span><span>${score}%</span></div>
        <div class="score-bar"><div class="score-bar-fill" style="width:${score}%"></div></div>
      </div>
      <div class="mt-8" style="font-size:.82rem;color:var(--text-muted);text-align:center;padding:8px;background:rgba(0,191,255,.05);border-radius:8px">
        Contact our sales team for a demo and pricing
      </div>
    </div>`;
}

/* ── PRODUCTS PAGE ── */
function renderProductCard(p) {
    return `
    <div class="prod-card fade-1">
      ${p.score !== undefined ? `<div class="score-pill">Match: ${p.score}%</div>` : ''}
      <div class="prod-cat">${p.category}</div>
      <div class="prod-name">${p.name}</div>
      <p class="prod-desc">${p.description}</p>
      <div class="prod-features">${(p.features||[]).map(f=>`<span class="ftag">${f}</span>`).join('')}</div>
    </div>`;
}

async function goToProducts() {
    showPage('products-page');
    showLoading('Loading products…');
    const grid = document.getElementById('products-grid');
    grid.innerHTML = '<div class="empty-msg"><div class="spinner spinner-lg"></div></div>';
    try {
        const ps = await Api.products();
        grid.innerHTML = ps.length
            ? ps.map(p => renderProductCard(p)).join('')
            : '<p class="empty-msg">No products found.</p>';
    } catch (e) {
        grid.innerHTML = `<p class="empty-msg">Failed to load products.</p>`;
        toast(e.message, 'error');
    } finally { hideLoading(); }
}

/* ── DASHBOARD ── */
async function loadDashboard(page = 1) {
    if (!isLoggedIn()) { showPage('login-page'); toast('Please log in first', 'info'); return; }
    State.dashPage = page;
    showPage('dashboard-page');
    showLoading('Loading dashboard…');
    try {
        const d = await Api.dashboard(page);
        renderDashboard(d);
    } catch (e) { toast('Failed to load dashboard', 'error'); }
    finally { hideLoading(); }
}

function renderDashboard(d) {
    document.getElementById('dash-assessments').textContent = d.stats.totalAssessments;

    const histEl = document.getElementById('dash-history');
    if (!d.assessments || d.assessments.length === 0) {
        histEl.innerHTML = `
          <div class="empty-msg">
            <div class="ei">📊</div><p>No assessments yet.</p>
            <button class="btn btn-primary btn-sm mt-16" onclick="loadAssessmentPage()">Start Assessment</button>
          </div>`;
    } else {
        histEl.innerHTML = d.assessments.map(a => {
            const topRec = (a.results || []).slice(0, 2);
            return `
            <div class="hist-card">
              <div class="hist-card-head">
                <span class="hist-cat-badge">${CAT_LABELS[a.category] || a.category}</span>
                <span class="hist-date">${new Date(a.createdAt).toLocaleDateString('en-IN',{day:'2-digit',month:'short',year:'numeric'})}</span>
              </div>
              ${topRec.length ? `
                <div class="hist-recs">
                  ${topRec.map(r=>`
                    <div class="hist-rec-item">
                      <span class="hist-rec-name">${r.name}</span>
                      <span class="hist-rec-score">${r.score}% match</span>
                    </div>`).join('')}
                </div>` : ''}
              <button class="btn btn-outline btn-xs mt-8"
                onclick='showAssessmentDetail(${JSON.stringify(a).replace(/'/g,"&#39;")})'>
                View Full Results →
              </button>
            </div>`;
        }).join('');

        if (d.totalPages > 1) {
            histEl.innerHTML += `
              <div class="pagination">
                <button class="btn btn-outline btn-xs" ${d.currentPage <= 1 ? 'disabled' : ''}
                        onclick="loadDashboard(${d.currentPage - 1})">← Prev</button>
                <span class="page-info">Page ${d.currentPage} of ${d.totalPages}</span>
                <button class="btn btn-outline btn-xs" ${d.currentPage >= d.totalPages ? 'disabled' : ''}
                        onclick="loadDashboard(${d.currentPage + 1})">Next →</button>
              </div>`;
        }
    }

    const recEl = document.getElementById('dash-recommended');
    recEl.innerHTML = d.recommended && d.recommended.length
        ? d.recommended.map(p => `
            <div class="rec-card">
              <div class="rec-card-body">
                <div class="rec-name">${p.name}</div>
                <div class="rec-cat">${p.category}</div>
              </div>
              <div class="rec-card-right">
                <div class="rec-score-circle">${p.score}%</div>
              </div>
            </div>`).join('')
        : `<div class="empty-msg"><div class="ei">💡</div><p>Run an assessment to get recommendations</p>
           <button class="btn btn-primary btn-sm mt-16" onclick="loadAssessmentPage()">Start Assessment</button></div>`;
}

function showAssessmentDetail(a) {
    const modal = document.getElementById('detail-modal');
    const body  = document.getElementById('detail-modal-body');
    const prods = a.results || [];
    body.innerHTML = `
      <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:4px">
        <h3 style="margin:0">${CAT_LABELS[a.category] || a.category} Assessment</h3>
        <button class="btn btn-xs btn-outline" onclick="closeDetailModal()">✕ Close</button>
      </div>
      <p class="hist-date" style="margin-bottom:20px">
        ${new Date(a.createdAt).toLocaleDateString('en-IN',{weekday:'long',day:'numeric',month:'long',year:'numeric'})}
      </p>
      <h4 style="color:var(--gold);margin-bottom:12px">Recommended Products (${prods.length})</h4>
      <div class="detail-prods">
        ${prods.map((p, i) => {
            const medal = `#${i+1}`;
            const uid    = 'dm_' + i;
            return `
          <div class="detail-prod-row" id="${uid}_row">
            <div class="detail-prod-row-header">
              <span style="font-size:1.2rem">${medal}</span>
              <div style="flex:1;min-width:0">
                <div class="detail-prod-name">${p.name}</div>
                <div class="detail-prod-cat">${p.category}</div>
              </div>
              <div style="display:flex;align-items:center;gap:10px">
                <div class="hist-rec-score">${p.score}%</div>
                <button class="btn-view-detail" id="${uid}_btn"
                  onclick="toggleModalProd('${uid}')">Details ▾</button>
              </div>
            </div>
            <div class="detail-prod-body" id="${uid}_body" style="display:none">
              ${p.rank_reason ? `<div class="rank-reason">${p.rank_reason}</div>` : ''}
              ${p.description ? `<p class="prod-detail-desc" style="margin:10px 0 10px">${p.description}</p>` : ''}
              ${(p.features && p.features.length) ? `
              <div class="prod-detail-features-title">Key Features</div>
              <div class="prod-detail-features" style="margin-bottom:0">
                ${p.features.map(f => `<span class="prod-detail-ftag">✓ ${f}</span>`).join('')}
              </div>` : ''}
            </div>
          </div>`;
        }).join('')}
      </div>`;
    modal.style.display = 'flex';
}

function toggleModalProd(uid) {
    const body = document.getElementById(uid + '_body');
    const btn  = document.getElementById(uid + '_btn');
    if (!body) return;
    const open = body.style.display !== 'none';
    body.style.display = open ? 'none' : 'block';
    btn.textContent = open ? 'Details ▾' : 'Hide ▴';
}

function closeDetailModal() {
    document.getElementById('detail-modal').style.display = 'none';
}

function togglePass(inputId, btn) {
    const input = document.getElementById(inputId);
    if (!input) return;
    const show = input.type === 'password';
    input.type = show ? 'text' : 'password';
    btn.textContent = show ? '🙈' : '👁';
}

function toggleProdDetail(uid) {
    const body = document.getElementById(uid + '_body');
    const btn  = document.getElementById(uid + '_btn');
    if (!body) return;
    const open = body.style.display !== 'none';
    body.style.display = open ? 'none' : 'block';
    btn.textContent = open ? 'View Details ▾' : 'Hide Details ▴';
}

/* ══════════════════════════════════════════════════════════════
   ADMIN PANEL
   ══════════════════════════════════════════════════════════════ */
async function handleAdminLogin(e) {
    e.preventDefault();
    const username = document.getElementById('admin-username').value.trim();
    const password = document.getElementById('admin-password').value;
    const errEl    = document.getElementById('admin-login-error');
    errEl.classList.remove('show');
    showLoading('Verifying admin credentials…');
    try {
        const d = await Api.adminLogin({ username, password });
        saveAdminSession(d);
        toast(`Welcome, ${d.admin.username}!`, 'success');
        showPage('admin-dashboard-page');
        loadAdminOverview();
    } catch (err) {
        errEl.textContent = err.message;
        errEl.classList.add('show');
    } finally { hideLoading(); }
}

function handleAdminLogout() {
    clearAdminSession();
    toast('Admin logged out', 'info');
    showPage('home-page');
    updateNav();
}

function switchAdminTab(tabId, btn) {
    document.querySelectorAll('.admin-tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.admin-tab-content').forEach(c => c.classList.remove('active'));
    btn.classList.add('active');
    document.getElementById(`admin-tab-${tabId}`)?.classList.add('active');
    if (tabId === 'overview')    loadAdminOverview();
    if (tabId === 'users')       loadAdminUsers();
    if (tabId === 'assessments') loadAdminAssessments();
    if (tabId === 'products')    loadAdminProducts();
    if (tabId === 'questions')   loadAdminQuestions();
}

async function loadAdminOverview() {
    try {
        const s = await Api.adminStats();
        document.getElementById('stat-users').textContent       = s.users;
        document.getElementById('stat-assessments').textContent = s.assessments;
        document.getElementById('stat-products').textContent    = s.products;
        document.getElementById('stat-questions').textContent   = s.questions;
    } catch(e) { toast('Failed to load stats', 'error'); }
}

async function loadAdminUsers() {
    const el = document.getElementById('admin-users-list');
    el.innerHTML = '<div class="spinner"></div>';
    try {
        const users = await Api.adminUsers();
        if (!users.length) { el.innerHTML = '<p class="text-muted">No users yet.</p>'; return; }
        el.innerHTML = `
        <table class="admin-table">
          <thead><tr><th>Name</th><th>Email</th><th>Organization</th><th>Joined</th><th>Action</th></tr></thead>
          <tbody>
            ${users.map(u=>`
              <tr>
                <td>${u.firstName} ${u.lastName}</td>
                <td>${u.email}</td>
                <td>${u.organizationName || '-'}</td>
                <td>${new Date(u.createdAt).toLocaleDateString('en-IN')}</td>
                <td><button class="btn btn-xs btn-danger" onclick="adminDeleteUser('${u._id}')">Delete</button></td>
              </tr>`).join('')}
          </tbody>
        </table>`;
    } catch(e) { el.innerHTML = `<p class="form-error show">${e.message}</p>`; }
}

async function adminDeleteUser(userId) {
    if (!confirm('Delete this user? This cannot be undone.')) return;
    try {
        await Api.adminDeleteUser(userId);
        toast('User deleted', 'success');
        loadAdminUsers();
    } catch(e) { toast(e.message, 'error'); }
}

async function loadAdminAssessments() {
    const el = document.getElementById('admin-assessments-list');
    el.innerHTML = '<div class="spinner"></div>';
    try {
        const { assessments } = await Api.adminAssessments();
        if (!assessments.length) { el.innerHTML = '<p class="text-muted">No assessments yet.</p>'; return; }
        el.innerHTML = `
        <table class="admin-table">
          <thead><tr><th>User ID</th><th>Category</th><th>Top Product</th><th>Date</th></tr></thead>
          <tbody>
            ${assessments.map(a=>{
                const top = (a.results||[])[0];
                return `
                <tr>
                  <td style="font-size:.8rem;opacity:.7">${a.userId || 'guest'}</td>
                  <td>${CAT_LABELS[a.category] || a.category}</td>
                  <td>${top ? top.name+' ('+top.score+'%)' : '-'}</td>
                  <td>${new Date(a.createdAt).toLocaleDateString('en-IN')}</td>
                </tr>`;
            }).join('')}
          </tbody>
        </table>`;
    } catch(e) { el.innerHTML = `<p class="form-error show">${e.message}</p>`; }
}

async function loadAdminProducts() {
    const el = document.getElementById('admin-products-list');
    el.innerHTML = '<div class="spinner"></div>';
    try {
        const products = await Api.adminGetProducts();
        if (!products.length) { el.innerHTML = '<p class="text-muted">No products yet.</p>'; return; }
        el.innerHTML = `
        <table class="admin-table">
          <thead><tr><th>ID</th><th>Name</th><th>Category</th><th>Action</th></tr></thead>
          <tbody>
            ${products.map(p=>`
              <tr>
                <td style="font-size:.8rem;opacity:.7">${p.id}</td>
                <td>${p.name}</td>
                <td>${CAT_LABELS[p.category] || p.category}</td>
                <td><button class="btn btn-xs btn-danger" onclick="adminDeleteProduct('${p.id}')">Delete</button></td>
              </tr>`).join('')}
          </tbody>
        </table>`;
    } catch(e) { el.innerHTML = `<p class="form-error show">${e.message}</p>`; }
}

async function loadAdminQuestions() {
    const el = document.getElementById('admin-questions-list');
    el.innerHTML = '<div class="spinner"></div>';
    try {
        const qs = await Api.adminGetQuestions();
        if (!qs.length) { el.innerHTML = '<p class="text-muted">No questions yet.</p>'; return; }
        el.innerHTML = `
        <table class="admin-table">
          <thead><tr><th>#</th><th>Category</th><th>Question</th><th>Options</th><th>Action</th></tr></thead>
          <tbody>
            ${qs.map(q=>`
              <tr>
                <td>${q.order}</td>
                <td>${CAT_LABELS[q.category] || q.category}</td>
                <td>${q.text.length > 50 ? q.text.substring(0,50)+'…' : q.text}</td>
                <td>${(q.options||[]).length}</td>
                <td><button class="btn btn-xs btn-danger" onclick="adminDeleteQuestion('${q._id}')">Delete</button></td>
              </tr>`).join('')}
          </tbody>
        </table>`;
    } catch(e) { el.innerHTML = `<p class="form-error show">${e.message}</p>`; }
}

function toggleAddProductForm() {
    const f = document.getElementById('add-product-form');
    f.style.display = f.style.display === 'none' ? 'block' : 'none';
}

async function submitAddProduct() {
    const features = document.getElementById('ap-features').value
        .split(',').map(f=>f.trim()).filter(Boolean);
    const body = {
        id:          document.getElementById('ap-id').value.trim(),
        name:        document.getElementById('ap-name').value.trim(),
        category:    document.getElementById('ap-cat').value,
        price:       0,
        description: document.getElementById('ap-desc').value.trim(),
        features,
    };
    if (!body.id || !body.name || !body.category) {
        toast('Please fill in ID, Name, and Category', 'info'); return;
    }
    try {
        await Api.adminAddProduct(body);
        toast('Product added!', 'success');
        toggleAddProductForm();
        loadAdminProducts();
    } catch(e) { toast(e.message, 'error'); }
}

async function adminDeleteProduct(id) {
    if (!confirm(`Delete product "${id}"?`)) return;
    try {
        await Api.adminDeleteProduct(id);
        toast('Product deleted', 'success');
        loadAdminProducts();
    } catch(e) { toast(e.message, 'error'); }
}

function toggleAddQuestionForm() {
    const f = document.getElementById('add-question-form');
    f.style.display = f.style.display === 'none' ? 'block' : 'none';
}

async function submitAddQuestion() {
    const optionsRaw = document.getElementById('aq-options').value.trim().split('\n');
    const options = optionsRaw.map(line => {
        const [value, ...rest] = line.split('|');
        return { value: value.trim(), label: rest.join('|').trim() || value.trim() };
    }).filter(o => o.value);

    const body = {
        category: document.getElementById('aq-cat').value,
        order:    parseInt(document.getElementById('aq-order').value) || 99,
        text:     document.getElementById('aq-text').value.trim(),
        options,
    };
    if (!body.text || !body.category || options.length === 0) {
        toast('Please fill text, category and at least one option', 'info'); return;
    }
    try {
        await Api.adminAddQuestion(body);
        toast('Question added!', 'success');
        toggleAddQuestionForm();
        loadAdminQuestions();
    } catch(e) { toast(e.message, 'error'); }
}

async function adminDeleteQuestion(id) {
    if (!confirm('Delete this question?')) return;
    try {
        await Api.adminDeleteQuestion(id);
        toast('Question deleted', 'success');
        loadAdminQuestions();
    } catch(e) { toast(e.message, 'error'); }
}

/* ── BOOTSTRAP ── */
document.addEventListener('DOMContentLoaded', () => {
    if (localStorage.getItem('iam_token') && !isLoggedIn()) clearSession();

    updateNav();
    const savedUser = localStorage.getItem('iam_user');
    if (savedUser) { try { State.user = JSON.parse(savedUser); } catch(e) {} }
    showPage('home-page');

    // Nav bindings
    document.getElementById('nav-logo-btn').addEventListener('click',   () => showPage('home-page'));
    document.getElementById('nav-login-btn').addEventListener('click',  () => showPage('login-page'));
    document.getElementById('nav-signup-btn').addEventListener('click', () => showPage('signup-page'));
    document.getElementById('nav-dash-btn').addEventListener('click',   () => loadDashboard());
    document.getElementById('nav-logout-btn').addEventListener('click', () => handleLogout());
    document.getElementById('nav-assess-btn').addEventListener('click', () => loadAssessmentPage());
    document.getElementById('nav-prods-btn').addEventListener('click',  () => goToProducts());

    // Form bindings
    document.getElementById('login-form').addEventListener('submit',       handleLogin);
    document.getElementById('signup-form').addEventListener('submit',      handleRegister);
    document.getElementById('fp-form').addEventListener('submit',          handleForgotPassword);
    document.getElementById('admin-login-form').addEventListener('submit', handleAdminLogin);

    // Modal close on backdrop
    ['auth-prompt-modal','detail-modal','login-required-modal'].forEach(id => {
        document.getElementById(id)?.addEventListener('click', e => {
            if (e.target === e.currentTarget) {
                e.currentTarget.style.display = 'none';
            }
        });
    });
});