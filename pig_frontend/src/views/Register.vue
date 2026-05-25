<template>
  <div class="auth-container">
    <div class="auth-card">
      <h2>注册</h2>
      <form @submit.prevent="handleRegister">
        <input type="text" v-model="username" placeholder="用户名" required />
        <input type="password" v-model="password" placeholder="密码" required />
        <button type="submit">注册</button>
        <p>已有账号？ <router-link to="/login">立即登录</router-link></p>
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
    async handleRegister() {
      try {
        await axios.post('/api/register', {
          username: this.username,
          password: this.password
        })
        alert('注册成功，请登录')
        this.$router.push('/login')
      } catch (err) {
        alert(err.response?.data?.error || '注册失败')
      }
    }
  }
}
</script>

<style scoped>
/* 与 Login.vue 相同，可复用或单独写 */
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