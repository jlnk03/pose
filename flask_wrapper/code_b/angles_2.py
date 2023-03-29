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
    hip_v = hip_l - hip_r
    normal = np.array([0, 0, 1]).T
    product = hip_v.T @ normal
    norm = np.linalg.norm(hip_v, axis=0)
    angle = np.arccos(product / norm)
    angle = 90 - np.degrees(angle)

    return angle


def angle_ground(left, right):
    vector = left - right
    normal = np.array([0, 1, 0])
    product = vector.T @ normal
    norm = np.linalg.norm(vector, axis=0)
    angle = np.arccos(product / norm)
    angle = 90 - np.degrees(angle)

    return angle


def back_angle(shoulder_l, shoulder_r):
    connection = shoulder_l - shoulder_r
    spine = shoulder_l + 0.5 * connection
    normal = np.array([0, 1, 0])
    product = spine.T @ normal
    norm = np.linalg.norm(spine, axis=0)
    angle = np.arccos(product / norm)
    angle = 90 - np.degrees(angle)

    return angle


def tilt_angle(shoulder_l, shoulder_r):
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
    hip_v = hip_l - hip_r
    # angle between hip vector and normal with atan2
    angle = np.arctan2(hip_v[0], hip_v[2])

    return -np.degrees(angle)


def pelvis_tilt(hip_l, hip_r):
    hip_v = hip_l - hip_r
    normal = np.array([0, 1, 0])
    product = hip_v.T @ normal
    norm = np.linalg.norm(hip_v, axis=0)
    angle = np.arccos(product / norm)

    return np.degrees(angle) - 90


def pelvis_sway(foot_l):
    hip_v = foot_l

    return -hip_v[2]


def pelvis_thrust(foot_l):
    hip_v = foot_l

    return -hip_v[0]


def pelvis_lift(foot_l):
    hip_v = foot_l

    return hip_v[1]


def thorax_rotation(shoulder_l, shoulder_r):
    shoulder_v = shoulder_l - shoulder_r
    normal = np.array([0, 0, 1])
    # angle between shoulder vector and normal with atan2
    angle = np.arctan2(shoulder_v[0], shoulder_v[2])

    return -np.degrees(angle)


def thorax_tilt(shoulder_l, shoulder_r):
    shoulder_v = shoulder_l - shoulder_r
    normal = np.array([0, 1, 0])
    product = shoulder_v.T @ normal
    norm = np.linalg.norm(shoulder_v, axis=0)
    angle = np.arccos(product / norm)

    return np.degrees(angle) - 90


def thorax_bend(shoulder_l, shoulder_r):
    shoulder_v = shoulder_l - shoulder_r
    spine = shoulder_l - 0.5 * shoulder_v
    spine[2] = 0
    normal = np.array([0, 1, 0])
    product = spine.T @ normal
    norm = np.linalg.norm(spine, axis=0)
    angle = np.arccos(product / norm)

    return 180 - np.degrees(angle)


def thorax_sway(shoulder_l, shoulder_r, foot_l):
    shoulder_v = shoulder_l - shoulder_r
    spine = shoulder_l - 0.5 * shoulder_v
    sway = spine - foot_l

    return sway[2]


def thorax_thrust(shoulder_l, shoulder_r, foot_l):
    shoulder_v = shoulder_l - shoulder_r
    spine = shoulder_l - 0.5 * shoulder_v
    thrust = spine - foot_l

    return thrust[0]


def thorax_lift(shoulder_l, shoulder_r, foot_l):
    shoulder_v = shoulder_l - shoulder_r
    spine = shoulder_l - 0.5 * shoulder_v
    lift = spine - foot_l

    return -lift[1]


# rotation between spine and pelvis
def spine_rotation(hip_l, hip_r, shoulder_l, shoulder_r):
    hip_v = hip_l - hip_r
    shoulder_v = shoulder_l - shoulder_r
    # angle between hip vector and shoulder vector with atan2
    angle = (np.arctan2(hip_v[2] * shoulder_v[0] - hip_v[0] * shoulder_v[2],
                        hip_v[2] * shoulder_v[2] + hip_v[0] * shoulder_v[0]))

    return np.degrees(angle)


# tilt between spine and pelvis
def spine_tilt(hip_l, hip_r, shoulder_l, shoulder_r):
    hip_v = hip_l - hip_r
    shoulder_v = shoulder_l - shoulder_r
    product = np.sum(hip_v * shoulder_v, axis=0)
    norm = np.linalg.norm(hip_v, axis=0) * np.linalg.norm(shoulder_v, axis=0)
    angle = np.arccos(product / norm)

    return np.degrees(angle)


# head rotation
def head_rotation(eye_l, eye_r):
    eye_v = eye_l - eye_r
    angle = (np.arctan2(eye_v[0], eye_v[2]))

    return -np.degrees(angle)


# head tilt
def head_tilt(eye_l, eye_r):
    eye_v = eye_l - eye_r
    normal = np.array([0, 1, 0])
    product = eye_v.T @ normal
    norm = np.linalg.norm(eye_v, axis=0)
    angle = np.arccos(product / norm)

    return np.degrees(angle) - 90


# distance from spine to left wrist
def left_arm_length(shoulder_l, shoulder_r, wrist_l):
    shoulder_v = shoulder_l - shoulder_r
    spine = shoulder_l - 0.5 * shoulder_v
    length = np.linalg.norm(spine - wrist_l, axis=0)

    return length


def wrist_angle(pinky_l, index_l, wrist_l, elbow_l):
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
    shoulder_v = (shoulder_l + shoulder_r) / 2
    arm = wrist_l - shoulder_v
    arm[0] = 0
    normal = np.array([0, 1, 0])

    print(shoulder_l)
    print(shoulder_r)
    print(shoulder_v)
    print(arm)

    impact_index = int(impact_ratio * np.shape(arm)[1])

    product = arm.T @ normal
    norm = np.linalg.norm(arm, axis=0)
    angle = np.arccos(product / norm)
    angle = np.degrees(angle)

    # plt.plot(angle)
    # plt.show()

    angle_before_impact = -angle[:impact_index]
    angle_after_impact = angle[impact_index:]

    mask_arm_above_back = (arm[1][:impact_index] < 0) * (shoulder_l[2][:impact_index] < wrist_l[2][:impact_index])
    angle_before_impact[mask_arm_above_back] = 360 - angle_before_impact[mask_arm_above_back]

    mask_arm_above_finish = (arm[1][impact_index:] < 0) * (shoulder_l[2][impact_index:] > wrist_l[2][impact_index:])
    angle_after_impact[mask_arm_above_finish] = 360 - angle_after_impact[mask_arm_above_finish]

    angle = np.concatenate((angle_before_impact, angle_after_impact))

    plt.plot(angle)
    plt.show()

    return angle

    # shoulder_v = r @ np.array([shoulder_l.x, shoulder_l.y, shoulder_l.z], dtype=np.float64)
    # wrist_v = r @ np.array([wrist_l.x, wrist_l.y, wrist_l.z], dtype=np.float64)
    # wrist_v[1] = 0
    # normal = np.array([1, 0, 0])
    # angle = (np.arctan2(-wrist_v[2], wrist_v[0]))
    #
    # return -np.degrees(angle)


def arm_to_ground(wrist_l, shoulder_l):
    arm = wrist_l - shoulder_l
    normal = np.array([0, 1, 0])
    product = arm.T @ normal
    norm = np.linalg.norm(arm, axis=0)
    angle = np.arccos(product / norm)

    return 90 - np.degrees(angle)


if __name__ == '__main__':
    pass
