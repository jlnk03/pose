import {angle_hip, calc_angle, thorax_rotation} from "./angles.js";

// import {Howl} from 'https://cdn.jsdelivr.net/npm/howler@2.2.3/dist/howler.min.js';
import {FilesetResolver, GestureRecognizer} from "https://cdn.skypack.dev/@mediapipe/tasks-vision@latest";

const videoElement = document.getElementById('video');
const canvasElement = document.getElementsByClassName('output_canvas')[0];
const canvasCtx = canvasElement.getContext('2d', {willReadFrequently: true});
const container = document.getElementById('container-pose');
// const landmarkContainer = document.getElementsByClassName('landmark-grid-container')[0];
const canvasLoader = document.getElementById('canvas-loader');
const videoContainer = document.getElementById('video-container');

const calculatedValue = document.getElementById('calculatedValue');
const lowerMargin = document.getElementById('lower-margin-in')
const upperMargin = document.getElementById('upper-margin-in')
const cameraAngle = document.getElementById('camera-angle')

const save = document.getElementById('save');

const audio = document.getElementById('audio');

// const audio = new Howl({
//     src: ['soundOK.mp4a'],
//     autoplay: false,
//     loop: true,
// })
//
// audio.play();

let gestureRecognizer

// check device OS
function iOS() {
    return [
            'iPad Simulator',
            'iPhone Simulator',
            'iPod Simulator',
            'iPad',
            'iPhone',
            'iPod'
        ].includes(navigator.platform)
        // iPad on iOS 13 detection
        || (navigator.userAgent.includes('Mac') && 'ontouchend' in document)
}

// const os = iOS()

// Before we can use HandLandmarker class we must wait for it to finish
// loading. Machine Learning models can be large and take a moment to
// get everything needed to run.
const createGestureRecognizer = async () => {
    const vision = await FilesetResolver.forVisionTasks(
        "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@latest/wasm"
    );
    gestureRecognizer = await GestureRecognizer.createFromOptions(vision, {
        baseOptions: {
            modelAssetPath:
                "https://storage.googleapis.com/mediapipe-tasks/gesture_recognizer/gesture_recognizer.task"
        },
        runningMode: 'VIDEO',
        numHands: 2
    });
};
createGestureRecognizer()


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
    // canvasCtx.globalCompositeOperation = 'source-in';
    // canvasCtx.fillStyle = '#00FF00';
    // canvasCtx.fillRect(0, 0, canvasElement.width, canvasElement.height);

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
    const hip_l = [worldLndmrks[23].x, worldLndmrks[23].y, worldLndmrks[23].z]
    const hip_r = [worldLndmrks[24].x, worldLndmrks[24].y, worldLndmrks[24].z]
    const foot_l = worldLndmrks[27];
    const foot_r = worldLndmrks[28];

    // Rotation matrix
    let theta = calc_angle(foot_l, foot_r);
    let c = Math.cos(theta), s = Math.sin(theta);
    let R = [[c, 0, -s], [0, 1, 0], [s, 0, c]];
    R = math.matrix(R);

    // Set first rotation matrix text
    if (rotationMatrixBuffer._data[0][0] === 1 && rotationMatrixBuffer._data[2][2] === 1) {
        cameraAngle.innerText = `Camera Angle: ${Math.round(theta * 180 / Math.PI)}°`
    }

    rotationMatrixBuffer = R

    const bodyPart = document.getElementById('body-part-selection').value;
    let displayValue = 0

    if (bodyPart == 'pelvisRotation') {
        // Rotate hip vectors
        let hip_l_rot = math.multiply(rotationMatrix, hip_l)
        let hip_r_rot = math.multiply(rotationMatrix, hip_r)
        displayValue = angle_hip(hip_l_rot, hip_r_rot);
    } else {
        // Rotate shoulder vectors
        let shoulder_l_rot = math.multiply(rotationMatrix, shoulder_l);
        let shoulder_r_rot = math.multiply(rotationMatrix, shoulder_r);
        displayValue = thorax_rotation(shoulder_l_rot, shoulder_r_rot);
    }

    calculatedValue.innerText = `${displayValue}°`

    // Check range of values and change background color
    if (displayValue > upperMarginValue || displayValue < lowerMarginValue) {
        container.style.backgroundColor = "#fca5a5";
        audio.pause()
        audio.currentTime = 0
    } else {
        container.style.backgroundColor = "#d9f99d";
        audio.play()
    }


    // Recognize open palm gesture and set the rotation matrix after 3seconds
    let nowInMS = Date.now();
    let gestureResults = gestureRecognizer.recognizeForVideo(results.image, nowInMS);
    let gestureOne = gestureResults.gestures[0]
    let gestureTwo = gestureResults.gestures[1]

    if (gestureOne !== undefined) {
        gestureOne = gestureOne[0].categoryName;
    }

    if (gestureTwo !== undefined) {
        gestureTwo = gestureTwo[0].categoryName;
    }
    // console.log(gestureOne, gestureTwo)

    if (gestureOne === 'Open_Palm' || gestureTwo === 'Open_Palm') {
        rotationMatrix = rotationMatrixBuffer;
        cameraAngle.innerText = `Camera Angle: ${Math.round(theta * 180 / Math.PI)}°`
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
            aspectRatio(settings, canvasElement)
            canvasLoader.style.display = 'none';
            videoContainer.style.display = 'block';
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
    audio.pause()
    audio.currentTime = 0
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

// camera selection
const selectCamera = document.getElementById('camera-selection');
selectCamera.addEventListener('change', () => {
    videoElement.srcObject.getTracks().forEach(track => track.stop());
    videoElement.srcObject = null;
    // canvasLoader.style.display = 'block';
    startCamera();
})

function aspectRatio(settings, canvas) {
    let aspectRatio = settings.width / settings.height;
    const width = 224;
    const height = width / aspectRatio;
    canvas.width = width;
    canvas.height = height;
}
