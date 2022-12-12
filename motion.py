import mediapipe as mp
import cv2
import numpy as np
import plotly.graph_objects as go
from dash import Dash
import  dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
from scipy import signal
import tempfile
import base64
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose


def square(x):
    return -0.1*(x ** 2)

image, save, save_hip, save_shoulder, save_wrist, save_head, save_spine, save_tilt, save_balance = np.tile(square(np.linspace(-50, 50, 200)), (9, 1))
duration = 10
timeline = np.linspace(0, duration, len(save))


def calc_angle(a, b, c):
    a1 = np.array([a.x, a.y, a.z])
    b1 = np.array([b.x, b.y, b.z])
    c1 = np.array([c.x, c.y, c.z])

    v = a1 - b1
    w = c1 - b1

    angle = np.arccos(v.dot(w) / (np.linalg.norm(v) * np.linalg.norm(w)))
    angle = np.degrees(angle)

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
    normal = np.array([1, 0, 0])
    angle = np.arccos(normal.dot(spine) / (np.linalg.norm(normal) * np.linalg.norm(spine)))
    angle = 90 - np.degrees(angle)

    return angle


def mass_balance(foot_l, foot_r):
    left = np.array([foot_l.x, foot_l.y, foot_l.z])
    right = np.array([foot_r.x, foot_r.y, foot_r.z])
    distance_l = np.linalg.norm(left)
    distance_r = np.linalg.norm(right)

    if distance_l > distance_r:
        return -1
    else:
        return 1


def process_motion(file):
    content_type, content_string = file.split(',')

    decoded = base64.b64decode(content_string)

    with tempfile.NamedTemporaryFile() as temp:
        temp.write(decoded)

        cap = cv2.VideoCapture(temp.name)

        frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        fps = cap.get(cv2.CAP_PROP_FPS)

        # calculate duration of the video
        duration = round(frames / fps)

        save = []
        save_hip = []
        save_shoulder = []
        save_wrist = []
        save_head = []
        save_spine = []
        save_tilt = []
        save_balance = []

        rot = False
        #meta_dict = ffmpeg.probe(file)
        #if int(meta_dict['streams'][0]['tags']['rotate']) == 180:
        #    rot = True

        with mp_pose.Pose (min_detection_confidence=0.5, min_tracking_confidence=0.5, model_complexity=2) as pose:
            while cap.isOpened():
                ret, frame = cap.read()

                if ret is False:
                    break

                if rot:
                    frame = cv2.rotate(frame, cv2.ROTATE_180)

                # Recolor image to RGB
                image = cv2. cvtColor (frame, cv2.COLOR_BGR2RGB)
                image.flags.writeable = False

                # Make detection
                results = pose.process (image)

                try:
                    landmarks = results.pose_world_landmarks.landmark

                    shoulder_l = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
                    elbow_l = landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value]
                    wrist_l = landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value]
                    hip_l = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]
                    hip_r = landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value]
                    shoulder_r = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
                    foot_r = landmarks[mp_pose.PoseLandmark.RIGHT_FOOT_INDEX.value]
                    foot_l = landmarks[mp_pose.PoseLandmark.LEFT_FOOT_INDEX.value]
                    nose = landmarks[mp_pose.PoseLandmark.NOSE.value]

                    angle = calc_angle(shoulder_l, elbow_l, wrist_l)
                    save.append(angle)

                    angle_h = angle_ground(hip_l, hip_r)
                    save_hip.append(angle_h)

                    angle_s = angle_ground(shoulder_l, shoulder_r)
                    save_shoulder.append(angle_s)

                    angle_w = angle_ground(shoulder_l, wrist_l)
                    save_wrist.append(angle_w)

                    save_head.append(abs(nose.y-foot_r.y))

                    angle_back = back_angle(shoulder_l, shoulder_r)
                    save_spine.append(abs(angle_back))

                    save_tilt.append(tilt_angle(shoulder_l, shoulder_r))

                    bal = mass_balance(foot_l, foot_r)
                    save_balance.append(bal)

                    cv2.putText(image,  f'Arm: {int(angle)}', (100,100), cv2. FONT_HERSHEY_SIMPLEX, 1.4, (255, 255, 255), 2, cv2.LINE_AA)
                    cv2.putText(image, f'Hip: {int(angle_h)}', (100,140), cv2. FONT_HERSHEY_SIMPLEX, 1.4, (255, 255, 255), 2, cv2.LINE_AA)
                    cv2.putText(image, f'Shoulder: {int(angle_s)}', (100,180), cv2. FONT_HERSHEY_SIMPLEX, 1.4, (255, 255, 255), 2, cv2.LINE_AA)
                    cv2.putText(image, f'Wrist: {int(angle_w)}', (100,220), cv2. FONT_HERSHEY_SIMPLEX, 1.4, (255, 255, 255), 2, cv2.LINE_AA)
                    cv2.putText(image, f'Spine: {int(angle_back)}', (100,260), cv2. FONT_HERSHEY_SIMPLEX, 1.4, (255, 255, 255), 2, cv2.LINE_AA)
                    cv2.putText(image, f'Bal: {bal}', (100,300), cv2. FONT_HERSHEY_SIMPLEX, 1.4, (255, 255, 255), 2, cv2.LINE_AA)
                    #cv2.putText(image, str(hip_l), (100,140), cv2. FONT_HERSHEY_SIMPLEX, 1.4, (255, 255, 255), 2, cv2.LINE_AA)
                    #cv2.putText(image, str(hip_r), (100,180), cv2. FONT_HERSHEY_SIMPLEX, 1.4, (255, 255, 255), 2, cv2.LINE_AA)

                except:
                    pass

                # Recolor back to BGR
                image.flags.writeable = True
                image = cv2. cvtColor (image, cv2.COLOR_RGB2BGR)

                # Render detections
                mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
                #cv2. imshow('Mediapipe Feed', image)

                #mp_drawing.plot_landmarks(results.pose_world_landmarks, mp_pose.POSE_CONNECTIONS)

                if cv2.waitKey(10) & 0xFF == ord('q'):
                       break

        cap.release ()
        cv2. destroyAllWindows ()
        cv2.waitKey(1)

        image = cv2. cvtColor (image, cv2.COLOR_BGR2RGB)

    return image, save, save_hip, save_shoulder, save_wrist, save_head, save_spine, save_tilt, save_balance, duration


