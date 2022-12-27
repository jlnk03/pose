import mediapipe as mp
import plotly.graph_objects as go
import plotly.io as pio
import plotly.express as px
from dash import Dash
from dash import html, dcc
from dash.dependencies import Input, Output
import pandas as pd
from scipy import signal
from process_mem import process_motion
from angles import *
# import firebase_admin
# from firebase_admin import credentials, auth

# Replace the path and filename with the path to and filename of your service account key file
# cred = credentials.Certificate('assests/private.json')
# firebase_admin.initialize_app(cred)

# Tools for mp to draw the pose
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose
# mp_pose = mp.solutions.holistic

# Set theme for dash
pio.templates.default = "plotly_white"

# Hide plotly logo
config = dict({'displaylogo': False})

_PRESENCE_THRESHOLD = 0.5
_VISIBILITY_THRESHOLD = 0.5


def plot_landmarks(
        landmark_list,
        connections=None,
        angle='connection'
):
    if not landmark_list:
        return
    plotted_landmarks = {}
    for idx, landmark in enumerate(landmark_list.landmark):
        if (
                landmark.HasField("visibility")
                and landmark.visibility < _VISIBILITY_THRESHOLD
        ) or (
                landmark.HasField("presence") and landmark.presence < _PRESENCE_THRESHOLD
        ):
            continue
        plotted_landmarks[idx] = (-landmark.z, landmark.x, -landmark.y)
    if connections:
        out_cn = []
        num_landmarks = len(landmark_list.landmark)
        # Draws the connections if the start and end landmarks are both visible.
        for connection in connections:
            start_idx = connection[0]
            end_idx = connection[1]
            if not (0 <= start_idx < num_landmarks and 0 <= end_idx < num_landmarks):
                raise ValueError(
                    f"Landmark index is out of range. Invalid connection "
                    f"from landmark #{start_idx} to landmark #{end_idx}."
                )
            if start_idx in plotted_landmarks and end_idx in plotted_landmarks:
                landmark_pair = [
                    plotted_landmarks[start_idx],
                    plotted_landmarks[end_idx],
                ]
                out_cn.append(
                    dict(
                        xs=[landmark_pair[0][0], landmark_pair[1][0]],
                        ys=[landmark_pair[0][1], landmark_pair[1][1]],
                        zs=[landmark_pair[0][2], landmark_pair[1][2]],
                    )
                )
        cn2 = {"xs": [], "ys": [], "zs": []}
        for pair in out_cn:
            for k in pair.keys():
                cn2[k].append(pair[k][0])
                cn2[k].append(pair[k][1])
                cn2[k].append(None)

    df = pd.DataFrame(plotted_landmarks).T.rename(columns={0: "z", 1: "x", 2: "y"})
    df["lm"] = df.index.map(lambda s: mp_pose.PoseLandmark(s).name).values
    fig = (
        px.scatter_3d(df, x="z", y="x", z="y", hover_name="lm")
        .update_traces(marker={"color": "red"})
        .update_layout(
            margin={"l": 0, "r": 0, "t": 0, "b": 0},
            scene={"camera": {"eye": {"x": 2.1, "y": 0, "z": 0}}},
        )
    )
    fig.add_traces(
        [
            go.Scatter3d(
                x=cn2["xs"],
                y=cn2["ys"],
                z=cn2["zs"],
                mode="lines",
                line={"color": "black", "width": 5},
                name=angle,
            )
        ]
    )

    return fig


# Random inititalization for data
def rand(length, size):
    full = [np.full(length, np.random.randint(0, 30)) for _ in range(size)]
    return full


save_pelvis_rotation, save_pelvis_tilt, save_pelvis_lift, save_pelvis_sway, save_pelvis_thrust, \
save_thorax_lift, save_thorax_bend, save_thorax_sway, save_thorax_rotation, save_thorax_thrust, \
save_thorax_tilt, save_spine_rotation, save_spine_tilt, save_head_rotation, save_head_tilt, save_left_arm_length, \
save_wrist_angle, save_wrist_tilt = rand(100, 18)

duration = 10
timeline = np.linspace(0, duration, len(save_pelvis_rotation))


def filter_data(data):
    b, a = signal.butter(3, 0.05)
    data = signal.filtfilt(b, a, data)
    return data


