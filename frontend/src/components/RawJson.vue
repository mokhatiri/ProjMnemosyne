<template>
  <details class="json-disclosure">
    <summary>
      inspect data
    </summary>

    <div class="json-panel">
      <button
        class="copy"
        :title="copied ? 'Copied!' : 'Copy JSON'"
        @click.stop="copy"
      >
        {{ copied ? 'copied ✓' : 'copy' }}
      </button>

      <div class="jv-wrap">
        <JsonView :data="data" />
      </div>
    </div>
  </details>
</template>

<script setup>
import { ref } from 'vue'
import JsonView from './JsonView.vue'

const props = defineProps({
  data: Object
})

const copied = ref(false)

async function copy() {
  try {
    await navigator.clipboard.writeText(JSON.stringify(props.data, null, 2))
    copied.value = true
    setTimeout(() => (copied.value = false), 1400)
  } catch {
    copied.value = false
  }
}
</script>

<style scoped>
.json-panel {
  position: relative;
  margin-top: 8px;
  padding: 12px 14px;
  background: var(--bg);
  border: 1px solid var(--line);
  border-radius: 10px;
  overflow: auto;
}

.copy {
  position: absolute;
  top: 8px;
  right: 8px;
  z-index: 1;
  padding: 4px 10px;
  font-size: 11px;
  font-weight: 530;
  color: var(--muted);
  background: var(--chip);
  border: 1px solid var(--line);
  border-radius: 7px;
  box-shadow: none;
}

.copy:hover:not(:disabled) {
  color: var(--fg);
  border-color: var(--accent);
  background: var(--panel-2);
  filter: none;
  transform: none;
}
</style>
