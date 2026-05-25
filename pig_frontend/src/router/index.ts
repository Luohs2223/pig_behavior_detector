import { createRouter, createWebHistory } from 'vue-router'
import Upload from '../views/Upload.vue'
import History from '../views/History.vue'
import RecordDetail from '../views/RecordDetail.vue'
import Register from '../views/Register.vue'
import Login from '../views/Login.vue'  
import VideoUpload from '../views/VideoUpload.vue'  
import VideoHistory from '../views/VideoHistory.vue'
import VideoRecordDetail from '../views/VideoRecordDetail.vue'

const routes = [
  { path: '/', name: 'Upload', component: Upload, meta: { requiresAuth: true } },
  { path: '/history', name: 'History', component: History, meta: { requiresAuth: true } },
  { path: '/record/:id', name: 'RecordDetail', component: RecordDetail, meta: { requiresAuth: true } },
  { path: '/video-upload', name: 'VideoUpload', component: VideoUpload, meta: { requiresAuth: true } },
  { path: '/register', name: 'Register', component: Register },
  { path: '/login', name: 'Login', component: Login },
  { path: '/video-history', name: 'VideoHistory', component: VideoHistory, meta: { requiresAuth: true } },
  { path: '/video-record/:id', name: 'VideoRecordDetail', component: VideoRecordDetail, meta: { requiresAuth: true } }
]


const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫：检查是否需要登录
router.beforeEach((to, from) => {
  const token = localStorage.getItem('token')
  
  // 如果目标路由需要登录 (requiresAuth 为 true) 且用户未登录
  if (to.meta.requiresAuth && !token) {
    // 直接返回登录页面的路由地址，而不是调用 next()
    return '/login'
  }
  
  // 如果已登录且要访问登录/注册页面，则重定向到首页
  if (token && (to.path === '/login' || to.path === '/register')) {
    return '/'
  }
  
  // 其他情况，继续导航
  return true
})

export default router