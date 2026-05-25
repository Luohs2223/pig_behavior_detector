<template>
  <div>
    <div class="upload-section">
      <div class="upload-bar">
        <label class="file-label">
          选择文件
          <input type="file" @change="handleFileChange" accept="image/jpeg,image/png,image/jpg" style="display: none;" />
        </label>
        <div class="file-name">{{ fileName || '未选择文件' }}</div>
        <button class="upload-btn" @click="uploadImage" :disabled="!selectedFile || uploading">
          {{ uploading ? '检测中...' : '上传并检测' }}
        </button>
      </div>
    </div>

    <!-- 检测结果卡片 -->
    <div class="result-section">
      <div class="result-title">检测结果</div>
      <div class="result-card">
        <div class="canvas-wrapper">
          <canvas ref="canvasRef" class="result-canvas"></canvas>
        </div>
        <div v-if="result && result.summary" class="summary-text">
          {{ result.summary }}
        </div>
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
      imagePreviewUrl: '',
      uploading: false,
      result: null,
      errorMsg: ''
    }
  },
  methods: {
    handleFileChange(event) {
      const file = event.target.files[0]
      if (!file) return
      this.selectedFile = file
      this.errorMsg = ''
      this.result = null
      const reader = new FileReader()
      reader.onload = (e) => {
        this.imagePreviewUrl = e.target.result
        console.log('[Upload] 图片预览URL已生成')
        // 立即尝试显示图片（无需等待上传）
        this.drawImageOnCanvas(this.imagePreviewUrl)
      }
      reader.readAsDataURL(file)
    },

    async uploadImage() {
      if (!this.selectedFile) return
      this.uploading = true
      this.errorMsg = ''
      const formData = new FormData()
      formData.append('file', this.selectedFile)

      try {
        console.log('[Upload] 开始上传...')
        const response = await axios.post('/api/upload', formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        })
        console.log('[Upload] 上传成功，响应数据:', response.data)
        this.result = response.data
        // 重新绘制，添加检测框
        this.drawImageOnCanvas(this.imagePreviewUrl, this.result.detections)
      } catch (error) {
        console.error('[Upload] 上传失败:', error)
        this.errorMsg = error.response?.data?.error || '上传失败'
      } finally {
        this.uploading = false
      }
    },

    drawImageOnCanvas(imageUrl, detections = null) {
      const canvas = this.$refs.canvasRef
      if (!canvas) {
        console.error('[Upload] Canvas 元素未找到！')
        return
      }
      const ctx = canvas.getContext('2d')
      const img = new Image()
      img.crossOrigin = 'Anonymous' // 避免跨域问题
      img.onload = () => {
        console.log('[Upload] 图片加载完成，原始尺寸:', img.width, 'x', img.height)
        // 设置 Canvas 尺寸（固定宽度 800px，高度按比例）
        const maxWidth = 800
        const ratio = img.height / img.width
        const canvasWidth = maxWidth
        const canvasHeight = canvasWidth * ratio
        canvas.width = canvasWidth
        canvas.height = canvasHeight
        // 关键：强制设置 CSS 尺寸与绘图尺寸一致
        canvas.style.width = `${canvasWidth}px`
        canvas.style.height = `${canvasHeight}px`
        
        // 清空并绘制图片
        ctx.clearRect(0, 0, canvasWidth, canvasHeight)
        ctx.drawImage(img, 0, 0, canvasWidth, canvasHeight)
        console.log('[Upload] 图片已绘制到 Canvas，尺寸:', canvasWidth, 'x', canvasHeight)

        // 如果有检测结果，绘制框
        if (detections && detections.length > 0) {
          console.log('[Upload] 开始绘制检测框，数量:', detections.length)
          const scaleX = canvasWidth / img.width
          const scaleY = canvasHeight / img.height
          detections.forEach((det, idx) => {
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
            console.log(`[Upload] 绘制第${idx+1}个框:`, { rectX, rectY, rectW, rectH })
          })
        } else {
          console.log('[Upload] 没有检测框需要绘制')
        }
      }
      img.onerror = (err) => {
        console.error('[Upload] 图片加载失败，URL:', imageUrl, err)
        this.errorMsg = '图片加载失败，请检查网络或图片格式'
      }
      img.src = imageUrl
    }
  }
}
</script>

<style scoped>
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

.result-section {
  margin: 40px 0 48px;
}
.result-title {
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 20px;
}
.result-card {
  background: var(--card-bg);
  border-radius: 24px;
  border: 1px solid var(--border-color);
  padding: 24px;
}
.canvas-wrapper {
  display: flex;
  justify-content: center;
  background: #FDFAF5;
  border-radius: 20px;
  padding: 20px;
}
.summary-text {
  margin-top: 18px;
  background: #F2EBE1;
  padding: 12px 16px;
  border-radius: 32px;
  text-align: center;
  color: var(--text-main);
}

.result-canvas {
  display: block;
  max-width: 100%;
  height: auto;
  border-radius: 16px;
  background: #FDFAF5;
  box-shadow: 0 0 0 1px red; 
}

</style>