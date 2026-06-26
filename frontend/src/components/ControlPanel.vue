<template>
  <div>
    <div class="controls">
      <select
        v-if="mode === 'agent'"
        v-model="localAgent"
      >
        <option value="contradiction">contradiction</option>
        <option value="synergy">synergy</option>
        <option value="gap">gap</option>
        <option value="evidence">evidence</option>
      </select>

      <input
        v-model="localQuery"
        :placeholder="placeholder"
        @keydown.enter="$emit('run')"
      >

      <button
        :disabled="loading"
        @click="$emit('run')"
      >
        {{ loading ? 'Running…' : 'Run' }}
      </button>
    </div>

    <div class="hint">
      {{ hint }}
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  mode: String,
  agent: String,
  query: String,
  loading: Boolean
})

const emit = defineEmits(['update:agent', 'update:query', 'run'])

const localAgent = computed({
  get: () => props.agent,
  set: v => emit('update:agent', v)
})

const localQuery = computed({
  get: () => props.query,
  set: v => emit('update:query', v)
})

const placeholders = {
  search: "Free-text query, e.g. 'chain of thought reasoning'",
  related: "A paper id, e.g. 'arxiv:2606.11189v1'",
  citations: "A paper id, e.g. 'semantic_scholar:1b6e8…'",
  agent: 'Topic for the agent (blank scans the whole corpus)',
  investigate: "A topic/proposition, e.g. 'supervised fine-tuning'"
}

const hints = {
  search: 'Ranks papers by semantic similarity of their title + abstract (Layer 4). Click any result to jump to its related work or citations.',
  related: 'Surfaces similar papers, what it cites, and papers sharing a method (Layer 4).',
  citations: 'Walks the outgoing citation graph; out-of-corpus citations come back flagged as stubs (Layer 4).',
  agent: 'Runs one analytical agent over the corpus and returns structured findings (Layer 5).',
  investigate: 'Runs every agent on the topic, then cross-validates their findings (Layer 6 A2A).'
}

const placeholder = computed(() => placeholders[props.mode] || 'query…')
const hint = computed(() => hints[props.mode] || '')
</script>
