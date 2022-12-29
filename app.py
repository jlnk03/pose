import mediapipe as mp
import plotly.graph_objects as go
import plotly.io as pio
import plotly.express as px
from dash import Dash
from dash import html, dcc
from dash.dependencies import Input, Output
import pandas as pd
from scipy import signal
import io
import base64
from collections import deque
import imageio.v3 as iio
import numpy as np

# Tools for mp to draw the pose
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose
# mp_pose = mp.solutions.holistic

# Set theme for dash
pio.templates.default = "plotly_white"

# Hide plotly logo
config = dict({'displaylogo': False})

_PRESENCE_THRESHOLD = 0.5
_VISIBILITY_THRESHOLD = 0.5


def plot_landmarks(
        landmark_list,
        connections=None,
        angle='connection'
):
    if not landmark_list:
        return
    plotted_landmarks = {}
    for idx, landmark in enumerate(landmark_list.landmark):
        if (
                landmark.HasField("visibility")
                and landmark.visibility < _VISIBILITY_THRESHOLD
        ) or (
                landmark.HasField("presence") and landmark.presence < _PRESENCE_THRESHOLD
        ):
            continue
        plotted_landmarks[idx] = (-landmark.z, landmark.x, -landmark.y)
    if connections:
        out_cn = []
        num_landmarks = len(landmark_list.landmark)
        # Draws the connections if the start and end landmarks are both visible.
        for connection in connections:
            start_idx = connection[0]
            end_idx = connection[1]
            if not (0 <= start_idx < num_landmarks and 0 <= end_idx < num_landmarks):
                raise ValueError(
                    f"Landmark index is out of range. Invalid connection "
                    f"from landmark #{start_idx} to landmark #{end_idx}."
                )
            if start_idx in plotted_landmarks and end_idx in plotted_landmarks:
                landmark_pair = [
                    plotted_landmarks[start_idx],
                    plotted_landmarks[end_idx],
                ]
                out_cn.append(
                    dict(
                        xs=[landmark_pair[0][0], landmark_pair[1][0]],
                        ys=[landmark_pair[0][1], landmark_pair[1][1]],
                        zs=[landmark_pair[0][2], landmark_pair[1][2]],
                    )
                )
        cn2 = {"xs": [], "ys": [], "zs": []}
        for pair in out_cn:
            for k in pair.keys():
                cn2[k].append(pair[k][0])
                cn2[k].append(pair[k][1])
                cn2[k].append(None)

    df = pd.DataFrame(plotted_landmarks).T.rename(columns={0: "z", 1: "x", 2: "y"})
    df["lm"] = df.index.map(lambda s: mp_pose.PoseLandmark(s).name).values
    fig = (
        px.scatter_3d(df, x="z", y="x", z="y", hover_name="lm")
        .update_traces(marker={"color": "red"})
        .update_layout(
            margin={"l": 0, "r": 0, "t": 0, "b": 0},
            scene={"camera": {"eye": {"x": 2.1, "y": 0, "z": 0}}},
        )
    )
    fig.add_traces(
        [
            go.Scatter3d(
                x=cn2["xs"],
                y=cn2["ys"],
                z=cn2["zs"],
                mode="lines",
                line={"color": "black", "width": 5},
                name=angle,
            )
        ]
    )

    return fig


# Random inititalization for data
def rand(length, size):
    full = [np.full(length, np.random.randint(0, 30)) for _ in range(size)]
    return full


save_pelvis_rotation, save_pelvis_tilt, save_pelvis_lift, save_pelvis_sway, save_pelvis_thrust, \
save_thorax_lift, save_thorax_bend, save_thorax_sway, save_thorax_rotation, save_thorax_thrust, \
save_thorax_tilt, save_spine_rotation, save_spine_tilt, save_head_rotation, save_head_tilt, save_left_arm_length, \
save_wrist_angle, save_wrist_tilt = rand(100, 18)

duration = 10
timeline = np.linspace(0, duration, len(save_pelvis_rotation))


def filter_data(data):
    b, a = signal.butter(3, 0.05)
    data = signal.filtfilt(b, a, data)
    return data


def calc_angle(landmark1, landmark2):
    goal_direction = np.array([landmark1.x - landmark2.x, 0, landmark1.z - landmark2.z])
    camera = np.array([0, 0, 1])

    # angle = np.arccos(camera.dot(goal_direction) / (np.linalg.norm(camera) * np.linalg.norm(goal_direction)))
    # angle = np.degrees(angle)
    # angle between goal direction and camera with atan2
    angle = np.arctan2(goal_direction[0], goal_direction[2])

    return angle


def angle_hip(hip_l, hip_r):
    hip_v = np.array([hip_l.x - hip_r.x, hip_l.y - hip_r.y, hip_l.z - hip_r.z])
    normal = np.array([0, 0, 1])
    angle = np.arccos(normal.dot(hip_v) / (np.linalg.norm(normal) * np.linalg.norm(hip_v)))
    angle = 90 - np.degrees(angle)

    return angle


def angle_ground(left, right):
    vector = np.array([left.x - right.x, left.y - right.y, left.z - right.z])
    normal = np.array([0, 1, 0])
    angle = np.arccos(normal.dot(vector) / (np.linalg.norm(normal) * np.linalg.norm(vector)))
    angle = 90 - np.degrees(angle)

    return angle