# Update plots after video is processed/callback
def update_plots(save_pelvis_rotation, save_pelvis_tilt, save_pelvis_lift, save_pelvis_sway, save_pelvis_thrust,
                 save_thorax_lift, save_thorax_bend, save_thorax_sway, save_thorax_rotation, save_thorax_thrust,
                 save_thorax_tilt, save_spine_rotation, save_spine_tilt, save_head_rotation, save_head_tilt,
                 save_left_arm_length, save_wrist_angle, save_wrist_tilt, duration):
    converted = [filter_data(np.array(name)) for name in
                 [save_pelvis_rotation, save_pelvis_tilt, save_pelvis_lift, save_pelvis_sway, save_pelvis_thrust,
                  save_thorax_lift, save_thorax_bend, save_thorax_sway, save_thorax_rotation, save_thorax_thrust,
                  save_thorax_tilt, save_spine_rotation, save_spine_tilt, save_head_rotation, save_head_tilt,
                  save_left_arm_length, save_wrist_angle, save_wrist_tilt]]

    save_pelvis_rotation, save_pelvis_tilt, save_pelvis_lift, save_pelvis_sway, save_pelvis_thrust, \
    save_thorax_lift, save_thorax_bend, save_thorax_sway, save_thorax_rotation, save_thorax_thrust, \
    save_thorax_tilt, save_spine_rotation, save_spine_tilt, save_head_rotation, save_head_tilt, save_left_arm_length, save_wrist_angle, save_wrist_tilt = converted

    timeline = np.linspace(0, duration, len(save_pelvis_rotation))

    save_pelvis_lift = save_pelvis_lift - save_pelvis_lift[0]
    save_pelvis_sway = save_pelvis_sway - save_pelvis_sway[0]
    save_pelvis_thrust = save_pelvis_thrust - save_pelvis_thrust[0]
    save_thorax_lift = save_thorax_lift - save_thorax_lift[0]
    save_thorax_sway = save_thorax_sway - save_thorax_sway[0]
    save_thorax_thrust = save_thorax_thrust - save_thorax_thrust[0]

    fig = go.Figure(data=go.Scatter(x=timeline, y=-np.gradient(save_pelvis_rotation), name=f'Pelvis'))

    fig.add_trace(
        go.Scatter(
            x=timeline,
            y=-np.gradient(save_thorax_rotation),
            name=f'Thorax',
            # legendrank=seq_sorted['Shoulder']
        )
    )

    fig.update_layout(
        title='Kinematic Sequence',
        title_x=0.5,
        font_size=15,
        yaxis_title="Angular velocity in °/s",
        xaxis_title="time in s",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        legend_orientation="h",
        legend=dict(y=1, yanchor="bottom"),
        margin=dict(
            l=100
        ),
        modebar=dict(
            bgcolor='rgba(0,0,0,0)',
            color='rgba(1,1,1,0.3)',
            activecolor='rgba(58, 73, 99, 1)'
        )
    ),

    fig3 = go.Figure(data=go.Scatter(x=timeline, y=save_pelvis_tilt, name=f'Pelvis side bend'))

    fig3.add_trace(
        go.Scatter(x=timeline, y=save_pelvis_rotation, name=f'Pelvis rotation')
    )

    fig3.update_layout(
        title='Pelvis angles',
        title_x=0.5,
        font_size=15,
        yaxis_title='angle in °',
        xaxis_title="time in s",
        paper_bgcolor='rgba(0,0,0,0)',
        legend_orientation="h",
        legend=dict(y=1, yanchor="bottom"),
        margin=dict(
            l=100
        ),
        modebar=dict(
            bgcolor='rgba(0,0,0,0)',
            color='rgba(1,1,1,0.3)',
            activecolor='rgba(58, 73, 99, 1)'
        )
    )

    fig4 = go.Figure(data=go.Scatter(x=timeline, y=save_pelvis_lift, name=f'Pelvis lift'))

    fig4.add_trace(
        go.Scatter(x=timeline, y=save_pelvis_sway, name=f'Pelvis_sway')
    )

    fig4.add_trace(
        go.Scatter(x=timeline, y=save_pelvis_thrust, name=f'Pelvis_thrust')
    )

    fig4.update_layout(
        title='Pelvis displacement',
        title_x=0.5,
        font_size=15,
        yaxis_title='Displacement in m',
        xaxis_title="time in s",
        paper_bgcolor='rgba(0,0,0,0)',
        legend_orientation="h",
        legend=dict(y=1, yanchor="bottom"),
        margin=dict(
            l=100
        ),
        modebar=dict(
            bgcolor='rgba(0,0,0,0)',
            color='rgba(1,1,1,0.3)',
            activecolor='rgba(58, 73, 99, 1)'
        )
    )

    fig5 = go.Figure(data=go.Scatter(x=timeline, y=save_thorax_rotation, name=f'Thorax rotation'))

    fig5.add_trace(
        go.Scatter(x=timeline, y=save_thorax_bend, name=f'Thorax bend')
    )

    fig5.add_trace(
        go.Scatter(x=timeline, y=save_thorax_tilt, name=f'Thorax tilt')
    )

    fig5.update_layout(
        title='Thorax angles',
        title_x=0.5,
        font_size=15,
        yaxis_title='angle in °',
        xaxis_title="time in s",
        paper_bgcolor='rgba(0,0,0,0)',
        legend_orientation="h",
        legend=dict(y=1, yanchor="bottom"),
        margin=dict(
            l=100
        ),
        modebar=dict(
            bgcolor='rgba(0,0,0,0)',
            color='rgba(1,1,1,0.3)',
            activecolor='rgba(58, 73, 99, 1)'
        )
    )

    fig6 = go.Figure(data=go.Scatter(x=timeline, y=save_thorax_thrust, name=f'Thorax thrust'))

    fig6.add_trace(
        go.Scatter(x=timeline, y=save_thorax_sway, name=f'Thorax sway')
    )

    fig6.add_trace(
        go.Scatter(x=timeline, y=save_thorax_lift, name=f'Thorax lift')
    )

    fig6.update_layout(
        title='Thorax displacement',
        title_x=0.5,
        font_size=15,
        yaxis_title='Displacement in m',
        xaxis_title="time in s",
        paper_bgcolor='rgba(0,0,0,0)',
        legend_orientation="h",
        legend=dict(y=1, yanchor="bottom"),
        margin=dict(
            l=100
        ),
        modebar=dict(
            bgcolor='rgba(0,0,0,0)',
            color='rgba(1,1,1,0.3)',
            activecolor='rgba(58, 73, 99, 1)'
        )
    )

    fig11 = go.Figure(data=go.Scatter(x=timeline, y=save_spine_tilt))

    fig11.update_layout(
        title='Tilt between pelvis and shoulder',
        title_x=0.5,
        font_size=15,
        yaxis_title='angle in °',
        xaxis_title="time in s",
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(
            l=100
        ),
        modebar=dict(
            bgcolor='rgba(0,0,0,0)',
            color='rgba(1,1,1,0.3)',
            activecolor='rgba(58, 73, 99, 1)'
        )
    )

    fig12 = go.Figure(data=go.Scatter(x=timeline, y=save_head_tilt))

    fig12.update_layout(
        title='Head tilt',
        title_x=0.5,
        font_size=15,
        yaxis_title='angle in °',
        xaxis_title="time in s",
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(
            l=100
        ),
        modebar=dict(
            bgcolor='rgba(0,0,0,0)',
            color='rgba(1,1,1,0.3)',
            activecolor='rgba(58, 73, 99, 1)'
        )
    )

    fig13 = go.Figure(data=go.Scatter(x=timeline, y=save_head_rotation))

    fig13.update_layout(
        title='Head rotation',
        title_x=0.5,
        font_size=15,
        yaxis_title='angle in °',
        xaxis_title="time in s",
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(
            l=100
        ),
        modebar=dict(
            bgcolor='rgba(0,0,0,0)',
            color='rgba(1,1,1,0.3)',
            activecolor='rgba(58, 73, 99, 1)'
        )
    )

    fig14 = go.Figure(data=go.Scatter(x=timeline, y=save_left_arm_length))

    fig14.update_layout(
        title='Left arm length',
        title_x=0.5,
        font_size=15,
        yaxis_title='length in m',
        xaxis_title="time in s",
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(
            l=100
        ),
        modebar=dict(
            bgcolor='rgba(0,0,0,0)',
            color='rgba(1,1,1,0.3)',
            activecolor='rgba(58, 73, 99, 1)'
        )
    )

    fig15 = go.Figure(data=go.Scatter(x=timeline, y=save_spine_rotation))

    fig15.update_layout(
        title='Spine rotation',
        title_x=0.5,
        font_size=15,
        yaxis_title='angle in °',
        xaxis_title="time in s",
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(
            l=100
        ),
        modebar=dict(
            bgcolor='rgba(0,0,0,0)',
            color='rgba(1,1,1,0.3)',
            activecolor='rgba(58, 73, 99, 1)'
        )
    )

    fig16 = go.Figure(data=go.Scatter(x=timeline, y=save_wrist_angle, name=f'Wrist angle'))

    fig16.add_trace(
        go.Scatter(x=timeline, y=save_wrist_tilt, name=f'Wrist tilt')
    )

    fig16.update_layout(
        title='Wrist angle',
        title_x=0.5,
        font_size=15,
        yaxis_title='angle in °',
        xaxis_title="time in s",
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(
            l=100
        ),
        modebar=dict(
            bgcolor='rgba(0,0,0,0)',
            color='rgba(1,1,1,0.3)',
            activecolor='rgba(58, 73, 99, 1)'
        )
    )

    return fig, fig3, fig4, fig5, fig6, fig11, fig12, fig13, fig14, fig15, fig16


