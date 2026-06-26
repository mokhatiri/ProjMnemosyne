<template>
  <aside class="sidebar">
    <div class="brand">
      <span class="logo"
        ><Icon name="spark" style="width: 18px; height: 18px"
      /></span>
      <span class="name">
        ProjMnemosyne
        <small>Research Intelligence</small>
      </span>
    </div>

    <div v-for="group in groups" :key="group.label" class="nav-group">
      <div class="nav-label">{{ group.label }}</div>
      <button
        v-for="item in group.items"
        :key="item.id"
        class="nav-item"
        :class="{ active: modelValue === item.id }"
        @click="$emit('update:modelValue', item.id)"
      >
        <Icon :name="item.icon" />
        <span class="t">{{ item.label }}</span>
        <span v-if="item.badge != null" class="badge">{{ item.badge }}</span>
      </button>
    </div>

    <div class="sidebar-foot">
      code orchestrates, models judge.<br />
      L1 ingest &middot; L2 extract &middot; L3 retrieve+graph &middot; L4 tools
      &middot; L5 agents &middot; L6 A2A
    </div>
  </aside>
</template>

<script setup>
import { computed } from "vue";
import Icon from "./Icon.vue";

const props = defineProps({
  modelValue: String,
  insightCount: { type: Number, default: null },
});
defineEmits(["update:modelValue"]);

const groups = computed(() => [
  {
    label: "Discover",
    items: [
      { id: "overview", label: "Overview", icon: "grid" },
      { id: "search", label: "Search papers", icon: "search" },
      { id: "related", label: "Related work", icon: "link" },
      { id: "citations", label: "Citations", icon: "share" },
    ],
  },
  {
    label: "Analyze",
    items: [
      { id: "agent", label: "Agents", icon: "cpu" },
      { id: "investigate", label: "Investigate", icon: "network" },
      {
        id: "insights",
        label: "Insights",
        icon: "bulb",
        badge: props.insightCount,
      },
    ],
  },
  {
    label: "Automate",
    items: [{ id: "analyst", label: "Analyst", icon: "bot" }],
  },
]);
</script>
