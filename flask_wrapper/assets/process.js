import {thorax_rotation} from "./angles.js";

const videoElement = document.getElementsByClassName('input_video')[0];
const canvasElement = document.getElementsByClassName('output_canvas')[0];
const canvasCtx = canvasElement.getContext('2d', {willReadFrequently: true});
const container = document.getElementsByClassName('container')[0];
// const landmarkContainer = document.getElementsByClassName('landmark-grid-container')[0];

const thoraxRotation = document.getElementById('thorax-rotation');

// const grid = new LandmarkGrid(landmarkContainer);

function onResults(results) {
    if (!results.poseLandmarks) {
        // grid.updateLandmarks([]);
        return;
    }

    canvasCtx.save();
    canvasCtx.clearRect(0, 0, canvasElement.width, canvasElement.height);
    // canvasCtx.drawImage(results.segmentationMask, 0, 0,
    //     canvasElement.width, canvasElement.height);
    //
    // Only overwrite existing pixels.
    canvasCtx.globalCompositeOperation = 'source-in';
    canvasCtx.fillStyle = '#00FF00';
    canvasCtx.fillRect(0, 0, canvasElement.width, canvasElement.height);

    // Only overwrite missing pixels.
    canvasCtx.globalCompositeOperation = 'destination-atop';
    canvasCtx.drawImage(
        results.image, 0, 0, canvasElement.width, canvasElement.height);

    canvasCtx.globalCompositeOperation = 'source-over';
    drawConnectors(
        canvasCtx, results.poseLandmarks, POSE_CONNECTIONS,
        {visibilityMin: 0.65, color: 'white', lineWidth: 1});
    drawLandmarks(
        canvasCtx,
        Object.values(POSE_LANDMARKS_LEFT)
            .map(index => results.poseLandmarks[index]),
        {visibilityMin: 0.65, color: 'white', fillColor: 'rgb(255,138,0)', lineWidth: 1, radius: 2});
    drawLandmarks(
        canvasCtx,
        Object.values(POSE_LANDMARKS_RIGHT)
            .map(index => results.poseLandmarks[index]),
        {visibilityMin: 0.65, color: 'white', fillColor: 'rgb(0,217,231)', lineWidth: 1, radius: 2});
    drawLandmarks(
        canvasCtx,
        Object.values(POSE_LANDMARKS_NEUTRAL)
            .map(index => results.poseLandmarks[index]),
        {visibilityMin: 0.65, color: 'white', fillColor: 'white', lineWidth: 1, radius: 2});

    canvasCtx.restore();

    const worldLndmrks = results.poseWorldLandmarks;
    const shoulder_l = [worldLndmrks[11].x, worldLndmrks[11].y, worldLndmrks[11].z];
    const shoulder_r = [worldLndmrks[12].x, worldLndmrks[12].y, worldLndmrks[12].z];
    const foot_l = worldLndmrks[27];
    const foot_r = worldLndmrks[28];

    // Rotation matrix
    // let theta = calc_angle(foot_l, foot_r);
    // let c = Math.cos(theta), s = Math.sin(theta);
    // let R = [[c, 0, -s], [0, 1, 0], [s, 0, c]];
    // R = math.matrix(R);
    //
    // // Rotate shoulder vectors
    // let shoulder_l_rot = math.multiply(R, shoulder_l);
    // let shoulder_r_rot = math.multiply(R, shoulder_r);

    const thorax_rot = thorax_rotation(shoulder_l, shoulder_r);

    thoraxRotation.innerText = `${thorax_rot}°`

    // Check range of values and change background color
    if (thorax_rot > 70 || thorax_rot < -7) {
        container.style.backgroundColor = "#f87171";
    } else {
        container.style.backgroundColor = "#a3e635";
    }


    // grid.updateLandmarks(results.poseWorldLandmarks);

}

const pose = new Pose({
    locateFile: (file) => {
        return `https://cdn.jsdelivr.net/npm/@mediapipe/pose/${file}`;
    }
});
pose.setOptions({
    modelComplexity: 2,
    smoothLandmarks: true,
    enableSegmentation: true,
    smoothSegmentation: true,
    minDetectionConfidence: 0.5,
    minTrackingConfidence: 0.5
});
pose.onResults(onResults);

const camera = new Camera(videoElement, {
    onFrame: async () => {
        await pose.send({image: videoElement});
    },
    width: 256,
    height: 144
});
camera.start();