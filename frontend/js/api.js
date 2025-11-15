// API client with token and error handling
import { setMessage, sanitizeText } from './dom.js';

// Enable/disable debug traces
const DEBUG = true;

const API_BASE = '';
let accessToken = null;
let expiresMinutes = null;
let scopesGranted = [];

export function getToken() { return accessToken; }
export function isAuthenticated() { return !!accessToken; }
export function clearAuth() { accessToken = null; expiresMinutes = null; scopesGranted = []; }

export async function apiFetch(path, options = {}) {
  const headers = options.headers || {};
  headers['Accept'] = 'application/json';
  const isForm = options.body instanceof URLSearchParams;
  if (!(options.body instanceof FormData) && !isForm && !headers['Content-Type']) {
    headers['Content-Type'] = 'application/json';
  }
  if (isForm && !headers['Content-Type']) {
    headers['Content-Type'] = 'application/x-www-form-urlencoded';
  }
  if (accessToken) headers['Authorization'] = `Bearer ${accessToken}`;
  const final = { ...options, headers };
  if (DEBUG) console.debug('[apiFetch] request', API_BASE + path, final);
  try {
    const res = await fetch(API_BASE + path, final);
    const ct = res.headers.get('content-type') || '';
    const isJson = ct.includes('application/json');
    if (DEBUG) console.debug('[apiFetch] response', path, res.status, ct);
    if (!res.ok) {
      let errText = `Error ${res.status}`;
      if (isJson) {
        const data = await res.json().catch(() => ({}));
        errText = sanitizeText(data.detail || JSON.stringify(data) || errText);
      } else {
        errText = sanitizeText(await res.text());
      }
      if (DEBUG) console.error('[apiFetch] error', errText);
      throw new Error(errText);
    }
    const payload = isJson ? await res.json() : await res.text();
    if (DEBUG) console.debug('[apiFetch] payload', payload);
    return payload;
  } catch (e) {
    setMessage(e.message, 'error');
    if (DEBUG) console.error('[apiFetch] exception', e);
    throw e;
  }
}

export async function login(username, password, scopesInput) {
  const scopeList = scopesInput?.trim() ? scopesInput.trim().split(/\s+/) : [];
  const formData = new URLSearchParams();
  formData.set('username', username);
  formData.set('password', password);
  scopeList.forEach(s => formData.append('scopes', s));
  const data = await apiFetch('/auth/login', { method: 'POST', body: formData });
  accessToken = data.access_token;
  expiresMinutes = data.expires_minutes;
  scopesGranted = data.scopes || [];
  setMessage('Login successful', 'success');
  if (DEBUG) console.debug('[login] scopesGranted', scopesGranted);
  return data;
}

export async function loadScopes() {
  return apiFetch('/auth/scopes');
}

export async function loadAvailableModels() {
  return apiFetch('/tabular_regressor/available_models', { method: 'POST' });
}

export async function trainPredict(payload) {
  return apiFetch('/tabular_regressor/train_predict', { method: 'POST', body: JSON.stringify(payload) });
}

export async function getApiVersions() {
  return apiFetch('/health', { method: 'GET' });
}
