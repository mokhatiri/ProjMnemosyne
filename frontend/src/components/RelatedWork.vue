<template>
  <div>
    <div class="card head-card">
      <h3>Related work</h3>
      <div class="muted">
        for <code>{{ data.paper_id }}</code> · match: {{ data.match }}
      </div>
    </div>

    <!-- semantically similar -->
    <div class="card">
      <h3>Similar papers · {{ similar.length }}</h3>
      <div v-if="!similar.length" class="muted">
        No semantically similar papers found.
      </div>
      <div
        v-for="p in similar"
        :key="p.paper_id"
        class="row"
      >
        <span class="score">{{ p.score }}</span>
        <strong
          class="link"
          title="Find related work for this paper"
          @click="$emit('open', { view: 'related', query: p.paper_id })"
        >{{ p.title || p.paper_id }}</strong>
        <div class="muted">
          <code>{{ p.paper_id }}</code>
        </div>
        <div class="chip-row">
          <span class="link" @click="$emit('open', { view: 'citations', query: p.paper_id })">→ citations</span>
        </div>
      </div>
    </div>

    <!-- cites -->
    <div class="card">
      <h3>Cites · {{ cites.length }}</h3>
      <div v-if="!cites.length" class="muted">
        No in-corpus citations recorded for this paper.
      </div>
      <div
        v-for="c in cites"
        :key="c.paper_id"
        class="row"
      >
        <span v-if="c.stub" class="tag stub">external</span>
        <strong
          v-if="!c.stub"
          class="link"
          @click="$emit('open', { view: 'related', query: c.paper_id })"
        >{{ c.title || c.paper_id }}</strong>
        <strong v-else>{{ c.title || c.paper_id }}</strong>
        <div class="muted"><code>{{ c.paper_id }}</code></div>
      </div>
    </div>

    <!-- shares methods -->
    <div class="card">
      <h3>Shares methods · {{ shares.length }}</h3>
      <div v-if="!shares.length" class="muted">
        No other paper shares a method with this one yet.
      </div>
      <div
        v-for="(s, i) in shares"
        :key="i"
        class="row"
      >
        <strong
          class="link"
          @click="$emit('open', { view: 'related', query: s.paper_id })"
        >{{ s.title || s.paper_id }}</strong>
        <div class="muted">
          via <span class="tag">{{ s.via_method }}</span>
          <template v-if="s.relation">· {{ s.relation }}</template>
        </div>
        <div class="muted"><code>{{ s.paper_id }}</code></div>
      </div>
    </div>

    <RawJson :data="data" />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import RawJson from './RawJson.vue'

const props = defineProps({ data: Object })
defineEmits(['open'])

const similar = computed(() => props.data.semantically_similar || [])
const cites = computed(() => props.data.cites || [])
const shares = computed(() => props.data.shares_methods || [])
</script>

<style scoped>
.head-card { padding-bottom: 14px; }
</style>
