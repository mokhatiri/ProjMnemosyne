<template>
  <div>
    <!-- ===== live status ===== -->
    <div class="card">
      <h3>Autonomous analyst &middot; control</h3>

      <div
        v-if="error"
        class="muted"
        style="color: var(--red)"
      >
        {{ error }}
      </div>

      <div
        v-if="status"
        class="filterbar"
        style="gap: 14px; align-items: center"
      >
        <span
          class="tag"
          :class="phaseClass"
        >{{ status.phase }}</span>
        <span class="muted">generation <strong>{{ status.generation }}</strong></span>
        <span class="muted">
          tasks <strong>{{ status.tasks.done }}</strong> /
          {{ status.tasks.total }}
          <template v-if="status.tasks.pending">
            ({{ status.tasks.pending }} pending)
          </template>
        </span>
        <span class="muted">insights banked <strong>{{ status.insights_banked }}</strong></span>
      </div>

      <!-- the wait + fast-forward -->
      <div
        v-if="status && status.phase === 'sleeping' && countdown !== null"
        class="muted"
        style="margin-top: 10px"
      >
        next generation in <strong>{{ countdown }}s</strong>
        &middot; or
        <button
          class="llm-action"
          style="margin: 0 0 0 4px; padding: 4px 10px"
          @click="act('run-now')"
        >
          Run now
        </button>
      </div>
      <div
        v-else-if="status && status.phase === 'idle'"
        class="muted"
        style="margin-top: 10px"
      >
        all current tasks done &mdash; idle. Set <code>grow &gt; 0</code> below (then Save)
        to keep finding papers, or
        <button
          class="llm-action"
          style="margin: 0 0 0 4px; padding: 4px 10px"
          @click="act('run-now')"
        >
          Run a generation now
        </button>
      </div>

      <!-- what's coming up -->
      <div
        v-if="status && status.next_up?.length"
        class="muted"
        style="margin-top: 8px"
      >
        next up: {{ status.next_up.join(', ') }}
      </div>

      <!-- last generation summary -->
      <div
        v-if="status?.last_summary"
        class="muted"
        style="margin-top: 8px"
      >
        last generation: ran {{ status.last_summary.ran }} task(s),
        {{ status.last_summary.new_insights }} new insight(s),
        {{ status.last_summary.pending_after }} still pending.
      </div>

      <div
        v-if="status?.last_error"
        class="muted"
        style="margin-top: 8px; color: var(--red)"
      >
        last error: {{ status.last_error }}
      </div>

      <!-- lifecycle buttons -->
      <div
        class="filterbar"
        style="margin-top: 14px"
      >
        <button
          v-if="!status?.running"
          :disabled="busy"
          @click="act('start')"
        >
          Start
        </button>
        <button
          v-if="status?.running && !status?.paused"
          class="filterbar-btn"
          :disabled="busy"
          @click="act('pause')"
        >
          Pause
        </button>
        <button
          v-if="status?.running && status?.paused"
          :disabled="busy"
          @click="act('resume')"
        >
          Resume
        </button>
        <button
          v-if="status?.running"
          :disabled="busy"
          @click="act('run-now')"
        >
          Fast-forward
        </button>
        <button
          v-if="status?.running"
          :disabled="busy"
          @click="act('stop')"
        >
          Stop
        </button>
        <button
          v-if="!status?.running"
          :disabled="busy"
          title="Archive current state + insights, then start fresh from generation 0"
          @click="confirmReset"
        >
          New analyst (reset)
        </button>
      </div>

      <div
        v-if="message"
        class="muted"
        style="margin-top: 10px; color: var(--green)"
      >
        {{ message }}
      </div>
    </div>

    <!-- ===== editable configuration ===== -->
    <div
      v-if="form"
      class="card"
    >
      <h3>Pace and data sources</h3>
      <div class="muted" style="margin-bottom: 12px">
        Changes apply from the next generation. Saving while sleeping wakes the
        analyst so a shorter wait or a new <code>grow</code> takes effect immediately.
      </div>

      <div class="filterbar">
        <label class="field">
          <span class="muted">wait between generations (s)</span>
          <input v-model.number="form.interval_seconds" type="number" min="0">
        </label>
        <label class="field">
          <span class="muted">analysis tasks / generation</span>
          <input v-model.number="form.batch_size" type="number" min="1">
        </label>
        <label class="field">
          <span class="muted">grow: new papers / generation</span>
          <input v-model.number="form.grow" type="number" min="0">
        </label>
        <label class="field">
          <span class="muted">papers requested / source</span>
          <input v-model.number="form.limit" type="number" min="1">
        </label>
        <div class="field">
          <span class="muted">reasoning mode</span>
          <button
            type="button"
            class="toggle"
            :class="{ on: form.offline }"
            @click="form.offline = !form.offline"
          >
            <span class="box">{{ form.offline ? '✓' : '' }}</span>
            offline (stub reasoner, no HF_TOKEN)
          </button>
        </div>
      </div>

      <h4 style="margin: 18px 0 8px; color: var(--accent); font-size: 12px">
        Sources to ingest from (when growing)
      </h4>
      <div class="toggle-row">
        <button
          v-for="src in allSources"
          :key="src"
          type="button"
          class="toggle"
          :class="{ on: form.sources.includes(src) }"
          @click="toggleSource(src)"
        >
          <span class="box">{{ form.sources.includes(src) ? '✓' : '' }}</span>
          {{ src }}
        </button>
      </div>

      <h4 style="margin: 18px 0 8px; color: var(--accent); font-size: 12px">
        Per-source search queries
      </h4>
      <div
        v-for="src in allSources"
        :key="`q-${src}`"
        class="query-row"
      >
        <span class="muted query-label">{{ src }}</span>
        <input
          v-model="form.queries[src]"
          :placeholder="defaultQueries[src]"
        >
      </div>
      <div class="muted" style="margin-top: 6px; font-size: 11px">
        arXiv uses search_query syntax (e.g. <code>cat:cs.LG</code>),
        Semantic Scholar takes free text, OpenReview takes a venue id
        (e.g. <code>ICLR.cc/2024/Conference</code>).
      </div>

      <div class="filterbar" style="margin-top: 14px">
        <button :disabled="savingConfig" @click="saveConfig">
          {{ savingConfig ? 'Saving...' : 'Save configuration' }}
        </button>
        <button @click="resetForm">
          Revert edits
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { getAnalystStatus, getAnalystConfig, analystAction } from '../composables/useApi.js'

