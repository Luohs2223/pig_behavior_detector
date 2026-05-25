from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from datetime import datetime
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)
    
class DetectionRecord(db.Model):
    __tablename__ = 'detection_records'
    #SQLAlchemy().Column()定义一个字段
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(200), nullable=False)          # 原始文件名
    saved_filename = db.Column(db.String(200), nullable=False)    # 实际存储的文件名（避免重名）
    image_path = db.Column(db.String(500), nullable=False)        # 访问路径，如 /uploads/xxx.jpg
    upload_time = db.Column(db.DateTime, default=datetime.utcnow)
    detection_result = db.Column(db.Text, nullable=True)          # 存储JSON字符串
    summary = db.Column(db.String(200), nullable=True)            # 简要摘要
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', backref='records')

    def to_dict(self, include_result=False):
        data = {
            'id': self.id,
            'filename': self.filename,
            'image_path': self.image_path,
            'upload_time': self.upload_time.isoformat(),
            'summary': self.summary
        }
        if include_result and self.detection_result:
            import json
            data['detection_result'] = json.loads(self.detection_result)
        return data
    
class VideoRecord(db.Model):
    __tablename__ = 'video_records'
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(200), nullable=False)
    saved_filename = db.Column(db.String(200), nullable=False)
    video_path = db.Column(db.String(500), nullable=False)
    upload_time = db.Column(db.DateTime, default=datetime.utcnow)
    duration = db.Column(db.Float, nullable=True)           # 视频时长（秒）
    anomalies = db.Column(db.Text, nullable=True)           # 存储异常事件 JSON 字符串
    behavior_stats = db.Column(db.Text, nullable=True)      # 存储每头猪的行为统计 JSON
    summary = db.Column(db.String(500), nullable=True)      # 简要摘要，如“检测到2次异常”
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', backref='video_records')
    ai_advice = db.Column(db.Text, nullable=True)  # 存储 AI 生成的养殖建议

    def to_dict(self, include_result=False):
        data = {
            'id': self.id,
            'filename': self.filename,
            'video_path': self.video_path,
            'upload_time': self.upload_time.isoformat(),
            'summary': self.summary,
            'duration': self.duration,
            'ai_advice': self.ai_advice   # 新增
        }
        if include_result:
            import json
            if self.anomalies:
                data['anomalies'] = json.loads(self.anomalies)
            if self.behavior_stats:
                data['behavior_stats'] = json.loads(self.behavior_stats)
        return data