<template>
  <div>
    <div class="card head-card">
      <h3>Citation graph</h3>
      <div class="muted">
        from <code>{{ rootId }}</code> · depth {{ data.depth }} ·
        {{ data.resolved_count }} in-corpus / {{ data.stub_count }} external
      </div>
    </div>

    <div class="card">
      <h3>{{ edges.length }} citation edge(s)</h3>

      <div v-if="!edges.length" class="empty">
        <div>
          No outgoing citations were recorded for this paper.
        </div>
        <div class="muted" style="margin-top:6px">
          Citation edges only exist when a paper's reference list was captured at
          ingest and the cited work is matched in the graph. Try a paper with a
          richer reference list, or a larger <code>depth</code>.
        </div>
      </div>

      <template v-else>
        <div
          v-for="hop in hops"
          :key="hop.level"
        >
          <div class="section-title">hop {{ hop.level }}</div>
          <div
            v-for="(e, i) in hop.edges"
            :key="i"
            class="row"
          >
            <span
              v-if="e.stub"
              class="tag stub"
            >external</span>
            <strong
              v-if="!e.stub"
              class="link"
              title="Find related work for this paper"
              @click="$emit('open', { view: 'related', query: cleanId(e.to) })"
            >{{ e.to_label || cleanId(e.to) }}</strong>
            <strong v-else>{{ e.to_label || cleanId(e.to) }}</strong>

            <div class="muted">
              <code>{{ cleanId(e.from) }}</code> → <code>{{ cleanId(e.to) }}</code>
            </div>
          </div>
        </div>
      </template>
    </div>

    <RawJson :data="data" />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import RawJson from './RawJson.vue'

const props = defineProps({ data: Object })
defineEmits(['open'])

const cleanId = (nid) => (nid || '').replace(/^paper:/, '')
const rootId = computed(() => cleanId(props.data.root) || '(unresolved)')
const edges = computed(() => props.data.edges || [])

// group edges by hop level for a readable breadth-first layout
const hops = computed(() => {
  const map = new Map()
  for (const e of edges.value) {
    const lvl = e.hop ?? 1
    if (!map.has(lvl)) map.set(lvl, [])
    map.get(lvl).push(e)
  }
  return [...map.entries()]
    .sort((a, b) => a[0] - b[0])
    .map(([level, es]) => ({ level, edges: es }))
})
</script>

<style scoped>
.head-card { padding-bottom: 14px; }
.section-title { margin: 14px 2px 6px; }
</style>
