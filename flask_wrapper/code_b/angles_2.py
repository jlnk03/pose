import numpy as np
import matplotlib.pyplot as plt


def calc_angle(landmark1, landmark2):
    goal_direction = np.array([landmark1.x - landmark2.x, 0, landmark1.z - landmark2.z])
    camera = np.array([0, 0, 1])

    angle = np.arccos(camera.dot(goal_direction) / (np.linalg.norm(camera) * np.linalg.norm(goal_direction)))
    # angle = np.degrees(angle)
    # angle between goal direction and camera with atan2
    # angle = np.arctan2(goal_direction[0], goal_direction[2])

    return angle


def angle_hip(hip_l, hip_r):
    hip_l = np.array(hip_l)
    hip_r = np.array(hip_r)
    hip_v = hip_l - hip_r
    normal = np.array([0, 0, 1]).T
    product = hip_v.T @ normal
    norm = np.linalg.norm(hip_v, axis=0)
    angle = np.arccos(product / norm)
    angle = 90 - np.degrees(angle)

    return angle


def angle_ground(left, right):
    left = np.array(left)
    right = np.array(right)
    vector = left - right
    normal = np.array([0, 1, 0])
    product = vector.T @ normal
    norm = np.linalg.norm(vector, axis=0)
    angle = np.arccos(product / norm)
    angle = 90 - np.degrees(angle)

    return angle


def back_angle(shoulder_l, shoulder_r):
    shoulder_l = np.array(shoulder_l)
    shoulder_r = np.array(shoulder_r)
    connection = shoulder_l - shoulder_r
    spine = shoulder_l + 0.5 * connection
    normal = np.array([0, 1, 0])
    product = spine.T @ normal
    norm = np.linalg.norm(spine, axis=0)
    angle = np.arccos(product / norm)
    angle = 90 - np.degrees(angle)

    return angle


def tilt_angle(shoulder_l, shoulder_r):
    shoulder_l = np.array(shoulder_l)
    shoulder_r = np.array(shoulder_r)
    connection = shoulder_l - shoulder_r
    spine = shoulder_l + 0.5 * connection
    normal = np.array([0, 1, 0])
    product = spine.T @ normal
    norm = np.linalg.norm(spine, axis=0)
    angle = np.arccos(product / norm)
    # angle = 90 - np.degrees(angle)

    return angle


def mass_balance(foot_l, foot_r):
    distance_l = np.linalg.norm(foot_l, axis=0)
    distance_r = np.linalg.norm(foot_r, axis=0)

    return round(distance_l - distance_r, 4)


def pelvis_rotation(hip_l, hip_r):
    hip_l = np.array(hip_l)
    hip_r = np.array(hip_r)
    hip_v = hip_l - hip_r
    # angle between hip vector and normal with atan2
    angle = np.arctan2(hip_v[0], hip_v[2])

    return -np.degrees(angle)


def pelvis_tilt(hip_l, hip_r):
    hip_l = np.array(hip_l)
    hip_r = np.array(hip_r)
    hip_v = hip_l - hip_r
    normal = np.array([0, 1, 0])
    product = hip_v.T @ normal
    norm = np.linalg.norm(hip_v, axis=0)
    angle = np.arccos(product / norm)

    return np.degrees(angle) - 90


def pelvis_sway(foot_l):
    foot_l = np.array(foot_l)
    hip_v = foot_l

    return -hip_v[2]


def pelvis_thrust(foot_l):
    foot_l = np.array(foot_l)

    hip_v = foot_l

    return -hip_v[0]


def pelvis_lift(foot_l):
    foot_l = np.array(foot_l)
    hip_v = foot_l

    return hip_v[1]


def thorax_rotation(shoulder_l, shoulder_r):
    shoulder_l = np.array(shoulder_l)
    shoulder_r = np.array(shoulder_r)
    shoulder_v = shoulder_l - shoulder_r
    normal = np.array([0, 0, 1])
    # angle between shoulder vector and normal with atan2
    angle = np.arctan2(shoulder_v[0], shoulder_v[2])

    return -np.degrees(angle)