# Plots
fig = go.Figure(data=go.Scatter(x=timeline, y=save_pelvis_rotation, name=f'Pelvis'))

fig.add_trace(
    go.Scatter(
        x=timeline,
        y=save_thorax_rotation,
        name=f'Thorax',
        # legendrank=seq_sorted['Shoulder']
    )
)

fig.update_layout(
    title=' Kinematic Sequence',
    title_x=0.5,
    font_size=15,
    yaxis_title="Angular velocity in °/s",
    xaxis_title="time in s",
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    legend_orientation="h",
    legend=dict(y=1, yanchor="bottom"),
    margin=dict(
        l=100
    ),
    modebar=dict(
        bgcolor='rgba(0,0,0,0)',
        color='rgba(1,1,1,0.3)',
        activecolor='rgba(58, 73, 99, 1)'
    )
),

fig3 = go.Figure(data=go.Scatter(x=timeline, y=save_pelvis_tilt, name=f'Pelvis side bend'))

fig3.add_trace(
    go.Scatter(x=timeline, y=save_pelvis_rotation, name=f'Pelvis rotation')
)

fig3.update_layout(
    title='Pelvis angles',
    title_x=0.5,
    font_size=15,
    yaxis_title='angle in °',
    xaxis_title="time in s",
    paper_bgcolor='rgba(0,0,0,0)',
    legend_orientation="h",
    legend=dict(y=1, yanchor="bottom"),
    margin=dict(
        l=100
    ),
    modebar=dict(
        bgcolor='rgba(0,0,0,0)',
        color='rgba(1,1,1,0.3)',
        activecolor='rgba(58, 73, 99, 1)'
    )
)

