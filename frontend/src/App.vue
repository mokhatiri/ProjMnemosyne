<template>
  <div class="app">
    <SideNav
      :model-value="view"
      :insight-count="insightCount"
      @update:model-value="goTo"
    />

    <div class="content">
      <TopBar
        :title="meta[0]"
        :subtitle="meta[1]"
        @go="goTo"
      />

      <div
        :key="view"
        class="page"
      >
        <div class="page-head">
          <h2>{{ meta[0] }}</h2>
          <p>{{ meta[1] }}</p>
        </div>

        <!-- self-managed views -->
        <Overview
          v-if="view === 'overview'"
          @go="goTo"
        />
        <AnalystControl v-else-if="view === 'analyst'" />

        <!-- query-driven views -->
        <template v-else>
          <ControlPanel
            :mode="view"
            v-model:agent="agent"
            v-model:query="query"
            :loading="loading"
            @run="run"
          />

          <div
            v-if="data?.error"
            class="card"
          >
            <span class="muted">error:</span> {{ data.error }}
          </div>

          <div
            v-else-if="loading"
            class="card"
          >
            <div class="skeleton" style="width:30%" />
            <div class="skeleton" style="width:90%" />
            <div class="skeleton" style="width:80%" />
            <div class="skeleton" style="width:60%" />
          </div>

          <SearchResults
            v-else-if="view === 'search' && data"
            :data="data"
            @open="openEntity"
          />
          <RelatedWork
            v-else-if="view === 'related' && data"
            :data="data"
            @open="openEntity"
          />
          <Citations
            v-else-if="view === 'citations' && data"
            :data="data"
            @open="openEntity"
          />
          <FindingsList
            v-else-if="view === 'agent' && data"
            :title="`Agent: ${data.agent}`"
            :findings="data.findings || []"
          />
          <InvestigateReport
            v-else-if="view === 'investigate' && data"
            :report="data"
          />
          <InsightsView
            v-else-if="view === 'insights' && data"
            :data="data"
          />
          <RawJson
            v-else-if="data"
            :data="data"
          />

          <BrowseCorpus
            v-else
            :view="view"
            @open="openEntity"
          />
        </template>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import SideNav from './components/SideNav.vue'
import TopBar from './components/TopBar.vue'
import Overview from './components/Overview.vue'
import BrowseCorpus from './components/BrowseCorpus.vue'
import ControlPanel from './components/ControlPanel.vue'
import SearchResults from './components/SearchResults.vue'
import RelatedWork from './components/RelatedWork.vue'
import Citations from './components/Citations.vue'
import FindingsList from './components/FindingsList.vue'
import InvestigateReport from './components/InvestigateReport.vue'
import InsightsView from './components/InsightsView.vue'
import AnalystControl from './components/AnalystControl.vue'
import RawJson from './components/RawJson.vue'
import { getAnalystStatus } from './composables/useApi.js'

const META = {
  overview: ['Overview', 'Corpus, knowledge graph and analyst at a glance'],
  search: ['Search papers', 'Semantic retrieval over the corpus (Layer 4)'],
  related: ['Related work', 'Similar papers, citations and shared methods (Layer 4)'],
  citations: ['Citations', 'Walk the citation graph from a paper (Layer 4)'],
  agent: ['Agents', 'Run one analytical agent over the corpus (Layer 5)'],
  investigate: ['Investigate', 'All agents on a topic, then cross-validation (Layer 6 · A2A)'],
  insights: ['Insights', 'Ranked findings banked by the autonomous analyst'],
  analyst: ['Analyst', 'Drive the autonomous analysis loop — run, pace, sources']
}

const view = ref('overview')
const agent = ref('contradiction')
const query = ref('')
const loading = ref(false)
const data = ref(null)
const insightCount = ref(null)

const meta = computed(() => META[view.value] || ['', ''])

function goTo(target, q) {
  view.value = target
  data.value = null
  if (q !== undefined) query.value = q
  if (target === 'insights') return run()      // auto-load banked insights
  if (q !== undefined) run()                    // cross-navigation with a paper id
}

// a result item asked to open another view (e.g. paper -> related work)
function openEntity({ view: target, query: q }) {
  goTo(target, q)
}

async function run() {
  loading.value = true
  data.value = null

  const v = query.value.trim()
  let url
  switch (view.value) {
    case 'search': url = `/api/search?q=${encodeURIComponent(v)}`; break
    case 'related': url = `/api/related?paper_id=${encodeURIComponent(v)}`; break
    case 'citations': url = `/api/citations?paper_id=${encodeURIComponent(v)}&depth=1`; break
    case 'agent': url = `/api/agent?name=${agent.value}&topic=${encodeURIComponent(v)}`; break
    case 'investigate': url = `/api/investigate?topic=${encodeURIComponent(v)}`; break
    case 'insights': url = '/api/insights?top=50'; break
    default: loading.value = false; return
  }

  try {
    data.value = await (await fetch(url)).json()
    if (view.value === 'insights' && typeof data.value.count === 'number') {
      insightCount.value = data.value.count
    }
  } catch (e) {
    data.value = { error: String(e) }
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  try {
    insightCount.value = (await getAnalystStatus()).insights_banked
  } catch { /* badge stays blank */ }
})
</script>
