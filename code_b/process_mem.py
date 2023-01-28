import io
import cv2
import mediapipe as mp
import base64
from collections import deque
import imageio.v3 as iio
import numpy as np

from code_b.angles import *
# import memory_profiler
import tempfile
import os


mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose


# @memory_profiler.profile
def process_motion(contents, filename, location):
    # print("Processing video: " + filename)
    content_type, content_string = contents.split(',')
    # content_string = contents
    # name = filename.split('.')[0]
    name = filename

    decoded = base64.b64decode(content_string)
    vid_bytes = io.BytesIO(decoded)
    # print('bytes')

    # with tempfile.NamedTemporaryFile() as temp:
    #     temp.write(decoded)
    #    print(f'Path is: {os.path.abspath(temp.name)}')

    # frames = iio.imread(vid_bytes, plugin='pyav')
    # frames = iio.imread(temp.name, plugin='pyav')
    frames = iio.imiter(vid_bytes, plugin='pyav')
    # print(f'Frames shape is: {frames.shape}')

    # bytes = iio.imwrite('<bytes>', frames, extension='.mp4')
    # print(type(bytes))

    # temp = tempfile.NamedTemporaryFile()
    # temp.write(decoded)

    meta = iio.immeta(decoded, plugin='pyav')
    print(meta)
    # meta = iio.immeta(temp.name, plugin='pyav')
    fps = meta['fps']
    duration = meta['duration']

    try:
        rotation = int(meta['rotate'])
    except KeyError:
        rotation = 360

    rot_angle = 360 - rotation
    frame = next(frames)
    frame = np.rot90(frame, k=rot_angle // 90)
    height, width, _ = frame.shape

    fourcc = cv2.VideoWriter_fourcc(*'h264')
    writer = cv2.VideoWriter(location + '/motion.mp4', fourcc, fps, (width, height))

    save_pelvis_rotation = deque([])
    save_pelvis_tilt = deque([])
    save_pelvis_sway = deque([])
    save_pelvis_thrust = deque([])
    save_pelvis_lift = deque([])
    save_thorax_rotation = deque([])
    save_thorax_bend = deque([])
    save_thorax_sway = deque([])
    save_thorax_thrust = deque([])
    save_thorax_lift = deque([])
    save_thorax_tilt = deque([])
    save_spine_rotation = deque([])
    save_spine_tilt = deque([])
    save_head_rotation = deque([])
    save_head_tilt = deque([])
    save_left_arm_length = deque([])
    save_wrist_angle = deque([])
    save_wrist_tilt = deque([])

    rot = False
    # meta_dict = ffmpeg.probe(file)
    # if int(meta_dict['streams'][0]['tags']['rotate']) == 180:
    #    rot = True
    # i = 0
    # fig, ax = plt.subplots(1, 1)
    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5, model_complexity=2) as pose:
        # for i, image in enumerate(frames.iter_data()):
        for i, image in enumerate(frames):

            image = np.rot90(image, k=rot_angle // 90)

            # Make detection
            results = pose.process(image)

            try:
                landmarks = results.pose_world_landmarks.landmark
                # landmarks_hand = results.left_hand_landmarks.landmark

                shoulder_l = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
                shoulder_r = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
                elbow_l = landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value]
                wrist_l = landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value]
                hip_l = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]
                hip_r = landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value]
                foot_r = landmarks[mp_pose.PoseLandmark.RIGHT_FOOT_INDEX.value]
                foot_l = landmarks[mp_pose.PoseLandmark.LEFT_FOOT_INDEX.value]
                nose = landmarks[mp_pose.PoseLandmark.NOSE.value]
                eye_l = landmarks[mp_pose.PoseLandmark.LEFT_EYE.value]
                eye_r = landmarks[mp_pose.PoseLandmark.RIGHT_EYE.value]
                pinky_l = landmarks[mp_pose.PoseLandmark.LEFT_PINKY.value]
                index_l = landmarks[mp_pose.PoseLandmark.LEFT_INDEX.value]

                if i == 0:
                    # print(i)
                    theta = calc_angle(foot_l, foot_r)
                    c, s = np.cos(theta), np.sin(theta)
                    print(np.degrees(theta))
                    R = np.array([[c, 0, -s], [0, 1, 0], [s, 0, c]], dtype=np.float16)
                    # print(R)
                    # R = np.identity(3)
                    # R = np.flip(R, axis=1)
                    print(R)

                pelvis_r = pelvis_rotation(hip_l, hip_r, R)
                save_pelvis_rotation.append(-pelvis_r)
                # print('pelvis_rotation: ', pelvis_r)

                pelvis_t = pelvis_tilt(hip_l, hip_r, R)
                save_pelvis_tilt.append(-pelvis_t)
                # print('pelvis_tilt: ', pelvis_t)

                pelvis_s = pelvis_sway(foot_l, R)
                save_pelvis_sway.append(-pelvis_s)
                # print('pelvis_sway: ', pelvis_s)

                pelvis_th = pelvis_thrust(foot_l, R)
                save_pelvis_thrust.append(-pelvis_th)
                # print('pelvis_thrust: ', pelvis_th)

                pelvis_l = pelvis_lift(foot_l, R)
                save_pelvis_lift.append(pelvis_l)
                # print('pelvis_lift: ', pelvis_l)

                thorax_r = thorax_rotation(shoulder_l, shoulder_r, R)
                save_thorax_rotation.append(-thorax_r)
                # print('thorax_rotation: ', thorax_r)

                thorax_b = thorax_bend(shoulder_l, shoulder_r, R)
                save_thorax_bend.append(thorax_b)

                thorax_t = thorax_tilt(shoulder_l, shoulder_r, R)
                save_thorax_tilt.append(thorax_t)

                thorax_s = thorax_sway(shoulder_l, shoulder_r, foot_l, R)
                save_thorax_sway.append(thorax_s)
                # print('thorax_sway: ', thorax_s)

                thorax_th = thorax_thrust(shoulder_l, shoulder_r, foot_l, R)
                save_thorax_thrust.append(thorax_th)
                # print('thorax_thrust: ', thorax_th)

                thorax_l = thorax_lift(shoulder_l, shoulder_r, foot_l, R)
                save_thorax_lift.append(thorax_l)
                # print('thorax_lift: ', thorax_l)

                spine_r = spine_rotation(hip_l, hip_r, shoulder_l, shoulder_r, R)
                save_spine_rotation.append(spine_r)
                # print('spine_rotation: ', spine_r)

                spine_t = spine_tilt(hip_l, hip_r, shoulder_l, shoulder_r, R)
                save_spine_tilt.append(spine_t)
                # print('spine_tilt: ', spine_t)

                head_r = head_rotation(eye_l, eye_r, R)
                save_head_rotation.append(head_r)
                # print('head_rotation: ', head_r)

                head_t = head_tilt(eye_l, eye_r, R)
                save_head_tilt.append(head_t)
                # print('head_tilt: ', head_t)

                wrist_a = wrist_angle(pinky_l, index_l, wrist_l, elbow_l, R)
                save_wrist_angle.append(wrist_a)

                wrist_t = wrist_tilt(pinky_l, index_l, wrist_l, elbow_l, R)
                save_wrist_tilt.append(wrist_t)

                left_arm = left_arm_length(shoulder_l, shoulder_r, wrist_l, R)
                save_left_arm_length.append(left_arm)

                # cv2.putText(image, f'Pelvis rotation: {int(pelvis_r)}', (100, 100), cv2.FONT_HERSHEY_SIMPLEX,
                #             1.4, (255, 255, 255),
                #             2, cv2.LINE_AA)
                # cv2.putText(image, f'Thorax tilt: {int(thorax_t)}', (100, 140), cv2.FONT_HERSHEY_SIMPLEX,
                #             1.4,
                #             (255, 255, 255), 2, cv2.LINE_AA)
                # cv2.putText(image, f'Wrist: {int(wrist_t)}', (100, 180), cv2.FONT_HERSHEY_SIMPLEX, 1.4,
                #             (255, 255, 255), 2, cv2.LINE_AA)
                # cv2.putText(image, f'Wrist: {int(angle_w)}', (100, 220), cv2.FONT_HERSHEY_SIMPLEX, 1.4,
                #             (255, 255, 255), 2, cv2.LINE_AA)
                # cv2.putText(image, f'Spine: {int(angle_back)}', (100, 260), cv2.FONT_HERSHEY_SIMPLEX, 1.4,
                #             (255, 255, 255), 2, cv2.LINE_AA)
                # cv2.putText(image, f'Tilt: {int(tilt)}', (100, 300), cv2.FONT_HERSHEY_SIMPLEX, 1.4, (255, 255, 255),
                #             2, cv2.LINE_AA)
                # cv2.putText(image, f'Bal.: {bal}', (100, 340), cv2.FONT_HERSHEY_SIMPLEX, 1.4, (255, 255, 255), 2,
                #             cv2.LINE_AA)

            except:
                pass

            # Recolor back to BGR
            # image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            # Render detections

            mp_drawing.draw_landmarks(
                image,
                results.pose_landmarks,
                mp_pose.POSE_CONNECTIONS,
                landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style()
            )

            # mp_drawing.draw_landmarks(
            #     image,
            #     results.left_hand_landmarks,
            #     mp_pose.HAND_CONNECTIONS,
            #     # landmark_drawing_spec=mp_drawing_styles.get_default_hand_landmarks_style()
            # )

            # cv2. imshow('Mediapipe Feed', image)
            writer.write(image)

            # mp_drawing.plot_landmarks(results.pose_world_landmarks, mp_pose.POSE_CONNECTIONS)
            # fig = plot_landmarks(results.pose_world_landmarks, mp_pose.POSE_CONNECTIONS)
            # plotly save figure as png
            # fig.write_image(f"frame{i}.png")
            # i += 1

        # image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    return save_pelvis_rotation, save_pelvis_tilt, save_pelvis_lift, save_pelvis_sway, save_pelvis_thrust, \
           save_thorax_lift, save_thorax_bend, save_thorax_sway, save_thorax_rotation, save_thorax_thrust, \
           save_thorax_tilt, save_spine_rotation, save_spine_tilt, save_head_rotation, save_head_tilt, save_left_arm_length, save_wrist_angle, save_wrist_tilt, duration