def back_angle(shoulder_l, shoulder_r):
    sl = np.array([shoulder_l.x, shoulder_l.y, shoulder_l.z])
    sr = np.array([shoulder_r.x, shoulder_r.y, shoulder_r.z])
    connection = np.array(sl - sr)
    spine = sl + 0.5 * connection
    normal = np.array([0, 1, 0])
    angle = np.arccos(normal.dot(spine) / (np.linalg.norm(normal) * np.linalg.norm(spine)))
    angle = 90 - np.degrees(angle)

    return angle


def tilt_angle(shoulder_l, shoulder_r):
    sl = np.array([shoulder_l.x, shoulder_l.y, shoulder_l.z])
    sr = np.array([shoulder_r.x, shoulder_r.y, shoulder_r.z])
    connection = np.array(sl - sr)
    spine = sl + 0.5 * connection
    normal = np.array([0, 1, 0])
    angle = np.arccos(normal.dot(spine) / (np.linalg.norm(normal) * np.linalg.norm(spine)))
    # angle = 90 - np.degrees(angle)

    return angle


def mass_balance(foot_l, foot_r):
    left = np.array([foot_l.x, foot_l.y, foot_l.z])
    right = np.array([foot_r.x, foot_r.y, foot_r.z])
    distance_l = np.linalg.norm(left)
    distance_r = np.linalg.norm(right)

    return round(distance_l - distance_r, 4)


# def angle_xy(left, right):
#     vector = np.array([left.x - right.x, 0, left.z - right.z])
#     normal = np.array([0, 0, 1])
#     angle = np.arccos(normal.dot(vector) / (np.linalg.norm(normal) * np.linalg.norm(vector)))
#     angle = 90 - np.degrees(angle)
#
#     return angle


def pelvis_rotation(hip_l, hip_r, r):
    hip_v = r @ np.array([hip_l.x - hip_r.x, 0, hip_l.z - hip_r.z])
    normal = np.array([0, 0, 1])
    # angle = np.arccos(normal.dot(hip_v) / (np.linalg.norm(normal) * np.linalg.norm(hip_v)))
    # angle between hip vector and normal with atan2
    angle = (np.arctan2(hip_v[0], hip_v[2]))

    return np.degrees(angle)


def pelvis_tilt(hip_l, hip_r, r):
    hip_v = r @ np.array([hip_l.x - hip_r.x, hip_l.y - hip_r.y, hip_l.z - hip_r.z])
    normal = np.array([0, 1, 0])
    angle = np.arccos(normal.dot(hip_v) / (np.linalg.norm(normal) * np.linalg.norm(hip_v)))

    return 90 - np.degrees(angle)


def pelvis_sway(foot_l, r):
    hip_v = r @ np.array([0, 0, foot_l.z])

    return hip_v[2]


def pelvis_thrust(foot_l, r):
    hip_v = r @ np.array([foot_l.x, 0, 0])

    return hip_v[0]


def pelvis_lift(foot_l, r):
    hip_v = r @ np.array([0, foot_l.y, 0])

    return hip_v[1]


def thorax_rotation(shoulder_l, shoulder_r, r):
    shoulder_v = r @ np.array([shoulder_l.x - shoulder_r.x, 0, shoulder_l.z - shoulder_r.z])
    normal = np.array([0, 0, 1])
    # angle = np.arccos(normal.dot(shoulder_v) / (np.linalg.norm(normal) * np.linalg.norm(shoulder_v)))
    # angle between shoulder vector and normal with atan2
    angle = (np.arctan2(shoulder_v[0], shoulder_v[2]))

    return np.degrees(angle)


def thorax_tilt(shoulder_l, shoulder_r, r):
    shoulder_v = r @ np.array([shoulder_l.x - shoulder_r.x, shoulder_l.y - shoulder_r.y, shoulder_l.z - shoulder_r.z])
    shoulder_l = r @ np.array([shoulder_l.x, shoulder_l.y, shoulder_l.z])
    spine = shoulder_l - 0.5 * shoulder_v
    spine[0] = 0
    normal = np.array([0, 1, 0])
    angle = np.arccos(normal.dot(spine) / (np.linalg.norm(normal) * np.linalg.norm(spine)))
    # angle between shoulder vector and normal with atan2
    # angle = np.arctan2(spine[1], spine[2])

    return 180 - np.degrees(angle)


def thorax_bend(shoulder_l, shoulder_r, r):
    shoulder_v = r @ np.array([shoulder_l.x - shoulder_r.x, shoulder_l.y - shoulder_r.y, shoulder_l.z - shoulder_r.z])
    shoulder_l = r @ np.array([shoulder_l.x, shoulder_l.y, shoulder_l.z])
    spine = shoulder_l - 0.5 * shoulder_v
    spine[2] = 0
    normal = np.array([0, 1, 0])
    angle = np.arccos(normal.dot(spine) / (np.linalg.norm(normal) * np.linalg.norm(spine)))

    return 180 - np.degrees(angle)


def thorax_sway(shoulder_l, shoulder_r, foot_l, r):
    shoulder_v = r @ np.array([0, 0, shoulder_l.z - shoulder_r.z])
    shoulder_l = r @ np.array([0, 0, shoulder_l.z])
    foot_l = r @ np.array([0, 0, foot_l.z])
    spine = shoulder_l - 0.5 * shoulder_v
    sway = spine - foot_l

    return sway[2]


