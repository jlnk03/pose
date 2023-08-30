import {acos, atan2, divide, dot, multiply, norm, subtract, transpose} from 'mathjs';

function matrixNorm(matrix, axis = null) {

    if (axis === null) {
        return norm(matrix.flat(Infinity)); // Flatten to 1D array and compute norm
    }

    // Check if matrix is a 1D array
    if (!Array.isArray(matrix[0])) {
        if (axis === 0) {
            return norm(matrix);
        } else {
            throw new Error("Invalid axis for 1D array. Axis can be 0 or null.");
        }
    }

    if (axis === 0) {
        // Compute norms of each column
        return matrix[0].map((_, colIdx) => {
            const column = matrix.map(row => row[colIdx]);
            return norm(column);
        });
    } else if (axis === 1) {
        // Compute norms of each row
        return matrix.map(row => norm(row));
    } else {
        throw new Error("Invalid axis. Axis can be 0, 1, or null.");
    }
}

function pelvisRotation(hipL, hipR) {
    let hipV = subtract(hipL, hipR);
    // Note: [hipV[0], hipV[2]] extracts x and z components respectively
    let angle = atan2(hipV[0], hipV[2]);

    return -angle * (180 / Math.PI);
}

function pelvisTilt(hipL, hipR) {
    let hipV = subtract(hipL, hipR);
    let normal = [0, 1, 0];
    let product = multiply(transpose(hipV), normal);
    let hipNorm = matrixNorm(hipV, 0)
    let angle = acos(product / hipNorm);

    return angle * (180 / Math.PI) - 90;
}

function pelvisSway(footL) {
    return -footL[2];
}

function pelvisThrust(footL) {
    return -footL[0];
}

function pelvisLift(footL) {
    return footL[1];
}

function thoraxRotation(shoulderL, shoulderR) {
    const shoulderV = [
        shoulderL[0] - shoulderR[0],
        shoulderL[1] - shoulderR[1],
        shoulderL[2] - shoulderR[2]
    ];
    const angle = Math.atan2(shoulderV[0], shoulderV[2]);
    return -angle * (180 / Math.PI);
}

function thoraxTilt(shoulderL, shoulderR) {
    const shoulderV = [
        shoulderL[0] - shoulderR[0],
        shoulderL[1] - shoulderR[1],
        shoulderL[2] - shoulderR[2]
    ];

    const normal = [0, 1, 0];
    const product = multiply(transpose(shoulderV), normal);
    const norm = matrixNorm(shoulderV, 0)

    const angle = Math.acos(divide(product, norm));
    return (angle * (180 / Math.PI)) - 90;
}

function thoraxBend(shoulderL, shoulderR) {
    const shoulderV = [
        shoulderL[0] - shoulderR[0],
        shoulderL[1] - shoulderR[1],
        shoulderL[2] - shoulderR[2]
    ];

    const spine = [
        shoulderL[0] - 0.5 * shoulderV[0],
        shoulderL[1] - 0.5 * shoulderV[1],
        0
    ];

    const normal = [0, 1, 0];
    const product = multiply(transpose(spine), normal);
    const norm = matrixNorm(spine, 0)

    const angle = Math.acos(divide(product, norm));
    return 180 - (angle * (180 / Math.PI));
}

function thoraxSway(shoulderL, shoulderR, footL) {
    const shoulderV = [
        shoulderL[0] - shoulderR[0],
        shoulderL[1] - shoulderR[1],
        shoulderL[2] - shoulderR[2]
    ];

    const spine = [
        shoulderL[0] - 0.5 * shoulderV[0],
        shoulderL[1] - 0.5 * shoulderV[1],
        shoulderL[2] - 0.5 * shoulderV[2]
    ];

    const sway = [
        spine[0] - footL[0],
        spine[1] - footL[1],
        spine[2] - footL[2]
    ];

    return sway[2];
}

