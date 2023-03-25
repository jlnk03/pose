import io
import os.path
import cv2
import mediapipe as mp
import base64
from collections import deque
import imageio.v3 as iio
import imageio
from .angles import *
from PIL import ImageFont, ImageDraw, Image
from flask import url_for
import shutil
from scipy.ndimage.filters import gaussian_filter
import aggdraw
import av
import tempfile
from moviepy.editor import AudioFileClip

# import memory_profiler


def gradient(shape, start_color, end_color):
    gradient = np.ones(shape + (3,), dtype=np.uint8)
    for i in range(3):
        gradient[:, :, i] = np.linspace(start_color[i], end_color[i], shape[0]).reshape(-1, 1)
    return gradient


def blurred_gradient(shape, start_color, end_color, sigma=5):
    gradient_array = gradient(shape, start_color, end_color)
    # return gaussian_filter(gradient_array, sigma=sigma)
    return gradient_array


# Add padding to image
def add_padding(img, padding_size, padding_color=(0, 0, 0)):
    # print(img.shape)
    height, width, _ = img.shape
    # lin_grad = blurred_gradient((height, padding_size), (255, 251, 235), (221, 214, 254)) (233, 213, 255) (236, 252, 203) (255, 251, 235)
    # lin_grad = blurred_gradient((height, padding_size), (31, 41, 55), (31, 41, 55))
    padding = np.full((height, width + padding_size, 3), padding_color, dtype=np.uint8)
    padding[:, padding_size:width + padding_size, :] = img
    # padding[:, :padding_size, :] = lin_grad
    # print(padding.shape)
    return padding


def impact_from_audio(audio_bytes):
    # Create a temporary file and write the BytesIO contents to it
    with tempfile.NamedTemporaryFile(suffix='.mp4') as temp_file:
        temp_file.write(audio_bytes.getvalue())

        # Extract the audio using moviepy
        audio = AudioFileClip(temp_file.name)

        # Convert the audio to a numpy array
        audio_data = audio.to_soundarray()[:, 0]

        if len(audio_data) == 0:
            return -1

        impact_ratio = np.argmax(audio_data) / len(audio_data)
        return impact_ratio