def thorax_thrust(shoulder_l, shoulder_r, foot_l, r):
    shoulder_v = r @ np.array([shoulder_l.x - shoulder_r.x, 0, 0])
    shoulder_l = r @ np.array([shoulder_l.x, 0, 0])
    foot_l = r @ np.array([foot_l.x, 0, 0])
    spine = shoulder_l - 0.5 * shoulder_v
    thrust = spine - foot_l

    return thrust[0]


def thorax_lift(shoulder_l, shoulder_r, foot_l, r):
    shoulder_v = r @ np.array([0, shoulder_l.y - shoulder_r.y, 0])
    shoulder_l = r @ np.array([0, shoulder_l.y, 0])
    foot_l = r @ np.array([0, foot_l.y, 0])
    spine = shoulder_l - 0.5 * shoulder_v
    lift = spine - foot_l

    return lift[1]


# rotation between spine and pelvis
def spine_rotation(hip_l, hip_r, shoulder_l, shoulder_r, r):
    hip_v = r @ np.array([hip_l.x - hip_r.x, 0, hip_l.z - hip_r.z])
    shoulder_v = r @ np.array([shoulder_l.x - shoulder_r.x, 0, shoulder_l.z - shoulder_r.z])
    # angle = np.arccos(hip_v.dot(shoulder_v) / (np.linalg.norm(hip_v) * np.linalg.norm(shoulder_v)))
    # angle between hip vector and shoulder vector with atan2
    angle = (np.arctan2(hip_v[2] * shoulder_v[0] - hip_v[0] * shoulder_v[2],
                        hip_v[2] * shoulder_v[2] + hip_v[0] * shoulder_v[0]))

    return np.degrees(angle)


# tilt between spine and pelvis
def spine_tilt(hip_l, hip_r, shoulder_l, shoulder_r, r):
    hip_v = r @ np.array([hip_l.x - hip_r.x, hip_l.y - hip_r.y, hip_l.z - hip_r.z])
    shoulder_v = r @ np.array([shoulder_l.x - shoulder_r.x, shoulder_l.y - shoulder_r.y, shoulder_l.z - shoulder_r.z])
    angle = np.arccos(hip_v.dot(shoulder_v) / (np.linalg.norm(hip_v) * np.linalg.norm(shoulder_v)))

    return np.degrees(angle)


# head rotation
def head_rotation(eye_l, eye_r, r):
    eye_v = r @ np.array([eye_l.x - eye_r.x, 0, eye_l.z - eye_r.z])
    normal = np.array([0, 0, 1])
    # angle = np.arccos(normal.dot(eye_v) / (np.linalg.norm(normal) * np.linalg.norm(eye_v)))
    # angle between eye vector and normal with atan2
    angle = (np.arctan2(eye_v[0], eye_v[2]))

    return np.degrees(angle)


# head tilt
def head_tilt(eye_l, eye_r, r):
    eye_v = r @ np.array([eye_l.x - eye_r.x, eye_l.y - eye_r.y, eye_l.z - eye_r.z])
    eye_v[0] = 0
    normal = np.array([0, 0, 1])
    angle = np.arccos(normal.dot(eye_v) / (np.linalg.norm(normal) * np.linalg.norm(eye_v)))

    return np.degrees(angle)


# distance from spine to left wrist
def left_arm_length(shoulder_l, shoulder_r, wrist_l, r):
    shoulder_v = r @ np.array([shoulder_l.x - shoulder_r.x, shoulder_l.y - shoulder_r.y, shoulder_l.z - shoulder_r.z])
    shoulder_l = r @ np.array([shoulder_l.x, shoulder_l.y, shoulder_l.z])
    wrist_l = r @ np.array([wrist_l.x, wrist_l.y, wrist_l.z])
    spine = shoulder_l - 0.5 * shoulder_v
    length = np.linalg.norm(spine - wrist_l)

    return length


def wrist_angle(pinky_l, index_l, wrist_l, elbow_l, r):
    pinky_l = r @ np.array([pinky_l.x, pinky_l.y, pinky_l.z])
    index_l = r @ np.array([index_l.x, index_l.y, index_l.z])
    wrist_l = r @ np.array([wrist_l.x, wrist_l.y, wrist_l.z])
    elbow_l = r @ np.array([elbow_l.x, elbow_l.y, elbow_l.z])
    pinky_v = pinky_l - wrist_l
    index_v = index_l - wrist_l
    normal = np.cross(pinky_v, index_v)
    arm_l = wrist_l - elbow_l
    # angle = np.arccos(normal.dot(arm_l) / (np.linalg.norm(normal) * np.linalg.norm(arm_l)))
    # angle between normal and arm vector with atan2
    angle = (np.arctan2(normal[0] * arm_l[2] - normal[2] * arm_l[0],
                        normal[2] * arm_l[2] + normal[0] * arm_l[0]))

    return np.degrees(angle) + 90

