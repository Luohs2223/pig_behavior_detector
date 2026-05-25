<template>
  <div>
    <h2 style="text-align: center; margin: 15px 0;">视频分析详情</h2>
    <div v-if="loading">加载中...</div>

    <div v-else-if="record">
      <!-- 视频部分 -->
      <video controls style="width: 100%; max-width: 800px; border-radius: 8px; display: block; margin: 0 auto;">
        <source :src="record.video_path" type="video/mp4">
        您的浏览器不支持视频播放。
      </video>
      <!-- 摘要部分 -->
      <div class="progress">
        <p><strong >视频时长：</strong>{{ record.duration }} 秒</p>
        <p><strong >上传时间：</strong>{{ record.upload_time }}</p>
        <p><strong >文件名：</strong>{{ record.filename }}</p>
        <p><strong >摘要：</strong>{{ record.summary }}</p>
      </div>
      <!-- 异常事件部分 -->
      <div v-if="record.anomalies && record.anomalies.length">
        <h4 style="text-align: center; margin: 10px;">异常事件</h4>
        <ul>
          <li style="text-align: center;" v-for="(anom, idx) in record.anomalies" :key="idx">
            时间 {{ anom.time }} 秒，猪 ID {{ anom.id }}：{{ anom.type }} ({{ anom.detail }})
          </li>
        </ul>
      </div>
      <div v-else style="text-align: center; margin: 10px;">
        <p>未检测到异常行为</p>
      </div>

      <h4 style="text-align: center; margin: 10px;">每头猪的行为统计</h4>
      <div v-for="(stats, id) in record.behavior_stats" :key="id">
        <strong style="margin-left: 400px;">猪 ID {{ id }}:</strong>
        <ul>
          <li class="stat-item" v-for="(count, behavior) in stats" :key="behavior">{{ behavior }}: {{ count }} 次</li>
        </ul>
      </div>
      <!-- ai建议部分 -->
      <div v-if="record.ai_advice" class="ai-card">
        <div class="ai-header">
          <span>🤖 AI 养殖专家建议</span>
        </div>
        <div class="ai-content">{{ record.ai_advice }}</div>
      </div>
      <div style="text-align: center; margin: 20px;">
        <router-link to="/video-history">返回视频历史</router-link>
      </div>
    </div>
    <div v-else style="text-align: center ;">未找到记录</div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  data() {
    return {
      record: null,
      loading: false
    }
  },
  mounted() {
    this.fetchRecord()
  },
  methods: {
    async fetchRecord() {
      const recordId = this.$route.params.id
      this.loading = true
      try {
        const res = await axios.get(`/api/video_record/${recordId}`)
        this.record = res.data
      } catch (err) {
        console.error('获取视频详情失败', err)
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
video {
  margin-bottom: 20px;
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
.progress {
  margin-top: 20px;
  margin-left: 125px;
  margin-right: 125px;
  background-color: hsla(86, 48%, 64%, 0.199);
  border-radius: 16px;
  padding: 16px;
  text-align: center;
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