def update_plots(save, save_hip, save_shoulder, save_wrist, save_head, save_spine, save_tilt, save_balance, duration):
    timeline = np.linspace(0, duration, len(save))
    hip_filt = np.array(signal.savgol_filter(save_hip, 61, 4))
    shoulder_filt = np.array(signal.savgol_filter(save_shoulder, 91, 4))
    wrist_filt = np.array(signal.savgol_filter(save_wrist, 121, 4))

    ind, = signal.argrelextrema(np.array(hip_filt), np.greater, order=10)
    ind2, = signal.argrelextrema(np.array(shoulder_filt), np.greater, order=10)
    ind3, = signal.argrelextrema(np.array(wrist_filt), np.greater, order=10)

    '''ind_sort = ind[np.argpartition(hip_filt[ind], -2)[-2:]]
    ind2_sort = ind2[np.argpartition(shoulder_filt[ind2], -2)[-2:]]
    ind3_sort = ind3[np.argpartition(wrist_filt[ind3], -2)[-2:]]'''

    #ind = np.argmax(hip_filt)
    #ind2 = np.argmax(shoulder_filt)
    #ind3 = np.argmax(wrist_filt)

    seq = {'Hip':ind[0], 'Shoulder':ind2[0], 'Wrist':ind3[0]}
    seq_sorted = dict(sorted(seq.items(), key=lambda x: x[1]))

    fig = go.Figure(data=go.Scatter(x=timeline, y=hip_filt, name=f'Hip', legendrank=seq_sorted['Hip']))

    fig.add_trace(
        go.Scatter(
            x=timeline,
            y=shoulder_filt,
            name=f'Shoulder',
            legendrank=seq_sorted['Shoulder']
        )
    )

    fig.add_trace(
        go.Scatter(
            x=timeline,
            y=wrist_filt,
            name=f'Wrist',
            legendrank=seq_sorted['Wrist']
        )
    )

    fig.add_trace(
        go.Scatter(
            x=timeline[ind],
            y=hip_filt[ind],
            mode='markers',
            marker_size=10,
            showlegend=False
        )
    )

    fig.add_trace(
        go.Scatter(
            x=timeline[ind2],
            y=shoulder_filt[ind2],
            mode='markers',
            marker_size=10,
            showlegend=False
        )
    )

    fig.add_trace(
        go.Scatter(
            x=timeline[ind3],
            y=wrist_filt[ind3],
            mode='markers',
            marker_size=10,
            showlegend=False
        )
    )

    fig.update_layout(
        title='Sequence',
        yaxis_title="angle in degree",
        xaxis_title="time in s"
    )

    fig3 = go.Figure(data=go.Scatter(x=timeline, y=signal.savgol_filter(save_head, 61, 4)))

    fig3.update_layout(
        title='Head movement',
        yaxis_title='position from ground in m',
        xaxis_title="time in s"
    )

    fig4 = go.Figure(data=go.Scatter(x=timeline, y=signal.savgol_filter(save_spine, 31, 4)))

    fig4.update_layout(
        title='Angle of spine to ground',
        yaxis_title='angle in °',
        xaxis_title="time in s"
    )

    fig5 = go.Figure(data=go.Scatter(x=timeline, y=signal.savgol_filter(save_tilt, 31, 4)))

    fig5.update_layout(
        title='Spine tilt',
        yaxis_title='angle in °',
        xaxis_title="time in s"
    )

    fig6 = go.Figure(data=go.Scatter(x=timeline, y=save_balance))

    fig6.update_layout(
        title='Balance',
        yaxis_title='right left',
        xaxis_title="time in s"
    )

    return fig, fig3, fig4, fig5, fig6