function thoraxThrust(shoulderL, shoulderR, footL) {
    const shoulderV = [
        shoulderL[0] - shoulderR[0],
        shoulderL[1] - shoulderR[1],
        shoulderL[2] - shoulderR[2]
    ];

    const spine = [
        shoulderL[0] - 0.5 * shoulderV[0],
        shoulderL[1] - 0.5 * shoulderV[1],
        shoulderL[2] - 0.5 * shoulderV[2]
    ];

    const thrust = [
        spine[0] - footL[0],
        spine[1] - footL[1],
        spine[2] - footL[2]
    ];

    return thrust[0];
}

function thoraxLift(shoulderL, shoulderR, footL) {
    const shoulderV = [
        shoulderL[0] - shoulderR[0],
        shoulderL[1] - shoulderR[1],
        shoulderL[2] - shoulderR[2]
    ];

    const spine = [
        shoulderL[0] - 0.5 * shoulderV[0],
        shoulderL[1] - 0.5 * shoulderV[1],
        shoulderL[2] - 0.5 * shoulderV[2]
    ];

    const lift = [
        spine[0] - footL[0],
        spine[1] - footL[1],
        spine[2] - footL[2]
    ];

    return -lift[1];
}

function spineRotation(hipL, hipR, shoulderL, shoulderR) {
    const hipV = [
        hipL[0] - hipR[0],
        hipL[1] - hipR[1],
        hipL[2] - hipR[2]
    ];

    const shoulderV = [
        shoulderL[0] - shoulderR[0],
        shoulderL[1] - shoulderR[1],
        shoulderL[2] - shoulderR[2]
    ];

    const angle = Math.atan2(
        hipV[2] * shoulderV[0] - hipV[0] * shoulderV[2],
        hipV[2] * shoulderV[2] + hipV[0] * shoulderV[0]
    );

    return angle * (180 / Math.PI);
}

function spineTilt(hipL, hipR, shoulderL, shoulderR) {
    const hipV = [
        hipL[0] - hipR[0],
        hipL[1] - hipR[1],
        hipL[2] - hipR[2]
    ];

    const shoulderV = [
        shoulderL[0] - shoulderR[0],
        shoulderL[1] - shoulderR[1],
        shoulderL[2] - shoulderR[2]
    ];

    const product = dot(hipV, shoulderV);
    const norm = matrixNorm(hipV, 0) * matrixNorm(shoulderV, 0);

    const angle = Math.acos(divide(product, norm));
    return angle * (180 / Math.PI);
}

function headRotation(eyeL, eyeR) {
    const eyeV = [
        eyeL[0] - eyeR[0],
        eyeL[1] - eyeR[1],
        eyeL[2] - eyeR[2]
    ];

    const angle = Math.atan2(eyeV[0], eyeV[2]);
    return -angle * (180 / Math.PI);
}

function headTilt(eyeL, eyeR) {
    const eyeV = [
        eyeL[0] - eyeR[0],
        eyeL[1] - eyeR[1],
        eyeL[2] - eyeR[2]
    ];
    const normal = [0, 1, 0];
    const product = multiply(transpose(eyeV), normal);
    const norm = matrixNorm(eyeV, 0);

    const angle = Math.acos(divide(product, norm));
    return angle * (180 / Math.PI) - 90;
}

function leftArmLength(shoulderL, shoulderR, wristL) {
    const shoulderV = [
        shoulderL[0] - shoulderR[0],
        shoulderL[1] - shoulderR[1],
        shoulderL[2] - shoulderR[2]
    ];

    const spine = [
        shoulderL[0] - 0.5 * shoulderV[0],
        shoulderL[1] - 0.5 * shoulderV[1],
        shoulderL[2] - 0.5 * shoulderV[2]
    ];

    const lengthVector = [
        spine[0] - wristL[0],
        spine[1] - wristL[1],
        spine[2] - wristL[2]
    ];

    return norm(lengthVector);
}

function wristAngle(pinkyL, indexL) {
    return pinkyL[1] - indexL[1];
}

function wristTilt(pinkyL) {
    return pinkyL[0];
}

