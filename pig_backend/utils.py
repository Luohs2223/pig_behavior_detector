import os
import time
from werkzeug.utils import secure_filename
from ultralytics import YOLO
import cv2
from collections import deque

class PigBehaviorDetector:
    def __init__(self, model_path='pig1.pt'):
        self.model = YOLO(model_path)
        self.class_names = ['饲槽', '侧卧', '坐姿饮水', '坐姿吃食', '坐姿无行为',
                            '站立饮水', '站立吃食', '站立无行为', '俯卧饮水',
                            '俯卧吃食', '俯卧无行为', '饮水器']

    def detect(self, image_path):
        results = self.model(image_path)
        detections = []
        class_counts = {}

        for r in results:
            for box in r.boxes:
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                cls = int(box.cls[0])
                conf = float(box.conf[0])
                label = self.class_names[cls]
                detections.append({
                    'bbox': [x1, y1, x2, y2],
                    'class': label,
                    'confidence': conf
                })
                class_counts[label] = class_counts.get(label, 0) + 1

        summary = ', '.join([f"{k}({v})" for k, v in class_counts.items()])
        return detections, summary

def allowed_file(filename, allowed_extensions):
    """检查文件扩展名是否允许"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def save_upload_file(file, upload_folder):
    """保存上传文件，返回保存的文件名和访问路径"""
    filename = secure_filename(file.filename)
    name, ext = os.path.splitext(filename)
    timestamp = int(time.time())
    saved_filename = f"{name}_{timestamp}{ext}"
    filepath = os.path.join(upload_folder, saved_filename)
    file.save(filepath)
    return saved_filename, f"/uploads/{saved_filename}"

import cv2
from collections import deque

def process_video(video_path, model, sample_rate=0.5):
    """
    视频处理核心函数：个体行为统计 + 长时间异常检测
    必须依赖多目标跟踪ID，无跟踪ID时跳过该帧。
    """
    # ======================= 参数配置 =======================
    ANOREXIA_LIMIT = 9000
    LYING_ALARM_LIMIT = 7200
    ACTIVITY_WINDOW = 600
    ACTIVITY_RATIO_THRESH = 0.05
    ANOREXIA_DEDUP = 1800
    LYING_DEDUP = 1200
    MAX_DELTA = 5.0

    EATING_DRINKING_KEYWORDS = ('吃食', '饮水')
    LYING_BEHAVIORS = {'侧卧', '坐姿无行为', '俯卧无行为'}

    # ======================= 视频初始化 =======================
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps

    frame_interval = max(1, int(fps / sample_rate))
    max_deque_len = int(ACTIVITY_WINDOW * sample_rate)

    pig_state = {}
    behavior_stats = {}
    anomalies = []
    processed = 0
    frame_count = 0
    tracking_warned = False

    # ======================= 主循环 =======================
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if frame_count % frame_interval == 0:
            processed += 1
            timestamp = frame_count / fps

            results = model.track(frame, persist=True, verbose=False)
            boxes = results[0].boxes
            if boxes is None:
                frame_count += 1
                continue

            # 必须要有跟踪ID
            if boxes.id is None:
                if not tracking_warned:
                    print("[警告] 跟踪ID不可用。请安装 scipy 和 lapx：pip install scipy lapx")
                    print(" 未安装跟踪依赖时，所有帧将被跳过，无任何输出。")
                    tracking_warned = True
                frame_count += 1
                continue

            ids = boxes.id.cpu().numpy().astype(int)
            xyxy = boxes.xyxy.cpu().numpy()
            classes = boxes.cls.cpu().numpy().astype(int)
            class_names = model.names

            for box, tid, cls in zip(xyxy, ids, classes):
                behavior = class_names[cls]

                # ---------- 行为统计 ----------
                if tid not in behavior_stats:
                    behavior_stats[tid] = {}
                behavior_stats[tid][behavior] = behavior_stats[tid].get(behavior, 0) + 1

                # ---------- 初始化异常检测状态 ----------
                if tid not in pig_state:
                    pig_state[tid] = {
                        'last_feed_time': None,
                        'lying_timer': 0.0,
                        'lying_activity_deque': deque(),
                        'lying_last_update_time': timestamp,
                    }
                state = pig_state[tid]
                delta_t = timestamp - state['lying_last_update_time']
                state['lying_last_update_time'] = timestamp

                # ---------- 丢失帧保护 ----------
                if delta_t > MAX_DELTA:
                    state['lying_timer'] = 0.0
                    state['lying_activity_deque'].clear()
                    continue

                # ---------- 规则1：饮食废绝 ----------
                if any(k in behavior for k in EATING_DRINKING_KEYWORDS):
                    state['last_feed_time'] = timestamp

                if state['last_feed_time'] is not None:
                    time_since_feed = timestamp - state['last_feed_time']
                    if time_since_feed >= ANOREXIA_LIMIT:
                        last_anorexia = next(
                            (a for a in reversed(anomalies)
                             if a['id'] == tid and a['type'] == '饮食废绝'),
                            None
                        )
                        if last_anorexia is None or (timestamp - last_anorexia['time']) > ANOREXIA_DEDUP:
                            anomalies.append({
                                'id': int(tid),
                                'time': round(timestamp, 1),
                                'type': '饮食废绝',
                                'detail': f'已{time_since_feed/60:.0f}分钟无进食饮水'
                            })

                # ---------- 规则2：长时间躺卧无行为 ----------
                is_lying = behavior in LYING_BEHAVIORS
                is_active = 0 if is_lying else 1

                state['lying_timer'] += delta_t
                state['lying_activity_deque'].append(is_active)
                while len(state['lying_activity_deque']) > max_deque_len:
                    state['lying_activity_deque'].popleft()

                if state['lying_activity_deque']:
                    activity_ratio = sum(state['lying_activity_deque']) / len(state['lying_activity_deque'])
                else:
                    activity_ratio = 0.0

                if activity_ratio > ACTIVITY_RATIO_THRESH:
                    state['lying_timer'] = 0.0
                    state['lying_activity_deque'].clear()

                if state['lying_timer'] >= LYING_ALARM_LIMIT:
                    last_lying = next(
                        (a for a in reversed(anomalies)
                         if a['id'] == tid and a['type'] == '长时间躺卧无行为'),
                        None
                    )
                    if last_lying is None or (timestamp - last_lying['time']) > LYING_DEDUP:
                        anomalies.append({
                            'id': int(tid),
                            'time': round(timestamp, 1),
                            'type': '长时间躺卧无行为',
                            'detail': f'持续躺卧/无行为{state["lying_timer"]/3600:.1f}小时'
                        })

        frame_count += 1

    cap.release()

    behavior_stats = {int(k): v for k, v in behavior_stats.items()}
    result = {
        'duration': round(duration, 1),
        'total_frames_processed': processed,
        'anomalies': anomalies,
        'behavior_stats': behavior_stats
    }
    return result
"""
属性	形状	     数据类型	      说明
xyxy	(N, 4)	    torch.Tensor	每个框的坐标，格式为 [x1, y1, x2, y2]（左上角和右下角，像素坐标）。
xywh	(N, 4)	    torch.Tensor	坐标格式为 [x_center, y_center, width, height]。
xyxyn	(N, 4)	    torch.Tensor	归一化的 xyxy（坐标值除以图像宽高）。
xywhn	(N, 4)	    torch.Tensor	归一化的 xywh。
cls	    (N,)	    torch.Tensor	每个框对应的类别索引（整数）。
conf	(N,)	    torch.Tensor	每个框的置信度（浮点数，0~1）。
data	(N, 6)	    torch.Tensor	原始数据，通常为 [x1, y1, x2, y2, conf, cls]（每行6个值）。
id	    (N,)或None	torch.Tensor	如果启用了跟踪（track），则存储目标 ID。
"""

