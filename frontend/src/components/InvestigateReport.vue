<template>
  <div>
    <div class="card">
      <h3>A2A report</h3>
      {{ report.summary }}
    </div>

    <FindingsList
      title="Findings"
      :findings="report.findings || []"
    />

    <div class="card">
      <h3>
        Cross-validation links: {{ crossValidations.length }}
      </h3>

      <div
        v-for="(cv, i) in crossValidations"
        :key="i"
        class="row"
      >
        <span class="tag">{{ cv.type }}</span>{{ cv.note }}
        <div class="muted">
          links: {{ (cv.finding_ids || []).join(', ') }}
        </div>
      </div>

      <div
        v-if="!crossValidations.length"
        class="muted"
      >
        (agents' findings did not corroborate on this topic)
      </div>

      <RawJson :data="report" />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import FindingsList from './FindingsList.vue'
import RawJson from './RawJson.vue'

const props = defineProps({
  report: Object
})

const crossValidations = computed(() => props.report.cross_validations || [])
</script>
