<template>
  <NuxtLayout>
    <NuxtPage />
  </NuxtLayout>
</template>

<script setup lang="ts">
useHead({
  bodyAttrs: { class: 'theme-heritage' },
  htmlAttrs: { lang: 'zh-CN' },
})
</script>

<style>
html {
  scroll-behavior: smooth;
  -webkit-text-size-adjust: 100%;
  text-size-adjust: 100%;
  overflow-x: hidden;
}

::selection {
  background: rgba(176,138,80,0.25);
  color: var(--heritage-ink);
}
</style>
