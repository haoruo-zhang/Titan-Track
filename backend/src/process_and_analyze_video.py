import cv2
from ultralytics import YOLO
import os
import numpy as np
from ultralytics import YOLO
from src.utils import calculate_bounding_box_area, calculate_distance, determine_side, plot_dynamic_chart, calculate_angle

def process_and_analyze_video(video_path, output_dir, yolo_model_path=None):
    """
    Splits a video into multiple segments based on squat detection.
    :param video_path: Path to the input video
    :param output_dir: Directory to store segmented video clips
    :param yolo_model_path: Path to the YOLO model
    :return: List of segmented video file paths
    """
    # If the model path is not specified, dynamically get the default path
    if yolo_model_path is None:
        yolo_model_path = os.path.join(os.getcwd(), "models", "yolov8l-pose.pt")

    # Check if the YOLO model path exists
    if not os.path.exists(yolo_model_path):
        raise FileNotFoundError(f"YOLO model not found at {yolo_model_path}")

    # Load the YOLO model
    model = YOLO(yolo_model_path)

    # Open the video
    cap = cv2.VideoCapture(video_path)
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')

    # Variables to track squat status
    initial_shoulder_pos = None
    squat_start = False
    segment_count = 0
    current_video_writer = None

    threshold_down = 20  # Threshold (in pixels) for detecting significant downward shoulder movement
    threshold_up = 3  # Threshold for detecting the shoulder returning to the initial position
    threshold_horizontal = 30  # Threshold for horizontal movement

    extra_frames = 15  # Number of additional frames to include after squat ends
    extra_frame_counter = 0

    os.makedirs(output_dir, exist_ok=True)
    segment_files = []

    results = model(video_path, stream=True)  # Perform pose detection using YOLO
    for result in results:
        ret, frame = cap.read()
        if not ret:
            break

        all_keypoints = result.keypoints.data
        max_area = 0
        largest_person = None

        # Find the largest detected person
        for keypoints in all_keypoints:
            area = calculate_bounding_box_area(keypoints)
            if area > max_area:
                max_area = area
                largest_person = keypoints

        if largest_person is not None:
            # Get coordinates of key body joints
            side = None
            left_shoulder = largest_person[5][:2].cpu().numpy()
            left_hip = largest_person[11][:2].cpu().numpy()
            left_knee = largest_person[13][:2].cpu().numpy()
            left_ankle = largest_person[15][:2].cpu().numpy()

            right_shoulder = largest_person[6][:2].cpu().numpy()
            right_hip = largest_person[12][:2].cpu().numpy()
            right_knee = largest_person[14][:2].cpu().numpy()
            right_ankle = largest_person[16][:2].cpu().numpy()

            side, shoulder, hip, knee, ankle = determine_side(
                side, left_shoulder, left_hip, left_knee, left_ankle, 
                right_shoulder, right_hip, right_knee, right_ankle
            )

            if initial_shoulder_pos is None:
                # Initialize the shoulder position
                initial_shoulder_pos = shoulder
                continue

            shoulder_vertical_movement = shoulder[1] - initial_shoulder_pos[1]
            shoulder_horizontal_movement = abs(shoulder[0] - initial_shoulder_pos[0])

            # Detect the start of a squat
            if shoulder_vertical_movement > threshold_down and not squat_start and shoulder_horizontal_movement < threshold_horizontal:
                squat_start = True
                extra_frame_counter = 0
                segment_count += 1
                segment_file = os.path.join(output_dir, f'squat_segment_{segment_count}.mp4')
                segment_files.append(segment_file)
                current_video_writer = cv2.VideoWriter(segment_file, fourcc, fps, (width, height))
                print(f"Starting squat segment {segment_count}")

            # Detect the end of a squat
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

            # Write the frame to the current video segment
            if squat_start or (extra_frame_counter > 0 and extra_frame_counter <= extra_frames):
                if current_video_writer is not None:
                    current_video_writer.write(frame)
    
    cap.release()
    if current_video_writer:
        current_video_writer.release()

    segment_files_final = []

    for i, file_name in enumerate(segment_files):
        output_file = os.path.join(output_dir, f'squat_segment_{i+1}_second.mp4')
        segment_files_final.append(output_file)

        # Open squat video
        cap = cv2.VideoCapture(file_name)
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        video_length_seconds = total_frames / fps
        fourcc = cv2.VideoWriter_fourcc(*'H264')
        output_width = frame_width + 500  # Increase width by 500px for charts
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

            all_keypoints = result.keypoints.data  # All keypoints

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

                side, shoulder, hip, knee, ankle = determine_side(
                    side, left_shoulder, left_hip, left_knee, left_ankle, 
                    right_shoulder, right_hip, right_knee, right_ankle
                )

                knee_angle = calculate_angle(hip, knee, ankle)
                knee_angles.append(knee_angle)

                hip_angle = calculate_angle(shoulder, hip, knee)
                hip_angles.append(hip_angle)

                plot_image = plot_dynamic_chart(time_values, speed_values, knee_angles, hip_angles, video_length_seconds)
                plot_image_resized = cv2.resize(plot_image, (500, frame_height))

                combined_frame = np.hstack((frame, plot_image_resized))
                out.write(combined_frame)

            frame_number += 1

        cap.release()
        out.release()
      
    return segment_files_final
