<template>
  <!-- primitive: render inline with a type-coloured token -->
  <span
    v-if="!isContainer"
    class="jv-val"
    :class="valClass"
  >{{ display }}</span>

  <!-- object / array: a structured list, nested values collapsible -->
  <ul
    v-else
    class="jv"
    :class="{ root: depth === 0 }"
  >
    <li
      v-for="entry in entries"
      :key="entry.key"
      class="jv-row"
    >
      <!-- leaf: key + primitive on one line -->
      <template v-if="!entry.container">
        <span class="jv-key">{{ entry.key }}</span>
        <span class="jv-colon">:</span>
        <JsonView :data="entry.value" />
      </template>

      <!-- nested: collapsible disclosure -->
      <details
        v-else
        :open="depth < 1"
      >
        <summary>
          <span class="jv-key">{{ entry.key }}</span>
          <span class="jv-meta">{{ entry.meta }}</span>
        </summary>
        <JsonView
          :data="entry.value"
          :depth="depth + 1"
        />
      </details>
    </li>
  </ul>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  data: { default: null },
  depth: { type: Number, default: 0 }
})

const isArray = computed(() => Array.isArray(props.data))
const isContainer = computed(() =>
  props.data !== null && typeof props.data === 'object')

function container(v) {
  return v !== null && typeof v === 'object'
}

function meta(v) {
  if (Array.isArray(v)) return v.length ? `[${v.length}]` : '[ ]'
  return Object.keys(v).length ? `{${Object.keys(v).length}}` : '{ }'
}

// normalise object/array into a uniform [{key, value, container, meta}] list
const entries = computed(() => {
  if (!isContainer.value) return []
  const src = isArray.value
    ? props.data.map((v, i) => [String(i), v])
    : Object.entries(props.data)
  return src.map(([key, value]) => ({
    key,
    value,
    container: container(value) && (Array.isArray(value) ? value.length : Object.keys(value).length),
    meta: container(value) ? meta(value) : ''
  }))
})

// primitive rendering
const valClass = computed(() => {
  const v = props.data
  if (v === null) return 'jv-null'
  if (typeof v === 'boolean') return 'jv-bool'
  if (typeof v === 'number') return 'jv-num'
  if (Array.isArray(v)) return 'jv-empty'
  if (typeof v === 'object') return 'jv-empty'
  return 'jv-str'
})

const display = computed(() => {
  const v = props.data
  if (v === null) return 'null'
  if (Array.isArray(v)) return '[ ]'        // empty array
  if (typeof v === 'object') return '{ }'   // empty object
  if (typeof v === 'string') return v === '' ? '""' : v
  return String(v)
})
</script>

<style scoped>
.jv {
  list-style: none;
  margin: 0;
  padding: 0 0 0 14px;
  border-left: 1px solid var(--line-soft);
}

/* the outermost list shouldn't carry the guide line / indent */
.jv.root {
  padding-left: 0;
  border-left: none;
}

.jv-row {
  margin: 2px 0;
  line-height: 1.6;
}

.jv-key {
  color: var(--accent-strong);
  font-family: var(--mono);
  font-size: 12.5px;
}

.jv-colon {
  color: var(--muted-2);
  margin: 0 6px 0 2px;
}

.jv-meta {
  margin-left: 8px;
  font-size: 11px;
  color: var(--muted-2);
  font-variant-numeric: tabular-nums;
}

.jv-val {
  font-family: var(--mono);
  font-size: 12.5px;
  word-break: break-word;
}

.jv-str { color: var(--green); }
.jv-num { color: var(--cyan); }
.jv-bool { color: var(--amber); }
.jv-null { color: var(--muted-2); font-style: italic; }
.jv-empty { color: var(--muted-2); }

/* tighten the global <details> styling for the tree */
details > summary {
  margin-top: 0;
  display: inline-flex;
  align-items: baseline;
}
</style>
