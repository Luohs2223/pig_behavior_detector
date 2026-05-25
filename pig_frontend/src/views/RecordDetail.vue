<template>
  <div>
    <h2>检测详情</h2>
    <div v-if="loading">加载中...</div>

    <div v-else>
      <!-- 始终渲染容器，通过 v-show 控制显示 -->
      <div class="image-wrapper" v-show="record">
        <canvas class="result-canvas"></canvas>
      </div>
      <div class="record-details" v-if="record">
        <p><strong>文件名：</strong>{{ record.filename }}</p>
        <p><strong>上传时间：</strong>{{ record.upload_time }}</p>
        <p><strong>摘要：</strong>{{ record.summary }}</p>
        <div style="text-align: center; margin-top: 20px;">
        <router-link to="/history">返回历史</router-link>
        </div>
      </div>
      <div v-else>未找到记录</div>
    </div>

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
        console.log(`[RecordDetail] 请求记录 ID: ${recordId}`)
        const res = await axios.get(`/api/record/${recordId}`)
        this.record = res.data
        console.log('[RecordDetail] 获取记录成功，detection_result:', this.record.detection_result)
        await this.$nextTick()
        // 等待一小段时间确保 DOM 渲染
        setTimeout(() => {
          this.drawImage()
        }, 100)
      } catch (err) {
        console.error('[RecordDetail] 请求失败:', err)
      } finally {
        this.loading = false
      }
    },
    drawImage() {
      const canvas = document.querySelector('.image-wrapper canvas')
      if (!canvas) {
        console.error('[RecordDetail] Canvas 元素未找到')
        return
      }
      console.log('[RecordDetail] Canvas 已找到，开始绘制')
      const img = new Image()
      img.crossOrigin = 'Anonymous'
      img.onload = () => {
        console.log('[RecordDetail] 图片加载完成，尺寸:', img.width, 'x', img.height)
        const maxWidth = 800
        const ratio = img.height / img.width
        const canvasWidth = maxWidth
        const canvasHeight = canvasWidth * ratio
        canvas.width = canvasWidth
        canvas.height = canvasHeight
        canvas.style.width = `${canvasWidth}px`
        canvas.style.height = `${canvasHeight}px`
        const ctx = canvas.getContext('2d')
        ctx.clearRect(0, 0, canvasWidth, canvasHeight)
        ctx.drawImage(img, 0, 0, canvasWidth, canvasHeight)

        const detections = this.record.detection_result
        if (detections && detections.length > 0) {
          console.log('[RecordDetail] 绘制检测框，数量:', detections.length)
          const scaleX = canvasWidth / img.width
          const scaleY = canvasHeight / img.height
          detections.forEach(det => {
            const [x1, y1, x2, y2] = det.bbox
            const rectX = x1 * scaleX
            const rectY = y1 * scaleY
            const rectW = (x2 - x1) * scaleX
            const rectH = (y2 - y1) * scaleY
            ctx.strokeStyle = 'red'
            ctx.lineWidth = 2
            ctx.strokeRect(rectX, rectY, rectW, rectH)
            ctx.fillStyle = 'red'
            ctx.font = '16px Arial'
            ctx.fillText(`${det.class} ${(det.confidence * 100).toFixed(1)}%`, rectX, rectY - 5)
          })
        } else {
          console.warn('[RecordDetail] 没有检测结果')
        }
      }
      img.onerror = (err) => {
        console.error('[RecordDetail] 图片加载失败，路径:', this.record.image_path, err)
      }
      img.src = this.record.image_path
    }
  }
}
</script>

<style scoped>
h2 {
  margin-top: 20px;
  margin-bottom: 20px;
  border-radius: 5px;
  text-align: center;
}
p {
  text-align: justify;
  margin-left: 30px;
}
.record-details {
  margin-top: 20px;
  margin-left: 125px;
  margin-right: 125px;
  background-color: var(--card-bg);
  border-radius: 16px;
  padding: 20px;
} 
.image-wrapper {
  /* 关键：让容器自己居中 */
  display: block;
  margin: 0 auto;
  max-width: 100%;
  width: fit-content; /* 让盒子跟着canvas宽度走 */

  border: 1px solid #ddd;
  background: #f5f5f5;
  overflow-x: auto;
  min-height: 100px;

  /* 关键：让内部canvas水平居中 */
  text-align: center;
}
.result-canvas {
  display: inline-block;
}
</style>