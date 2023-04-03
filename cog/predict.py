# Prediction interface for Cog ⚙️
# https://github.com/replicate/cog/blob/main/docs/python.md

from cog import BasePredictor, Input, Path, File, BaseModel
import mediapipe as mp
from scipy import signal
import numpy as np
import tempfile
from moviepy.editor import AudioFileClip
from collections import deque
import io
import imageio.v3 as iio
import av
import cv2
import base64


def filter_data(data, fps):
    Wn = 4
    b, a = signal.butter(4, Wn, 'low', fs=fps)
    data = signal.filtfilt(b, a, data, method='gust')
    return data


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


def calc_angle(landmark1, landmark2):
    goal_direction = np.array([landmark1.x - landmark2.x, 0, landmark1.z - landmark2.z])
    camera = np.array([0, 0, 1])

    angle = np.arccos(camera.dot(goal_direction) / (np.linalg.norm(camera) * np.linalg.norm(goal_direction)))

    return angle


class Output(BaseModel):
    angles: list
    video: Path


class Predictor(BasePredictor):

    def setup(self):
        """Load the model into memory to make running multiple predictions efficient"""
        # self.model = torch.load("./weights.pth")
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        self.mp_pose = mp.solutions.pose
        self.pose = mp.solutions.pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5,
                                           model_complexity=2)

    def predict(
            self,
            video: str = Input(description="Input video to detect pose")
    ) -> tuple:
        """Run a single prediction on the model"""
        # processed_input = preprocess(image)
        # output = self.model(processed_image, scale)
        # return postprocess(output)

        # decoded = open(video, 'rb').read()

        decoded = base64.b64decode(video)

        # decoded = video

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

            out_path = Path('/tmp/motion.mp4')

            container = av.open('/tmp/motion.mp4', 'w')
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

            for i, image in enumerate(frames):

                print(f'Processing frame {i}')

                image = np.rot90(image, k=rot_angle // 90)
                image = np.ascontiguousarray(image)

                # Make detection
                results = self.pose.process(image)

                try:
                    landmarks = results.pose_world_landmarks.landmark

                    shoulder_l = landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value]
                    shoulder_r = landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
                    elbow_l = landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW.value]
                    wrist_l = landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST.value]
                    wrist_r = landmarks[self.mp_pose.PoseLandmark.RIGHT_WRIST.value]
                    hip_l = landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value]
                    hip_r = landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP.value]
                    foot_r = landmarks[self.mp_pose.PoseLandmark.RIGHT_FOOT_INDEX.value]
                    foot_l = landmarks[self.mp_pose.PoseLandmark.LEFT_FOOT_INDEX.value]
                    eye_l = landmarks[self.mp_pose.PoseLandmark.LEFT_EAR.value]
                    eye_r = landmarks[self.mp_pose.PoseLandmark.RIGHT_EAR.value]
                    pinky_l = landmarks[self.mp_pose.PoseLandmark.LEFT_PINKY.value]
                    index_l = landmarks[self.mp_pose.PoseLandmark.LEFT_INDEX.value]

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

                    # image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

                    self.mp_drawing.draw_landmarks(
                        image,
                        results.pose_landmarks,
                        self.mp_pose.POSE_CONNECTIONS,
                        landmark_drawing_spec=self.mp_drawing_styles.get_default_pose_landmarks_style()
                    )

                    # image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

                    # convert the image to numpy array
                    image = np.asarray(image)

                except Exception as e:
                    # shutil.rmtree(location)
                    break

                # image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

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
            shoulder_l_s = filter_data(R @ np.array(shoulder_l_s).T, fps)
            shoulder_r_s = filter_data(R @ np.array(shoulder_r_s).T, fps)
            wrist_l_s = filter_data(R @ np.array(wrist_l_s).T, fps)
            wrist_r_s = filter_data(R @ np.array(wrist_r_s).T, fps)
            hip_l_s = filter_data(R @ np.array(hip_l_s).T, fps)
            hip_r_s = filter_data(R @ np.array(hip_r_s).T, fps)
            foot_l_s = filter_data(R @ np.array(foot_l_s).T, fps)
            eye_l_s = filter_data(R @ np.array(eye_l_s).T, fps)
            eye_r_s = filter_data(R @ np.array(eye_r_s).T, fps)
            pinky_l_s = filter_data(R @ np.array(pinky_l_s).T, fps)
            index_l_s = filter_data(R @ np.array(index_l_s).T, fps)
            arm_v = foot_l_s - wrist_l_s
            arm_v = filter_data(arm_v, fps)

            return shoulder_l_s, shoulder_r_s, wrist_l_s, wrist_r_s, hip_l_s, hip_r_s, foot_l_s, eye_l_s, eye_r_s, pinky_l_s, index_l_s, arm_v, \
                duration, fps, impact_ratio, \
                out_path