fig4 = go.Figure(data=go.Scatter(x=timeline, y=save_pelvis_lift, name=f'Pelvis lift'))

fig4.add_trace(
    go.Scatter(x=timeline, y=save_pelvis_sway, name=f'Pelvis_sway')
)

fig4.add_trace(
    go.Scatter(x=timeline, y=save_pelvis_thrust, name=f'Pelvis_thrust')
)

fig4.update_layout(
    title='Pelvis displacement',
    title_x=0.5,
    font_size=15,
    yaxis_title='Displacement in m',
    xaxis_title="time in s",
    paper_bgcolor='rgba(0,0,0,0)',
    legend_orientation="h",
    legend=dict(y=1, yanchor="bottom"),
    margin=dict(
        l=100
    ),
    modebar=dict(
        bgcolor='rgba(0,0,0,0)',
        color='rgba(1,1,1,0.3)',
        activecolor='rgba(58, 73, 99, 1)'
    )
)

fig5 = go.Figure(data=go.Scatter(x=timeline, y=save_thorax_rotation, name=f'Thorax rotation'))

fig5.add_trace(
    go.Scatter(x=timeline, y=save_thorax_bend, name=f'Thorax bend')
)

fig5.add_trace(
    go.Scatter(x=timeline, y=save_thorax_tilt, name=f'Thorax tilt')
)

fig5.update_layout(
    title='Thorax angles',
    title_x=0.5,
    font_size=15,
    yaxis_title='angle in °',
    xaxis_title="time in s",
    paper_bgcolor='rgba(0,0,0,0)',
    legend_orientation="h",
    legend=dict(y=1, yanchor="bottom"),
    margin=dict(
        l=100
    ),
    modebar=dict(
        bgcolor='rgba(0,0,0,0)',
        color='rgba(1,1,1,0.3)',
        activecolor='rgba(58, 73, 99, 1)'
    )
)

