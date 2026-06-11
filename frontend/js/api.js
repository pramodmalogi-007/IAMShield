/**
 * IAMShield - API Client
 * Centralised fetch wrapper with JWT auth headers.
 */

const API_BASE = window.location.origin + '/api';
const Api = {
  _token: () => localStorage.getItem('iam_token'),

  _headers() {
    const h = { 'Content-Type': 'application/json' };
    const t = this._token();
    if (t) h['Authorization'] = `Bearer ${t}`;
    return h;
  },

  async _req(method, path, body = null) {
    const opts = { method, headers: this._headers() };
    if (body) opts.body = JSON.stringify(body);
    const r = await fetch(API_BASE + path, opts);
    const d = await r.json().catch(() => ({}));
    if (!r.ok) throw new Error(d.error || `HTTP ${r.status}`);
    return d;
  },

  get:  (p)    => Api._req('GET',    p),
  post: (p, b) => Api._req('POST',   p, b),
  del:  (p)    => Api._req('DELETE', p),

  // ── Auth ──────────────────────────────────────────────────────────────────
  register:             b     => Api.post('/register', b),
  login:                b     => Api.post('/login', b),
  forgotPassword:       b     => Api.post('/forgot-password', b),
  me:                   ()    => Api.get('/me'),

  // ── Assessment ────────────────────────────────────────────────────────────
  categories:            ()   => Api.get('/categories'),
  questions:             cat  => Api.get(`/questions?category=${cat}`),
  products:              cat  => Api.get(`/products${cat ? '?category='+cat : ''}`),
  submitGuestAssessment: b    => Api.post('/assessment/submit-guest', b),
  claimAssessment:       b    => Api.post('/assessment/claim', b),
  submitAssessment:      b    => Api.post('/assessment/submit', b),
  assessmentHistory:    (p=1) => Api.get(`/assessment/history?page=${p}&limit=20`),

  // ── Dashboard ─────────────────────────────────────────────────────────────
  dashboard: (p=1) => Api.get(`/dashboard?page=${p}&limit=10`),

  // ── Admin ─────────────────────────────────────────────────────────────────
  adminLogin:          b  => Api.post('/admin/login', b),
  adminStats:          () => Api.get('/admin/stats'),
  adminUsers:          () => Api.get('/admin/users'),
  adminDeleteUser:     id => Api.del(`/admin/users/${id}`),
  adminAssessments:    (p=1) => Api.get(`/admin/assessments?page=${p}&limit=20`),
  adminGetProducts:    () => Api.get('/admin/products'),
  adminAddProduct:     b  => Api.post('/admin/products', b),
  adminDeleteProduct:  id => Api.del(`/admin/products/${id}`),
  adminGetQuestions:   () => Api.get('/admin/questions'),
  adminAddQuestion:    b  => Api.post('/admin/questions', b),
  adminDeleteQuestion: id => Api.del(`/admin/questions/${id}`),
};