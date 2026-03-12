<template>
  <div>
    <div class="text-center mb-4">
      <p class="heritage-subtitle mb-3">寻亲联谊 · 共修宗谱</p>
      <h1 class="display-5 mb-2" style="letter-spacing: 0.08em">联系我们</h1>
      <p class="lead text-muted mb-0">欢迎各地屈氏宗亲联络交流、提供资料</p>
      <HeritageDivider />
    </div>

    <div class="row g-4">
      <div class="col-lg-7">
        <!-- Contact Info -->
        <div class="card heritage-card mb-4">
          <div class="card-header"><i class="bi bi-telephone me-2"></i>联系方式</div>
          <div class="card-body">
            <div class="contact-list">
              <div class="contact-item">
                <div class="contact-icon"><i class="bi bi-person"></i></div>
                <div>
                  <div class="contact-label">联系人</div>
                  <div class="contact-value">屈想顺</div>
                </div>
              </div>
              <div class="contact-item">
                <div class="contact-icon"><i class="bi bi-envelope"></i></div>
                <div>
                  <div class="contact-label">电子邮箱</div>
                  <div class="contact-value"><a href="mailto:735591110@qq.com">735591110@qq.com</a></div>
                </div>
              </div>
              <div class="contact-item">
                <div class="contact-icon"><i class="bi bi-phone"></i></div>
                <div>
                  <div class="contact-label">联系电话</div>
                  <div class="contact-value"><a href="tel:18262299378">182-6229-9378</a></div>
                </div>
              </div>
              <div class="contact-item">
                <div class="contact-icon"><i class="bi bi-chat-dots"></i></div>
                <div>
                  <div class="contact-label">QQ / 微信</div>
                  <div class="contact-value">735591110</div>
                </div>
              </div>
              <div class="contact-item">
                <div class="contact-icon"><i class="bi bi-geo-alt"></i></div>
                <div>
                  <div class="contact-label">研究中心</div>
                  <div class="contact-value">江苏省苏州市 · 屈氏文化研究中心</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- FAQ -->
        <div class="card heritage-card">
          <div class="card-header"><i class="bi bi-question-circle me-2"></i>常见问题</div>
          <div class="card-body">
            <div class="accordion" id="faqAccordion">
              <div class="accordion-item">
                <h3 class="accordion-header">
                  <button class="accordion-button" type="button" data-bs-toggle="collapse" data-bs-target="#faq1" aria-expanded="true">如何查找我的族谱分支？</button>
                </h3>
                <div id="faq1" class="accordion-collapse collapse show" data-bs-parent="#faqAccordion">
                  <div class="accordion-body">
                    <p class="mb-2">您可以通过以下方式寻找：</p>
                    <ol class="mb-0">
                      <li>使用<NuxtLink to="/culture/zibei">字辈查询</NuxtLink>，输入您名字中的辈字进行匹配</li>
                      <li>在<NuxtLink to="/genealogy">族谱库</NuxtLink>中按地区检索</li>
                      <li>联系我们提供您已知的信息（籍贯、辈字、长辈姓名等），我们协助查找</li>
                    </ol>
                  </div>
                </div>
              </div>
              <div class="accordion-item">
                <h3 class="accordion-header">
                  <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#faq2">如何提供族谱资料？</button>
                </h3>
                <div id="faq2" class="accordion-collapse collapse" data-bs-parent="#faqAccordion">
                  <div class="accordion-body">
                    您可以通过邮件或微信将族谱照片、文字资料、字辈排行等发送给我们。我们会在核实整理后录入平台，并注明资料来源和提供者。
                  </div>
                </div>
              </div>
              <div class="accordion-item">
                <h3 class="accordion-header">
                  <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#faq3">平台上的信息有误怎么办？</button>
                </h3>
                <div id="faq3" class="accordion-collapse collapse" data-bs-parent="#faqAccordion">
                  <div class="accordion-body">
                    如您发现平台上的族谱信息、成员关系、字辈排行等有误，请联系我们说明具体情况和正确信息，我们会尽快核实修正。宗谱数据的准确性依赖各地宗亲的共同维护。
                  </div>
                </div>
              </div>
              <div class="accordion-item">
                <h3 class="accordion-header">
                  <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#faq4">能否收录其他姓氏的族谱？</button>
                </h3>
                <div id="faq4" class="accordion-collapse collapse" data-bs-parent="#faqAccordion">
                  <div class="accordion-body">
                    本平台系统架构支持多姓氏管理，当前以屈氏为主。如有其他姓氏的族谱资料希望收录整理，欢迎联系我们商讨合作。
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="col-lg-5">
        <!-- Expectations -->
        <div class="card heritage-card mb-4">
          <div class="card-header"><i class="bi bi-gift me-2"></i>我们期望收到</div>
          <div class="card-body">
            <div class="expect-list">
              <div class="expect-item">
                <div class="expect-icon"><i class="bi bi-book"></i></div>
                <div>
                  <strong>族谱原件 / 照片</strong>
                  <p class="small text-muted mb-0">纸质族谱的翻拍照片或扫描件</p>
                </div>
              </div>
              <div class="expect-item">
                <div class="expect-icon"><i class="bi bi-list-ol"></i></div>
                <div>
                  <strong>字辈排行</strong>
                  <p class="small text-muted mb-0">您所属支系的完整字辈表</p>
                </div>
              </div>
              <div class="expect-item">
                <div class="expect-icon"><i class="bi bi-diagram-3"></i></div>
                <div>
                  <strong>世系信息</strong>
                  <p class="small text-muted mb-0">家族传承关系、世次、迁徙记录</p>
                </div>
              </div>
              <div class="expect-item">
                <div class="expect-icon"><i class="bi bi-person-badge"></i></div>
                <div>
                  <strong>名人事迹</strong>
                  <p class="small text-muted mb-0">本族历史名人、先贤事迹</p>
                </div>
              </div>
              <div class="expect-item">
                <div class="expect-icon"><i class="bi bi-bug"></i></div>
                <div>
                  <strong>纠错反馈</strong>
                  <p class="small text-muted mb-0">平台内容的错误更正建议</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Privacy -->
        <div class="card heritage-card">
          <div class="card-header"><i class="bi bi-shield-check me-2"></i>隐私与声明</div>
          <div class="card-body">
            <ul class="mb-0 small" style="color:var(--heritage-ink-muted)">
              <li class="mb-2">平台对非登录用户隐藏成员详细信息，仅以脱敏形式展示姓名</li>
              <li class="mb-2">您提供的个人资料仅用于族谱研究，不会用于商业目的</li>
              <li class="mb-2">上传的族谱资料将注明来源和提供者（除非您要求匿名）</li>
              <li>如需删除或修改已录入的个人信息，请随时联系我们</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
useHead({
  title: '联系我们 - 屈氏宗谱',
  meta: [
    {
      name: 'description',
      content: '联系屈氏宗谱平台，提交族谱资料、字辈信息，寻根问祖咨询。',
    },
  ],
})
</script>