fig6 = go.Figure(data=go.Scatter(x=timeline, y=save_thorax_thrust, name=f'Thorax thrust'))

fig6.add_trace(
    go.Scatter(x=timeline, y=save_thorax_sway, name=f'Thorax sway')
)

fig6.add_trace(
    go.Scatter(x=timeline, y=save_thorax_lift, name=f'Thorax lift')
)

fig6.update_layout(
    title='Thorax displacement',
    title_x=0.5,
    font_size=15,
    yaxis_title='Displacement in m',
    xaxis_title="time in s",
    paper_bgcolor='rgba(0,0,0,0)',
    legend_orientation="h",
    legend=dict(y=1, yanchor="bottom"),
    margin=dict(
        l=100
    ),
    modebar=dict(
        bgcolor='rgba(0,0,0,0)',
        color='rgba(1,1,1,0.3)',
        activecolor='rgba(58, 73, 99, 1)'
    )
)

fig11 = go.Figure(data=go.Scatter(x=timeline, y=save_spine_tilt))

fig11.update_layout(
    title='Tilt between pelvis and shoulder',
    title_x=0.5,
    font_size=15,
    yaxis_title='angle in °',
    xaxis_title="time in s",
    paper_bgcolor='rgba(0,0,0,0)',
    margin=dict(
        l=100
    ),
    modebar=dict(
        bgcolor='rgba(0,0,0,0)',
        color='rgba(1,1,1,0.3)',
        activecolor='rgba(58, 73, 99, 1)'
    )
)

fig12 = go.Figure(data=go.Scatter(x=timeline, y=save_head_tilt))

fig12.update_layout(
    title='Head tilt',
    title_x=0.5,
    font_size=15,
    yaxis_title='angle in °',
    xaxis_title="time in s",
    paper_bgcolor='rgba(0,0,0,0)',
    margin=dict(
        l=100
    ),
    modebar=dict(
        bgcolor='rgba(0,0,0,0)',
        color='rgba(1,1,1,0.3)',
        activecolor='rgba(58, 73, 99, 1)'
    )
)

fig13 = go.Figure(data=go.Scatter(x=timeline, y=save_head_rotation))

fig13.update_layout(
    title='Head rotation',
    title_x=0.5,
    font_size=15,
    yaxis_title='angle in °',
    xaxis_title="time in s",
    paper_bgcolor='rgba(0,0,0,0)',
    margin=dict(
        l=100
    ),
    modebar=dict(
        bgcolor='rgba(0,0,0,0)',
        color='rgba(1,1,1,0.3)',
        activecolor='rgba(58, 73, 99, 1)'
    )
)

fig14 = go.Figure(data=go.Scatter(x=timeline, y=save_left_arm_length))

fig14.update_layout(
    title='Left arm length',
    title_x=0.5,
    font_size=15,
    yaxis_title='length in m',
    xaxis_title="time in s",
    paper_bgcolor='rgba(0,0,0,0)',
    margin=dict(
        l=100
    ),
    modebar=dict(
        bgcolor='rgba(0,0,0,0)',
        color='rgba(1,1,1,0.3)',
        activecolor='rgba(58, 73, 99, 1)'
    )
)

fig15 = go.Figure(data=go.Scatter(x=timeline, y=save_spine_rotation))

fig15.update_layout(
    title='Spine rotation',
    title_x=0.5,
    font_size=15,
    yaxis_title='angle in °',
    xaxis_title="time in s",
    paper_bgcolor='rgba(0,0,0,0)',
    margin=dict(
        l=100
    ),
    modebar=dict(
        bgcolor='rgba(0,0,0,0)',
        color='rgba(1,1,1,0.3)',
        activecolor='rgba(58, 73, 99, 1)'
    )
)

fig16 = go.Figure(data=go.Scatter(x=timeline, y=save_wrist_angle, name=f'Wrist angle'))

fig16.add_trace(
    go.Scatter(x=timeline, y=save_wrist_tilt, name=f'Wrist tilt')
)