def wrist_tilt(pinky_l, index_l, wrist_l, elbow_l, r):
    pinky_l = r @ np.array([pinky_l.x, pinky_l.y, pinky_l.z])
    index_l = r @ np.array([index_l.x, index_l.y, index_l.z])
    wrist_l = r @ np.array([wrist_l.x, wrist_l.y, wrist_l.z])
    elbow_l = r @ np.array([elbow_l.x, elbow_l.y, elbow_l.z])
    hand_v = pinky_l - index_l
    arm_l = wrist_l - elbow_l
    # angle with atan2
    angle = (np.arctan2(hand_v[0] * arm_l[2] - hand_v[2] * arm_l[0],
                        hand_v[2] * arm_l[2] + hand_v[0] * arm_l[0]))

    return np.degrees(angle)


def process_motion(contents, filename):
    print("Processing video: " + filename)
    content_type, content_string = contents.split(',')
    name = filename.split('.')[0]

    decoded = base64.b64decode(content_string)
    vid_bytes = io.BytesIO(decoded)

    frames = iio.imread(vid_bytes, plugin='pyav')
    _, height, width, _ = frames.shape

    # bytes = iio.imwrite('<bytes>', frames, extension='.mp4')
    # print(type(bytes))

    # temp = tempfile.NamedTemporaryFile()
    # temp.write(decoded)

    meta = iio.immeta(decoded, plugin='pyav')
    fps = meta['fps']
    duration = meta['duration']

    # fourcc = cv2.VideoWriter_fourcc(*'h264')
    # writer = cv2.VideoWriter('out/' + name + '_motion.mp4', fourcc, fps, (width, height))

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
    i = 0
    # fig, ax = plt.subplots(1, 1)
    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5, model_complexity=2) as pose:
        # for i, image in enumerate(frames.iter_data()):
        for i, image in enumerate(frames):

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
                    theta = calc_angle(hip_l, hip_r)
                    c, s = np.cos(theta), np.sin(theta)
                    print(np.degrees(theta))
                    R = np.array([[c, 0, -s], [0, 1, 0], [s, 0, c]])
                    # print(R)
                    # R = np.identity(3)
                    # R = np.flip(R, axis=1)
                    print(R)

                pelvis_r = pelvis_rotation(hip_l, hip_r, R)
                save_pelvis_rotation.append(pelvis_r)
                # print('pelvis_rotation: ', pelvis_r)

                pelvis_t = pelvis_tilt(hip_l, hip_r, R)
                save_pelvis_tilt.append(pelvis_t)
                # print('pelvis_tilt: ', pelvis_t)

                pelvis_s = pelvis_sway(foot_l, R)
                save_pelvis_sway.append(pelvis_s)
                # print('pelvis_sway: ', pelvis_s)

                pelvis_th = pelvis_thrust(foot_l, R)
                save_pelvis_thrust.append(pelvis_th)
                # print('pelvis_thrust: ', pelvis_th)

                pelvis_l = pelvis_lift(foot_l, R)
                save_pelvis_lift.append(pelvis_l)
                # print('pelvis_lift: ', pelvis_l)

                thorax_r = thorax_rotation(shoulder_l, shoulder_r, R)
                save_thorax_rotation.append(thorax_r)
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
            # image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

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
            # writer.write(image)

            # mp_drawing.plot_landmarks(results.pose_world_landmarks, mp_pose.POSE_CONNECTIONS)
            # fig = plot_landmarks(results.pose_world_landmarks, mp_pose.POSE_CONNECTIONS)
            # plotly save figure as png
            # fig.write_image(f"frame{i}.png")
            i += 1

        # image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    return save_pelvis_rotation, save_pelvis_tilt, save_pelvis_lift, save_pelvis_sway, save_pelvis_thrust, \
           save_thorax_lift, save_thorax_bend, save_thorax_sway, save_thorax_rotation, save_thorax_thrust, \
           save_thorax_tilt, save_spine_rotation, save_spine_tilt, save_head_rotation, save_head_tilt, save_left_arm_length, save_wrist_angle, save_wrist_tilt, duration


