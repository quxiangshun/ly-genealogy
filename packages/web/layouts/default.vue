<template>
  <div class="page-wrap theme-heritage">
    <header ref="headerRef" class="heritage-header">
      <nav class="navbar navbar-expand-lg navbar-dark">
        <div class="container">
          <NuxtLink class="navbar-brand heritage-brand" to="/">屈氏宗谱</NuxtLink>
          <button
            class="navbar-toggler d-lg-none"
            type="button"
            aria-label="切换导航"
            @click="menuOpen = !menuOpen"
          >
            <i :class="menuOpen ? 'bi bi-x-lg' : 'bi bi-list'" style="font-size:1.2rem"></i>
          </button>
          <div class="navbar-collapse" :class="{ show: menuOpen, collapse: !menuOpen }" id="navbarNav">
            <ul class="navbar-nav me-auto" @click="menuOpen = false">
              <li class="nav-item">
                <NuxtLink to="/" class="nav-link" :class="{ active: isActive('/') }">
                  <i class="bi bi-house-door me-1"></i>首页
                </NuxtLink>
              </li>
              <li class="nav-item">
                <NuxtLink to="/genealogy" class="nav-link" :class="{ active: isGenealogyActive }">
                  <i class="bi bi-book me-1"></i>族谱库
                </NuxtLink>
              </li>
              <li class="nav-item">
                <NuxtLink to="/culture/zibei" class="nav-link" :class="{ active: isActive('/culture/zibei') }">
                  <i class="bi bi-list-ol me-1"></i>字辈查询
                </NuxtLink>
              </li>
              <li class="nav-item">
                <NuxtLink to="/culture/relationship" class="nav-link" :class="{ active: isActive('/culture/relationship') }">
                  <i class="bi bi-people me-1"></i>亲缘查询
                </NuxtLink>
              </li>
              <li class="nav-item">
                <NuxtLink to="/culture" class="nav-link" :class="{ active: isCultureActive }">
                  <i class="bi bi-bank me-1"></i>屈氏文化
                </NuxtLink>
              </li>
              <li class="nav-item">
                <NuxtLink to="/wiki" class="nav-link" :class="{ active: isWikiActive }">
                  <i class="bi bi-journal-bookmark me-1"></i>百科
                </NuxtLink>
              </li>
              <li class="nav-item">
                <NuxtLink to="/news" class="nav-link" :class="{ active: isNewsActive }">
                  <i class="bi bi-newspaper me-1"></i>动态
                </NuxtLink>
              </li>
            </ul>
            <ul class="navbar-nav" @click="menuOpen = false">
              <template v-if="authStore.isLoggedIn">
                <li class="nav-item">
                  <NuxtLink to="/change-password" class="nav-link">
                    <i class="bi bi-key me-1"></i>改密
                  </NuxtLink>
                </li>
                <li class="nav-item">
                  <a href="#" class="nav-link" @click.prevent="handleLogout">
                    <i class="bi bi-box-arrow-right me-1"></i>退出
                  </a>
                </li>
              </template>
              <template v-else>
                <li class="nav-item">
                  <NuxtLink to="/login" class="nav-link" :class="{ active: isActive('/login') }">
                    <i class="bi bi-person-circle me-1"></i>登录
                  </NuxtLink>
                </li>
              </template>
            </ul>
          </div>
        </div>
      </nav>
    </header>

    <div ref="scrollRef" class="scroll-content">
      <main class="heritage-main">
        <div class="container container-paper">
          <div v-if="flashStore.messages.length" class="flash-area mb-3">
            <div
              v-for="(msg, idx) in flashStore.messages"
              :key="idx"
              :class="['alert', `alert-${msg.category}`, 'alert-dismissible', 'fade', 'show', 'heritage-alert']"
              role="alert"
            >
              {{ msg.text }}
              <button type="button" class="btn-close" aria-label="关闭" @click="flashStore.dismiss(idx)"></button>
            </div>
          </div>
          <slot />
        </div>
      </main>

      <footer class="heritage-footer">
        <div class="container">
          <div class="footer-brand">屈氏宗谱</div>
          <div class="footer-inner">
            <span class="footer-divider">·</span>
            <span>慎终追远</span>
            <span class="footer-divider">·</span>
            <span>民德归厚</span>
            <span class="footer-divider">·</span>
            <span>传承家脉</span>
            <span class="footer-divider">·</span>
          </div>
          <div class="footer-links">
            <NuxtLink to="/genealogy">族谱库</NuxtLink>
            <NuxtLink to="/culture/zibei">字辈查询</NuxtLink>
            <NuxtLink to="/culture/relationship">亲缘查询</NuxtLink>
            <NuxtLink to="/culture">屈氏文化</NuxtLink>
            <NuxtLink to="/wiki">百科</NuxtLink>
            <NuxtLink to="/news">动态</NuxtLink>
            <NuxtLink to="/culture/contact">联系我们</NuxtLink>
          </div>
          <div class="footer-copy">
            路漫漫其修远兮，吾将上下而求索 —— 屈原《离骚》
          </div>
          <div class="footer-copyright">
            &copy; 2026-2030 quxiangshun. All rights reserved.
          </div>
        </div>
      </footer>
    </div>

    <MobileTabBar />
  </div>
</template>

<script setup lang="ts">
const route = useRoute()
const authStore = useAuthStore()
const flashStore = useFlashStore()

const headerRef = ref<HTMLElement | null>(null)
const scrollRef = ref<HTMLElement | null>(null)
const menuOpen = ref(false)

watch(() => route.path, () => { menuOpen.value = false })
watch(menuOpen, (open) => {
  if (typeof document !== 'undefined') {
    document.body.classList.toggle('menu-open', open)
  }
})

function isActive(path: string) {
  return route.path === path
}

const isGenealogyActive = computed(() => route.path.startsWith('/genealogy'))
const isCultureActive = computed(() =>
  route.path === '/culture' || route.path === '/culture/contact'
)
const isWikiActive = computed(() => route.path.startsWith('/wiki') && !route.path.includes('/admin'))
const isNewsActive = computed(() => route.path.startsWith('/news') && !route.path.includes('/admin'))

function handleLogout() {
  authStore.logout()
  navigateTo('/')
}

onMounted(() => {
  authStore.init()
  const hdr = headerRef.value
  if (!hdr) return
  const cls = 'scrolled'
  const scrollEl = scrollRef.value
  function check() {
    const y = scrollEl ? scrollEl.scrollTop : window.scrollY
    if (y > 30) {
      hdr.classList.add(cls)
    } else {
      hdr.classList.remove(cls)
    }
  }
  if (scrollEl) {
    scrollEl.addEventListener('scroll', check, { passive: true })
  }
  window.addEventListener('scroll', check, { passive: true })
  check()
})
</script>
