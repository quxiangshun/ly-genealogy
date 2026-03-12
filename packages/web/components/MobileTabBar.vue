<template>
  <nav class="mobile-tab-bar" aria-label="底部导航">
    <NuxtLink
      v-for="item in tabs"
      :key="item.to"
      :to="item.to"
      class="tab-item"
      :class="{ active: isTabActive(item) }"
    >
      <i :class="['bi', item.icon]"></i>
      <span>{{ item.label }}</span>
    </NuxtLink>
  </nav>
</template>

<script setup lang="ts">
const route = useRoute()

const tabs = [
  { to: '/', icon: 'bi-house-door-fill', label: '首页', exact: true },
  { to: '/genealogy', icon: 'bi-book-fill', label: '族谱', prefix: '/genealogy' },
  { to: '/culture/zibei', icon: 'bi-search', label: '字辈', exact: true },
  { to: '/culture/relationship', icon: 'bi-people-fill', label: '亲缘', exact: true },
  { to: '/culture', icon: 'bi-bank2', label: '文化', exact: true },
]

function isTabActive(item: { to: string; exact?: boolean; prefix?: string }) {
  if (item.exact) return route.path === item.to
  if (item.prefix) return route.path.startsWith(item.prefix)
  return route.path === item.to
}
</script>