def thorax_tilt(shoulder_l, shoulder_r):
    shoulder_l = np.array(shoulder_l)
    shoulder_r = np.array(shoulder_r)
    shoulder_v = shoulder_l - shoulder_r
    normal = np.array([0, 1, 0])
    product = shoulder_v.T @ normal
    norm = np.linalg.norm(shoulder_v, axis=0)
    angle = np.arccos(product / norm)

    return np.degrees(angle) - 90


def thorax_bend(shoulder_l, shoulder_r):
    shoulder_l = np.array(shoulder_l)
    shoulder_r = np.array(shoulder_r)
    shoulder_v = shoulder_l - shoulder_r
    spine = shoulder_l - 0.5 * shoulder_v
    spine[2] = 0
    normal = np.array([0, 1, 0])
    product = spine.T @ normal
    norm = np.linalg.norm(spine, axis=0)
    angle = np.arccos(product / norm)

    return 180 - np.degrees(angle)


def thorax_sway(shoulder_l, shoulder_r, foot_l):
    shoulder_l = np.array(shoulder_l)
    shoulder_r = np.array(shoulder_r)
    foot_l = np.array(foot_l)
    shoulder_v = shoulder_l - shoulder_r
    spine = shoulder_l - 0.5 * shoulder_v
    sway = spine - foot_l

    return sway[2]


def thorax_thrust(shoulder_l, shoulder_r, foot_l):
    shoulder_l = np.array(shoulder_l)
    shoulder_r = np.array(shoulder_r)
    foot_l = np.array(foot_l)
    shoulder_v = shoulder_l - shoulder_r
    spine = shoulder_l - 0.5 * shoulder_v
    thrust = spine - foot_l

    return thrust[0]


def thorax_lift(shoulder_l, shoulder_r, foot_l):
    shoulder_l = np.array(shoulder_l)
    shoulder_r = np.array(shoulder_r)
    foot_l = np.array(foot_l)
    shoulder_v = shoulder_l - shoulder_r
    spine = shoulder_l - 0.5 * shoulder_v
    lift = spine - foot_l

    return -lift[1]


# rotation between spine and pelvis
def spine_rotation(hip_l, hip_r, shoulder_l, shoulder_r):
    hip_l = np.array(hip_l)
    hip_r = np.array(hip_r)
    shoulder_l = np.array(shoulder_l)
    shoulder_r = np.array(shoulder_r)

    hip_v = hip_l - hip_r
    shoulder_v = shoulder_l - shoulder_r
    # angle between hip vector and shoulder vector with atan2
    angle = (np.arctan2(hip_v[2] * shoulder_v[0] - hip_v[0] * shoulder_v[2],
                        hip_v[2] * shoulder_v[2] + hip_v[0] * shoulder_v[0]))

    return np.degrees(angle)


# tilt between spine and pelvis
def spine_tilt(hip_l, hip_r, shoulder_l, shoulder_r):
    hip_l = np.array(hip_l)
    hip_r = np.array(hip_r)
    shoulder_l = np.array(shoulder_l)
    shoulder_r = np.array(shoulder_r)

    hip_v = hip_l - hip_r
    shoulder_v = shoulder_l - shoulder_r
    product = np.sum(hip_v * shoulder_v, axis=0)
    norm = np.linalg.norm(hip_v, axis=0) * np.linalg.norm(shoulder_v, axis=0)
    angle = np.arccos(product / norm)

    return np.degrees(angle)


# head rotation
def head_rotation(eye_l, eye_r):
    eye_l = np.array(eye_l)
    eye_r = np.array(eye_r)

    eye_v = eye_l - eye_r
    angle = (np.arctan2(eye_v[0], eye_v[2]))

    return -np.degrees(angle)


# head tilt
def head_tilt(eye_l, eye_r):
    eye_l = np.array(eye_l)
    eye_r = np.array(eye_r)

    eye_v = eye_l - eye_r
    normal = np.array([0, 1, 0])
    product = eye_v.T @ normal
    norm = np.linalg.norm(eye_v, axis=0)
    angle = np.arccos(product / norm)

    return np.degrees(angle) - 90