const status = ref(null)
const form = ref(null)
const allSources = ref([])
const defaultQueries = ref({})
const error = ref('')
const message = ref('')
const busy = ref(false)
const savingConfig = ref(false)

const countdown = ref(null)
let pollTimer = null
let tickTimer = null

const phaseClass = computed(() => {
  const p = status.value?.phase
  return {
    sleeping: 'tag--conf-medium',
    analyzing: 'tag--synergy',
    growing: 'tag--gap',
    idle: 'tag',
    paused: 'stub',
    stopped: 'tag'
  }[p] || 'tag'
})

async function poll() {
  try {
    status.value = await getAnalystStatus()
    error.value = ''
    // sync the local countdown to the server's reported remaining time
    countdown.value = status.value.seconds_to_next
  } catch (e) {
    error.value = `cannot reach analyst: ${e}`
  }
}

async function loadConfig() {
  const res = await getAnalystConfig()
  allSources.value = res.all_sources || []
  defaultQueries.value = res.default_queries || {}
  applyForm(res.config)
}

function applyForm(cfg) {
  // a deep-ish clone so editing the form doesn't mutate the last server state
  form.value = {
    interval_seconds: cfg.interval_seconds,
    batch_size: cfg.batch_size,
    grow: cfg.grow,
    limit: cfg.limit,
    offline: cfg.offline,
    sources: [...(cfg.sources || [])],
    queries: { ...defaultQueries.value, ...(cfg.queries || {}) }
  }
}

function resetForm() {
  if (status.value?.config) applyForm(status.value.config)
  message.value = ''
}

function toggleSource(src) {
  const list = form.value.sources
  const i = list.indexOf(src)
  if (i === -1) list.push(src)
  else if (list.length > 1) list.splice(i, 1)   // keep at least one source
}

async function act(action) {
  busy.value = true
  message.value = ''
  try {
    const res = await analystAction(action)
    message.value = res.message || res.error || ''
    if (res.error) error.value = res.error
    await poll()
  } catch (e) {
    error.value = String(e)
  } finally {
    busy.value = false
  }
}

function confirmReset() {
  if (confirm('Archive the current analyst state + banked insights and start a '
    + 'brand-new analyst from generation 0?')) {
    act('reset')
  }
}

async function saveConfig() {
  savingConfig.value = true
  message.value = ''
  try {
    const res = await analystAction('config', form.value)
    message.value = res.ok ? 'configuration saved' : (res.error || 'save failed')
    if (res.config) applyForm(res.config)
    await poll()
  } catch (e) {
    error.value = String(e)
  } finally {
    savingConfig.value = false
  }
}

onMounted(async () => {
  await loadConfig()
  await poll()
  pollTimer = setInterval(poll, 2000)
  // smooth 1s countdown between polls
  tickTimer = setInterval(() => {
    if (countdown.value !== null && countdown.value > 0) countdown.value -= 1
  }, 1000)
})

onUnmounted(() => {
  clearInterval(pollTimer)
  clearInterval(tickTimer)
})
</script>

<style scoped>
.field {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.field input[type="number"] {
  width: 160px;
  flex: 0 0 auto;
}

.query-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 6px 0;
}

.query-label {
  width: 150px;
  flex: 0 0 auto;
}

/* clickable source / mode toggles (replace native checkboxes, which the global
   input styling mangles) */
.toggle-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.toggle {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 14px 8px 10px;
  font: inherit;
  font-size: 13px;
  font-weight: 530;
  color: var(--muted);
  background: var(--chip);
  border: 1px solid var(--line);
  border-radius: 999px;
  box-shadow: none;
  cursor: pointer;
  transition: border-color .12s ease, color .12s ease, background .12s ease;
}

.toggle:hover:not(:disabled) {
  border-color: #39405a;
  background: var(--panel-2);
  filter: none;
  transform: none;
}

.toggle.on {
  color: var(--accent-strong);
  border-color: rgba(122, 162, 247, .45);
  background: var(--accent-soft);
}

/* the little check box at the start of each toggle */
.toggle .box {
  display: grid;
  place-items: center;
  width: 16px;
  height: 16px;
  flex: 0 0 auto;
  font-size: 11px;
  line-height: 1;
  color: #0a0e16;
  border: 1px solid var(--line);
  border-radius: 5px;
  background: transparent;
}

.toggle.on .box {
  background: var(--accent);
  border-color: var(--accent);
}
</style>
