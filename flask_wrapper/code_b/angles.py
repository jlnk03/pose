import numpy as np


def calc_angle(landmark1, landmark2):
    goal_direction = np.array([landmark1.x - landmark2.x, 0, landmark1.z - landmark2.z], dtype=np.float64)
    camera = np.array([0, 0, 1])

    angle = np.arccos(camera.dot(goal_direction) / (np.linalg.norm(camera) * np.linalg.norm(goal_direction)))
    # angle = np.degrees(angle)
    # angle between goal direction and camera with atan2
    # angle = np.arctan2(goal_direction[0], goal_direction[2])

    return angle


def angle_hip(hip_l, hip_r):
    hip_v = np.array([hip_l.x - hip_r.x, hip_l.y - hip_r.y, hip_l.z - hip_r.z], dtype=np.float64)
    normal = np.array([0, 0, 1])
    angle = np.arccos(normal.dot(hip_v) / (np.linalg.norm(normal) * np.linalg.norm(hip_v)))
    angle = 90 - np.degrees(angle)

    return angle


def angle_ground(left, right):
    vector = np.array([left.x - right.x, left.y - right.y, left.z - right.z], dtype=np.float64)
    normal = np.array([0, 1, 0])
    angle = np.arccos(normal.dot(vector) / (np.linalg.norm(normal) * np.linalg.norm(vector)))
    angle = 90 - np.degrees(angle)

    return angle


def back_angle(shoulder_l, shoulder_r):
    sl = np.array([shoulder_l.x, shoulder_l.y, shoulder_l.z], dtype=np.float64)
    sr = np.array([shoulder_r.x, shoulder_r.y, shoulder_r.z], dtype=np.float64)
    connection = sl - sr
    spine = sl + 0.5 * connection
    normal = np.array([0, 1, 0])
    angle = np.arccos(normal.dot(spine) / (np.linalg.norm(normal) * np.linalg.norm(spine)))
    angle = 90 - np.degrees(angle)

    return angle


def tilt_angle(shoulder_l, shoulder_r):
    sl = np.array([shoulder_l.x, shoulder_l.y, shoulder_l.z], dtype=np.float64)
    sr = np.array([shoulder_r.x, shoulder_r.y, shoulder_r.z], dtype=np.float64)
    connection = sl - sr
    spine = sl + 0.5 * connection
    normal = np.array([0, 1, 0])
    angle = np.arccos(normal.dot(spine) / (np.linalg.norm(normal) * np.linalg.norm(spine)))
    # angle = 90 - np.degrees(angle)

    return angle


def mass_balance(foot_l, foot_r):
    left = np.array([foot_l.x, foot_l.y, foot_l.z], dtype=np.float64)
    right = np.array([foot_r.x, foot_r.y, foot_r.z], dtype=np.float64)
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
    hip_v = r @ np.array([hip_l.x - hip_r.x, hip_l.y - hip_r.y, hip_l.z - hip_r.z], dtype=np.float64)
    normal = np.array([0, 0, 1])
    # angle = np.arccos(normal.dot(hip_v) / (np.linalg.norm(normal) * np.linalg.norm(hip_v)))
    # angle between hip vector and normal with atan2
    angle = np.arctan2(hip_v[0], hip_v[2])

    return np.degrees(angle)


def pelvis_tilt(hip_l, hip_r, r):
    hip_v = r @ np.array([hip_l.x - hip_r.x, hip_l.y - hip_r.y, hip_l.z - hip_r.z], dtype=np.float64)
    normal = np.array([0, 1, 0])
    angle = np.arccos(normal.dot(hip_v) / (np.linalg.norm(normal) * np.linalg.norm(hip_v)))

    return 90 - np.degrees(angle)


def pelvis_sway(foot_l, r):
    hip_v = r @ np.array([foot_l.x, foot_l.y, foot_l.z], dtype=np.float64)

    return hip_v[2]


def pelvis_thrust(foot_l, r):
    hip_v = r @ np.array([foot_l.x, foot_l.y, foot_l.z], dtype=np.float64)

    return hip_v[0]


def pelvis_lift(foot_l, r):
    hip_v = r @ np.array([foot_l.x, foot_l.y, foot_l.z], dtype=np.float64)

    return hip_v[1]


def thorax_rotation(shoulder_l, shoulder_r, r):
    shoulder_v = r @ np.array([shoulder_l.x - shoulder_r.x, shoulder_l.y - shoulder_r.y, shoulder_l.z - shoulder_r.z], dtype=np.float64)
    normal = np.array([0, 0, 1])
    # angle = np.arccos(normal.dot(shoulder_v) / (np.linalg.norm(normal) * np.linalg.norm(shoulder_v)))
    # angle between shoulder vector and normal with atan2
    angle = (np.arctan2(shoulder_v[0], shoulder_v[2]))

    return np.degrees(angle)


