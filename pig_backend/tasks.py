# tasks.py
from celery_app import celery
from utils import process_video
from ai_service import get_ai_analysis   # 我们将创建这个文件
from models import db, VideoRecord
from ultralytics import YOLO
import json

@celery.task(bind=True)
def process_video_task(self, video_path, original_filename, saved_filename, video_url, user_id, sample_rate=0.5):
    self.update_state(state='PROGRESS', meta={'status': '加载模型中...', 'percent': 0})
    model = YOLO('pig1.pt')
    self.update_state(state='PROGRESS', meta={'status': '开始分析视频', 'percent': 10})
    
    # 调用视频处理核心函数（返回结果中包含 behavior_stats 和 anomalies）
    result = process_video(video_path, model, sample_rate)
    
    # 调用 AI 生成养殖建议（仅在行为统计非空或异常存在时调用）
    ai_advice = None
    if result.get('behavior_stats') or result.get('anomalies'):
        try:
            ai_advice = get_ai_analysis(
                behavior_stats=result['behavior_stats'],
                anomalies=result['anomalies'],
                duration=result['duration']
            )
        except Exception as e:
            print(f"AI 调用失败: {e}")
            ai_advice = "AI 分析暂不可用"
    
    # 保存到数据库
    from app import app
    with app.app_context():
        record = VideoRecord(
            filename=original_filename,
            saved_filename=saved_filename,
            video_path=video_url,
            duration=result['duration'],
            anomalies=json.dumps(result['anomalies']),
            behavior_stats=json.dumps(result['behavior_stats']),
            summary=f"检测到{len(result['anomalies'])}次异常",
            user_id=user_id,
            ai_advice=ai_advice   # 保存 AI 建议
        )
        db.session.add(record)
        db.session.commit()
    
    # 将 AI 建议也放入返回结果（供前端直接展示）
    result['ai_advice'] = ai_advice
    return result