<template>
  <div id="app">
    <!-- 顶部导航栏 -->
    <div class="navbar">
      <div class="nav-inner">
        <!-- 左侧导航链接 -->
        <div class="nav-links">
          <HoverDropdown title="上传" :items=" [
            { label: '图片上传', path: '/' },
            { label: '视频上传', path: '/video-upload' }
          ]" />
          <span class="nav-divider">|</span>
          <HoverDropdown title="历史记录" :items="[
            { label: '图片历史记录', path: '/history' },
            { label: '视频历史记录', path: '/video-history' }
          ]" />
        </div>
        <!-- 右侧用户信息或登录入口 -->
        <div class="user-info" v-if="isLoggedIn">
          <span class="username">{{ username }}</span>
          <button @click="logout" class="logout-btn">退出</button>
        </div>
        <div class="user-info" v-else>
          <router-link to="/login" class="login-link">登录</router-link>
        </div>
      </div>
    </div>

    <div class="container">
      <!-- 主标题区域（仅在上传页显示，且不在登录/注册页显示） -->
      <router-view v-slot="{ Component, route }">
        <div v-if="route.path === '/'">
          <div class="hero">
            <h1>上传猪舍图片进行行为检测</h1>
            <p>上传生猪图片，AI 自动识别站立、躺卧、进食、饮水、趴伏、走动等行为，助力智慧养殖</p>
          </div>
        </div>
        <component :is="Component" />
      </router-view>

      <!-- 步骤说明卡片（仅在上传页显示） -->
      <div v-if="$route.path === '/'" class="steps">
        <div class="step-card">
          <div class="step-number">1</div>
          <div class="step-title">上传图片</div>
          <div class="step-desc">上传生猪清晰图片，支持JPG/PNG/WebP，单张≤4MB</div>
        </div>
        <div class="step-card">
          <div class="step-number">2</div>
          <div class="step-title">AI分析</div>
          <div class="step-desc">AI智能分析生猪姿态、动作与行为特征</div>
        </div>
        <div class="step-card">
          <div class="step-number">3</div>
          <div class="step-title">获取结果</div>
          <div class="step-desc">1秒输出行为识别结果与置信度评分</div>
        </div>
      </div>

      <!-- 步骤说明卡片（仅在视频上传页显示） -->
      <div v-if="$route.path === '/video-upload'" class="steps">
        <div class="step-card">
          <div class="step-number">1</div>
          <div class="step-title">上传视频</div>
          <div class="step-desc">上传生猪视频，支持MP4/AVI/MOV/MKV</div>
        </div>
        <div class="step-card">
          <div class="step-number">2</div>
          <div class="step-title">异常行为报警</div>
          <div class="step-title">（每2秒抽帧一次进行行为判定）</div>
          <div class="step-desc">监控饮食废绝、长时间躺卧无行为等异常</div>
        </div>
        <div class="step-card">
          <div class="step-number">3</div>
          <div class="step-title">ai分析</div>
          <div class="step-desc">基于AI分析结果，提供专业的养殖建议</div>
        </div>
      </div>

      <!-- 底部提示栏（登录/注册页隐藏） -->
      <div v-if="$route.path !== '/login' && $route.path !== '/register'" class="footer-note">
        <p>识别结果为AI智能判断，仅供养殖参考使用</p>
        <p>建议结合现场观察、养殖环境与人工复核使用</p>
      </div>
    </div>
  </div>
</template>

<script>
import HoverDropdown from './components/HoverDropdown.vue'
export default {
  components: {
    HoverDropdown
  },
  data() {
    return {
      isLoggedIn: false,
      username: '',
    }
  },
  mounted() {
    this.checkLogin()
    window.addEventListener('storage', this.checkLogin)
  },
  beforeUnmount() {
    window.removeEventListener('storage', this.checkLogin)
  },
  methods: {
    checkLogin() {
      const token = localStorage.getItem('token')
      const user = localStorage.getItem('username')
      this.isLoggedIn = !!token
      this.username = user || ''
    },
    logout() {
      localStorage.removeItem('token')
      localStorage.removeItem('userId')
      localStorage.removeItem('username')
      this.checkLogin()
      this.$router.push('/login')
    }
  }
}
</script>

<style>
/* 全局样式 */
:root {
  --bg-primary: #F7F1E3;
  --card-bg: #F9F5ED;
  --border-color: #EADBC8;
  --accent: #C47B59;
  --text-main: #4A3728;
  --text-muted: #7D6A5C;
}
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}
body {
  background-color: var(--bg-primary);
  font-family: 'Inter', system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif;
  color: var(--text-main);
}
.container {
  max-width: 1280px;
  margin: 0 auto;
  padding: 0 24px;
}
#app {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.navbar {
  width: 100%;
  background: var(--card-bg);
  border-bottom: 1px solid var(--border-color);
  padding: 16px 0;
}
.nav-inner {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}
.nav-links {
  display: flex;
  gap: 24px;
  font-weight: 500;
}
.nav-link {
  color: var(--text-muted);
  text-decoration: none;
  transition: color 0.2s;
}
.nav-link:hover, .router-link-active {
  color: var(--accent);
}
.nav-divider {
  color: #DCCBB8;
}
.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}
.username {
  color: var(--text-main);
  font-weight: 500;
}
.logout-btn {
  background: none;
  border: 1px solid var(--accent);
  border-radius: 20px;
  padding: 4px 12px;
  cursor: pointer;
  color: var(--accent);
  transition: 0.2s;
}
.logout-btn:hover {
  background: var(--accent);
  color: white;
}
.login-link {
  color: var(--accent);
  text-decoration: none;
  font-weight: 500;
  border: 1px solid var(--accent);
  border-radius: 20px;
  padding: 4px 12px;
  transition: 0.2s;
}
.login-link:hover {
  background: var(--accent);
  color: white;
}
.hero {
  text-align: center;
  margin: 48px 0 32px;
}
.hero h1 {
  font-size: 2rem;
  font-weight: 600;
  color: var(--text-main);
}
.hero p {
  color: var(--text-muted);
  max-width: 560px;
  margin: 12px auto 0;
}
.steps {
  display: flex;
  flex-wrap: wrap;
  gap: 24px;
  margin: 56px 0 48px;
  justify-content: center;
}
.step-card {
  flex: 1;
  min-width: 200px;
  background: var(--card-bg);
  border-radius: 28px;
  padding: 28px 16px 24px;
  text-align: center;
  border: 1px solid var(--border-color);
}
.step-number {
  width: 48px;
  height: 48px;
  background: var(--bg-primary);
  border-radius: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 16px;
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--accent);
  border: 1px solid #EBDBCB;
}
.step-title {
  font-weight: 600;
  font-size: 1.2rem;
  margin-bottom: 10px;
}
.step-desc {
  font-size: 0.85rem;
  color: var(--text-muted);
}
.footer-note {
  background: var(--card-bg);
  border-radius: 24px;
  padding: 24px 28px;
  margin: 32px 0 48px;
  border: 1px solid var(--border-color);
}
.footer-note p:first-child {
  font-weight: 600;
  margin-bottom: 8px;
  text-align: center;
}
.footer-note p:last-child {
  font-size: 0.8rem;
  color: #8F7A68;
  text-align: center;
}
@media (max-width: 760px) {
  .hero h1 { font-size: 1.6rem; }
  .step-card { min-width: 100%; }
  .nav-inner {
    flex-wrap: wrap;
    gap: 12px;
  }
}
</style>