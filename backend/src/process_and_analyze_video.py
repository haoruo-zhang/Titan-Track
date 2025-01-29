import cv2
from ultralytics import YOLO
import os
import numpy as np
from ultralytics import YOLO
from src.utils import calculate_bounding_box_area, calculate_distance, determine_side, plot_dynamic_chart, calculate_angle
# from utils import calculate_bounding_box_area, calculate_distance, determine_side, plot_dynamic_chart, calculate_angle

def process_and_analyze_video(video_path, output_dir, yolo_model_path=None):
    """
    使用深蹲检测逻辑将视频分割为多个片段
    :param video_path: 输入视频路径
    :param output_dir: 输出视频片段目录
    :param yolo_model_path: YOLO 模型路径
    :return: 分割视频的文件路径列表
    """
     # 如果未指定模型路径，则动态获取默认路径
    if yolo_model_path is None:
        yolo_model_path = os.path.join(os.getcwd(), "models", "yolov8l-pose.pt")

    # 检查模型路径是否存在
    if not os.path.exists(yolo_model_path):
        raise FileNotFoundError(f"YOLO model not found at {yolo_model_path}")
    # 加载 YOLO 模型
    model = YOLO(yolo_model_path)

    # 打开视频
    cap = cv2.VideoCapture(video_path)
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')

    # 变量来跟踪深蹲的状态
    initial_shoulder_pos = None
    squat_start = False
    segment_count = 0
    current_video_writer = None

    threshold_down = 20  # 用于检测肩膀显著下移的阈值（单位：像素）
    threshold_up = 3 # 用于检测肩膀回到初始位置的阈值
    threshold_horizontal = 30

    extra_frames = 15   # 深蹲结束后，延长的帧数
    extra_frame_counter = 0

    os.makedirs(output_dir, exist_ok=True)
    segment_files = []

    results = model(video_path, stream=True)  # 使用 YOLO 进行姿态检测
    for result in results:
        ret, frame = cap.read()
        if not ret:
            break

        all_keypoints = result.keypoints.data
        max_area = 0
        largest_person = None

        # 找到检测到的最大目标
        for keypoints in all_keypoints:
            area = calculate_bounding_box_area(keypoints)
            if area > max_area:
                max_area = area
                largest_person = keypoints

        if largest_person is not None:
            # 获取左肩膀的坐标
            side = None
            left_shoulder = largest_person[5][:2].cpu().numpy()
            left_hip = largest_person[11][:2].cpu().numpy()
            left_knee = largest_person[13][:2].cpu().numpy()
            left_ankle = largest_person[15][:2].cpu().numpy()

            right_shoulder = largest_person[6][:2].cpu().numpy()
            right_hip = largest_person[12][:2].cpu().numpy()
            right_knee = largest_person[14][:2].cpu().numpy()
            right_ankle = largest_person[16][:2].cpu().numpy()

            side, shoulder, hip, knee, ankle = determine_side(side, left_shoulder, left_hip, left_knee, left_ankle, right_shoulder, right_hip, right_knee, right_ankle)
            if initial_shoulder_pos is None:
                # 初始化肩膀的初始位置
                initial_shoulder_pos = shoulder
                continue

            shoulder_vertical_movement = shoulder[1] - initial_shoulder_pos[1]
            shoulder_horizontal_movement = abs(shoulder[0] - initial_shoulder_pos[0])

            # 检测深蹲开始
            if shoulder_vertical_movement > threshold_down and not squat_start and shoulder_horizontal_movement < threshold_horizontal:
                squat_start = True
                extra_frame_counter = 0
                segment_count += 1
                segment_file = os.path.join(output_dir, f'squat_segment_{segment_count}.mp4')
                segment_files.append(segment_file)
                current_video_writer = cv2.VideoWriter(segment_file, fourcc, fps, (width, height))
                print(f"Starting squat segment {segment_count}")

            # 检测深蹲结束
            elif shoulder_vertical_movement < threshold_up and squat_start:
                if extra_frame_counter == 0:
                    print(f"Ending squat segment {segment_count}, but continuing for {extra_frames} more frames.")
                extra_frame_counter += 1
                if extra_frame_counter >= extra_frames:
                    squat_start = False
                    if current_video_writer is not None:
                        current_video_writer.release()
                        current_video_writer = None
                    print(f"Completely ended squat segment {segment_count}")
            

            # 写入帧到当前视频段
            if squat_start or (extra_frame_counter > 0 and extra_frame_counter <= extra_frames):
                if current_video_writer is not None:
                    current_video_writer.write(frame)
    cap.release()
    if current_video_writer:
        current_video_writer.release()
    
    segment_files_final = []

    for i in range(len(segment_files)):
        file_name = segment_files[i]
        output_file = segment_file = os.path.join(output_dir, f'squat_segment_{i+1}_second.mp4')
        segment_files_final.append(output_file)
        # 打开深蹲视频
        cap = cv2.VideoCapture(file_name)
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        video_length_seconds = total_frames / fps
        fourcc = cv2.VideoWriter_fourcc(*'H264')
        output_width = frame_width + 500  # 增加500px的宽度用于图表
        out = cv2.VideoWriter(output_file, fourcc, fps, (output_width, frame_height))

        time_values = []
        speed_values = []
        knee_angles = [] 
        hip_angles = []  
        frame_number = 0
        previous_position = None
        side = None

        results = model(file_name)

        for result in results:
            ret, frame = cap.read()
            if not ret:
                break

            all_keypoints = result.keypoints.data  # 所有关键点

            max_area = 0
            largest_person = None

            for keypoints in all_keypoints:
                area = calculate_bounding_box_area(keypoints)
                if area > max_area:
                    max_area = area
                    largest_person = keypoints

            if largest_person is not None:
                left_shoulder = largest_person[5][:2].cpu().numpy()
                left_hip = largest_person[11][:2].cpu().numpy()
                left_knee = largest_person[13][:2].cpu().numpy()
                left_ankle = largest_person[15][:2].cpu().numpy()

                right_shoulder = largest_person[6][:2].cpu().numpy()
                right_hip = largest_person[12][:2].cpu().numpy()
                right_knee = largest_person[14][:2].cpu().numpy()
                right_ankle = largest_person[16][:2].cpu().numpy()

                side, shoulder, hip, knee, ankle = determine_side(side, left_shoulder, left_hip, left_knee, left_ankle, right_shoulder, right_hip, right_knee, right_ankle)

                if previous_position is None:
                    previous_position = (shoulder + hip) / 2
                    frame_number += 1
                    continue

                knee_angle = calculate_angle(hip, knee, ankle)
                knee_angles.append(knee_angle)

                hip_angle = calculate_angle(shoulder, hip, knee)
                hip_angles.append(hip_angle)
                
                avg_position = (shoulder + hip) / 2
                vertical_movement = previous_position[1] - avg_position[1]
                frame_time = frame_number / fps
                speed = vertical_movement * fps
                time_values.append(frame_time)
                speed_values.append(speed)

                previous_position = avg_position

                distance1 = calculate_distance(hip, knee)
                distance2 = calculate_distance(knee, ankle)
                distance3 = calculate_distance(shoulder, hip)
                distance4 = distance1 + distance2 
                ratio1 = distance1 / distance2
                ratio2 = distance3 / distance4

                annotated_frame = result.plot()
                cv2.putText(annotated_frame, f"Femur Length: {distance1:.2f} px", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (238, 173, 14), 2)
                cv2.putText(annotated_frame, f"Tibia Length: {distance2:.2f} px", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (238, 173, 14), 2)
                cv2.putText(annotated_frame, f"Torso Length: {distance3:.2f} px", (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (238, 173, 14), 2)
                cv2.putText(annotated_frame, f"Leg Length: {distance4:.2f} px", (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (238, 173, 14), 2)
                cv2.putText(annotated_frame, f"Femur/Tibia: {ratio1:.2f}", (50, 250), cv2.FONT_HERSHEY_SIMPLEX, 1, (238, 173, 14), 2)
                cv2.putText(annotated_frame, f"Torso/Leg: {ratio2:.2f}", (50, 300), cv2.FONT_HERSHEY_SIMPLEX, 1, (238, 173, 14), 2)

                plot_image = plot_dynamic_chart(time_values, speed_values, knee_angles, hip_angles,video_length_seconds)
                plot_image_resized = cv2.resize(plot_image, (500, frame_height))

                combined_frame = np.hstack((annotated_frame, plot_image_resized))
                out.write(combined_frame)

            frame_number += 1

        cap.release()
        out.release()
      
    return segment_files_final

# if __name__ == "__main__":
#     file_path = r'D:\Titan_Track\backend\uploads\a\20241204_144613\sample6.mp4'
#     output_dir = r'D:\Titan_Track\backend\uploads\a\20241204_144613\test'
#     process_and_analyze_video(file_path,output_dir)
