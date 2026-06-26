<template>
  <div>
    <!-- loading -->
    <div v-if="!corpus" class="card">
      <div class="skeleton" style="width:35%" />
      <div class="skeleton" style="width:90%" />
      <div class="skeleton" style="width:70%" />
    </div>

    <!-- paper catalog: search / related / citations -->
    <div v-else-if="isPaperView" class="card">
      <h3>
        {{ corpus.counts.papers }} paper(s) already digested
        <span class="muted" style="font-weight:500">· pick one or search above</span>
      </h3>

      <div v-if="!corpus.papers.length" class="muted">
        No papers ingested yet. Run <code>python -m pipeline --ingest 2</code> or grow from the Analyst tab.
      </div>

      <div
        v-for="p in corpus.papers"
        :key="p.paper_id"
        class="row"
      >
        <span
          v-if="p.extracted"
          class="score"
          title="Fully extracted into the knowledge graph"
        >digested</span>

        <strong
          class="link"
          :title="primaryTitle"
          @click="$emit('open', { view: primaryView, query: p.paper_id })"
        >{{ p.title }}</strong>

        <div class="muted">
          <code>{{ p.paper_id }}</code>
          <template v-if="p.year"> · {{ p.year }}</template>
          <template v-if="p.categories.length"> · {{ p.categories.join(', ') }}</template>
        </div>

        <div v-if="p.authors.length" class="muted authors">
          {{ p.authors.join(', ') }}<template v-if="p.authors.length >= 4"> …</template>
        </div>

        <div class="muted snippet">
          {{ p.snippet }}<template v-if="p.snippet.length >= 220">…</template>
        </div>

        <div class="chip-row">
          <span class="link" @click="$emit('open', { view: 'related', query: p.paper_id })">→ related work</span>
          <span class="link" @click="$emit('open', { view: 'citations', query: p.paper_id })">→ citations</span>
        </div>
      </div>
    </div>

    <!-- method/topic catalog: agent / investigate -->
    <div v-else-if="isMethodView">
      <div class="card">
        <h3>
          {{ corpus.counts.methods }} method(s) the corpus is about
          <span class="muted" style="font-weight:500">· click one to {{ runVerb }}</span>
        </h3>

        <div v-if="!corpus.methods.length" class="muted">
          No methods in the graph yet. Build it with <code>python -m pipeline</code>.
        </div>

        <div class="tag-cloud">
          <button
            v-for="m in corpus.methods"
            :key="m.label"
            class="topic"
            @click="$emit('open', { view, query: m.label })"
          >
            {{ m.label }}
            <span class="topic-n">{{ m.papers }}</span>
          </button>
        </div>
      </div>

      <div v-if="corpus.datasets.length" class="card">
        <h3>
          {{ corpus.counts.datasets }} dataset(s) seen in the corpus
          <span class="muted" style="font-weight:500">· also valid topics</span>
        </h3>
        <div class="tag-cloud">
          <button
            v-for="d in corpus.datasets"
            :key="d.label"
            class="topic subtle"
            @click="$emit('open', { view, query: d.label })"
          >
            {{ d.label }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getCorpus } from '../composables/useApi.js'

const props = defineProps({ view: String })
defineEmits(['open'])

const corpus = ref(null)

const isPaperView = computed(() => ['search', 'related', 'citations'].includes(props.view))
const isMethodView = computed(() => ['agent', 'investigate'].includes(props.view))

// For the paper catalog, clicking a title does the page's primary action.
const primaryView = computed(() => (props.view === 'citations' ? 'citations' : 'related'))
const primaryTitle = computed(() =>
  props.view === 'citations' ? 'Trace citations' : 'Find related work')

const runVerb = computed(() => (props.view === 'investigate' ? 'investigate it' : 'run the agent on it'))

onMounted(async () => {
  corpus.value = await getCorpus()
})
</script>

<style scoped>
.authors { margin-top: 2px; font-size: 12px; }
.snippet { margin-top: 5px; }

.tag-cloud {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 2px;
}

.topic {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 7px 12px;
  font-weight: 530;
  font-size: 13px;
  color: var(--fg);
  background: var(--chip);
  border: 1px solid var(--line);
  border-radius: 999px;
  box-shadow: none;
  cursor: pointer;
}

.topic:hover:not(:disabled) {
  border-color: var(--accent);
  background: var(--panel-2);
  transform: translateY(-1px);
  filter: none;
}

.topic.subtle {
  color: var(--muted);
  font-size: 12px;
  padding: 6px 11px;
}

.topic-n {
  font-size: 11px;
  font-variant-numeric: tabular-nums;
  color: var(--accent-strong);
  background: var(--accent-soft);
  border-radius: 999px;
  padding: 0 7px;
}
</style>
