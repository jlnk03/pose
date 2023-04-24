import {calc_angle, thorax_rotation} from "./angles.js";

const videoElement = document.getElementById('video');
const canvasElement = document.getElementsByClassName('output_canvas')[0];
const canvasCtx = canvasElement.getContext('2d', {willReadFrequently: true});
const container = document.getElementById('container-pose');
// const landmarkContainer = document.getElementsByClassName('landmark-grid-container')[0];
const canvasLoader = document.getElementById('canvas-loader');

const thoraxRotation = document.getElementById('thorax-rotation');
const lowerMargin = document.getElementById('lower-margin')
const upperMargin = document.getElementById('upper-margin')

const save = document.getElementById('save');

let rotationMatrix = math.identity(3);
let rotationMatrixBuffer = math.identity(3);

let upperMarginValue = 180;
let lowerMarginValue = -180;

function setMargins() {
    try {
        lowerMarginValue = lowerMargin.value;
    } catch (e) {
        console.log('Using default value')
    }

    try {
        upperMarginValue = upperMargin.value;
    } catch (e) {
        console.log('Using default value')
    }

    if (lowerMarginValue > upperMarginValue) {
        const temp = lowerMarginValue;
        lowerMarginValue = upperMarginValue;
        upperMarginValue = temp;
    }
}

setMargins();

save.addEventListener('click', () => {
    setMargins()
});


// const grid = new LandmarkGrid(landmarkContainer);

// Get the list of available media input devices and add to the select element
navigator.mediaDevices.enumerateDevices()
    .then(function (devices) {
        // Filter the list to get only the video input devices (cameras)
        const videoDevices = devices.filter(function (device) {
            return device.kind === 'videoinput';
        });

        // Get a reference to the select element
        const select = document.getElementById('camera-selection');

        // Add an option element for each camera to the select element
        videoDevices.forEach(function (device) {
            const option = document.createElement('option');
            option.value = device.deviceId;
            option.text = device.label || `Camera ${select.options.length + 1}`;
            select.add(option);
        });
    })
    .catch(function (error) {
        console.error(error);
    });


function onResults(results) {
    if (!results.poseLandmarks) {
        canvasCtx.clearRect(0, 0, canvasElement.width, canvasElement.height);

        // draw new frame
        // Only overwrite missing pixels.
        canvasCtx.globalCompositeOperation = 'destination-atop';
        canvasCtx.drawImage(
            results.image, 0, 0, canvasElement.width, canvasElement.height);

        canvasCtx.restore();

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
    let theta = calc_angle(foot_l, foot_r);
    let c = Math.cos(theta), s = Math.sin(theta);
    let R = [[c, 0, -s], [0, 1, 0], [s, 0, c]];
    R = math.matrix(R);
    rotationMatrixBuffer = R

    // Rotate shoulder vectors
    let shoulder_l_rot = math.multiply(rotationMatrix, shoulder_l);
    let shoulder_r_rot = math.multiply(rotationMatrix, shoulder_r);

    const thorax_rot = thorax_rotation(shoulder_l_rot, shoulder_r_rot);

    thoraxRotation.innerText = `${thorax_rot}°`

    // Check range of values and change background color
    if (thorax_rot > upperMarginValue || thorax_rot < lowerMarginValue) {
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
    modelComplexity: 1,
    smoothLandmarks: true,
    enableSegmentation: false,
    smoothSegmentation: false,
    minDetectionConfidence: 0.5,
    minTrackingConfidence: 0.5
});
pose.onResults(onResults);

// const camera = new Camera(videoElement, {
//     onFrame: async () => {
//         await pose.send({image: videoElement});
//     },
//     width: 256,
//     height: 144
// });
// camera.start();


// camera
function startCamera() {

    const select = document.getElementById('camera-selection');
    const selectedDeviceId = select.value;

    navigator.mediaDevices
        .getUserMedia({
            video: {deviceId: {exact: selectedDeviceId}},
            audio: false
        })
        .catch(
            function (err) {
                alert("Access to the camera was denied. Please allow access to the camera and reload the page.")
            }
        )
        .then((stream) => {
            videoElement.srcObject = stream;
            const settings = stream.getVideoTracks()[0].getSettings();
            videoElement.width = settings.width;
            videoElement.height = settings.height;
            canvasElement.width = settings.width;
            canvasElement.height = settings.height;
            canvasElement.aspectRatio = settings.width / settings.height;
            canvasLoader.style.display = 'none';
            videoElement.play()

            // async function to update pose
            async function updatePose() {
                await pose.send({image: videoElement});
                videoElement.requestVideoFrameCallback(updatePose)
            }

            videoElement.requestVideoFrameCallback(updatePose)

        })
        .catch((err) => {
            console.log("An error occurred! " + err);
        })
}

// startCamera();


let stop = document.getElementById('stop');
stop.addEventListener('click', () => {
    videoElement.srcObject.getTracks().forEach(track => track.stop());
    videoElement.srcObject = null;
});

let start = document.getElementById('start');
start.addEventListener('click', () => {
    canvasLoader.style.display = 'block';
    startCamera();
});

let setup = document.getElementById('setup');
setup.addEventListener('click', () => {
    rotationMatrix = rotationMatrixBuffer;
});