def thorax_tilt(shoulder_l, shoulder_r, r):
    shoulder_v = r @ np.array([shoulder_l.x - shoulder_r.x, shoulder_l.y - shoulder_r.y, shoulder_l.z - shoulder_r.z], dtype=np.float64)
    # shoulder_v[0] = 0
    # shoulder_l = r @ np.array([shoulder_l.x, shoulder_l.y, shoulder_l.z], dtype=np.float64)
    # spine = shoulder_l - 0.5 * shoulder_v
    # spine[0] = 0
    normal = np.array([0, 1, 0])
    # angle = np.arccos(normal.dot(spine) / (np.linalg.norm(normal) * np.linalg.norm(spine)))
    # angle between shoulder vector and normal with atan2
    # angle = np.arctan2(spine[1], spine[2])
    angle = np.arccos(normal.dot(shoulder_v) / (np.linalg.norm(normal) * np.linalg.norm(shoulder_v)))

    return np.degrees(angle) - 90


def thorax_bend(shoulder_l, shoulder_r, r):
    shoulder_v = r @ np.array([shoulder_l.x - shoulder_r.x, shoulder_l.y - shoulder_r.y, shoulder_l.z - shoulder_r.z], dtype=np.float64)
    shoulder_l = r @ np.array([shoulder_l.x, shoulder_l.y, shoulder_l.z], dtype=np.float64)
    spine = shoulder_l - 0.5 * shoulder_v
    spine[2] = 0
    normal = np.array([0, 1, 0])
    angle = np.arccos(normal.dot(spine) / (np.linalg.norm(normal) * np.linalg.norm(spine)))

    return 180 - np.degrees(angle)


def thorax_sway(shoulder_l, shoulder_r, foot_l, r):
    shoulder_v = r @ np.array([shoulder_l.x - shoulder_r.x, shoulder_l.y - shoulder_r.y, shoulder_l.z - shoulder_r.z], dtype=np.float64)
    shoulder_l = r @ np.array([shoulder_l.x, shoulder_l.y, shoulder_l.z], dtype=np.float64)
    foot_l = r @ np.array([foot_l.x, foot_l.y, foot_l.z], dtype=np.float64)
    spine = shoulder_l - 0.5 * shoulder_v
    sway = spine - foot_l

    return sway[2]


def thorax_thrust(shoulder_l, shoulder_r, foot_l, r):
    shoulder_v = r @ np.array([shoulder_l.x - shoulder_r.x, shoulder_l.y - shoulder_r.y, shoulder_l.z - shoulder_r.z], dtype=np.float64)
    shoulder_l = r @ np.array([shoulder_l.x, shoulder_l.y, shoulder_l.z], dtype=np.float64)
    foot_l = r @ np.array([foot_l.x, foot_l.x, foot_l.x], dtype=np.float64)
    spine = shoulder_l - 0.5 * shoulder_v
    thrust = spine - foot_l

    return thrust[0]


def thorax_lift(shoulder_l, shoulder_r, foot_l, r):
    shoulder_v = r @ np.array([shoulder_l.x - shoulder_r.x, shoulder_l.y - shoulder_r.y, shoulder_l.z - shoulder_r.z], dtype=np.float64)
    shoulder_l = r @ np.array([shoulder_l.x, shoulder_l.y, shoulder_l.z], dtype=np.float64)
    foot_l = r @ np.array([foot_l.x, foot_l.y, foot_l.z], dtype=np.float64)
    spine = shoulder_l - 0.5 * shoulder_v
    lift = spine - foot_l

    return lift[1]


# rotation between spine and pelvis
def spine_rotation(hip_l, hip_r, shoulder_l, shoulder_r, r):
    hip_v = r @ np.array([hip_l.x - hip_r.x, 0, hip_l.z - hip_r.z], dtype=np.float64)
    shoulder_v = r @ np.array([shoulder_l.x - shoulder_r.x, 0, shoulder_l.z - shoulder_r.z], dtype=np.float64)
    # angle = np.arccos(hip_v.dot(shoulder_v) / (np.linalg.norm(hip_v) * np.linalg.norm(shoulder_v)))
    # angle between hip vector and shoulder vector with atan2
    angle = (np.arctan2(hip_v[2] * shoulder_v[0] - hip_v[0] * shoulder_v[2],
                        hip_v[2] * shoulder_v[2] + hip_v[0] * shoulder_v[0]))

    return np.degrees(angle)


