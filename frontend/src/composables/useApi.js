export async function getSearch(query) {
  return fetch(`/api/search?q=${encodeURIComponent(query)}`)
    .then(r => r.json())
}

export async function getRelated(id) {
  return fetch(`/api/related?paper_id=${id}`)
    .then(r => r.json())
}

export async function getCitations(id) {
  return fetch(`/api/citations?paper_id=${id}&depth=1`)
    .then(r => r.json())
}

export async function explainInsight(id) {
  return fetch(`/api/explain-insight?id=${encodeURIComponent(id)}`)
    .then(r => r.json())
}

export async function getOverview() {
  return fetch('/api/overview').then(r => r.json())
}

// Catalog of already-digested papers / methods / datasets. Cached after the
// first call so switching between query views doesn't refetch each time.
let _corpusPromise = null
export function getCorpus() {
  if (!_corpusPromise) {
    _corpusPromise = fetch('/api/corpus').then(r => r.json())
  }
  return _corpusPromise
}

// --- autonomous analyst control -------------------------------------------

export async function getAnalystStatus() {
  return fetch('/api/analyst/status').then(r => r.json())
}

export async function getAnalystConfig() {
  return fetch('/api/analyst/config').then(r => r.json())
}

// POST a control action (start/pause/resume/stop/run-now/reset) or config update.
export async function analystAction(action, body) {
  return fetch(`/api/analyst/${action}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: body ? JSON.stringify(body) : undefined
  }).then(r => r.json())
}