# Update plots after video is processed/callback
def update_plots(save_pelvis_rotation, save_pelvis_tilt, save_pelvis_lift, save_pelvis_sway, save_pelvis_thrust,
                 save_thorax_lift, save_thorax_bend, save_thorax_sway, save_thorax_rotation, save_thorax_thrust,
                 save_thorax_tilt, save_spine_rotation, save_spine_tilt, save_head_rotation, save_head_tilt,
                 save_left_arm_length, save_wrist_angle, save_wrist_tilt, duration):
    converted = [filter_data(np.array(name)) for name in
                 [save_pelvis_rotation, save_pelvis_tilt, save_pelvis_lift, save_pelvis_sway, save_pelvis_thrust,
                  save_thorax_lift, save_thorax_bend, save_thorax_sway, save_thorax_rotation, save_thorax_thrust,
                  save_thorax_tilt, save_spine_rotation, save_spine_tilt, save_head_rotation, save_head_tilt,
                  save_left_arm_length, save_wrist_angle, save_wrist_tilt]]

    save_pelvis_rotation, save_pelvis_tilt, save_pelvis_lift, save_pelvis_sway, save_pelvis_thrust, \
    save_thorax_lift, save_thorax_bend, save_thorax_sway, save_thorax_rotation, save_thorax_thrust, \
    save_thorax_tilt, save_spine_rotation, save_spine_tilt, save_head_rotation, save_head_tilt, save_left_arm_length, save_wrist_angle, save_wrist_tilt = converted

    timeline = np.linspace(0, duration, len(save_pelvis_rotation))

    save_pelvis_lift = save_pelvis_lift - save_pelvis_lift[0]
    save_pelvis_sway = save_pelvis_sway - save_pelvis_sway[0]
    save_pelvis_thrust = save_pelvis_thrust - save_pelvis_thrust[0]
    save_thorax_lift = save_thorax_lift - save_thorax_lift[0]
    save_thorax_sway = save_thorax_sway - save_thorax_sway[0]
    save_thorax_thrust = save_thorax_thrust - save_thorax_thrust[0]

    fig = go.Figure(data=go.Scatter(x=timeline, y=-np.gradient(save_pelvis_rotation), name=f'Pelvis'))

    fig.add_trace(
        go.Scatter(
            x=timeline,
            y=-np.gradient(save_thorax_rotation),
            name=f'Thorax',
            # legendrank=seq_sorted['Shoulder']
        )
    )

    fig.update_layout(
        title='Kinematic Sequence',
        title_x=0.5,
        font_size=15,
        yaxis_title="Angular velocity in °/s",
        xaxis_title="time in s",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        legend_orientation="h",
        legend=dict(y=1, yanchor="bottom"),
        margin=dict(
            l=100
        ),
        modebar=dict(
            bgcolor='rgba(0,0,0,0)',
            color='rgba(1,1,1,0.3)',
            activecolor='rgba(58, 73, 99, 1)'
        )
    ),

    fig3 = go.Figure(data=go.Scatter(x=timeline, y=save_pelvis_tilt, name=f'Pelvis side bend'))

    fig3.add_trace(
        go.Scatter(x=timeline, y=save_pelvis_rotation, name=f'Pelvis rotation')
    )

    fig3.update_layout(
        title='Pelvis angles',
        title_x=0.5,
        font_size=15,
        yaxis_title='angle in °',
        xaxis_title="time in s",
        paper_bgcolor='rgba(0,0,0,0)',
        legend_orientation="h",
        legend=dict(y=1, yanchor="bottom"),
        margin=dict(
            l=100
        ),
        modebar=dict(
            bgcolor='rgba(0,0,0,0)',
            color='rgba(1,1,1,0.3)',
            activecolor='rgba(58, 73, 99, 1)'
        )
    )

    fig4 = go.Figure(data=go.Scatter(x=timeline, y=save_pelvis_lift, name=f'Pelvis lift'))

    fig4.add_trace(
        go.Scatter(x=timeline, y=save_pelvis_sway, name=f'Pelvis_sway')
    )

    fig4.add_trace(
        go.Scatter(x=timeline, y=save_pelvis_thrust, name=f'Pelvis_thrust')
    )

    fig4.update_layout(
        title='Pelvis displacement',
        title_x=0.5,
        font_size=15,
        yaxis_title='Displacement in m',
        xaxis_title="time in s",
        paper_bgcolor='rgba(0,0,0,0)',
        legend_orientation="h",
        legend=dict(y=1, yanchor="bottom"),
        margin=dict(
            l=100
        ),
        modebar=dict(
            bgcolor='rgba(0,0,0,0)',
            color='rgba(1,1,1,0.3)',
            activecolor='rgba(58, 73, 99, 1)'
        )
    )

    fig5 = go.Figure(data=go.Scatter(x=timeline, y=save_thorax_rotation, name=f'Thorax rotation'))

    fig5.add_trace(
        go.Scatter(x=timeline, y=save_thorax_bend, name=f'Thorax bend')
    )

    fig5.add_trace(
        go.Scatter(x=timeline, y=save_thorax_tilt, name=f'Thorax tilt')
    )

    fig5.update_layout(
        title='Thorax angles',
        title_x=0.5,
        font_size=15,
        yaxis_title='angle in °',
        xaxis_title="time in s",
        paper_bgcolor='rgba(0,0,0,0)',
        legend_orientation="h",
        legend=dict(y=1, yanchor="bottom"),
        margin=dict(
            l=100
        ),
        modebar=dict(
            bgcolor='rgba(0,0,0,0)',
            color='rgba(1,1,1,0.3)',
            activecolor='rgba(58, 73, 99, 1)'
        )
    )

    fig6 = go.Figure(data=go.Scatter(x=timeline, y=save_thorax_thrust, name=f'Thorax thrust'))

    fig6.add_trace(
        go.Scatter(x=timeline, y=save_thorax_sway, name=f'Thorax sway')
    )

    fig6.add_trace(
        go.Scatter(x=timeline, y=save_thorax_lift, name=f'Thorax lift')
    )

    fig6.update_layout(
        title='Thorax displacement',
        title_x=0.5,
        font_size=15,
        yaxis_title='Displacement in m',
        xaxis_title="time in s",
        paper_bgcolor='rgba(0,0,0,0)',
        legend_orientation="h",
        legend=dict(y=1, yanchor="bottom"),
        margin=dict(
            l=100
        ),
        modebar=dict(
            bgcolor='rgba(0,0,0,0)',
            color='rgba(1,1,1,0.3)',
            activecolor='rgba(58, 73, 99, 1)'
        )
    )

    fig11 = go.Figure(data=go.Scatter(x=timeline, y=save_spine_tilt))

    fig11.update_layout(
        title='Tilt between pelvis and shoulder',
        title_x=0.5,
        font_size=15,
        yaxis_title='angle in °',
        xaxis_title="time in s",
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(
            l=100
        ),
        modebar=dict(
            bgcolor='rgba(0,0,0,0)',
            color='rgba(1,1,1,0.3)',
            activecolor='rgba(58, 73, 99, 1)'
        )
    )

    fig12 = go.Figure(data=go.Scatter(x=timeline, y=save_head_tilt))

    fig12.update_layout(
        title='Head tilt',
        title_x=0.5,
        font_size=15,
        yaxis_title='angle in °',
        xaxis_title="time in s",
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(
            l=100
        ),
        modebar=dict(
            bgcolor='rgba(0,0,0,0)',
            color='rgba(1,1,1,0.3)',
            activecolor='rgba(58, 73, 99, 1)'
        )
    )

    fig13 = go.Figure(data=go.Scatter(x=timeline, y=save_head_rotation))

    fig13.update_layout(
        title='Head rotation',
        title_x=0.5,
        font_size=15,
        yaxis_title='angle in °',
        xaxis_title="time in s",
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(
            l=100
        ),
        modebar=dict(
            bgcolor='rgba(0,0,0,0)',
            color='rgba(1,1,1,0.3)',
            activecolor='rgba(58, 73, 99, 1)'
        )
    )

    fig14 = go.Figure(data=go.Scatter(x=timeline, y=save_left_arm_length))

    fig14.update_layout(
        title='Left arm length',
        title_x=0.5,
        font_size=15,
        yaxis_title='length in m',
        xaxis_title="time in s",
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(
            l=100
        ),
        modebar=dict(
            bgcolor='rgba(0,0,0,0)',
            color='rgba(1,1,1,0.3)',
            activecolor='rgba(58, 73, 99, 1)'
        )
    )

    fig15 = go.Figure(data=go.Scatter(x=timeline, y=save_spine_rotation))

    fig15.update_layout(
        title='Spine rotation',
        title_x=0.5,
        font_size=15,
        yaxis_title='angle in °',
        xaxis_title="time in s",
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(
            l=100
        ),
        modebar=dict(
            bgcolor='rgba(0,0,0,0)',
            color='rgba(1,1,1,0.3)',
            activecolor='rgba(58, 73, 99, 1)'
        )
    )

    fig16 = go.Figure(data=go.Scatter(x=timeline, y=save_wrist_angle, name=f'Wrist angle'))

    fig16.add_trace(
        go.Scatter(x=timeline, y=save_wrist_tilt, name=f'Wrist tilt')
    )

    fig16.update_layout(
        title='Wrist angle',
        title_x=0.5,
        font_size=15,
        yaxis_title='angle in °',
        xaxis_title="time in s",
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(
            l=100
        ),
        modebar=dict(
            bgcolor='rgba(0,0,0,0)',
            color='rgba(1,1,1,0.3)',
            activecolor='rgba(58, 73, 99, 1)'
        )
    )

    return fig, fig3, fig4, fig5, fig6, fig11, fig12, fig13, fig14, fig15, fig16