@memory_profiler.profile
def process_motion(contents, filename, location):

    mp_drawing = mp.solutions.drawing_utils
    mp_drawing_styles = mp.solutions.drawing_styles
    mp_pose = mp.solutions.pose

    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)

    with io.BytesIO(decoded) as vid_bytes:

        frames = iio.imiter(vid_bytes, plugin='pyav')

        meta = iio.immeta(decoded, plugin='pyav')
        fps = meta['fps']
        duration = meta['duration']

        n_frames = duration * fps

        if n_frames > 300:
            return -1

        try:
            rotation = int(meta['rotate'])
        except KeyError:
            rotation = 360

        rot_angle = 360 - rotation
        frame = next(frames)
        frame = np.rot90(frame, k=rot_angle // 90)
        height, width, _ = frame.shape
        if width % 2 != 0:
            width += 1

        container = av.open(location + '/motion.mp4', 'w')
        stream = container.add_stream('libx264', rate=np.floor(fps))
        stream.options = {'preset': 'medium', 'crf': '20', 'profile': 'high'}
        stream.width = width
        stream.height = height
        stream.pix_fmt = 'yuv420p'

        # Audio
        impact_ratio = impact_from_audio(vid_bytes)
        duration_ratio = duration * impact_ratio
        # add half a frame
        duration_ratio += 0.008
        impact_ratio = duration_ratio / duration

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
        save_arm_rotation = deque([])
        save_arm_to_ground = deque([])
        arm_position = {'x': [], 'y': [], 'z': []}

        with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5, model_complexity=2) as pose:
            for i, image in enumerate(frames):

                image = np.rot90(image, k=rot_angle // 90)
                image = np.ascontiguousarray(image)

                # Make detection
                results = pose.process(image)

                try:
                    landmarks = results.pose_world_landmarks.landmark

                    shoulder_l = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
                    shoulder_r = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
                    elbow_l = landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value]
                    wrist_l = landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value]
                    wrist_r = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value]
                    hip_l = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]
                    hip_r = landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value]
                    foot_r = landmarks[mp_pose.PoseLandmark.RIGHT_FOOT_INDEX.value]
                    foot_l = landmarks[mp_pose.PoseLandmark.LEFT_FOOT_INDEX.value]
                    eye_l = landmarks[mp_pose.PoseLandmark.LEFT_EAR.value]
                    eye_r = landmarks[mp_pose.PoseLandmark.RIGHT_EAR.value]
                    pinky_l = landmarks[mp_pose.PoseLandmark.LEFT_PINKY.value]
                    index_l = landmarks[mp_pose.PoseLandmark.LEFT_INDEX.value]

                    if i == 0:
                        theta = calc_angle(foot_l, foot_r)
                        c, s = np.cos(theta), np.sin(theta)
                        R = np.array([[c, 0, -s], [0, 1, 0], [s, 0, c]], dtype=np.float16)

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

                    arm_rotation_l = arm_rotation(wrist_r, shoulder_l, shoulder_r, R)
                    save_arm_rotation.append(arm_rotation_l)

                    arm_ground = arm_to_ground(wrist_r, shoulder_r, R)
                    save_arm_to_ground.append(arm_ground)

                    arm_v = [foot_l.x - wrist_l.x, foot_l.y - wrist_l.y, foot_l.z - wrist_l.z]
                    arm_v = R @ arm_v

                    arm_position['x'].append(arm_v[0])
                    arm_position['y'].append(arm_v[2])
                    arm_position['z'].append(arm_v[1])

                    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

                    mp_drawing.draw_landmarks(
                        image,
                        results.pose_landmarks,
                        mp_pose.POSE_CONNECTIONS,
                        landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style()
                    )

                    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

                    # convert the image to numpy array
                    image = np.asarray(image)

                except Exception as e:
                    shutil.rmtree(location)
                    break

                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

                # Write with pyav
                frame = av.VideoFrame.from_ndarray(image, format='bgr24')
                for packet in stream.encode(frame):
                    container.mux(packet)

        # Flush the stream to make sure all frames have been written
        for packet in stream.encode():
            container.mux(packet)
        stream.close()
        container.close()

    return save_pelvis_rotation, save_pelvis_tilt, save_pelvis_lift, save_pelvis_sway, save_pelvis_thrust, \
        save_thorax_lift, save_thorax_bend, save_thorax_sway, save_thorax_rotation, save_thorax_thrust, \
        save_thorax_tilt, save_spine_rotation, save_spine_tilt, save_head_rotation, save_head_tilt, \
        save_left_arm_length, save_wrist_angle, save_wrist_tilt, save_arm_rotation, save_arm_to_ground, \
        arm_position, duration, fps, impact_ratio


def draw_rounded_rectangle_agg(img, pt1, pt2, color, radius):
    x1, y1 = pt1
    x2, y2 = pt2
    brush = aggdraw.Brush(color)
    pen = aggdraw.Pen(color, 1)
    draw = aggdraw.Draw(img)
    draw.rectangle((x1 + radius, y1, x2 - radius, y2), brush, pen)
    draw.rectangle((x1, y1 + radius, x2, y2 - radius), brush, pen)
    draw.ellipse((x1, y1, x1 + 2 * radius, y1 + 2 * radius), brush, pen)
    draw.ellipse((x2 - 2 * radius, y1, x2, y1 + 2 * radius), brush, pen)
    draw.ellipse((x1, y2 - 2 * radius, x1 + 2 * radius, y2), brush, pen)
    draw.ellipse((x2 - 2 * radius, y2 - 2 * radius, x2, y2), brush, pen)
    draw.flush()


if __name__ == '__main__':
    pass
