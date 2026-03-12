<template>
  <div class="stats-banner">
    <div class="stats-grid">
      <template v-for="(item, i) in items" :key="i">
        <div v-if="i > 0" class="stat-divider" />
        <div class="stat-item in-view">
          <span class="stat-number">{{ item.value }}</span>
          <span class="stat-unit">{{ item.unit }}</span>
          <span class="stat-label">{{ item.label }}</span>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  items: Array<{ value: number | string; unit: string; label: string }>
}>()
</script>
