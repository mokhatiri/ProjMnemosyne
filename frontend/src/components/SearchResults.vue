<template>
  <div class="card">
    <h3>
      {{ data.count }} paper(s) &middot; match: {{ data.match }}
    </h3>

    <div
      v-if="!data.results?.length"
      class="muted"
    >
      No papers matched. Try a broader query.
    </div>

    <div
      v-for="paper in data.results"
      :key="paper.paper_id"
      class="row"
    >
      <span class="score">
        {{ paper.score }}
      </span>

      <strong
        class="link"
        title="Find related work"
        @click="$emit('open', { view: 'related', query: paper.paper_id })"
      >{{ paper.title }}</strong>

      <div class="muted">
        <code>{{ paper.paper_id }}</code>
        <template v-if="(paper.categories || []).length">
          &middot; {{ (paper.categories || []).join(', ') }}
        </template>
        <template v-if="paper.year">
          &middot; {{ paper.year }}
        </template>
      </div>

      <div class="muted snippet">
        {{ paper.snippet }}
      </div>

      <div class="chip-row">
        <span
          class="link"
          @click="$emit('open', { view: 'related', query: paper.paper_id })"
        >→ related work</span>
        <span
          class="link"
          @click="$emit('open', { view: 'citations', query: paper.paper_id })"
        >→ citations</span>
      </div>
    </div>

    <RawJson :data="data" />
  </div>
</template>

<script setup>
import RawJson from './RawJson.vue'

defineProps({
  data: Object
})
defineEmits(['open'])
</script>

<style scoped>
.snippet { margin-top: 4px; }
</style>