function armRotation(wristL, shoulderL, shoulderR, impactRatio) {
    const shoulderV = [
        (shoulderL[0] + shoulderR[0]) / 2,
        (shoulderL[1] + shoulderR[1]) / 2,
        (shoulderL[2] + shoulderR[2]) / 2
    ];

    const arm = [
        0,
        wristL[1] - shoulderV[1],
        wristL[2] - shoulderV[2]
    ];

    const normal = [0, 1, 0];

    const impactIndex = Math.floor(impactRatio * arm.length);

    const product = multiply(transpose(arm), normal);
    const norm = matrixNorm(arm, 0);
    let angle = Math.acos(divide(product, norm));
    angle = angle * (180 / Math.PI);
    // console.log(angle)

    // const angleBeforeImpact = -angle.slice(0, impactIndex);
    // const angleAfterImpact = angle.slice(impactIndex);
    //
    // const maskArmAboveBack = arm[1].slice(0, impactIndex).map((value, index) => value < 0 && shoulderL[2][index] < wristL[2][index]);
    // maskArmAboveBack.forEach((value, index) => {
    //     if (value) angleBeforeImpact[index] = 360 - angleBeforeImpact[index];
    // });
    //
    // const maskArmAboveFinish = arm[1].slice(impactIndex).map((value, index) => value < 0 && shoulderL[2][index + impactIndex] > wristL[2][index + impactIndex]);
    // maskArmAboveFinish.forEach((value, index) => {
    //     if (value) angleAfterImpact[index] = 360 - angleAfterImpact[index];
    // });
    //
    // return angleBeforeImpact.concat(angleAfterImpact);
    return angle;
}

function armToGround(wristL, shoulderL) {
    const arm = [
        wristL[0] - shoulderL[0],
        wristL[1] - shoulderL[1],
        wristL[2] - shoulderL[2]
    ];

    const normal = [0, 1, 0];

    const product = multiply(transpose(arm), normal);
    const norm = matrixNorm(arm, 0);
    const angle = Math.acos(divide(product, norm));

    return 90 - angle * (180 / Math.PI);
}

function calculateAngles(shoulderLS, shoulderRS, wristLS, wristRS, hipLS, hipRS, footLS, eyeLS, eyeRS, pinkyLS, indexLS, armV, impactRatio) {
    // Calculate angles
    const pelvisR = pelvisRotation(hipLS, hipRS);
    const pelvisT = pelvisTilt(hipLS, hipRS);
    const pelvisS = pelvisSway(footLS);
    const pelvisTh = pelvisThrust(footLS);
    const pelvisL = pelvisLift(footLS);
    const thoraxR = thoraxRotation(shoulderLS, shoulderRS);
    const thoraxB = thoraxBend(shoulderLS, shoulderRS);
    const thoraxT = thoraxTilt(shoulderLS, shoulderRS);
    const thoraxS = thoraxSway(shoulderLS, shoulderRS, footLS);
    const thoraxTh = thoraxThrust(shoulderLS, shoulderRS, footLS);
    const thoraxL = thoraxLift(shoulderLS, shoulderRS, footLS);
    const spineR = spineRotation(hipLS, hipRS, shoulderLS, shoulderRS);
    const spineT = spineTilt(hipLS, hipRS, shoulderLS, shoulderRS);
    const headR = headRotation(eyeLS, eyeRS);
    const headT = headTilt(eyeLS, eyeRS);
    const wristA = wristAngle(pinkyLS, indexLS, wristLS, wristRS);
    const wristT = wristTilt(pinkyLS, indexLS, wristLS, wristRS);
    const leftArm = leftArmLength(shoulderLS, shoulderRS, wristLS);
    const armRotationL = armRotation(wristLS, shoulderLS, shoulderRS, impactRatio);
    const armGround = armToGround(wristLS, shoulderLS);
    const armPosition = {x: armV[0], y: armV[2], z: armV[1]};

    return {
        pelvisR, pelvisT, pelvisS, pelvisTh, pelvisL, thoraxR, thoraxB, thoraxT, thoraxS, thoraxTh,
        thoraxL, spineR, spineT, headR, headT, wristA, wristT, leftArm, armRotationL, armGround,
        armPosition
    };
}

export default calculateAngles;