# distance from spine to left wrist
def left_arm_length(shoulder_l, shoulder_r, wrist_l):
    shoulder_l = np.array(shoulder_l)
    shoulder_r = np.array(shoulder_r)
    wrist_l = np.array(wrist_l)

    shoulder_v = shoulder_l - shoulder_r
    spine = shoulder_l - 0.5 * shoulder_v
    length = np.linalg.norm(spine - wrist_l, axis=0)

    return length


def wrist_angle(pinky_l, index_l, wrist_l, elbow_l):
    pinky_l = np.array(pinky_l)
    index_l = np.array(index_l)
    # pinky_v = pinky_l - wrist_l
    # index_v = index_l - wrist_l
    # normal = np.cross(pinky_v, index_v)
    # arm_l = wrist_l - elbow_l
    # # angle = np.arccos(normal.dot(arm_l) / (np.linalg.norm(normal) * np.linalg.norm(arm_l)))
    # # angle between normal and arm vector with atan2
    # angle = (np.arctan2(normal[0] * arm_l[2] - normal[2] * arm_l[0],
    #                     normal[2] * arm_l[2] + normal[0] * arm_l[0]))

    return pinky_l[1] - index_l[1]


def wrist_tilt(pinky_l, index_l, wrist_l, elbow_l):
    # hand_v = pinky_l - index_l
    # arm_l = wrist_l - elbow_l
    # # angle with atan2
    # angle = (np.arctan2(hand_v[0] * arm_l[2] - hand_v[2] * arm_l[0],
    #                     hand_v[2] * arm_l[2] + hand_v[0] * arm_l[0]))

    return pinky_l[0]


def arm_rotation(wrist_l, shoulder_l, shoulder_r, impact_ratio):
    wrist_l = np.array(wrist_l)
    shoulder_l = np.array(shoulder_l)
    shoulder_r = np.array(shoulder_r)

    shoulder_v = (shoulder_l + shoulder_r) / 2
    arm = wrist_l - shoulder_v
    arm[0] = 0
    normal = np.array([0, 1, 0])

    impact_index = int(impact_ratio * np.shape(arm)[1])

    product = arm.T @ normal
    norm = np.linalg.norm(arm, axis=0)
    angle = np.arccos(product / norm)
    angle = np.degrees(angle)

    angle_before_impact = -angle[:impact_index]
    angle_after_impact = angle[impact_index:]

    mask_arm_above_back = (arm[1][:impact_index] < 0) * (shoulder_l[2][:impact_index] < wrist_l[2][:impact_index])
    angle_before_impact[mask_arm_above_back] = 360 - angle_before_impact[mask_arm_above_back]

    mask_arm_above_finish = (arm[1][impact_index:] < 0) * (shoulder_l[2][impact_index:] > wrist_l[2][impact_index:])
    angle_after_impact[mask_arm_above_finish] = 360 - angle_after_impact[mask_arm_above_finish]

    angle = np.concatenate((angle_before_impact, angle_after_impact))

    return angle


def arm_to_ground(wrist_l, shoulder_l):
    wrist_l = np.array(wrist_l)
    shoulder_l = np.array(shoulder_l)

    arm = wrist_l - shoulder_l
    normal = np.array([0, 1, 0])
    product = arm.T @ normal
    norm = np.linalg.norm(arm, axis=0)
    angle = np.arccos(product / norm)

    return 90 - np.degrees(angle)


def calculate_angles(shoulder_l_s, shoulder_r_s, wrist_l_s, wrist_r_s, hip_l_s, hip_r_s, foot_l_s, eye_l_s, eye_r_s, pinky_l_s, index_l_s, arm_v, impact_ratio):

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
    arm_rotation_l = arm_rotation(wrist_l_s, shoulder_l_s, shoulder_r_s, impact_ratio)
    arm_ground = arm_to_ground(wrist_l_s, shoulder_l_s)
    arm_position = {'x': arm_v[0], 'y': arm_v[2], 'z': arm_v[1]}

    return pelvis_r, pelvis_t, pelvis_s, pelvis_th, pelvis_l, thorax_r, thorax_b, thorax_t, thorax_s, thorax_th, \
        thorax_l, spine_r, spine_t, head_r, head_t, wist_a, wrist_t, left_arm, arm_rotation_l, arm_ground, \
        arm_position


if __name__ == '__main__':
    pass