# tilt between spine and pelvis
def spine_tilt(hip_l, hip_r, shoulder_l, shoulder_r, r):
    hip_v = r @ np.array([hip_l.x - hip_r.x, hip_l.y - hip_r.y, hip_l.z - hip_r.z], dtype=np.float64)
    shoulder_v = r @ np.array([shoulder_l.x - shoulder_r.x, shoulder_l.y - shoulder_r.y, shoulder_l.z - shoulder_r.z], dtype=np.float64)
    angle = np.arccos(hip_v.dot(shoulder_v) / (np.linalg.norm(hip_v) * np.linalg.norm(shoulder_v)))

    return np.degrees(angle)


# head rotation
def head_rotation(eye_l, eye_r, r):
    eye_v = r @ np.array([eye_l.x - eye_r.x, eye_l.y - eye_r.y, eye_l.z - eye_r.z], dtype=np.float64)
    normal = np.array([0, 0, 1])
    # angle = np.arccos(normal.dot(eye_v) / (np.linalg.norm(normal) * np.linalg.norm(eye_v)))
    # angle between eye vector and normal with atan2
    angle = (np.arctan2(eye_v[0], eye_v[2]))

    return np.degrees(angle)


# head tilt
def head_tilt(eye_l, eye_r, r):
    eye_v = r @ np.array([eye_l.x - eye_r.x, eye_l.y - eye_r.y, eye_l.z - eye_r.z], dtype=np.float64)
    # eye_v[0] = 0
    normal = np.array([0, 1, 0])
    angle = np.arccos(normal.dot(eye_v) / (np.linalg.norm(normal) * np.linalg.norm(eye_v)))

    return np.degrees(angle) - 90


# distance from spine to left wrist
def left_arm_length(shoulder_l, shoulder_r, wrist_l, r):
    shoulder_v = r @ np.array([shoulder_l.x - shoulder_r.x, shoulder_l.y - shoulder_r.y, shoulder_l.z - shoulder_r.z], dtype=np.float64)
    shoulder_l = r @ np.array([shoulder_l.x, shoulder_l.y, shoulder_l.z], dtype=np.float64)
    wrist_l = r @ np.array([wrist_l.x, wrist_l.y, wrist_l.z], dtype=np.float64)
    spine = shoulder_l - 0.5 * shoulder_v
    length = np.linalg.norm(spine - wrist_l)

    return length


def wrist_angle(pinky_l, index_l, wrist_l, elbow_l, r):
    pinky_l = r @ np.array([pinky_l.x, pinky_l.y, pinky_l.z], dtype=np.float64)
    index_l = r @ np.array([index_l.x, index_l.y, index_l.z], dtype=np.float64)
    wrist_l = r @ np.array([wrist_l.x, wrist_l.y, wrist_l.z], dtype=np.float64)
    elbow_l = r @ np.array([elbow_l.x, elbow_l.y, elbow_l.z], dtype=np.float64)
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
    pinky_l = r @ np.array([pinky_l.x, pinky_l.y, pinky_l.z], dtype=np.float64)
    index_l = r @ np.array([index_l.x, index_l.y, index_l.z], dtype=np.float64)
    wrist_l = r @ np.array([wrist_l.x, wrist_l.y, wrist_l.z], dtype=np.float64)
    elbow_l = r @ np.array([elbow_l.x, elbow_l.y, elbow_l.z], dtype=np.float64)
    hand_v = pinky_l - index_l
    arm_l = wrist_l - elbow_l
    # angle with atan2
    angle = (np.arctan2(hand_v[0] * arm_l[2] - hand_v[2] * arm_l[0],
                        hand_v[2] * arm_l[2] + hand_v[0] * arm_l[0]))

    return np.degrees(angle)


def arm_rotation(wrist_l, r):
    wrist_v = r @ np.array([wrist_l.x, wrist_l.y, wrist_l.z], dtype=np.float64)
    wrist_v[1] = 0
    normal = np.array([1, 0, 0])
    # angle = np.arccos(normal.dot(wrist_v) / (np.linalg.norm(normal) * np.linalg.norm(wrist_v)))
    # angle between wrist vector and normal with atan2
    angle = (np.arctan2(-wrist_v[2], wrist_v[0]))

    return -np.degrees(angle)


def arm_to_ground(wrist_l, shoulder_l, r):
    shoulder_v = r @ np.array([shoulder_l.x, shoulder_l.y, shoulder_l.z], dtype=np.float64)
    wrist_v = r @ np.array([wrist_l.x, wrist_l.y, wrist_l.z], dtype=np.float64)
    arm = wrist_v - shoulder_v
    normal = np.array([0, 1, 0])
    angle = np.arccos(normal.dot(arm) / (np.linalg.norm(normal) * np.linalg.norm(arm)))

    return 90 - np.degrees(angle)