# Plots
fig = go.Figure(data=go.Scatter(x=timeline, y=save_pelvis_rotation, name=f'Pelvis'))

fig.add_trace(
    go.Scatter(
        x=timeline,
        y=save_thorax_rotation,
        name=f'Thorax',
        # legendrank=seq_sorted['Shoulder']
    )
)

fig.update_layout(
    title=' Kinematic Sequence',
    title_x=0.5,
    font_size=15,
    yaxis_title="Angular velocity in °/s",
    xaxis_title="time in s",
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    legend_orientation="h",
    legend=dict(y=1, yanchor="bottom"),
    margin=dict(
        l=100
    ),
    modebar=dict(
        bgcolor='rgba(0,0,0,0)',
        color='rgba(1,1,1,0.3)',
        activecolor='rgba(58, 73, 99, 1)'
    )
),

fig3 = go.Figure(data=go.Scatter(x=timeline, y=save_pelvis_tilt, name=f'Pelvis side bend'))

fig3.add_trace(
    go.Scatter(x=timeline, y=save_pelvis_rotation, name=f'Pelvis rotation')
)

fig3.update_layout(
    title='Pelvis angles',
    title_x=0.5,
    font_size=15,
    yaxis_title='angle in °',
    xaxis_title="time in s",
    paper_bgcolor='rgba(0,0,0,0)',
    legend_orientation="h",
    legend=dict(y=1, yanchor="bottom"),
    margin=dict(
        l=100
    ),
    modebar=dict(
        bgcolor='rgba(0,0,0,0)',
        color='rgba(1,1,1,0.3)',
        activecolor='rgba(58, 73, 99, 1)'
    )
)

fig4 = go.Figure(data=go.Scatter(x=timeline, y=save_pelvis_lift, name=f'Pelvis lift'))

fig4.add_trace(
    go.Scatter(x=timeline, y=save_pelvis_sway, name=f'Pelvis_sway')
)

fig4.add_trace(
    go.Scatter(x=timeline, y=save_pelvis_thrust, name=f'Pelvis_thrust')
)

fig4.update_layout(
    title='Pelvis displacement',
    title_x=0.5,
    font_size=15,
    yaxis_title='Displacement in m',
    xaxis_title="time in s",
    paper_bgcolor='rgba(0,0,0,0)',
    legend_orientation="h",
    legend=dict(y=1, yanchor="bottom"),
    margin=dict(
        l=100
    ),
    modebar=dict(
        bgcolor='rgba(0,0,0,0)',
        color='rgba(1,1,1,0.3)',
        activecolor='rgba(58, 73, 99, 1)'
    )
)

