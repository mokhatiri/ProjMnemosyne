<template>
  <div class="card">
    <h3>
      {{ title }}: {{ findings.length }} finding(s)
    </h3>

    <div
      v-for="f in findings"
      :key="f.id || f.summary"
      class="row"
    >
      <span
        class="tag"
        :class="`tag--${f.kind}`"
      >
        {{ f.kind }}
      </span>

      <span
        class="tag"
        :class="`tag--conf-${f.confidence}`"
      >
        {{ f.confidence }}
      </span>

      <span
        v-if="f.stub"
        class="tag stub"
      >
        stub
      </span>

      {{ f.summary }}

      <div
        v-if="f.provenance?.length"
        class="muted"
      >
        provenance:
        {{ f.provenance.join(', ') }}
      </div>
    </div>

    <div
      v-if="!findings.length"
      class="muted"
    >
      (no findings)
    </div>
  </div>
</template>

<script setup>
defineProps({
  title: String,
  findings: {
    type: Array,
    default: () => []
  }
})
</script>
