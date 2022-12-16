import mediapipe as mp
import cv2
import numpy as np
import plotly.graph_objects as go
import plotly.io as pio
from dash import Dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
from scipy import signal
import tempfile
import base64
from collections import deque

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose

# Set theme for dash
pio.templates.default = "plotly_white"

# Hide plotly logo
config = dict({'displaylogo': False})


# Random inititalization for data
def rand(length, size):
    full = [np.full(length, np.random.randint(0, 30)) for _ in range(size)]
    return full


image, save, save_hip, save_shoulder, save_wrist, save_head, save_spine, save_tilt, save_balance = rand(10, 9)
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

    return round(distance_l - distance_r, 4)


# Read video and process frame by frame
def process_motion(contents, filename):
    content_type, content_string = contents.split(',')
    name = filename.split('.')[0]

    decoded = base64.b64decode(content_string)

    with tempfile.NamedTemporaryFile() as temp:
        temp.write(decoded)
        # with io.BytesIO(decoded).read() as temp:
        #     print(type(temp))

        cap = cv2.VideoCapture(temp.name)
        # cap = cv2.VideoCapture(temp)

        frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        fps = cap.get(cv2.CAP_PROP_FPS)

        # calculate duration of the video
        duration = round(frames / fps)

        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        # fourcc = cv2.VideoWriter_fourcc(*'MJPG')
        fourcc = cv2.VideoWriter_fourcc(*'h264')
        # fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        # writer = cv2.VideoWriter('out/' + name + '_motion.mp4', fourcc, fps, (width, height))

        save = deque([])
        save_hip = deque([])
        save_shoulder = deque([])
        save_wrist = deque([])
        save_head = deque([])
        save_spine = deque([])
        save_tilt = deque([])
        save_balance = deque([])

        rot = False
        # meta_dict = ffmpeg.probe(file)
        # if int(meta_dict['streams'][0]['tags']['rotate']) == 180:
        #    rot = True

        with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5, model_complexity=2) as pose:
            while cap.isOpened():
                ret, frame = cap.read()

                if ret is False:
                    break

                if rot:
                    frame = cv2.rotate(frame, cv2.ROTATE_180)

                # Recolor image to RGB
                image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image.flags.writeable = False

                # Make detection
                results = pose.process(image)

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

                    save_head.append(abs(nose.y - foot_r.y))

                    angle_back = back_angle(shoulder_l, shoulder_r)
                    save_spine.append(abs(angle_back))

                    tilt = tilt_angle(shoulder_l, shoulder_r)
                    save_tilt.append(tilt)

                    bal = mass_balance(foot_l, foot_r)
                    save_balance.append(bal)

                    cv2.putText(image, f'Arm: {int(angle)}', (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.4, (255, 255, 255),
                                2, cv2.LINE_AA)
                    cv2.putText(image, f'Hip: {int(angle_h)}', (100, 140), cv2.FONT_HERSHEY_SIMPLEX, 1.4,
                                (255, 255, 255), 2, cv2.LINE_AA)
                    cv2.putText(image, f'Shoulder: {int(angle_s)}', (100, 180), cv2.FONT_HERSHEY_SIMPLEX, 1.4,
                                (255, 255, 255), 2, cv2.LINE_AA)
                    cv2.putText(image, f'Wrist: {int(angle_w)}', (100, 220), cv2.FONT_HERSHEY_SIMPLEX, 1.4,
                                (255, 255, 255), 2, cv2.LINE_AA)
                    cv2.putText(image, f'Spine: {int(angle_back)}', (100, 260), cv2.FONT_HERSHEY_SIMPLEX, 1.4,
                                (255, 255, 255), 2, cv2.LINE_AA)
                    cv2.putText(image, f'Tilt: {int(tilt)}', (100, 300), cv2.FONT_HERSHEY_SIMPLEX, 1.4, (255, 255, 255),
                                2, cv2.LINE_AA)
                    cv2.putText(image, f'Bal.: {bal}', (100, 340), cv2.FONT_HERSHEY_SIMPLEX, 1.4, (255, 255, 255), 2,
                                cv2.LINE_AA)
                    # cv2.putText(image, str(hip_l), (100,140), cv2. FONT_HERSHEY_SIMPLEX, 1.4, (255, 255, 255), 2, cv2.LINE_AA)
                    # cv2.putText(image, str(hip_r), (100,180), cv2. FONT_HERSHEY_SIMPLEX, 1.4, (255, 255, 255), 2, cv2.LINE_AA)

                except:
                    pass

                # Recolor back to BGR
                image.flags.writeable = True
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

                # Render detections

                mp_drawing.draw_landmarks(
                    image,
                    results.pose_landmarks,
                    mp_pose.POSE_CONNECTIONS,
                    landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style()
                )

                # cv2. imshow('Mediapipe Feed', image)
                # writer.write(image)

                # mp_drawing.plot_landmarks(results.pose_world_landmarks, mp_pose.POSE_CONNECTIONS)

                if cv2.waitKey(10) & 0xFF == ord('q'):
                    break

        cap.release()
        cv2.destroyAllWindows()
        cv2.waitKey(1)

        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    return image, save, save_hip, save_shoulder, save_wrist, save_head, save_spine, save_tilt, save_balance, duration


# Update plots after video is processed/callback
def update_plots(save, save_hip, save_shoulder, save_wrist, save_head, save_spine, save_tilt, save_balance, duration):
    converted = [np.array(name) for name in
                 [save, save_hip, save_shoulder, save_wrist, save_head, save_spine, save_tilt, save_balance]]
    save, save_hip, save_shoulder, save_wrist, save_head, save_spine, save_tilt, save_balance = converted

    timeline = np.linspace(0, duration, len(save))
    hip_filt = np.array(signal.savgol_filter(save_hip, 21, 4))
    shoulder_filt = np.array(signal.savgol_filter(save_shoulder, 21, 4))
    wrist_filt = np.array(signal.savgol_filter(save_wrist, 21, 4))
    balance_filt = np.array(signal.savgol_filter(save_balance, 21, 4))

    # ind, = signal.argrelextrema(np.array(hip_filt), np.greater, order=10)
    # ind2, = signal.argrelextrema(np.array(shoulder_filt), np.greater, order=10)
    # ind3, = signal.argrelextrema(np.array(wrist_filt), np.greater, order=10)

    # seq = {'Hip':ind[0], 'Shoulder':ind2[0], 'Wrist':ind3[0]}
    # seq_sorted = dict(sorted(seq.items(), key=lambda x: x[1]))

    fig = go.Figure(data=go.Scatter(x=timeline, y=hip_filt, name=f'Hip',  # legendrank=seq_sorted['Hip']
                                    ))

    fig.add_trace(
        go.Scatter(
            x=timeline,
            y=shoulder_filt,
            name=f'Shoulder',
            # legendrank=seq_sorted['Shoulder']
        )
    )

    fig.add_trace(
        go.Scatter(
            x=timeline,
            y=wrist_filt,
            name=f'Wrist',
            # legendrank=seq_sorted['Wrist']
        )
    )

    '''fig.add_trace(
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
    )'''

    fig.update_layout(
        title='Sequence',
        title_x=0.5,
        font_size=15,
        yaxis_title="angle in degree",
        xaxis_title="time in s",
        paper_bgcolor='rgba(0,0,0,0)',
        modebar=dict(
            bgcolor='rgba(0,0,0,0)',
            color='rgba(1,1,1,0.3)',
            activecolor='rgba(58, 73, 99, 1)'
        )
    )

    fig3 = go.Figure(data=go.Scatter(x=timeline, y=signal.savgol_filter(save_head, 61, 4)))

    fig3.update_layout(
        title='Head movement',
        title_x=0.5,
        font_size=15,
        yaxis_title='position from ground in m',
        xaxis_title="time in s",
        paper_bgcolor='rgba(0,0,0,0)',
        modebar=dict(
            bgcolor='rgba(0,0,0,0)',
            color='rgba(1,1,1,0.3)',
            activecolor='rgba(58, 73, 99, 1)'
        )
    )

    fig4 = go.Figure(data=go.Scatter(x=timeline, y=signal.savgol_filter(save_spine, 31, 4)))

    fig4.update_layout(
        title='Angle of spine to ground',
        title_x=0.5,
        font_size=15,
        yaxis_title='angle in °',
        xaxis_title="time in s",
        paper_bgcolor='rgba(0,0,0,0)',
        modebar=dict(
            bgcolor='rgba(0,0,0,0)',
            color='rgba(1,1,1,0.3)',
            activecolor='rgba(58, 73, 99, 1)'
        )
    )

    fig5 = go.Figure(data=go.Scatter(x=timeline, y=signal.savgol_filter(save_tilt, 31, 4)))

    fig5.update_layout(
        title='Spine tilt',
        title_x=0.5,
        font_size=15,
        yaxis_title='angle in °',
        xaxis_title="time in s",
        paper_bgcolor='rgba(0,0,0,0)',
        modebar=dict(
            bgcolor='rgba(0,0,0,0)',
            color='rgba(1,1,1,0.3)',
            activecolor='rgba(58, 73, 99, 1)'
        )
    )

    fig6 = go.Figure(data=go.Scatter(x=timeline, y=balance_filt))

    fig6.update_layout(
        title='Balance',
        title_x=0.5,
        font_size=15,
        yaxis_title='Right          Left',
        xaxis_title="time in s",
        paper_bgcolor='rgba(0,0,0,0)',
        modebar=dict(
            bgcolor='rgba(0,0,0,0)',
            color='rgba(1,1,1,0.3)',
            activecolor='rgba(58, 73, 99, 1)'
        )
    )

    return fig, fig3, fig4, fig5, fig6


# Plots

# hip_filt = np.array(signal.savgol_filter(save_hip, 61, 4))
# shoulder_filt = np.array(signal.savgol_filter(save_shoulder, 91, 4))
# wrist_filt = np.array(signal.savgol_filter(save_wrist, 121, 4))

# ind, = signal.argrelextrema(np.array(hip_filt), np.greater, order=10)
# ind2, = signal.argrelextrema(np.array(shoulder_filt), np.greater, order=10)
# ind3, = signal.argrelextrema(np.array(wrist_filt), np.greater, order=10)


# seq = {'Hip':ind[0], 'Shoulder':ind2[0], 'Wrist':ind3[0]}
# seq_sorted = dict(sorted(seq.items(), key=lambda x: x[1]))

fig = go.Figure(data=go.Scatter(x=timeline, y=save_hip, name=f'Hip',  # legendrank=seq_sorted['Hip']
                                ))

fig.add_trace(
    go.Scatter(
        x=timeline,
        y=save_shoulder,
        name=f'Shoulder',
        # legendrank=seq_sorted['Shoulder']
    )
)

fig.add_trace(
    go.Scatter(
        x=timeline,
        y=save_wrist,
        name=f'Wrist',
        # legendrank=seq_sorted['Wrist']
    )
)

'''fig.add_trace(
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
)'''

fig.update_layout(
    title='Sequence',
    title_x=0.5,
    font_size=15,
    yaxis_title="angle in °",
    xaxis_title="time in s",
    paper_bgcolor='rgba(0,0,0,0)',
    modebar=dict(
        bgcolor='rgba(0,0,0,0)',
        color='rgba(1,1,1,0.3)',
        activecolor='rgba(58, 73, 99, 1)'
    )
),

fig3 = go.Figure(data=go.Scatter(x=timeline, y=save_head))

fig3.update_layout(
    title='Head movement',
    title_x=0.5,
    font_size=15,
    yaxis_title='position from ground in m',
    xaxis_title="time in s",
    paper_bgcolor='rgba(0,0,0,0)',
    modebar=dict(
        bgcolor='rgba(0,0,0,0)',
        color='rgba(1,1,1,0.3)',
        activecolor='rgba(58, 73, 99, 1)'
    )
)

fig4 = go.Figure(data=go.Scatter(x=timeline, y=save_spine))

fig4.update_layout(
    title='Angle of spine to ground',
    title_x=0.5,
    font_size=15,
    yaxis_title='angle in °',
    xaxis_title="time in s",
    paper_bgcolor='rgba(0,0,0,0)',
    modebar=dict(
        bgcolor='rgba(0,0,0,0)',
        color='rgba(1,1,1,0.3)',
        activecolor='rgba(58, 73, 99, 1)'
    )
)

fig5 = go.Figure(data=go.Scatter(x=timeline, y=save_tilt))

fig5.update_layout(
    title='Spine tilt',
    title_x=0.5,
    font_size=15,
    yaxis_title='angle in °',
    xaxis_title="time in s",
    paper_bgcolor='rgba(0,0,0,0)',
    modebar=dict(
        bgcolor='rgba(0,0,0,0)',
        color='rgba(1,1,1,0.3)',
        activecolor='rgba(58, 73, 99, 1)'
    )
)

fig6 = go.Figure(data=go.Scatter(x=timeline, y=save_balance))

fig6.update_layout(
    title='Balance',
    title_x=0.5,
    font_size=15,
    yaxis_title='Right Left',
    xaxis_title="time in s",
    paper_bgcolor='rgba(0,0,0,0)',
    modebar=dict(
        bgcolor='rgba(0,0,0,0)',
        color='rgba(1,1,1,0.3)',
        activecolor='rgba(58, 73, 99, 1)'
    )
)


# Initialize the app
app = Dash(__name__)
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

        html.Center(
            html.Div(children=[
                dcc.Upload(
                    id='upload-data',
                    children=html.Div([
                        'Drag and Drop or ',
                        html.A('Select Video️'),
                        ' ⛳️'
                    ]),
                    style={
                        'width': '90%',
                        'height': '130px',
                        'lineHeight': '130px',
                        'borderWidth': '4px',
                        'borderStyle': 'dashed',
                        'borderRadius': '30px',
                        'textAlign': 'center',
                        'margin-bottom': '2%',
                        'display': 'inline-block',
                        'font-family': 'sans-serif',
                        'font-size': '20px',
                        'font-weight': 'bold',
                        'color': 'rgba(58, 73, 99, 1)',
                        'borderColor': 'rgba(58, 73, 99, 1)'
                    },
                )]
            ),
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

        html.Div(
            dcc.Graph(
                id='head',
                figure=fig3,
                config=config,
                className='container'
            )
        ),

        html.Div(children=[

            dcc.Graph(
                id='spine_ground',
                figure=fig4,
                config=config,
                className='container_half_left'
            ),

            dcc.Graph(
                id='spine_tilt',
                figure=fig5,
                config=config,
                className='container_half_right'
            ),
        ],
        ),

        dcc.Graph(
            id='balance',
            figure=fig6,
            config=config,
            className='container'
        ),
    ]
)


@app.callback(
    [Output('sequence', 'figure'), Output('head', 'figure'), Output('spine_ground', 'figure'),
     Output('spine_tilt', 'figure'), Output('balance', 'figure')],
    [Input('upload-data', 'contents'), Input('upload-data', 'filename')],
    prevent_initial_call=True
)
def process(contents, filename):
    image, save, save_hip, save_shoulder, save_wrist, save_head, save_spine, save_tilt, save_balance, duration = process_motion(
        contents, filename)
    # fig = go.Figure(data=go.Image(z=image))

    seq, head, spine_ground, spine_tilt, balance = update_plots(save, save_hip, save_shoulder, save_wrist, save_head,
                                                                save_spine, save_tilt, save_balance, duration)

    return [seq, head, spine_ground, spine_tilt, balance]


if __name__ == '__main__':
    server.run(debug=False)
