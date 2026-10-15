const $ = (id) => document.getElementById(id);
const sampleSelect = $('sampleSelect');
const datasetName = $('datasetName');
const datasetInput = $('datasetInput');
const analyzeButton = $('analyzeButton');
const errorMessage = $('errorMessage');
let samples = {};
let currentUnit = 'marks';
let lastResults = null;

function numberText(value) {
  const n = Number(value);
  if (!Number.isFinite(n)) return '—';
  return n.toLocaleString(undefined, { maximumFractionDigits: 4 });
}

function parseInput() {
  const raw = datasetInput.value.trim();
  if (!raw) throw new Error('Enter some numerical observations first.');
  const tokens = raw.split(/[\s,;]+/).filter(Boolean);
  if (tokens.length < 3) throw new Error('Please enter at least 3 numbers.');
  if (tokens.length > 500) throw new Error('Please enter no more than 500 observations.');
  const values = tokens.map((token, index) => {
    const value = Number(token);
    if (token === '' || !Number.isFinite(value)) throw new Error(`“${token}” (observation ${index + 1}) is not a valid number.`);
    return value;
  });
  return values;
}

function setSample(key) {
  if (key === 'custom') {
    $('sampleDescription').textContent = 'Paste your own numbers to explore a different dataset.';
    datasetName.value = 'My custom dataset';
    currentUnit = 'observations';
    datasetInput.focus();
    updatePointCount();
    return;
  }
  const sample = samples[key];
  if (!sample) return;
  datasetName.value = sample.name;
  datasetInput.value = sample.values.join(', ');
  $('sampleDescription').textContent = sample.description;
  currentUnit = sample.unit;
  updatePointCount();
  runAnalysis();
}

function updatePointCount() {
  const count = datasetInput.value.trim() ? datasetInput.value.trim().split(/[\s,;]+/).filter(Boolean).length : 0;
  $('pointCount').textContent = `${count} VALUE${count === 1 ? '' : 'S'}`;
}

function putText(id, value) { $(id).textContent = value; }

function renderCenter(results) {
  const mean = Number(results.mean);
  const median = Number(results.median);
  const min = Number(results.min);
  const max = Number(results.max);
  const spread = max - min;
  const position = (value) => spread === 0 ? 50 : Math.min(98, Math.max(2, ((value - min) / spread) * 100));
  $('meanMarker').style.left = `${position(mean)}%`;
  $('medianMarker').style.left = `${position(median)}%`;
  putText('legendMean', numberText(mean));
  putText('legendMedian', numberText(median));
  putText('trackMin', `MIN ${numberText(min)}`);
  putText('trackMax', `MAX ${numberText(max)}`);
  putText('rangeChip', `RANGE ${numberText(results.range)}`);

  let message;
  const gap = Math.abs(mean - median);
  if (gap < 0.00005) {
    message = `Mean and median are nearly identical (${numberText(mean)}). The dataset is reasonably balanced around its centre.`;
  } else if (mean > median) {
    message = `The mean is ${numberText(gap)} above the median. Higher observations may be pulling the average upward.`;
  } else {
    message = `The mean is ${numberText(gap)} below the median. Lower observations may be pulling the average downward.`;
  }
  $('centerInsight').textContent = message;
}

