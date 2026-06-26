<template>
  <div class="topbar">
    <div class="crumb">
      {{ title }}
      <small>{{ subtitle }}</small>
    </div>

    <div class="spacer" />

    <button
      class="status-pill"
      :title="pillTitle"
      @click="$emit('go', 'analyst')"
    >
      <span
        class="dot"
        :class="dotClass"
      />
      <span>{{ pillText }}</span>
    </button>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { getAnalystStatus } from '../composables/useApi.js'

defineProps({ title: String, subtitle: String })
defineEmits(['go'])

const status = ref(null)
let timer = null

async function poll() {
  try {
    status.value = await getAnalystStatus()
  } catch {
    status.value = null
  }
}

const dotClass = computed(() => {
  const s = status.value
  if (!s || !s.running) return ''
  if (s.paused) return 'paused'
  if (s.phase === 'analyzing' || s.phase === 'growing') return 'busy'
  return 'live'
})

const pillText = computed(() => {
  const s = status.value
  if (!s) return 'analyst offline'
  if (!s.running) return 'analyst idle'
  if (s.paused) return 'analyst paused'
  const phase = { analyzing: 'analyzing', growing: 'fetching papers',
                  sleeping: 'waiting', idle: 'idle' }[s.phase] || s.phase
  return `analyst ${phase} · gen ${s.generation}`
})

const pillTitle = computed(() => {
  const s = status.value
  if (!s) return 'Open analyst control'
  return `${s.insights_banked} insights banked · ${s.tasks.done}/${s.tasks.total} tasks done · click to control`
})

onMounted(() => {
  poll()
  timer = setInterval(poll, 3000)
})
onUnmounted(() => clearInterval(timer))
</script>
