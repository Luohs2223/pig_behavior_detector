import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import axios from 'axios'

//本机
axios.defaults.baseURL = 'http://127.0.0.1:5000' 
//服务器
// axios.defaults.baseURL = axios.defaults.baseURL = 'http://134.175.7.233'

// 请求拦截器：自动添加 token
axios.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
}, error => {
  return Promise.reject(error)
})

// 响应拦截器：处理 401 未授权，清除 token 并跳转登录
axios.interceptors.response.use(response => {
  return response
}, error => {
  if (error.response && error.response.status === 401) {
    localStorage.removeItem('token')
    localStorage.removeItem('userId')
    localStorage.removeItem('username')
    router.push('/login')
  }
  return Promise.reject(error)
})

createApp(App).use(router).use(ElementPlus).mount('#app')