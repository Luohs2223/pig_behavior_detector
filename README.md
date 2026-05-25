# 🐷 生猪行为检测全栈系统

基于 YOLOv8s + Flask + Vue3 的生猪行为识别与异常分析平台，支持图片实时检测与视频异步分析，集成多目标跟踪、异常规则引擎及大语言模型养殖建议。

## ✨ 功能特性

- ✅ **图片检测**：上传猪只图片，实时识别12种行为（侧卧、坐姿/站立/俯卧状态下的饮水、吃食、无行为等），Canvas绘制边界框
- ✅ **视频分析**：上传视频，异步处理（Celery+Redis），支持抽帧、多目标跟踪、长时间异常判定
- ✅ **多目标跟踪**：基于 ByteTrack 为每头猪分配跨帧唯一 ID，实现个体级行为记录
- ✅ **异常报警**：基于累计计时与活动容错的规则引擎，自动识别“饮食废绝”和“长时间躺卧无行为”，支持去重报警
- ✅ **AI养殖建议**：集成 DeepSeek 大语言模型，将行为统计与异常事件转化为自然语言养殖建议
- ✅ **用户系统**：JWT 认证，用户数据隔离，历史记录查询与删除
- ✅ **全栈部署**：前后端分离，Nginx 反向代理，已部署至腾讯云轻量服务器

## 🛠 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue3 + Vue Router + Axios + Canvas |
| 后端 | Flask + Flask-SQLAlchemy + Flask-CORS + JWT |
| 数据库 | MySQL |
| 缓存/消息队列 | Redis |
| 异步任务 | Celery |
| AI 模型 | YOLOv8s + ByteTrack |
| 大语言模型 | DeepSeek API |
| 部署 | Nginx + Gunicorn + 腾讯云（Ubuntu） |

## 📦 安装与运行

### 前置要求
- Python 3.10+
- Node.js 18+
- MySQL 8.0+
- Redis

### 后端部署

```bash
# 克隆项目
git clone https://github.com/yourname/pig-behavior-system.git
cd pig-behavior-system/backend

# 创建虚拟环境
conda create -n yolotrain python=3.10
conda activate yolotrain

# 安装依赖
pip install -r requirements.txt

# 配置环境变量（.env 文件）
cp .env.example .env
# 编辑 .env 填写数据库、Redis、DeepSeek API Key 等

# 初始化数据库
flask db upgrade  # 或 python -c "from app import app, db; app.app_context().push(); db.create_all()"

# 启动后端服务
gunicorn -w 2 -b 127.0.0.1:5000 app:app &
celery -A app.celery worker --loglevel=info -P eventlet &
```

### 前端部署

```bash
cd ../frontend
npm install
npm run build
# 将 dist 目录内容上传至服务器 Nginx 根目录
```

### Nginx 配置示例

```nginx
server {
    listen 80;
    server_name your-domain.com;
    root /var/www/pig_frontend;
    index index.html;

    client_max_body_size 2048M;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 🎯 使用说明

1. 访问 `http://your-server-ip` 注册/登录
2. 点击 **上传图片** → 选择图片 → 查看检测结果（边界框 + 摘要）
3. 点击 **上传视频** → 选择视频 → 系统返回 `task_id`，前端轮询进度 → 完成后展示异常列表、行为统计及 AI 建议
4. 进入 **历史记录** 可查看过往检测结果，支持删除

## 📄 许可证

本项目仅用于辅修毕业设计展示，未经许可不得用于商业用途。

## 🙏 致谢

- [Ultralytics YOLOv8](https://github.com/ultralytics/ultralytics)
- [ByteTrack](https://github.com/ifzhang/ByteTrack)
- [DeepSeek](https://www.deepseek.com/)
- 腾讯云开发者社区提供的猪只行为数据集

---