fig16.update_layout(
    title='Wrist angles',
    title_x=0.5,
    font_size=15,
    yaxis_title='angle in °',
    xaxis_title="time in s",
    paper_bgcolor='rgba(0,0,0,0)',
    margin=dict(
        l=100
    ),
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
# Welcome back, Julian
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

        html.Div(children=[
            dcc.Markdown(
                '''
                ##### Upload your video
                as mp4, mov or avi – max. 50 MB
                '''
                ,
                style={
                    'margin-top': '1%',
                }
            ),
            dcc.Upload(
                id='upload-data',
                children=html.Div([
                    'Drop your video here or ',
                    html.A('browse'),
                    ' ⛳️',
                ]),
                multiple=False,
                max_size=50e6,
                style_active=(dict(
                    backgroundColor='rgba(230, 240, 250, 1)',
                    borderColor='rgba(115, 165, 250, 1)',
                )),
                className='upload'
            )
        ],
            className='container',
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

        html.Div(children=[

            dcc.Graph(
                id='pelvis_rotation',
                figure=fig3,
                config=config,
                className='container_half_left'
            ),

            dcc.Graph(
                id='pelvis_displacement',
                figure=fig4,
                config=config,
                className='container_half_right'
            ),
        ],
        ),

        html.Div(children=[

            dcc.Graph(
                id='thorax_rotation',
                figure=fig5,
                config=config,
                className='container_half_left'
            ),

            dcc.Graph(
                id='thorax_displacement',
                figure=fig6,
                config=config,
                className='container_half_right'
            ),
        ],
        ),

        html.Div(children=[

            dcc.Graph(
                id='h_tilt',
                figure=fig12,
                config=config,
                className='container_half_left'
            ),

            dcc.Graph(
                id='h_rotation',
                figure=fig13,
                config=config,
                className='container_half_right'
            ),
        ],
        ),

        html.Div(
            dcc.Graph(
                id='s_tilt',
                figure=fig11,
                config=config,
                className='container'
            )
        ),

        html.Div(
            dcc.Graph(
                id='arm_length',
                figure=fig14,
                config=config,
                className='container'
            )
        ),

        html.Div(
            dcc.Graph(
                id='spine_rotation',
                figure=fig15,
                config=config,
                className='container'
            )
        ),

        html.Div(
            dcc.Graph(
                id='wrist_angle',
                figure=fig16,
                config=config,
                className='container'
            )
        ),
    ]
)


@app.callback(
    [Output('sequence', 'figure'), Output('pelvis_rotation', 'figure'), Output('pelvis_displacement', 'figure'),
     Output('thorax_rotation', 'figure'), Output('thorax_displacement', 'figure'), Output('s_tilt', 'figure'),
     Output('h_tilt', 'figure'),
     Output('h_rotation', 'figure'), Output('arm_length', 'figure'), Output('spine_rotation', 'figure'), Output('wrist_angle', 'figure')],
    [Input('upload-data', 'contents'), Input('upload-data', 'filename')],
    prevent_initial_call=True
)
def process(contents, filename):
    save_pelvis_rotation, save_pelvis_tilt, save_pelvis_lift, save_pelvis_sway, save_pelvis_thrust, \
    save_thorax_lift, save_thorax_bend, save_thorax_sway, save_thorax_rotation, save_thorax_thrust, \
    save_thorax_tilt, save_spine_rotation, save_spine_tilt, save_head_rotation, save_head_tilt, save_left_arm_length, save_wrist_angle, save_wrist_tilt, duration = process_motion(
        contents, filename)
    # fig = go.Figure(data=go.Image(z=image))

    fig, fig3, fig4, fig5, fig6, fig11, fig12, fig13, fig14, fig15, fig16 = update_plots(save_pelvis_rotation,
                                                                                  save_pelvis_tilt, save_pelvis_lift,
                                                                                  save_pelvis_sway, save_pelvis_thrust,
                                                                                  save_thorax_lift, save_thorax_bend,
                                                                                  save_thorax_sway,
                                                                                  save_thorax_rotation,
                                                                                  save_thorax_thrust,
                                                                                  save_thorax_tilt, save_spine_rotation,
                                                                                  save_spine_tilt, save_head_rotation,
                                                                                  save_head_tilt, save_left_arm_length, save_wrist_angle, save_wrist_tilt,
                                                                                  duration)

    return [fig, fig3, fig4, fig5, fig6, fig11, fig12, fig13, fig14, fig15, fig16]


if __name__ == '__main__':
    app.run_server(debug=True)
