<template>
  <el-container class="admin-layout" direction="vertical">
    <el-header class="admin-header">
      <div class="header-left">
        <span class="logo" @click="$router.push('/dashboard')">屈氏宗谱管理</span>
        <el-menu
          v-if="!auth.mustChangePassword"
          :default-active="activeMenu"
          mode="horizontal"
          class="admin-menu"
          background-color="transparent"
          text-color="#e8dcc8"
          active-text-color="#d4b06a"
          @select="handleMenuSelect"
        >
          <el-menu-item index="dashboard">
            <el-icon><DataLine /></el-icon>仪表盘
          </el-menu-item>
          <el-menu-item index="genealogy">
            <el-icon><Collection /></el-icon>族谱管理
          </el-menu-item>
          <el-menu-item index="member">
            <el-icon><User /></el-icon>成员管理
          </el-menu-item>
          <el-menu-item index="wiki">
            <el-icon><Document /></el-icon>百科管理
          </el-menu-item>
          <el-menu-item index="news">
            <el-icon><Promotion /></el-icon>新闻管理
          </el-menu-item>
        </el-menu>
        <span v-else class="pwd-lock-hint">请先修改默认密码</span>
      </div>
      <div class="header-right">
        <el-dropdown trigger="click" @command="handleCommand">
          <span class="username-trigger">
            <el-icon><UserFilled /></el-icon>
            {{ auth.username || '管理员' }}
            <el-icon class="el-icon--right"><ArrowDown /></el-icon>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="change-password">
                <el-icon><Key /></el-icon>修改密码
              </el-dropdown-item>
              <el-dropdown-item command="logout" divided>
                <el-icon><SwitchButton /></el-icon>退出登录
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </el-header>
    <el-main class="admin-main">
      <router-view />
    </el-main>
  </el-container>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  DataLine, Collection, Document, Promotion, User,
  UserFilled, ArrowDown, Key, SwitchButton,
} from '@element-plus/icons-vue'
import { useAuthStore } from '../stores/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const activeMenu = computed(() => {
  const p = route.path
  if (p.startsWith('/genealogy')) return 'genealogy'
  if (p.startsWith('/member')) return 'member'
  if (p.startsWith('/wiki')) return 'wiki'
  if (p.startsWith('/news')) return 'news'
  if (p.startsWith('/dashboard')) return 'dashboard'
  return ''
})

function handleMenuSelect(index: string) {
  router.push('/' + index)
}

function handleCommand(cmd: string) {
  if (cmd === 'logout') {
    auth.logout()
    router.push('/login')
  } else if (cmd === 'change-password') {
    router.push('/change-password')
  }
}
</script>

<style scoped>
.admin-layout {
  min-height: 100vh;
  background-color: var(--admin-bg);
}

.admin-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: linear-gradient(180deg, rgba(35,24,8,0.92) 0%, rgba(50,36,18,0.88) 100%);
  backdrop-filter: blur(16px) saturate(180%);
  -webkit-backdrop-filter: blur(16px) saturate(180%);
  padding: 0 20px;
  height: 56px;
  box-shadow: 0 2px 16px rgba(28,23,8,0.3);
  border-bottom: 1px solid rgba(156,118,56,0.25);
  z-index: 100;
  position: sticky;
  top: 0;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 0;
  height: 100%;
}

.logo {
  font-family: var(--font-title);
  font-size: 17px;
  font-weight: 700;
  color: var(--admin-gold-bright);
  white-space: nowrap;
  margin-right: 24px;
  letter-spacing: 0.12em;
  cursor: pointer;
  text-shadow: 0 1px 2px rgba(0,0,0,0.3);
}

.admin-menu {
  border-bottom: none !important;
  height: 56px;
}

.admin-menu :deep(.el-menu-item) {
  height: 56px;
  line-height: 56px;
  font-size: 14px;
  border-bottom: 2px solid transparent;
  transition: border-color 0.25s, color 0.2s;
}

.admin-menu :deep(.el-menu-item:hover) {
  background-color: rgba(156,118,56,0.12) !important;
}

.admin-menu :deep(.el-menu-item.is-active) {
  border-bottom-color: var(--admin-gold-bright);
  background-color: rgba(156,118,56,0.1) !important;
}

.header-right {
  display: flex;
  align-items: center;
}

.username-trigger {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: #e8dcc8;
  font-size: 14px;
  cursor: pointer;
  transition: color 0.2s;
  padding: 4px 8px;
  border-radius: 4px;
}

.username-trigger:hover {
  color: var(--admin-gold-bright);
  background: rgba(156,118,56,0.12);
}

.admin-main {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}

.pwd-lock-hint {
  color: var(--admin-gold-bright);
  font-size: 13px;
  letter-spacing: 0.04em;
}
</style>