function renderDistribution(results) {
  const container = $('distributionRows');
  container.replaceChildren();
  const observations = results.observations;
  const shown = observations.slice(0, 40);
  const min = Number(results.min);
  const max = Number(results.max);
  const spread = max - min;
  shown.forEach((observation) => {
    const row = document.createElement('div');
    row.className = `distribution-row${observation.is_outlier ? ' is-outlier' : ''}`;
    const label = document.createElement('span');
    label.className = 'observation-label';
    label.textContent = `OBS. ${String(observation.index).padStart(2, '0')}`;
    const track = document.createElement('div');
    track.className = 'bar-track';
    track.setAttribute('aria-label', `Observation ${observation.index}: ${numberText(observation.value)}`);
    const fill = document.createElement('div');
    fill.className = 'bar-fill';
    const width = spread === 0 ? 100 : 8 + ((Number(observation.value) - min) / spread) * 92;
    fill.style.width = `${Math.max(0, Math.min(100, width))}%`;
    track.append(fill);
    const value = document.createElement('span');
    value.className = 'observation-value';
    value.append(document.createTextNode(numberText(observation.value)));
    if (observation.is_outlier) {
      const flag = document.createElement('span');
      flag.className = 'flag';
      flag.textContent = ' !';
      flag.title = `${observation.outlier_kind} outlier`;
      value.append(flag);
    }
    row.append(label, track, value);
    container.append(row);
  });
  putText('observationChip', `${results.count} OBSERVATIONS`);
  putText('chartFootnote', results.count > shown.length
    ? `Showing the first ${shown.length} of ${results.count} observations. All values are included in the statistical calculations.`
    : 'Bars are scaled relative to the selected dataset; flagged values are shown in coral.');
}

function renderOutliers(results) {
  const container = $('outlierResults');
  container.replaceChildren();
  putText('outlierCount', `${results.outliers.length} FLAGGED`);
  putText('lowFence', numberText(results.low_fence));
  putText('highFence', numberText(results.high_fence));
  putText('iqrValue', numberText(results.iqr));
  if (!results.outliers.length) {
    const empty = document.createElement('div');
    empty.className = 'empty-state good';
    empty.textContent = 'No IQR outliers found. Every observation falls within the calculated fences.';
    container.append(empty);
    return;
  }
  results.outliers.forEach((item) => {
    const row = document.createElement('div');
    row.className = 'outlier-item';
    const label = document.createElement('span');
    label.textContent = `Observation ${item.index} · ${item.outlier_kind} outlier`;
    const value = document.createElement('b');
    value.textContent = numberText(item.value);
    row.append(label, value);
    container.append(row);
  });
}

function renderResults(results) {
  lastResults = results;
  putText('meanValue', numberText(results.mean));
  putText('medianValue', numberText(results.median));
  putText('stdValue', numberText(results.std_dev));
  putText('minValue', numberText(results.min));
  putText('maxValue', numberText(results.max));
  putText('activeDataset', results.dataset_name || datasetName.value || 'Custom dataset');
  renderCenter(results);
  renderDistribution(results);
  renderOutliers(results);
}

async function runAnalysis() {
  errorMessage.hidden = true;
  analyzeButton.disabled = true;
  analyzeButton.querySelector('span:first-child').textContent = 'Calculating…';
  try {
    const values = parseInput();
    const name = datasetName.value.trim() || 'Custom dataset';
    const response = await fetch('/api/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ dataset_name: name, values, unit: currentUnit }),
    });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || 'The analysis could not be completed.');
    renderResults(result);
  } catch (error) {
    errorMessage.textContent = error.message || 'Something went wrong. Check the values and try again.';
    errorMessage.hidden = false;
  } finally {
    analyzeButton.disabled = false;
    analyzeButton.querySelector('span:first-child').textContent = 'Run statistical analysis';
  }
}

sampleSelect.addEventListener('change', () => setSample(sampleSelect.value));
datasetInput.addEventListener('input', updatePointCount);
$('analyzeButton').addEventListener('click', runAnalysis);

async function initialise() {
  try {
    const [healthResponse, samplesResponse] = await Promise.all([fetch('/api/health'), fetch('/api/samples')]);
    if (!healthResponse.ok || !samplesResponse.ok) throw new Error('The Python server did not respond.');
    samples = (await samplesResponse.json()).samples;
    const health = await healthResponse.json();
    putText('engineStatus', `ENGINE READY · NUMPY ${health.numpy_version}`);
    setSample(sampleSelect.value || 'student');
  } catch (error) {
    putText('engineStatus', 'ENGINE OFFLINE');
    errorMessage.textContent = 'Could not connect to the Python engine. Start the app with “python app.py” and refresh this page.';
    errorMessage.hidden = false;
  }
}

updatePointCount();
initialise();
