<template>
  <div>
    <div class="card">
      <h3>Filter insights</h3>

      <div class="filterbar">
        <select v-model="kind">
          <option value="all">all kinds</option>
          <option value="evidence">evidence</option>
          <option value="synergy">synergy</option>
          <option value="gap">gap</option>
          <option value="contradiction">contradiction</option>
          <option value="hypothesis">hypothesis</option>
        </select>

        <select v-model="confidence">
          <option value="all">all confidence</option>
          <option value="high">high</option>
          <option value="medium">medium</option>
          <option value="low">low</option>
        </select>

        <input
          v-model.number="minScore"
          type="number"
          placeholder="min score"
          style="width: 120px"
        >

        <button @click="reset">
          Reset
        </button>
      </div>
    </div>

    <div class="card">
      <h3>
        Autonomous analyst &middot; top {{ filtered.length }} of {{ data.count }} insight(s)
      </h3>

      <div
        v-if="!filtered.length"
        class="muted"
      >
        No insights yet. Run the analyst: <code>python -m analyst run</code>
      </div>

      <div
        v-for="insight in filtered"
        :key="insight.id"
        class="row"
      >
        <span class="score">score {{ insight._score }}</span>

        <span
          class="tag"
          :class="`tag--${insight.kind}`"
        >{{ insight.kind }}</span>
        <span
          class="tag"
          :class="`tag--conf-${insight.confidence}`"
        >{{ insight.confidence }}</span>
        <span
          v-if="insight.stub"
          class="tag stub"
        >stub</span>

        {{ insight.summary }}

        <div
          v-if="insight.provenance?.length"
          class="muted"
        >
          provenance: {{ insight.provenance.join(', ') }}
        </div>

        <InsightExplanation :insight="insight" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import InsightExplanation from './InsightExplanation.vue'

const props = defineProps({
  data: Object
})

const kind = ref('all')
const confidence = ref('all')
const minScore = ref(0)

function reset() {
  kind.value = 'all'
  confidence.value = 'all'
  minScore.value = 0
}

const filtered = computed(() =>
  (props.data.insights || []).filter(i => {
    if (kind.value !== 'all' && i.kind !== kind.value)
      return false

    if (confidence.value !== 'all' && i.confidence !== confidence.value)
      return false

    return (i._score ?? 0) >= (minScore.value || 0)
  })
)
</script>
