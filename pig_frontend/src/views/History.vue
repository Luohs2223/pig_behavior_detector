<template>
  <div>
    <h2 style="text-align: center; margin: 15px 0;">历史检测记录</h2>
    <div v-if="loading">加载中...</div>
    <div v-else-if="records.length === 0">暂无记录</div>
    <ul v-else style="width: 1700px; margin: 0 auto; padding-left: 0;">
      <li v-for="record in records" :key="record.id">
        <router-link :to="`/record/${record.id}`">
          <img :src="record.image_path" width="100" height="auto" @error="handleImageError(record)" />
          <span style="margin-left: 20px;">{{ record.upload_time }} - {{ record.summary }}</span>
        </router-link>
          <button @click="deleteRecord(record.id)" class="delete-btn">删除</button>
      </li>
    </ul>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  data() {
    return {
      records: [],
      loading: false
    }
  },
  mounted() {
    this.fetchHistory()
  },
  methods: {
    async fetchHistory() {
      this.loading = true
      try {
        console.log('[History] 请求历史记录...')
        const res = await axios.get('/api/history')
        this.records = res.data
        console.log('[History] 获取到记录数:', this.records.length)
      } catch (err) {
        console.error('[History] 请求失败:', err)
      } finally {
        this.loading = false
      }
    },
    handleImageError(record) {
      console.warn('[History] 图片加载失败，路径:', record.image_path)
    },
    async deleteRecord(id) {
      if (!confirm('确定要删除该记录吗？不可恢复。')) return
      try {
        await axios.delete(`/api/record/${id}`)
        this.records = this.records.filter(r => r.id !== id)
        alert('删除成功')
      } catch (err) {
        console.error(err)
        alert('删除失败：' + (err.response?.data?.error || '未知错误'))
      }
    }
  }
}
</script>

<style scoped>
li {
  margin-bottom: 10px;
  list-style: none;
}
img {
  vertical-align: middle;
  margin-right: 10px;
}
.delete-btn {
  margin-left: 100px;
  background-color: #f56c6c;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 4px 10px;
  cursor: pointer;
}
.delete-btn:hover {
  background-color: #f78989;
}
</style>