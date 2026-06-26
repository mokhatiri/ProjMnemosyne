<template>
  <div>
    <!-- loading skeleton -->
    <div v-if="!data" class="stat-grid">
      <div v-for="n in 6" :key="n" class="stat-card">
        <div class="skeleton" style="width:40%" />
        <div class="skeleton" style="width:70%;height:24px" />
      </div>
    </div>

    <template v-else>
      <!-- KPI cards -->
      <div class="stat-grid">
        <button
          v-for="s in stats"
          :key="s.label"
          class="stat-card"
          @click="s.go && $emit('go', s.go)"
        >
          <span class="ico" :class="s.color"><Icon :name="s.icon" /></span>
          <div class="num">{{ s.value }}</div>
          <div class="label">{{ s.label }}</div>
          <div v-if="s.sub" class="sub">{{ s.sub }}</div>
        </button>
      </div>

      <!-- two-column: insight mix + analyst snapshot -->
      <div class="ov-cols">
        <div class="card">
          <h3>Insight distribution</h3>
          <div v-if="!data.insights.total" class="muted">
            No insights yet &mdash; start the analyst to begin banking findings.
          </div>
          <div v-else class="bars">
            <div v-for="k in kinds" :key="k.name" class="bar-row">
              <span class="blabel">
                <span class="tag" :class="`tag--${k.name}`">{{ k.name }}</span>
              </span>
              <span class="bar-track">
                <span class="bar-fill" :class="k.name" :style="{ width: k.pct + '%' }" />
              </span>
              <span class="bval">{{ k.count }}</span>
            </div>
          </div>

          <div v-if="data.insights.total" class="conf-line">
            <span class="muted">confidence</span>
            <span class="tag tag--conf-high">{{ data.insights.by_confidence.high || 0 }} high</span>
            <span class="tag tag--conf-medium">{{ data.insights.by_confidence.medium || 0 }} medium</span>
            <span class="tag">{{ data.insights.by_confidence.low || 0 }} low</span>
            <span class="muted">&middot; {{ data.insights.real }} real / {{ data.insights.stub }} stub</span>
          </div>
        </div>

        <div class="card">
          <h3>Autonomous analyst</h3>
          <div class="analyst-snap">
            <span class="dot" :class="dotClass" />
            <strong>{{ phaseText }}</strong>
            <span class="muted">generation {{ a.generation }}</span>
          </div>
          <div class="snap-grid">
            <div><span class="snum">{{ a.tasks.done }}</span><span class="muted">/ {{ a.tasks.total }} tasks</span></div>
            <div><span class="snum">{{ a.tasks.pending }}</span><span class="muted">pending</span></div>
            <div><span class="snum">{{ a.insights_banked }}</span><span class="muted">banked</span></div>
          </div>
          <div v-if="a.next_up?.length" class="muted" style="margin-top:10px">
            next up: {{ a.next_up.slice(0, 3).join(', ') }}
          </div>
          <button class="ghost" style="margin-top:14px" @click="$emit('go', 'analyst')">
            Open analyst control →
          </button>
        </div>
      </div>

      <!-- quick actions -->
      <div class="section-title">Quick actions</div>
      <div class="quick-actions">
        <button class="action" @click="$emit('go', 'search')">
          <span class="ico"><Icon name="search" /></span>
          <span><span class="at">Search the corpus</span><span class="ad">semantic paper search (L4)</span></span>
        </button>
        <button class="action" @click="$emit('go', 'investigate')">
          <span class="ico"><Icon name="network" /></span>
          <span><span class="at">Investigate a topic</span><span class="ad">all agents + cross-validation (L6)</span></span>
        </button>
        <button class="action" @click="$emit('go', 'insights')">
          <span class="ico"><Icon name="bulb" /></span>
          <span><span class="at">Browse insights</span><span class="ad">ranked analyst findings</span></span>
        </button>
        <button class="action" @click="$emit('go', 'analyst')">
          <span class="ico"><Icon name="bot" /></span>
          <span><span class="at">Run the analyst</span><span class="ad">grow the corpus, find more</span></span>
        </button>
      </div>

      <!-- recent top insights -->
      <div class="section-title">Top insights</div>
      <div class="card" style="margin-top:0">
        <div v-if="!data.insights.top.length" class="empty">
          <span class="ico"><Icon name="bulb" /></span>
          Nothing banked yet. The analyst surfaces insights as it works the corpus.
        </div>
        <div
          v-for="ins in data.insights.top"
          :key="ins.id"
          class="row link-row"
          @click="$emit('go', 'insights')"
        >
          <span class="score">score {{ ins._score }}</span>
          <span class="tag" :class="`tag--${ins.kind}`">{{ ins.kind }}</span>
          <span class="tag" :class="`tag--conf-${ins.confidence}`">{{ ins.confidence }}</span>
          {{ ins.summary }}
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import Icon from './Icon.vue'
import { getOverview } from '../composables/useApi.js'

defineEmits(['go'])

const data = ref(null)

const a = computed(() => data.value?.analyst || { tasks: {}, generation: 0 })

const stats = computed(() => {
  if (!data.value) return []
  const c = data.value.corpus
  return [
    { label: 'Papers in corpus', value: c.papers, icon: 'file', color: '', go: 'search',
      sub: c.papers_cited_external ? `+${c.papers_cited_external} cited externally` : '' },
    { label: 'Methods', value: c.methods, icon: 'flask', color: 'cyan', go: 'agent' },
    { label: 'Claims', value: c.claims, icon: 'pulse', color: 'green' },
    { label: 'Datasets', value: c.datasets, icon: 'database', color: 'amber' },
    { label: 'Authors', value: c.authors, icon: 'users', color: 'purple' },
    { label: 'Insights banked', value: data.value.insights.total, icon: 'bulb', color: 'green', go: 'insights',
      sub: `${data.value.insights.real} from real reasoning` }
  ]
})

const kinds = computed(() => {
  const by = data.value?.insights.by_kind || {}
  const max = Math.max(1, ...Object.values(by))
  return Object.entries(by)
    .sort((x, y) => y[1] - x[1])
    .map(([name, count]) => ({ name, count, pct: Math.round((count / max) * 100) }))
})

const dotClass = computed(() => {
  if (!a.value.running) return ''
  if (a.value.paused) return 'paused'
  if (['analyzing', 'growing'].includes(a.value.phase)) return 'busy'
  return 'live'
})

const phaseText = computed(() => {
  if (!a.value.running) return 'stopped'
  if (a.value.paused) return 'paused'
  return ({ analyzing: 'analyzing', growing: 'fetching papers',
            sleeping: 'waiting for next generation', idle: 'idle' }[a.value.phase]) || a.value.phase
})

onMounted(async () => {
  data.value = await getOverview()
})
</script>

<style scoped>
.ov-cols {
  display: grid;
  grid-template-columns: 1.4fr 1fr;
  gap: 16px;
}

.ov-cols .card { margin-top: 16px; }

@media (max-width: 760px) {
  .ov-cols { grid-template-columns: 1fr; }
}

.conf-line {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
  margin-top: 16px;
  padding-top: 14px;
  border-top: 1px solid var(--line-soft);
}

.analyst-snap {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 14px;
}

.snap-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
}

.snap-grid > div {
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding: 10px 12px;
  border-radius: 10px;
  background: var(--panel-2);
  border: 1px solid var(--line-soft);
}

.snum {
  font-size: 19px;
  font-weight: 660;
  font-variant-numeric: tabular-nums;
}

.snap-grid .muted { font-size: 11.5px; }

.link-row { cursor: pointer; }
</style>
