import { $, activateView, setMessage } from './dom.js';
import { login, loadScopes, getToken, clearAuth, isAuthenticated } from './api.js';

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
  updateNav();
}

window.addEventListener('DOMContentLoaded', () => {
  initAuth();
});