# Plots

fig2 = go.Figure(data=go.Scatter(x=timeline, y=save))

fig2.update_layout(
    title='Angle between left wrist, elbow and shoulder',
    yaxis_title="angle in degree",
    xaxis_title="time in s"
)

grad = np.gradient(signal.savgol_filter(save, 5, 4))

fig1 = go.Figure(data=go.Scatter(x=timeline, y=signal.savgol_filter(grad, 5, 4)))

fig1.update_layout(
    title='Angular velocity',
    yaxis_title="angular velocity in degree/s",
    xaxis_title="time in s"
)

hip_filt = np.array(signal.savgol_filter(save_hip, 61, 4))
shoulder_filt = np.array(signal.savgol_filter(save_shoulder, 91, 4))
wrist_filt = np.array(signal.savgol_filter(save_wrist, 121, 4))

ind, = signal.argrelextrema(np.array(hip_filt), np.greater, order=10)
ind2, = signal.argrelextrema(np.array(shoulder_filt), np.greater, order=10)
ind3, = signal.argrelextrema(np.array(wrist_filt), np.greater, order=10)

'''ind_sort = ind[np.argpartition(hip_filt[ind], -2)[-2:]]
ind2_sort = ind2[np.argpartition(shoulder_filt[ind2], -2)[-2:]]
ind3_sort = ind3[np.argpartition(wrist_filt[ind3], -2)[-2:]]'''

#ind = np.argmax(hip_filt)
#ind2 = np.argmax(shoulder_filt)
#ind3 = np.argmax(wrist_filt)

seq = {'Hip':ind[0], 'Shoulder':ind2[0], 'Wrist':ind3[0]}
seq_sorted = dict(sorted(seq.items(), key=lambda x: x[1]))

fig = go.Figure(data=go.Scatter(x=timeline, y=hip_filt, name=f'Hip', legendrank=seq_sorted['Hip']))

fig.add_trace(
    go.Scatter(
        x=timeline,
        y=shoulder_filt,
        name=f'Shoulder',
        legendrank=seq_sorted['Shoulder']
    )
)

