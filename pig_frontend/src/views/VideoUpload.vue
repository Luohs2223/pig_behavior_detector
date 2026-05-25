<template>
  <div>
    <h2>上传猪舍视频进行行为分析</h2>

    <div class="upload-section">
      <div class="upload-bar">
        <label class="file-label">
          选择文件
          <input type="file" @change="handleFileChange" accept="video/mp4,video/avi,video/mov,video/mkv" style="display: none;" />
        </label>
        <div class="file-name">{{ fileName || '未选择文件' }}</div>
        <button class="upload-btn" @click="uploadVideo" :disabled="!selectedFile || uploading">
          {{ uploading ? '检测中...' : '上传并检测' }}
        </button>
      </div>
    </div>

    <div v-if="taskId" class="progress">
      <p>状态: {{ taskStatus }}</p>
      <p>任务ID: {{ taskId }}</p>
      <p>视频分析可能需要的时间较长，请耐心等待</p>
    </div>

    <div v-if="result" class="result">
      <h3 style="text-align: center; margin:10px">分析结果</h3>
      <p style="text-align: center;">视频时长: {{ result.duration }} 秒</p>

      <div v-if="result.anomalies && result.anomalies.length">
        <h4 style="text-align: center;">异常事件</h4>
        <ul>
          <li style="text-align: center;" v-for="(anom, idx) in result.anomalies" :key="idx">
            时间 {{ anom.time }} 秒，猪 ID {{ anom.id }}：{{ anom.type }} ({{ anom.detail }})
          </li>
        </ul>
      </div>
      <div v-else>
        <p style="text-align: center; margin:10px;">未检测到异常行为</p>
      </div>

      <h4 style="text-align: center; margin: 10px;">每头猪的行为统计</h4>
      <div v-for="(stats, id) in result.behavior_stats" :key="id">
        <strong style="margin-left: 400px;">猪 ID {{ id }}:</strong>
        <ul>
          <li class="stat-item"   v-for="(count, behavior) in stats" :key="behavior">{{ behavior }}: {{ count }} 次</li>
        </ul>
      </div>
      <div v-if="result.ai_advice" class="ai-card">
        <div class="ai-header">🤖 养殖专家建议</div>
        <div class="ai-content">{{ result.ai_advice }}</div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  data() {
    return {
      selectedFile: null,
      uploading: false,
      taskId: null,
      taskStatus: '',
      progressPercent: 0,
      result: null,
      pollInterval: null
    }
  },
  methods: {
    handleFileChange(e) {
      this.selectedFile = e.target.files[0]
      this.result = null
      this.taskId = null
      this.taskStatus = ''
      this.progressPercent = 0
      if (this.pollInterval) clearInterval(this.pollInterval)
    },
    async uploadVideo() {
      if (!this.selectedFile) return
      this.uploading = true
      const formData = new FormData()
      formData.append('file', this.selectedFile)

      try {
        const res = await axios.post('/api/upload_video', formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        })
        this.taskId = res.data.task_id
        this.taskStatus = '任务已提交，等待处理...'
        this.pollStatus()
      } catch (err) {
        alert('上传失败：' + (err.response?.data?.error || '网络错误'))
        this.uploading = false
      }
    },
    pollStatus() {
      this.pollInterval = setInterval(async () => {
        if (!this.taskId) return
        try {
          const res = await axios.get(`/api/task_status/${this.taskId}`)
          const status = res.data
          this.taskStatus = status.status || status.state
          if (status.percent) this.progressPercent = status.percent
          if (status.state === 'SUCCESS') {
            clearInterval(this.pollInterval)
            this.result = status.result
            this.uploading = false
            this.taskStatus = '分析完成'
          } else if (status.state === 'FAILURE') {
            clearInterval(this.pollInterval)
            this.uploading = false
            this.taskStatus = '分析失败：' + (status.error || '未知错误')
          }
        } catch (err) {
          console.error('轮询状态失败', err)
        }
      }, 2000) // 每2秒轮询一次
    }
  },
  beforeUnmount() {
    if (this.pollInterval) clearInterval(this.pollInterval)
  }
}
</script>

<style scoped>
h2 {
  text-align: center;
  margin-top: 20px;
}
.upload-section {
  background: var(--card-bg);
  border-radius: 20px;
  padding: 28px 24px;
  margin: 32px 0 40px;
  border: 1px solid var(--border-color);
}
.upload-bar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: center;
  gap: 16px;
}
.file-label {
  background: #FFFFFF;
  border: 1px solid #E2D4C4;
  border-radius: 40px;
  padding: 10px 20px;
  cursor: pointer;
  transition: all 0.2s;
}
.file-label:hover {
  border-color: var(--accent);
}
.file-name {
  background: #FFFFFF;
  padding: 8px 18px;
  border-radius: 40px;
  border: 1px solid #F0E4D4;
  color: var(--text-muted);
}
.upload-btn {
  background: var(--accent);
  border: none;
  border-radius: 40px;
  padding: 10px 28px;
  color: white;
  font-weight: 500;
  cursor: pointer;
}
.upload-btn:hover { background: #AF6747; }
.upload-btn:disabled { background: #D2B8A6; cursor: not-allowed; }
.progress {
  margin-top: 20px;
  background: #eae8e0;
  border-radius: 16px;
  padding: 16px;
  text-align: center;
}
.result {
  margin-top: 20px;
  background: #F9F5ED;
  border-radius: 16px;
  padding: 16px;
}
ul {
  list-style: none;  /* 去掉小圆点 */
  padding: 0;        /* 去掉默认左边空白 */
  margin: 0;
}
.stat-item {
  margin-bottom: 4px;
  text-align: center;
  margin-left:100px;
}
.ai-card {
  margin: 20px 0;
  background: #F0F7EE;
  border-left: 5px solid #67C23A;
  padding: 12px 16px;
  border-radius: 8px;
}
.ai-header {
  font-weight: bold;
  margin-bottom: 8px;
}
.ai-content {
  line-height: 1.5;
}
</style>