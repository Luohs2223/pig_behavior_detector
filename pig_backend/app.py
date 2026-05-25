import os
import json
import jwt
from flask import Flask, request, jsonify, send_from_directory
from config import Config
from models import db, DetectionRecord, bcrypt, User,VideoRecord
from utils import PigBehaviorDetector, allowed_file, save_upload_file
from datetime import datetime, timedelta, timezone
from functools import wraps
from flask_cors import CORS
from celery_app import celery
from tasks import process_video_task
import uuid

# 创建 Flask 应用实例
app = Flask(__name__)
app.config.from_object(Config)
CORS(app, origins=Config.CORS_ORIGINS)

# 可选：为任务绑定 Flask 应用上下文（如果任务中需要用到 Flask 的配置或数据库）
class ContextTask(celery.Task):
    def __call__(self, *args, **kwargs):
        with app.app_context():
            return self.run(*args, **kwargs)

celery.Task = ContextTask


# 初始化数据库和加密工具
db.init_app(app)
bcrypt.init_app(app)

# 确保上传文件夹存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# 加载检测器（模型在应用启动时加载一次）
detector = PigBehaviorDetector(model_path=app.config['MODEL_PATH'])
app.detector = detector

# 创建数据库表（如果不存在）
with app.app_context():
    db.create_all()

# ---------- 错误处理 ----------
@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(400)
def bad_request(e):
    return jsonify({'error': 'Bad request'}), 400

# ---------- 静态文件路由 ----------
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """提供上传图片的访问"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# ---------- JWT 验证装饰器 ----------
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Missing token'}), 401
        if token.startswith('Bearer '):
            token = token[7:]
        try:
            payload = jwt.decode(token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
            current_user = User.query.get(payload['user_id'])
            if not current_user:
                raise Exception('User not found')
        except Exception:
            return jsonify({'error': 'Invalid or expired token'}), 401
        request.current_user = current_user
        return f(*args, **kwargs)
    return decorated

# ---------- 用户认证接口 ----------
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'error': 'Username and password required'}), 400
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 400
    user = User(username=data['username'])
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'User created successfully'}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'error': 'Username and password required'}), 400
    user = User.query.filter_by(username=data['username']).first()
    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Invalid username or password'}), 401
    token = jwt.encode({
        'user_id': user.id,
        'exp': datetime.now(timezone.utc) + timedelta(hours=24)
    }, app.config['JWT_SECRET_KEY'], algorithm='HS256')
    return jsonify({'token': token, 'user_id': user.id, 'username': user.username})

# ---------- 图片上传接口 ----------
@app.route('/api/upload', methods=['POST'])
@login_required
def upload_image():
    """上传图片并执行检测（需要登录）"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    allowed_extensions = app.config['ALLOWED_EXTENSIONS']
    if not allowed_file(file.filename, allowed_extensions):
        return jsonify({'error': 'File type not allowed'}), 400

    try:
        saved_filename, image_url = save_upload_file(file, app.config['UPLOAD_FOLDER'])
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], saved_filename)

        detections, summary = app.detector.detect(image_path)

        record = DetectionRecord(
            filename=file.filename,
            saved_filename=saved_filename,
            image_path=image_url,
            detection_result=json.dumps(detections),
            summary=summary,
            user_id=request.current_user.id      # 关联当前登录用户
        )
        db.session.add(record)
        db.session.commit()

        return jsonify({
            'id': record.id,
            'image_path': image_url,
            'summary': summary,
            'detections': detections
        }), 201

    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Upload error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Server error during processing'}), 500

@app.route('/api/history', methods=['GET'])
@login_required
def get_history():
    """获取当前用户的历史记录列表（不包含检测详情）"""
    records = DetectionRecord.query.filter_by(user_id=request.current_user.id).order_by(DetectionRecord.upload_time.desc()).all()
    return jsonify([record.to_dict() for record in records])

@app.route('/api/record/<int:record_id>', methods=['GET'])
@login_required
def get_record(record_id):
    """获取当前用户的单条记录详情（包含检测结果）"""
    record = DetectionRecord.query.filter_by(id=record_id, user_id=request.current_user.id).first()
    if not record:
        return jsonify({'error': 'Record not found'}), 404
    return jsonify(record.to_dict(include_result=True))

@app.route('/api/record/<int:record_id>', methods=['DELETE'])
@login_required
def delete_record(record_id):
    record = DetectionRecord.query.filter_by(id=record_id, user_id=request.current_user.id).first()
    if not record:
        return jsonify({'error': '记录不存在或无权删除'}), 404
    
    # 删除图片文件（可选）
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], record.saved_filename)
    if os.path.exists(image_path):
        try:
            os.remove(image_path)
        except Exception as e:
            app.logger.error(f"删除图片文件失败: {e}")
    
    db.session.delete(record)
    db.session.commit()
    return jsonify({'message': '删除成功'}), 200

# ---------- 视频处理接口 ----------
@app.route('/api/upload_video', methods=['POST'])
@login_required
def upload_video():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # 保存视频文件
    saved_filename, video_url = save_upload_file(file, app.config['UPLOAD_FOLDER'])
    video_path = os.path.join(app.config['UPLOAD_FOLDER'], saved_filename)
    
    # 创建异步任务，传递必要信息
    task = process_video_task.delay(
    video_path=video_path,
    original_filename=file.filename,
    saved_filename=saved_filename,
    video_url=video_url,
    user_id=request.current_user.id,
    sample_rate=0.5
    )
    return jsonify({'task_id': task.id}), 202

@app.route('/api/video_history', methods=['GET'])
@login_required
def get_video_history():
    records = VideoRecord.query.filter_by(user_id=request.current_user.id).order_by(VideoRecord.upload_time.desc()).all()
    return jsonify([record.to_dict() for record in records])

@app.route('/api/video_record/<int:record_id>', methods=['GET'])
@login_required
def get_video_record(record_id):
    record = VideoRecord.query.filter_by(id=record_id, user_id=request.current_user.id).first()
    if not record:
        return jsonify({'error': 'Record not found'}), 404
    return jsonify(record.to_dict(include_result=True))

@app.route('/api/task_status/<task_id>', methods=['GET'])
@login_required
def task_status(task_id):
    from celery.result import AsyncResult
    task = AsyncResult(task_id, app=celery)
    if task.state == 'PENDING':
        response = {'state': 'PENDING', 'status': '等待处理...'}
    elif task.state == 'STARTED':
        response = {'state': 'STARTED', 'status': '处理中...'}
    elif task.state == 'PROGRESS':
        response = {
            'state': 'PROGRESS',
            'percent': task.info.get('percent', 0),
            'status': task.info.get('status', '')
        }
    elif task.state == 'SUCCESS':
        response = {'state': 'SUCCESS', 'result': task.result}
    else:
        response = {'state': 'FAILURE', 'error': str(task.info)}
    return jsonify(response)

@app.route('/api/video_record/<int:record_id>', methods=['DELETE'])
@login_required
def delete_video_record(record_id):
    record = VideoRecord.query.filter_by(id=record_id, user_id=request.current_user.id).first()
    if not record:
        return jsonify({'error': '记录不存在或无权删除'}), 404
    
    # 删除视频文件
    video_path = os.path.join(app.config['UPLOAD_FOLDER'], record.saved_filename)
    if os.path.exists(video_path):
        try:
            os.remove(video_path)
        except Exception as e:
            app.logger.error(f"删除视频文件失败: {e}")
    
    db.session.delete(record)
    db.session.commit()
    return jsonify({'message': '删除成功'}), 200


# ---------- 启动应用 ----------
if __name__ == '__main__':
    app.run(debug=True)