fig.add_trace(
    go.Scatter(
        x=timeline,
        y=wrist_filt,
        name=f'Wrist',
        legendrank=seq_sorted['Wrist']
    )
)

fig.add_trace(
    go.Scatter(
        x=timeline[ind],
        y=hip_filt[ind],
        mode='markers',
        marker_size=10,
        showlegend=False
    )
)

fig.add_trace(
    go.Scatter(
        x=timeline[ind2],
        y=shoulder_filt[ind2],
        mode='markers',
        marker_size=10,
        showlegend=False
    )
)

fig.add_trace(
    go.Scatter(
        x=timeline[ind3],
        y=wrist_filt[ind3],
        mode='markers',
        marker_size=10,
        showlegend=False
    )
)

fig.update_layout(
    title='Sequence',
    yaxis_title="angle in degree",
    xaxis_title="time in s"
)

fig3 = go.Figure(data=go.Scatter(x=timeline, y=signal.savgol_filter(save_head, 61, 4)))

fig3.update_layout(
    title='Head movement',
    yaxis_title='position from ground in m',
    xaxis_title="time in s"
)

fig4 = go.Figure(data=go.Scatter(x=timeline, y=signal.savgol_filter(save_spine, 31, 4)))

fig4.update_layout(
    title='Angle of spine to ground',
    yaxis_title='angle in °',
    xaxis_title="time in s"
)

fig5 = go.Figure(data=go.Scatter(x=timeline, y=signal.savgol_filter(save_tilt, 31, 4)))

fig5.update_layout(
    title='Spine tilt',
    yaxis_title='angle in °',
    xaxis_title="time in s"
)

fig6 = go.Figure(data=go.Scatter(x=timeline, y=save_balance))

fig6.update_layout(
    title='Balance',
    yaxis_title='right left',
    xaxis_title="time in s"
)


# Initialize the app
app = Dash(__name__)
server = app.server

app.title = 'Swing Analysis'

app.layout = html.Div(
    children=[

        html.Center(
            html.Div(children=[
                dcc.Upload(
                    id='upload-data',
                    children=html.Div([
                        'Drag and Drop or ',
                        html.A('Select Files')
                    ]),
                    style={
                        'width': '90%',
                        'height': '100px',
                        'lineHeight': '100px',
                        'borderWidth': '1px',
                        'borderStyle': 'dashed',
                        'borderRadius': '5px',
                        'textAlign': 'center',
                        'margin': '30px',
                        #'margin-top':'80px',
                        'display': 'inline-block',
                        'font-family':'sans-serif',
                    },
                )]
            ),
        ),

        dcc.Loading(
                id='loading',
                type='graph',
                fullscreen=True,
                children=
                    dcc.Graph(
                        id='sequence',
                        figure=fig,
                        style={'width': '100%', 'display': 'inline-block'}
                    ),
        ),

        dcc.Graph(
            id='head',
            figure=fig3
        ),

        html.Div(children=[

            dcc.Graph(
                id='spine_ground',
                figure=fig4,
                style={'width': '50%', 'display': 'inline-block'}
            ),

            dcc.Graph(
                id='spine_tilt',
                figure=fig5,
                style={'width': '50%', 'display': 'inline-block'}
            ),
        ]),

        dcc.Graph(
            id='balance',
            figure=fig6
        ),
    ]
)

@app.callback(
    [Output('sequence', 'figure'), Output('head', 'figure'), Output('spine_ground', 'figure'), Output('spine_tilt', 'figure'), Output('balance', 'figure')],
    Input('upload-data', 'contents'),
    prevent_initial_call=True
)
def process(filename):

    image, save, save_hip, save_shoulder, save_wrist, save_head, save_spine, save_tilt, save_balance, duration = process_motion(filename)
    fig = go.Figure(data=go.Image(z=image))

    seq, head, spine_ground, spine_tilt, balance = update_plots(save, save_hip, save_shoulder, save_wrist, save_head, save_spine, save_tilt, save_balance, duration)

    return [seq, head, spine_ground, spine_tilt, balance]


if  __name__ == '__main__':
    app.run_server(debug=True)