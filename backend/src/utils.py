import math
import numpy as np
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.pyplot as plt
import cv2
from io import BytesIO
from PIL import Image

def calculate_distance(point1, point2):
    return math.sqrt((point2[0] - point1[0]) ** 2 + (point2[1] - point1[1]) ** 2)

def calculate_angle(a, b, c):
    """计算三个点之间的夹角"""
    ba = a - b
    bc = c - b
    cos_angle = (ba @ bc) / (math.sqrt(ba @ ba) * math.sqrt(bc @ bc))
    angle = math.degrees(math.acos(cos_angle))
    return angle

def calculate_bounding_box_area(keypoints):
    """根据关键点计算包围盒面积"""
    x_coords = [p[0] for p in keypoints]
    y_coords = [p[1] for p in keypoints]
    width = max(x_coords) - min(x_coords)
    height = max(y_coords) - min(y_coords)
    return width * height

def determine_side(side,left_shoulder,left_hip,left_knee,left_ankle, right_shoulder,right_hip,right_knee,right_ankle):
    left_shoulder_x = left_shoulder[0]
    left_hip_x = left_hip[0]
    left_knee_x = left_knee[0]
    left_ankle_x = left_ankle[0]

    # 右侧关节的x坐标
    right_shoulder_x = right_shoulder[0]
    right_hip_x = right_hip[0]
    right_knee_x = right_knee[0]
    right_ankle_x = right_ankle[0]

    # 计算左侧和右侧关节x坐标的平均值
    left_side_avg_x = np.mean([left_shoulder_x, left_hip_x, left_knee_x, left_ankle_x])
    right_side_avg_x = np.mean([right_shoulder_x, right_hip_x, right_knee_x, right_ankle_x])
    if side == None:
        # 根据x坐标的平均值选择最靠近镜头的一侧
        if left_side_avg_x < right_side_avg_x:
            side = 'left'
            selected_shoulder = left_shoulder
            selected_hip = left_hip
            selected_knee = left_knee
            selected_ankle = left_ankle
        else:
            side = 'right'
            selected_shoulder = right_shoulder
            selected_hip = right_hip
            selected_knee = right_knee
            selected_ankle = right_ankle
    else:
        if side == 'left':
            selected_shoulder = left_shoulder
            selected_hip = left_hip
            selected_knee = left_knee
            selected_ankle = left_ankle
        elif side=='right':
            selected_shoulder = right_shoulder
            selected_hip = right_hip
            selected_knee = right_knee
            selected_ankle = right_ankle
    
    return side,selected_shoulder,selected_hip,selected_knee,selected_ankle


def plot_dynamic_chart(time_values, speed_values, knee_angles, hip_angles,video_length_seconds):
    """绘制动态图表并返回BGR格式图像"""
    fig, ax = plt.subplots(3, 1, figsize=(5, 12))

    ax[0].set_xlim([0, video_length_seconds])
    ax[1].set_xlim([0, video_length_seconds])
    ax[2].set_xlim([0, video_length_seconds])


    ax[0].set_ylim([-1000,1000])
    ax[1].set_ylim([0, 180])  # 膝盖角度通常在 0 到 180 度之间
    ax[2].set_ylim([0, 180])  # 髋部角度通常也在 0 到 180 度之间

    ax[0].plot(time_values, speed_values, label='Rise Speed (px/s)', color='b')
    ax[0].set_xlabel('Time (s)')
    ax[0].set_ylabel('Speed (px/s)')
    ax[0].set_title('Shoulder Rising Speed')
    ax[0].legend()
    ax[0].grid(True)

    ax[1].plot(time_values, knee_angles, label='Knee Angle (degrees)', color='r')
    ax[1].set_xlabel('Time (s)')
    ax[1].set_ylabel('Angle (degrees)')
    ax[1].set_title('Knee Angle Change')
    ax[1].legend()
    ax[1].grid(True)

    ax[2].plot(time_values, hip_angles, label='Hip Angle (degrees)', color='g')
    ax[2].set_xlabel('Time (s)')
    ax[2].set_ylabel('Angle (degrees)')
    ax[2].set_title('Hip Angle Change')
    ax[2].legend()
    ax[2].grid(True)

    buf = BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format='png')
    plt.close(fig)
    buf.seek(0)

    img = Image.open(buf).convert('RGB')
    img_np = np.array(img)
    img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
    
    return img_bgr

def calculate_angle(p1, p2, p3):
    """计算p2处的角度，使用余弦定理"""
    v1 = p1 - p2
    v2 = p3 - p2
    angle = np.arccos(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)))
    return np.degrees(angle)
