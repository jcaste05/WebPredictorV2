import { $, activateView, setMessage } from './dom.js';
import { login, loadScopes, getToken, clearAuth, isAuthenticated, getApiVersions } from './api.js';
import { WEB_VERSION } from './config.js';

async function renderVersions() {
  const webVersionEl = document.getElementById('web-version');
  if (webVersionEl) webVersionEl.textContent = WEB_VERSION;
  // Get API and model versions
  try {
    const v = await getApiVersions();
    const apiVersionEl = document.getElementById('api-version');
    const modelVersionEl = document.getElementById('model-version');
    if (apiVersionEl) apiVersionEl.textContent = v.api_version;
    if (modelVersionEl) modelVersionEl.textContent = v.model_version;
  } catch (_) { /* ignore */ }
}

function updateNav() {
  const authed = isAuthenticated();
  $('#nav-login').disabled = authed;
  $('#nav-tabular').disabled = !authed;
  $('#nav-logout').disabled = !authed;
  if (!authed) activateView('login-view');
}

async function initLoginForm() {
  const form = $('#login-form');
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = $('#login-username').value.trim();
    const password = $('#login-password').value.trim();
    const scopes = $('#login-scopes').value.trim();
    if (!username || !password) { setMessage('Username and password required', 'error'); return; }
    try {
      await login(username, password, scopes);
      updateNav();
      activateView('tabular-view');
    } catch (_) { /* message already handled */ }
  });
}

async function loadAndRenderScopes() {
  try {
    const data = await loadScopes();
    const ul = $('#scopes-list');
    ul.innerHTML = '';
    Object.entries(data.scopes || {}).forEach(([name, desc]) => {
      const li = document.createElement('li');
      const code = document.createElement('code');
      code.textContent = name;
      li.appendChild(code);
      const span = document.createElement('span');
      span.textContent = ' - ' + desc;
      li.appendChild(span);
      ul.appendChild(li);
    });
  } catch (_) { /* ignore */ }
}

function initNav() {
  document.addEventListener('click', (e) => {
    const target = e.target;
    if (!(target instanceof HTMLElement)) return;
    if (target.matches('[data-view]')) {
      const view = target.getAttribute('data-view');
      if (view) activateView(view);
    }
    if (target.matches('[data-action="logout"]')) {
      clearAuth();
      setMessage('Logged out', 'success');
      updateNav();
    }
  });
}


export function initAuth() {
  initLoginForm();
  initNav();
  loadAndRenderScopes();
  renderVersions();
  updateNav();
}

window.addEventListener('DOMContentLoaded', () => {
  initAuth();
});