fig5 = go.Figure(data=go.Scatter(x=timeline, y=save_thorax_rotation, name=f'Thorax rotation'))

fig5.add_trace(
    go.Scatter(x=timeline, y=save_thorax_bend, name=f'Thorax bend')
)

fig5.add_trace(
    go.Scatter(x=timeline, y=save_thorax_tilt, name=f'Thorax tilt')
)

fig5.update_layout(
    title='Thorax angles',
    title_x=0.5,
    font_size=15,
    yaxis_title='angle in °',
    xaxis_title="time in s",
    paper_bgcolor='rgba(0,0,0,0)',
    legend_orientation="h",
    legend=dict(y=1, yanchor="bottom"),
    margin=dict(
        l=100
    ),
    modebar=dict(
        bgcolor='rgba(0,0,0,0)',
        color='rgba(1,1,1,0.3)',
        activecolor='rgba(58, 73, 99, 1)'
    )
)

fig6 = go.Figure(data=go.Scatter(x=timeline, y=save_thorax_thrust, name=f'Thorax thrust'))

fig6.add_trace(
    go.Scatter(x=timeline, y=save_thorax_sway, name=f'Thorax sway')
)

fig6.add_trace(
    go.Scatter(x=timeline, y=save_thorax_lift, name=f'Thorax lift')
)

fig6.update_layout(
    title='Thorax displacement',
    title_x=0.5,
    font_size=15,
    yaxis_title='Displacement in m',
    xaxis_title="time in s",
    paper_bgcolor='rgba(0,0,0,0)',
    legend_orientation="h",
    legend=dict(y=1, yanchor="bottom"),
    margin=dict(
        l=100
    ),
    modebar=dict(
        bgcolor='rgba(0,0,0,0)',
        color='rgba(1,1,1,0.3)',
        activecolor='rgba(58, 73, 99, 1)'
    )
)

fig11 = go.Figure(data=go.Scatter(x=timeline, y=save_spine_tilt))

fig11.update_layout(
    title='Tilt between pelvis and shoulder',
    title_x=0.5,
    font_size=15,
    yaxis_title='angle in °',
    xaxis_title="time in s",
    paper_bgcolor='rgba(0,0,0,0)',
    margin=dict(
        l=100
    ),
    modebar=dict(
        bgcolor='rgba(0,0,0,0)',
        color='rgba(1,1,1,0.3)',
        activecolor='rgba(58, 73, 99, 1)'
    )
)

fig12 = go.Figure(data=go.Scatter(x=timeline, y=save_head_tilt))

fig12.update_layout(
    title='Head tilt',
    title_x=0.5,
    font_size=15,
    yaxis_title='angle in °',
    xaxis_title="time in s",
    paper_bgcolor='rgba(0,0,0,0)',
    margin=dict(
        l=100
    ),
    modebar=dict(
        bgcolor='rgba(0,0,0,0)',
        color='rgba(1,1,1,0.3)',
        activecolor='rgba(58, 73, 99, 1)'
    )
)

fig13 = go.Figure(data=go.Scatter(x=timeline, y=save_head_rotation))

fig13.update_layout(
    title='Head rotation',
    title_x=0.5,
    font_size=15,
    yaxis_title='angle in °',
    xaxis_title="time in s",
    paper_bgcolor='rgba(0,0,0,0)',
    margin=dict(
        l=100
    ),
    modebar=dict(
        bgcolor='rgba(0,0,0,0)',
        color='rgba(1,1,1,0.3)',
        activecolor='rgba(58, 73, 99, 1)'
    )
)

fig14 = go.Figure(data=go.Scatter(x=timeline, y=save_left_arm_length))

fig14.update_layout(
    title='Left arm length',
    title_x=0.5,
    font_size=15,
    yaxis_title='length in m',
    xaxis_title="time in s",
    paper_bgcolor='rgba(0,0,0,0)',
    margin=dict(
        l=100
    ),
    modebar=dict(
        bgcolor='rgba(0,0,0,0)',
        color='rgba(1,1,1,0.3)',
        activecolor='rgba(58, 73, 99, 1)'
    )
)

fig15 = go.Figure(data=go.Scatter(x=timeline, y=save_spine_rotation))

fig15.update_layout(
    title='Spine rotation',
    title_x=0.5,
    font_size=15,
    yaxis_title='angle in °',
    xaxis_title="time in s",
    paper_bgcolor='rgba(0,0,0,0)',
    margin=dict(
        l=100
    ),
    modebar=dict(
        bgcolor='rgba(0,0,0,0)',
        color='rgba(1,1,1,0.3)',
        activecolor='rgba(58, 73, 99, 1)'
    )
)

fig16 = go.Figure(data=go.Scatter(x=timeline, y=save_wrist_angle, name=f'Wrist angle'))

fig16.add_trace(
    go.Scatter(x=timeline, y=save_wrist_tilt, name=f'Wrist tilt')
)

