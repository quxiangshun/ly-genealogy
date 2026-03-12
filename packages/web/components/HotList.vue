<template>
  <div class="hot-list">
    <NuxtLink
      v-for="(item, i) in items"
      :key="item.slug"
      :to="baseUrl + '/' + item.slug"
      class="hot-item"
    >
      <span class="hot-rank" :class="{ 'hot-rank-top': i < 3 }">{{ i + 1 }}</span>
      <span class="hot-title">{{ item.title }}</span>
      <span class="hot-views"><i class="bi bi-eye me-1"></i>{{ item.viewCount ?? item.view_count ?? 0 }}</span>
    </NuxtLink>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  items: Array<{ slug: string; title: string; viewCount?: number; view_count?: number }>
  baseUrl: string
}>()
</script>
