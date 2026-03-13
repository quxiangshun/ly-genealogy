export default defineNuxtConfig({
  compatibilityDate: '2025-01-01',
  ssr: true,
  modules: ['@pinia/nuxt'],
  css: [
    'bootstrap/dist/css/bootstrap.min.css',
    'bootstrap-icons/font/bootstrap-icons.css',
    '~/assets/css/main.css',
  ],
  app: {
    head: {
      htmlAttrs: { lang: 'zh-CN' },
      meta: [
        { charset: 'utf-8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1, maximum-scale=5, viewport-fit=cover' },
        { name: 'theme-color', content: '#2c1e0e' },
        { name: 'keywords', content: '屈氏,屈氏族谱,屈氏宗谱,字辈,族谱,家谱,屈原' },
        { name: 'format-detection', content: 'telephone=no' },
        { name: 'apple-mobile-web-app-capable', content: 'yes' },
        { name: 'apple-mobile-web-app-status-bar-style', content: 'black-translucent' },
        { name: 'apple-mobile-web-app-title', content: '屈氏宗谱' },
        { property: 'og:type', content: 'website' },
        { property: 'og:site_name', content: '屈氏宗谱' },
        { property: 'og:title', content: '屈氏宗谱 - 屈氏宗亲族谱与文化传承' },
        { property: 'og:description', content: '屈氏宗亲族谱与文化传承，按地区年代检索屈氏族谱，字辈表、成员查询、世系树。' },
      ],
      link: [
        { rel: 'icon', type: 'image/svg+xml', href: '/favicon.svg' },
        { rel: 'preconnect', href: 'https://fonts.googleapis.com' },
        { rel: 'preconnect', href: 'https://fonts.gstatic.com', crossorigin: '' },
        { rel: 'stylesheet', href: 'https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;600;700&family=ZCOOL+XiaoWei&display=swap' },
        { rel: 'manifest', href: '/manifest.json' },
        { rel: 'apple-touch-icon', href: '/favicon.svg' },
      ],
      script: [
        { src: 'https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js', defer: true },
      ],
    },
  },
  runtimeConfig: {
    public: {
      apiBase: process.env.API_BASE || '',
      siteName: '屈氏宗谱',
    },
  },
  routeRules: {
    '/api/**': { proxy: 'http://localhost:5001/api/**' },
    '/uploads/**': { proxy: 'http://localhost:5001/uploads/**' },
    '/': { swr: 3600 },
    '/genealogy/**': { swr: 1800 },
    '/wiki/**': { swr: 600 },
    '/news/**': { swr: 600 },
    '/culture': { swr: 3600 },
    '/culture/contact': { swr: 3600 },
    '/login': { ssr: false },
    '/change-password': { ssr: false },
  },
  nitro: {
    devProxy: {
      '/api': { target: 'http://localhost:5001/api', changeOrigin: true },
      '/uploads': { target: 'http://localhost:5001/uploads', changeOrigin: true },
    },
  },
  devtools: { enabled: false },
})