fig16.update_layout(
    title='Wrist angles',
    title_x=0.5,
    font_size=15,
    yaxis_title='angle in °',
    xaxis_title="time in s",
    paper_bgcolor='rgba(0,0,0,0)',
    margin=dict(
        l=100
    ),
    modebar=dict(
        bgcolor='rgba(0,0,0,0)',
        color='rgba(1,1,1,0.3)',
        activecolor='rgba(58, 73, 99, 1)'
    )
)

# Initialize the app
external_stylesheets = ["static/style.css"]
app = Dash(__name__, external_stylesheets=external_stylesheets)
app.css.config.serve_locally = False
server = app.server

markdown = '''
# Welcome back
'''

app.title = 'Swing Analysis'

app.layout = html.Div(
    children=[
        html.Div(
            dcc.Markdown(children=markdown),
            style={'margin-left': '5%',
                   'margin-bottom': '2%',
                   'margin-top': '2%',
                   'color': 'rgba(58, 73, 99, 1)',
                   }
        ),

        html.Div(children=[
            dcc.Markdown(
                '''
                ##### Upload your video
                as mp4, mov or avi – max. 50 MB
                '''
                ,
                style={
                    'margin-top': '1%',
                }
            ),
            dcc.Upload(
                id='upload-data',
                children=html.Div([
                    'Drop your video here or ',
                    html.A('browse'),
                    ' ⛳️',
                ]),
                multiple=False,
                max_size=50e6,
                style_active=(dict(
                    backgroundColor='rgba(230, 240, 250, 1)',
                    borderColor='rgba(115, 165, 250, 1)',
                )),
                className='upload'
            )
        ],
            className='container',
        ),

        dcc.Loading(
            id='loading',
            type='graph',
            fullscreen=True,
            children=
            html.Div(
                dcc.Graph(
                    id='sequence',
                    figure=fig,
                    config=config,
                    className='container'
                )
            ),
        ),

        html.Div(children=[

            dcc.Graph(
                id='pelvis_rotation',
                figure=fig3,
                config=config,
                className='container_half_left'
            ),

            dcc.Graph(
                id='pelvis_displacement',
                figure=fig4,
                config=config,
                className='container_half_right'
            ),
        ],
        ),

        html.Div(children=[

            dcc.Graph(
                id='thorax_rotation',
                figure=fig5,
                config=config,
                className='container_half_left'
            ),

            dcc.Graph(
                id='thorax_displacement',
                figure=fig6,
                config=config,
                className='container_half_right'
            ),
        ],
        ),

        html.Div(children=[

            dcc.Graph(
                id='h_tilt',
                figure=fig12,
                config=config,
                className='container_half_left'
            ),

            dcc.Graph(
                id='h_rotation',
                figure=fig13,
                config=config,
                className='container_half_right'
            ),
        ],
        ),

        html.Div(
            dcc.Graph(
                id='s_tilt',
                figure=fig11,
                config=config,
                className='container'
            )
        ),

        html.Div(
            dcc.Graph(
                id='arm_length',
                figure=fig14,
                config=config,
                className='container'
            )
        ),

        html.Div(
            dcc.Graph(
                id='spine_rotation',
                figure=fig15,
                config=config,
                className='container'
            )
        ),

        html.Div(
            dcc.Graph(
                id='wrist_angle',
                figure=fig16,
                config=config,
                className='container'
            )
        ),
    ]
)


@app.callback(
    [Output('sequence', 'figure'), Output('pelvis_rotation', 'figure'), Output('pelvis_displacement', 'figure'),
     Output('thorax_rotation', 'figure'), Output('thorax_displacement', 'figure'), Output('s_tilt', 'figure'),
     Output('h_tilt', 'figure'),
     Output('h_rotation', 'figure'), Output('arm_length', 'figure'), Output('spine_rotation', 'figure'), Output('wrist_angle', 'figure')],
    [Input('upload-data', 'contents'), Input('upload-data', 'filename')],
    prevent_initial_call=True
)
def process(contents, filename):
    save_pelvis_rotation, save_pelvis_tilt, save_pelvis_lift, save_pelvis_sway, save_pelvis_thrust, \
    save_thorax_lift, save_thorax_bend, save_thorax_sway, save_thorax_rotation, save_thorax_thrust, \
    save_thorax_tilt, save_spine_rotation, save_spine_tilt, save_head_rotation, save_head_tilt, save_left_arm_length, save_wrist_angle, save_wrist_tilt, duration = process_motion(
        contents, filename)
    # fig = go.Figure(data=go.Image(z=image))

    fig, fig3, fig4, fig5, fig6, fig11, fig12, fig13, fig14, fig15, fig16 = update_plots(save_pelvis_rotation,
                                                                                  save_pelvis_tilt, save_pelvis_lift,
                                                                                  save_pelvis_sway, save_pelvis_thrust,
                                                                                  save_thorax_lift, save_thorax_bend,
                                                                                  save_thorax_sway,
                                                                                  save_thorax_rotation,
                                                                                  save_thorax_thrust,
                                                                                  save_thorax_tilt, save_spine_rotation,
                                                                                  save_spine_tilt, save_head_rotation,
                                                                                  save_head_tilt, save_left_arm_length, save_wrist_angle, save_wrist_tilt,
                                                                                  duration)

    return [fig, fig3, fig4, fig5, fig6, fig11, fig12, fig13, fig14, fig15, fig16]


if __name__ == '__main__':
    # app.run_server(debug=True)
    server.run(debug=True, port=8080, host='0.0.0.0')
