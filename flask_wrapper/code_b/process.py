import io
import os.path
import cv2
import mediapipe as mp
import base64
from collections import deque
import imageio.v3 as iio
import imageio
from .angles_2 import *
from PIL import ImageFont, ImageDraw, Image
from flask import url_for
import shutil
from scipy.ndimage.filters import gaussian_filter
import aggdraw
import av
import tempfile
from moviepy.editor import AudioFileClip
import numpy as np


def impact_from_audio(audio_bytes):
    """Calculate the impact ratio from an audio file in BytesIO format.

       Args:
           audio_bytes (BytesIO): A BytesIO object containing the audio file.

       Returns:
           float: The impact ratio, defined as the position of the highest-amplitude
               sample in the audio array, normalized by the length of the array.
               Returns -1 if the array is empty.
       """

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
        return float(impact_ratio)


# @memory_profiler.profile
def process_motion(contents, filename, location):
    """Processes a motion video file and extracts pose data for analysis.

       Args:
           contents (str): The contents of the motion video file.
           filename (str): The name of the motion video file.
           location (str): The directory where the motion video file will be saved.

       Returns:
           int: Returns -1 if the video has more than 300 frames.
           Tuple[deque]: Returns deques of pose data for each body part extracted from the video.
       """

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
            # Too many frames
            # Comma required for tuple
            return -1, 'Too many frames'

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

        shoulder_l_s = deque()
        shoulder_r_s = deque()
        elbow_l_s = deque()
        wrist_l_s = deque()
        wrist_r_s = deque()
        hip_l_s = deque()
        hip_r_s = deque()
        foot_r_s = deque()
        foot_l_s = deque()
        eye_l_s = deque()
        eye_r_s = deque()
        pinky_l_s = deque()
        index_l_s = deque()

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
                        R = np.array([[c, 0, -s], [0, 1, 0], [s, 0, c]])

                    shoulder_l_v = np.array([shoulder_l.x, shoulder_l.y, shoulder_l.z])
                    shoulder_r_v = np.array([shoulder_r.x, shoulder_r.y, shoulder_r.z])
                    elbow_l_v = np.array([elbow_l.x, elbow_l.y, elbow_l.z])
                    wrist_l_v = np.array([wrist_l.x, wrist_l.y, wrist_l.z])
                    wrist_r_v = np.array([wrist_r.x, wrist_r.y, wrist_r.z])
                    hip_l_v = np.array([hip_l.x, hip_l.y, hip_l.z])
                    hip_r_v = np.array([hip_r.x, hip_r.y, hip_r.z])
                    foot_r_v = np.array([foot_r.x, foot_r.y, foot_r.z])
                    foot_l_v = np.array([foot_l.x, foot_l.y, foot_l.z])
                    eye_l_v = np.array([eye_l.x, eye_l.y, eye_l.z])
                    eye_r_v = np.array([eye_r.x, eye_r.y, eye_r.z])
                    pinky_l_v = np.array([pinky_l.x, pinky_l.y, pinky_l.z])
                    index_l_v = np.array([index_l.x, index_l.y, index_l.z])

                    shoulder_l_s.append(shoulder_l_v)
                    shoulder_r_s.append(shoulder_r_v)
                    elbow_l_s.append(elbow_l_v)
                    wrist_l_s.append(wrist_l_v)
                    wrist_r_s.append(wrist_r_v)
                    hip_l_s.append(hip_l_v)
                    hip_r_s.append(hip_r_v)
                    foot_r_s.append(foot_r_v)
                    foot_l_s.append(foot_l_v)
                    eye_l_s.append(eye_l_v)
                    eye_r_s.append(eye_r_v)
                    pinky_l_s.append(pinky_l_v)
                    index_l_s.append(index_l_v)

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

        # Rotate data
        shoulder_l_s = R @ np.array(shoulder_l_s).T
        shoulder_r_s = R @ np.array(shoulder_r_s).T
        elbow_l_s = R @ np.array(elbow_l_s).T
        wrist_l_s = R @ np.array(wrist_l_s).T
        wrist_r_s = R @ np.array(wrist_r_s).T
        hip_l_s = R @ np.array(hip_l_s).T
        hip_r_s = R @ np.array(hip_r_s).T
        foot_r_s = R @ np.array(foot_r_s).T
        foot_l_s = R @ np.array(foot_l_s).T
        eye_l_s = R @ np.array(eye_l_s).T
        eye_r_s = R @ np.array(eye_r_s).T
        pinky_l_s = R @ np.array(pinky_l_s).T
        index_l_s = R @ np.array(index_l_s).T
        arm_v = foot_l_s - wrist_l_s
        arm_v = R @ arm_v

        # Calculate angles
        pelvis_r = pelvis_rotation(hip_l_s, hip_r_s)
        pelvis_t = pelvis_tilt(hip_l_s, hip_r_s)
        pelvis_s = pelvis_sway(foot_l_s)
        pelvis_th = pelvis_thrust(foot_l_s)
        pelvis_l = pelvis_lift(foot_l_s)
        thorax_r = thorax_rotation(shoulder_l_s, shoulder_r_s)
        thorax_b = thorax_bend(shoulder_l_s, shoulder_r_s)
        thorax_t = thorax_tilt(shoulder_l_s, shoulder_r_s)
        thorax_s = thorax_sway(shoulder_l_s, shoulder_r_s, foot_l_s)
        thorax_th = thorax_thrust(shoulder_l_s, shoulder_r_s, foot_l_s)
        thorax_l = thorax_lift(shoulder_l_s, shoulder_r_s, foot_l_s)
        spine_r = spine_rotation(hip_l_s, hip_r_s, shoulder_l_s, shoulder_r_s)
        spine_t = spine_tilt(hip_l_s, hip_r_s, shoulder_l_s, shoulder_r_s)
        head_r = head_rotation(eye_l_s, eye_r_s)
        head_t = head_tilt(eye_l_s, eye_r_s)
        wist_a = wrist_angle(pinky_l_s, index_l_s, wrist_l_s, wrist_r_s)
        wrist_t = wrist_tilt(pinky_l_s, index_l_s, wrist_l_s, wrist_r_s)
        left_arm = left_arm_length(shoulder_l_s, shoulder_r_s, wrist_l_s)
        arm_rotation_l = arm_rotation(wrist_l_s, shoulder_l_s, shoulder_r_s)
        arm_ground = arm_to_ground(wrist_l_s, shoulder_l_s)
        arm_position = {'x': arm_v[0].tolist(), 'y': arm_v[2].tolist(), 'z': arm_v[1].tolist()}

    return pelvis_r, pelvis_t, pelvis_s, pelvis_th, pelvis_l, thorax_r, thorax_b, thorax_t, thorax_s, thorax_th, \
        thorax_l, spine_r, spine_t, head_r, head_t, wist_a, wrist_t, left_arm, arm_rotation_l, arm_ground, \
        arm_position, duration, fps, impact_ratio


if __name__ == '__main__':
    pass
