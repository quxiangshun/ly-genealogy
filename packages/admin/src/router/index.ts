import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = createRouter({
  history: createWebHistory('/admin/'),
  routes: [
    {
      path: '/login',
      name: 'Login',
      component: () => import('../views/Login.vue'),
      meta: { public: true },
    },
    {
      path: '/',
      component: () => import('../components/AdminLayout.vue'),
      redirect: '/dashboard',
      meta: { requiresAuth: true },
      children: [
        {
          path: 'dashboard',
          name: 'Dashboard',
          component: () => import('../views/Dashboard.vue'),
        },
        {
          path: 'genealogy',
          name: 'GenealogyList',
          component: () => import('../views/genealogy/List.vue'),
        },
        {
          path: 'genealogy/add',
          name: 'GenealogyAdd',
          component: () => import('../views/genealogy/Form.vue'),
        },
        {
          path: 'genealogy/:id/edit',
          name: 'GenealogyEdit',
          component: () => import('../views/genealogy/Form.vue'),
        },
        {
          path: 'genealogy/:id/generations',
          name: 'GenealogyGenerations',
          component: () => import('../views/genealogy/Generations.vue'),
        },
        {
          path: 'genealogy/:id/members',
          name: 'GenealogyMembers',
          component: () => import('../views/genealogy/Members.vue'),
        },
        {
          path: 'member',
          name: 'MemberList',
          component: () => import('../views/member/List.vue'),
        },
        {
          path: 'member/query',
          name: 'MemberQuery',
          component: () => import('../views/member/Query.vue'),
        },
        {
          path: 'member/add',
          name: 'MemberAdd',
          component: () => import('../views/member/Form.vue'),
        },
        {
          path: 'member/:id',
          name: 'MemberEdit',
          component: () => import('../views/member/Form.vue'),
        },
        {
          path: 'change-password',
          name: 'ChangePasswordInLayout',
          component: () => import('../views/ChangePassword.vue'),
        },
        {
          path: 'wiki',
          name: 'WikiList',
          component: () => import('../views/wiki/List.vue'),
        },
        {
          path: 'wiki/add',
          name: 'WikiAdd',
          component: () => import('../views/wiki/Form.vue'),
        },
        {
          path: 'wiki/:id/edit',
          name: 'WikiEdit',
          component: () => import('../views/wiki/Form.vue'),
        },
        {
          path: 'news',
          name: 'NewsList',
          component: () => import('../views/news/List.vue'),
        },
        {
          path: 'news/add',
          name: 'NewsAdd',
          component: () => import('../views/news/Form.vue'),
        },
        {
          path: 'news/:id/edit',
          name: 'NewsEdit',
          component: () => import('../views/news/Form.vue'),
        },
      ],
    },
  ],
})

router.beforeEach((to, _from, next) => {
  const auth = useAuthStore()
  const requiresAuth = to.matched.some((r) => r.meta.requiresAuth)
  const isPublic = to.matched.some((r) => r.meta.public)

  if (requiresAuth && !auth.isLoggedIn) {
    next({ path: '/login', query: { redirect: to.fullPath } })
  } else if (auth.isLoggedIn && auth.mustChangePassword && to.path !== '/change-password') {
    next({ path: '/change-password' })
  } else if (isPublic && auth.isLoggedIn && to.path === '/login') {
    next({ path: '/dashboard' })
  } else {
    next()
  }
})

export default router
