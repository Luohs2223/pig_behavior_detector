<template>
  <div class="auth-container">
    <div class="auth-card">
      <h2>登录</h2>
      <form @submit.prevent="handleLogin">
        <input type="text" v-model="username" placeholder="用户名" required />
        <input type="password" v-model="password" placeholder="密码" required />
        <button type="submit">登录</button>
        <p>没有账号？ <router-link to="/register">立即注册</router-link></p>
      </form>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  data() {
    return {
      username: '',
      password: ''
    }
  },
  methods: {
    async handleLogin() {
        try {
            const res = await axios.post('/api/login', {
            username: this.username,
            password: this.password
            })
            localStorage.setItem('token', res.data.token)
            localStorage.setItem('userId', res.data.user_id)
            localStorage.setItem('username', res.data.username)
            
            // 手动触发 storage 事件，立即更新 App.vue 的登录状态
            window.dispatchEvent(new Event('storage'))
            
            this.$router.push('/')
        } catch (err) {
            alert(err.response?.data?.error || '登录失败')
        }
    }
  }
}
</script>

<style scoped>
.auth-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 80vh;
}
.auth-card {
  background: #F9F5ED;
  border-radius: 20px;
  padding: 40px;
  width: 320px;
  border: 1px solid #EADBC8;
}
.auth-card h2 {
  text-align: center;
  margin-bottom: 24px;
  color: #4A3728;
}
.auth-card input {
  width: 100%;
  padding: 10px;
  margin-bottom: 16px;
  border: 1px solid #E2D4C4;
  border-radius: 40px;
  outline: none;
}
.auth-card button {
  width: 100%;
  background: #C47B59;
  color: white;
  border: none;
  padding: 10px;
  border-radius: 40px;
  cursor: pointer;
}
.auth-card button:hover {
  background: #AF6747;
}
</style>