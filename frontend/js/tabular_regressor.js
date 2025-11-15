import { $, setMessage, renderTable } from './dom.js';
import { loadAvailableModels, trainPredict, isAuthenticated } from './api.js';

function parseCSV(text) {
  const lines = text.trim().split(/\r?\n/).filter(l => l.trim());
  if (lines.length === 0) return { header: [], rows: [] };
  const header = lines[0].split(',').map(h => h.trim());
  const rows = lines.slice(1).map(line => {
    const cells = line.split(',').map(c => c.trim());
    const obj = {};
    header.forEach((h, i) => { obj[h] = isNaN(Number(cells[i])) ? cells[i] : Number(cells[i]); });
    return obj;
  });
  return { header, rows };
}

function toSchemaRows(rows) {
  return rows.map((r, idx) => ({ index: r.index ?? idx, ...r }));
}

function buildDataSection(rows, header) {
  // Remove index from each row for schema conversion except keep at root
  return { rows: rows.map((r, i) => ({ index: r.index ?? i, ...Object.fromEntries(Object.entries(r).filter(([k]) => k !== 'index')) })) };
}

async function initModelSelect() {
  try {
    const data = await loadAvailableModels();
    const select = $('#model-type');
    select.innerHTML = '';
    (data.available_models || []).forEach(m => {
      const opt = document.createElement('option');
      opt.value = m; opt.textContent = m; select.appendChild(opt);
    });
  } catch (e) { setMessage('Could not load models', 'error'); }
}

function initTabularForm() {
  const form = $('#tabular-form');
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    if (!isAuthenticated()) { setMessage('Please login first', 'error'); return; }
    const modelType = $('#model-type').value.trim();
    const targets = $('#target-columns').value.split(',').map(s => s.trim()).filter(Boolean);
    if (!modelType || targets.length === 0) { setMessage('Model and targets required', 'error'); return; }
    const featuresInput = $('#feature-columns').value.trim();
    const features = featuresInput ? featuresInput.split(',').map(s => s.trim()).filter(Boolean) : null;
    const trainCSV = $('#train-csv').value;
    const predictCSV = $('#predict-csv').value;
    if (!trainCSV || !predictCSV) { setMessage('Train and predict CSV required', 'error'); return; }

    const trainParsed = parseCSV(trainCSV);
    const predictParsed = parseCSV(predictCSV);

    // Expects 'index' column to align with backend; if not present, it is generated.
    const payload = {
      model_type: modelType,
      target_columns: targets,
      feature_columns: features,
      train_data: buildDataSection(trainParsed.rows, trainParsed.header),
      predict_data: buildDataSection(predictParsed.rows, predictParsed.header)
    };

    setMessage('Training and predicting...', 'info');
    try {
      const res = await trainPredict(payload);
      setMessage('Operation completed', 'success');
      renderMetrics(res.metrics, targets);
      renderPredictions(res.predictions);
      $('#results').hidden = false;
      $('#api-version').textContent = res.api_version;
      $('#model-version').textContent = res.model_version;
    } catch (err) {
      // message already handled in apiFetch
    }
  });
}

function renderMetrics(metrics, targets) {
  if (!metrics) return;
  const rows = targets.map(t => ({ target: t, mse: metrics.mse?.[t], mae: metrics.mae?.[t], baseline_mse: metrics.baseline_mse?.[t] }));
  renderTable('#metrics', ['target','mse','mae','baseline_mse'], rows);
}

function renderPredictions(predictions) {
  if (!Array.isArray(predictions)) return;
  // Flatten predictions: index + each target prediction value
  const colsSet = new Set(['index']);
  predictions.forEach(p => { Object.keys(p.values || {}).forEach(k => colsSet.add(k)); });
  const columns = Array.from(colsSet);
  const rows = predictions.map(p => ({ index: p.index, ...p.values }));
  renderTable('#predictions', columns, rows);
}

export function initTabular() {
  initModelSelect();
  initTabularForm();
}

window.addEventListener('DOMContentLoaded', () => {
  initTabular();
});
