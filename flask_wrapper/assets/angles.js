export function calc_angle(landmark1, landmark2) {
    const goal_direction = [landmark1.x - landmark2.x, 0, landmark1.z - landmark2.z];
    const camera = [0, 0, 1];

    const dot_product = camera[0] * goal_direction[0] + camera[1] * goal_direction[1] + camera[2] * goal_direction[2];
    const camera_norm = Math.sqrt(camera[0] * camera[0] + camera[1] * camera[1] + camera[2] * camera[2]);
    const goal_norm = Math.sqrt(goal_direction[0] * goal_direction[0] + goal_direction[1] * goal_direction[1] + goal_direction[2] * goal_direction[2]);
    return Math.acos(dot_product / (camera_norm * goal_norm));
}

export function angle_hip(hip_l, hip_r) {
    const hip_v = [hip_l[0] - hip_r[0], hip_l[1] - hip_r[1], hip_l[2] - hip_r[2]];
    const normal = [0, 0, 1];
    const product = hip_v[0] * normal[0] + hip_v[1] * normal[1] + hip_v[2] * normal[2];
    const norm = Math.sqrt(hip_v[0] * hip_v[0] + hip_v[1] * hip_v[1] + hip_v[2] * hip_v[2]);
    const angle = Math.acos(product / norm);
    return 90 - angle * 180 / Math.PI;
}

export function angle_ground(left, right) {
    const vector = [left[0] - right[0], left[1] - right[1], left[2] - right[2]];
    const normal = [0, 1, 0];
    const product = vector[0] * normal[0] + vector[1] * normal[1] + vector[2] * normal[2];
    const norm = Math.sqrt(vector[0] * vector[0] + vector[1] * vector[1] + vector[2] * vector[2]);
    const angle = Math.acos(product / norm);
    return 90 - angle * 180 / Math.PI;

}

export function back_angle(shoulder_l, shoulder_r) {
    const connection = [shoulder_l[0] - shoulder_r[0], shoulder_l[1] - shoulder_r[1], shoulder_l[2] - shoulder_r[2]];
    const spine = [shoulder_l[0] + 0.5 * connection[0], shoulder_l[1] + 0.5 * connection[1], shoulder_l[2] + 0.5 * connection[2]];
    const normal = [0, 1, 0];
    const product = spine[0] * normal[0] + spine[1] * normal[1] + spine[2] * normal[2];
    const norm = Math.sqrt(spine[0] * spine[0] + spine[1] * spine[1] + spine[2] * spine[2]);
    const angle = Math.acos(product / norm);
    return 90 - angle * 180 / Math.PI;

}

export function thorax_rotation(shoulder_l, shoulder_r) {
    let shoulder_v = math.subtract(shoulder_l, shoulder_r);
    // shoulder_v.toArray();

    // angle between shoulder vector and normal with atan2
    let angle = Math.atan2(shoulder_v[0], shoulder_v[2]);

    return Math.round(-angle * (180 / Math.PI));
}


export function thorax_tilt(shoulder_l, shoulder_r) {
    shoulder_l = new Array(shoulder_l);
    shoulder_r = new Array(shoulder_r);
    let shoulder_v = [shoulder_l[0] - shoulder_r[0], shoulder_l[1] - shoulder_r[1], shoulder_l[2] - shoulder_r[2]];
    let normal = [0, 1, 0];
    let product = shoulder_v[0] * normal[0] + shoulder_v[1] * normal[1] + shoulder_v[2] * normal[2];
    let norm = Math.sqrt(shoulder_v[0] ** 2 + shoulder_v[1] ** 2 + shoulder_v[2] ** 2);
    let angle = Math.acos(product / norm);

    return angle * (180 / Math.PI) - 90;
}


export function thorax_bend(shoulder_l, shoulder_r) {
    shoulder_l = new Array(shoulder_l);
    shoulder_r = new Array(shoulder_r);
    let shoulder_v = [shoulder_l[0] - shoulder_r[0], shoulder_l[1] - shoulder_r[1], shoulder_l[2] - shoulder_r[2]];
    let spine = [shoulder_l[0] - 0.5 * shoulder_v[0], shoulder_l[1] - 0.5 * shoulder_v[1], shoulder_l[2] - 0.5 * shoulder_v[2]];
    spine[2] = 0;
    let normal = [0, 1, 0];
    let product = spine[0] * normal[0] + spine[1] * normal[1] + spine[2] * normal[2];
    let norm = Math.sqrt(spine[0] ** 2 + spine[1] ** 2 + spine[2] ** 2);
    let angle = Math.acos(product / norm);

    return 180 - angle * (180 / Math.PI);
}
