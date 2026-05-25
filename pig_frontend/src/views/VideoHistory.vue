<template>
  <div>
    <h2 style="text-align: center; margin: 15px 0;">视频分析历史记录</h2>
    <div v-if="loading">加载中...</div>
    <div v-else-if="records.length === 0">暂无记录</div>
    <ul v-else style="width: 750px; margin: 0 auto; padding-left: 0;">
      <li v-for="record in records" :key="record.id">
        <router-link :to="`/video-record/${record.id}`">
          <video :src="record.video_path" width="100" controls preload="metadata"></video>
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
        const res = await axios.get('/api/video_history')
        this.records = res.data
      } catch (err) {
        console.error('获取视频历史记录失败:', err)
      } finally {
        this.loading = false
      }
    },
    async deleteRecord(id) {
      if (!confirm('确定要删除该视频记录吗？不可恢复。')) return
      try {
        await axios.delete(`/api/video_record/${id}`)
        this.records = this.records.filter(r => r.id !== id)
        alert('删除成功')
      } catch (err) {
        console.error('删除失败:', err)
        alert('删除失败：' + (err.response?.data?.error || '未知错误'))
      }
    }
  }
}
</script>

<style scoped>
li {
  margin-bottom: 15px;
  list-style: none;
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
}
video {
  vertical-align: middle;
  margin-right: 10px;
}
.delete-btn {
  margin-left: 150px;
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