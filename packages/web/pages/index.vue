<template>
  <div>
    <!-- Hero -->
    <div class="hero-section">
      <p class="heritage-subtitle mb-3">慎终追远 · 民德归厚</p>
      <h1 class="display-5 mb-2">屈氏宗谱</h1>
      <p class="lead text-muted mb-0">屈氏宗亲族谱与文化传承</p>
      <p class="text-muted small mb-0">按地区、年代检索屈氏族谱 · 字辈表 · 世系树 · 成员查询</p>
      <div class="heritage-divider" />
    </div>

    <!-- Stats -->
    <div class="stats-banner">
      <div class="stats-grid">
        <div class="stat-item in-view">
          <span class="stat-number">{{ stats?.genealogyCount ?? 0 }}</span>
          <span class="stat-unit">部</span>
          <span class="stat-label">收录族谱</span>
        </div>
        <div class="stat-divider" />
        <div class="stat-item in-view">
          <span class="stat-number">{{ stats?.memberCount ?? 0 }}</span>
          <span class="stat-unit">人</span>
          <span class="stat-label">宗亲成员</span>
        </div>
        <div class="stat-divider" />
        <div class="stat-item in-view">
          <span class="stat-number">{{ stats?.generationCount ?? 0 }}</span>
          <span class="stat-unit">字</span>
          <span class="stat-label">字辈收录</span>
        </div>
        <div class="stat-divider" />
        <div class="stat-item in-view">
          <span class="stat-number">{{ stats?.regions?.length ?? 0 }}</span>
          <span class="stat-unit">地</span>
          <span class="stat-label">覆盖地区</span>
        </div>
      </div>
    </div>

    <!-- Entry Cards -->
    <div class="home-entry-grid">
      <NuxtLink to="/genealogy" class="home-entry-card">
        <div class="entry-icon">谱</div>
        <div class="entry-title">族谱库</div>
        <div class="entry-desc">按地区、年代检索收录族谱</div>
      </NuxtLink>
      <NuxtLink to="/culture/zibei" class="home-entry-card">
        <div class="entry-icon">辈</div>
        <div class="entry-title">字辈查询</div>
        <div class="entry-desc">输入辈字查找所属族谱</div>
      </NuxtLink>
      <NuxtLink to="/culture" class="home-entry-card">
        <div class="entry-icon">文</div>
        <div class="entry-title">屈氏文化</div>
        <div class="entry-desc">屈姓起源、郡望堂号</div>
      </NuxtLink>
      <NuxtLink to="/wiki" class="home-entry-card">
        <div class="entry-icon">典</div>
        <div class="entry-title">屈氏百科</div>
        <div class="entry-desc">名人、堂号、礼俗知识库</div>
      </NuxtLink>
      <NuxtLink to="/news" class="home-entry-card">
        <div class="entry-icon">闻</div>
        <div class="entry-title">新闻动态</div>
        <div class="entry-desc">宗亲活动、历史事件</div>
      </NuxtLink>
      <NuxtLink to="/culture/contact" class="home-entry-card">
        <div class="entry-icon">联</div>
        <div class="entry-title">联系我们</div>
        <div class="entry-desc">寻根问祖、提供资料</div>
      </NuxtLink>
    </div>

    <!-- Origin -->
    <div class="heritage-section-divider"><span>屈氏渊源</span></div>
    <div class="origin-section">
      <div class="row g-4">
        <div class="col-lg-7">
          <div class="origin-card">
            <div class="origin-card-deco">源</div>
            <h4 class="origin-title">屈姓溯源</h4>
            <p>屈姓源出有二：其一出自芈姓，为春秋时楚国莫敖之后，以封地名为氏。楚武王熊通之子瑕受封于屈邑（今湖北秭归），其后世以邑名为氏，是为屈氏正宗。</p>
            <p class="mb-0">其二出自北魏时期鲜卑族屈突氏，后汉化改姓为屈。屈氏族人历经数千年繁衍，遍布华夏大地，以湖南、陕西、贵州、湖北等地为盛。</p>
            <div class="origin-tags">
              <span class="origin-tag"><i class="bi bi-geo-alt"></i> 发源地：湖北秭归</span>
              <span class="origin-tag"><i class="bi bi-calendar3"></i> 始于：春秋时期</span>
              <span class="origin-tag"><i class="bi bi-bookmark"></i> 始祖：屈瑕</span>
            </div>
          </div>
        </div>
        <div class="col-lg-5">
          <div class="origin-card origin-card-highlight">
            <div class="origin-card-deco">堂</div>
            <h4 class="origin-title">郡望堂号</h4>
            <div class="hall-list">
              <div class="hall-item">
                <span class="hall-name">临海郡</span>
                <span class="hall-note">三国吴太平二年置</span>
              </div>
              <div class="hall-item">
                <span class="hall-name">河南郡</span>
                <span class="hall-note">汉高帝二年改秦三川郡置</span>
              </div>
              <div class="hall-item">
                <span class="hall-name">三闾堂</span>
                <span class="hall-note">屈原任三闾大夫而得名</span>
              </div>
              <div class="hall-item">
                <span class="hall-name">敦睦堂</span>
                <span class="hall-note">敦亲睦族之义</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Famous -->
    <div class="heritage-section-divider"><span>屈氏名人</span></div>
    <div class="famous-section">
      <div class="row g-3">
        <div class="col-md-4">
          <div class="famous-card">
            <div class="famous-era">战国</div>
            <h5 class="famous-name">屈 原</h5>
            <p class="famous-title">三闾大夫 · 爱国诗人</p>
            <p class="famous-desc">中国最伟大的浪漫主义诗人之一，创立了"楚辞"文体。代表作《离骚》《天问》《九歌》等，被誉为"中华诗祖"。</p>
            <div class="famous-quote">"路漫漫其修远兮，吾将上下而求索"</div>
          </div>
        </div>
        <div class="col-md-4">
          <div class="famous-card">
            <div class="famous-era">春秋</div>
            <h5 class="famous-name">屈 瑕</h5>
            <p class="famous-title">楚国莫敖 · 屈氏始祖</p>
            <p class="famous-desc">楚武王之子，受封于屈邑，为屈氏得姓始祖。官至莫敖（楚国最高军事官职之一），多次率师征战。</p>
            <div class="famous-quote">屈氏开族之祖，薪火相传数千年</div>
          </div>
        </div>
        <div class="col-md-4">
          <div class="famous-card">
            <div class="famous-era">唐代</div>
            <h5 class="famous-name">屈突通</h5>
            <p class="famous-title">凌烟阁功臣 · 蒋国公</p>
            <p class="famous-desc">唐朝开国名将，凌烟阁二十四功臣之一。历仕隋唐两朝，以忠勇著称，封蒋国公，谥号"忠"。</p>
            <div class="famous-quote">忠勇双全，名列凌烟阁二十四功臣</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Quick Search Tags -->
    <template v-if="stats?.surnames?.length || stats?.regions?.length">
      <div class="heritage-section-divider"><span>快速检索</span></div>
      <div class="search-section">
        <div v-if="stats?.surnames?.length" class="search-group">
          <span class="search-group-label"><i class="bi bi-person-vcard me-1"></i>按姓氏</span>
          <div class="search-tags">
            <NuxtLink
              v-for="s in stats.surnames"
              :key="s"
              :to="`/genealogy?surname=${s}`"
              class="search-tag"
            >{{ s }}氏</NuxtLink>
          </div>
        </div>
        <div v-if="stats?.regions?.length" class="search-group">
          <span class="search-group-label"><i class="bi bi-geo-alt me-1"></i>按地区</span>
          <div class="search-tags">
            <NuxtLink
              v-for="r in stats.regions"
              :key="r"
              :to="`/genealogy?region=${r}`"
              class="search-tag search-tag-region"
            >{{ r }}</NuxtLink>
          </div>
        </div>
      </div>
    </template>

    <!-- Recent Genealogies -->
    <template v-if="stats?.recentGenealogies?.length">
      <div class="heritage-section-divider"><span>近期收录</span></div>
      <div class="row g-3">
        <div
          v-for="g in stats.recentGenealogies"
          :key="g.id"
          class="col-md-6 col-lg-4"
        >
          <div class="card heritage-card h-100">
            <div class="card-body">
              <div class="d-flex align-items-start justify-content-between mb-2">
                <h6 class="mb-0 flex-grow-1">
                  <NuxtLink :to="`/genealogy/${g.id}`">{{ g.genealogy_name }}</NuxtLink>
                </h6>
                <span v-if="g.hall_name" class="genealogy-hall-badge">{{ g.hall_name }}</span>
              </div>
              <div class="d-flex flex-wrap gap-2 mb-2">
                <span v-if="g.region" class="badge" style="background:rgba(176,138,80,0.15);color:var(--heritage-accent)">
                  <i class="bi bi-geo-alt me-1"></i>{{ g.region }}
                </span>
                <span v-if="g.period" class="badge" style="background:rgba(139,58,46,0.1);color:var(--heritage-red)">
                  <i class="bi bi-clock-history me-1"></i>{{ g.period }}
                </span>
              </div>
              <p v-if="g.description" class="card-text small text-muted mb-2" style="display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;">
                {{ g.description?.slice(0, 80) }}
              </p>
              <p v-if="g.scattered_region" class="card-text small mb-2" style="color:var(--heritage-ink-muted)">
                <i class="bi bi-signpost-split me-1"></i>散居：{{ g.scattered_region?.slice(0, 40) }}
              </p>
              <div class="d-flex gap-2 mt-auto">
                <NuxtLink :to="`/genealogy/${g.id}`" class="btn btn-sm btn-outline-primary flex-grow-1">
                  <i class="bi bi-eye me-1"></i>查看
                </NuxtLink>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="text-center mt-3">
        <NuxtLink to="/genealogy" class="btn btn-primary">
          <i class="bi bi-collection me-1"></i>查看全部族谱
        </NuxtLink>
      </div>
    </template>

    <!-- Recent News -->
    <template v-if="stats?.recentNews?.length">
      <div class="heritage-section-divider"><span>最新动态</span></div>
      <div class="news-home-list">
        <NuxtLink
          v-for="art in stats.recentNews"
          :key="art.id"
          :to="`/news/${art.slug}`"
          class="news-home-item"
        >
          <span class="news-home-date">{{ formatDate(art.event_date || art.create_time) }}</span>
          <span class="news-home-cat">{{ art.category || '' }}</span>
          <span class="news-home-title">
            <i v-if="art.is_pinned" class="bi bi-pin-angle-fill text-danger me-1"></i>
            {{ art.title }}
          </span>
        </NuxtLink>
        <div class="text-center mt-3">
          <NuxtLink to="/news" class="btn btn-outline-primary btn-sm">
            查看全部动态 <i class="bi bi-arrow-right ms-1"></i>
          </NuxtLink>
        </div>
      </div>
    </template>

    <!-- Quotes -->
    <div class="heritage-section-divider"><span>传世名句</span></div>
    <div class="quotes-section">
      <div class="row g-3">
        <div class="col-md-6">
          <div class="heritage-quote">
            "亦余心之所善兮，虽九死其犹未悔。"<br>
            <span class="quote-source">—— 屈原《离骚》</span>
          </div>
        </div>
        <div class="col-md-6">
          <div class="heritage-quote">
            "长太息以掩涕兮，哀民生之多艰。"<br>
            <span class="quote-source">—— 屈原《离骚》</span>
          </div>
        </div>
        <div class="col-md-6">
          <div class="heritage-quote">
            "举世皆浊我独清，众人皆醉我独醒。"<br>
            <span class="quote-source">—— 屈原《渔父》</span>
          </div>
        </div>
        <div class="col-md-6">
          <div class="heritage-quote">
            "吾不能变心以从俗兮，固将愁苦而终穷。"<br>
            <span class="quote-source">—— 屈原《涉江》</span>
          </div>
        </div>
      </div>
    </div>

    <!-- About -->
    <div class="heritage-section-divider"><span>关于本站</span></div>
    <div class="about-section">
      <div class="row g-4 align-items-center">
        <div class="col-md-8">
          <p>本站为<strong>屈氏宗谱与文化平台</strong>，致力于收录整理各地屈氏族谱，展现屈氏历史渊源与文化传承。平台涵盖族谱检索、世系树查看、成员关系查询、字辈表查阅等功能。</p>
          <p class="mb-0">系统保留多姓氏管理接口，可拓展收录其他姓氏族谱。</p>
        </div>
        <div class="col-md-4">
          <div class="about-features">
            <div class="about-feature"><i class="bi bi-book"></i><span>族谱数字化存档</span></div>
            <div class="about-feature"><i class="bi bi-diagram-3"></i><span>可视化世系树</span></div>
            <div class="about-feature"><i class="bi bi-search"></i><span>智能亲属查询</span></div>
            <div class="about-feature"><i class="bi bi-shield-check"></i><span>隐私信息保护</span></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const config = useRuntimeConfig()

const { data: stats } = useLazyFetch<Record<string, unknown>>(
  `${config.public.apiBase}/api/stats`,
  { key: 'home-stats', server: false }
)

function formatDate(t: string | undefined) {
  if (!t) return ''
  return t.slice(5, 10)
}

const animSelector = '.origin-card, .famous-card, .stat-item, .about-feature, .search-group'
let observer: IntersectionObserver | null = null

function observeNewElements() {
  nextTick(() => {
    if (!observer) return
    document.querySelectorAll(animSelector).forEach((el) => {
      if (!el.classList.contains('in-view')) {
        observer!.observe(el)
      }
    })
  })
}

onMounted(() => {
  observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add('in-view')
        observer?.unobserve(entry.target)
      }
    })
  }, { threshold: 0.15 })

  observeNewElements()
})

watch(stats, () => { observeNewElements() })

useHead({
  title: '首页 - 屈氏宗谱',
  meta: [
    {
      name: 'description',
      content: '屈氏宗谱官网：屈氏宗亲族谱与文化传承，按地区年代检索屈氏族谱，字辈表、成员查询、世系树，屈氏文化。',
    },
  ],
})
</script>
