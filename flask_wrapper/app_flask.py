import datetime
import shutil

import mediapipe as mp
import plotly.graph_objects as go
import plotly.io as pio
import plotly.express as px
from dash import Dash, ctx, ALL, MATCH, Input, Output, State, html, dcc
import pandas as pd
from scipy import signal
from code_b.angles import *
from code_b.process_mem import process_motion
import os
from flask_login import current_user
from . import db

# Tools for mp to draw the pose
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose
# mp_pose = mp.solutions.holistic

# Set theme for dash
pio.templates.default = "plotly_white"

# Hide plotly logo
config = dict({'displaylogo': False, 'displayModeBar': False})

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


def upload_video(disabled=True, path=None):
    layout = [
        html.Div(children=[
            html.Div(
                children=[
                    html.Span(
                        'Upload your video',
                        className='text-lg font-medium text-[#3A4963FF] hover:text-gray-900 pt-4'
                    ),
                    html.Span(
                        'as mp4, mov or avi – max. 20 MB',
                        className='text-sm font-medium text-[#3A4963FF] hover:text-gray-900'
                    )
                ],
                className='flex flex-col items-start mx-10 mb-4'
            ),
            html.Div(
                dcc.Upload(
                    disabled=disabled,
                    id='upload-data',
                    children=html.Div(
                        children=
                        [
                            'Drop your video here or ',
                            html.A(' browse'),
                            ' ⛳️',
                        ],
                    ),
                    className='bg-[rgba(251, 252, 254, 1)] mx-10 rounded-2xl flex items-center justify-center py-10 mb-5 text-center inline-block text-sm border-dashed border-4 border-gray-400 h-60',
                    multiple=False,
                    max_size=50e6,
                    accept=['.mp4', '.mov', '.avi'],
                    style_active=(dict(
                        backgroundColor='rgba(230, 240, 250, 1)',
                        borderColor='rgba(115, 165, 250, 1)',
                        borderRadius='12px',
                    )),
                    style_reject=(dict(
                        backgroundColor='bg-red-200',
                        borderColor='bg-red-400',
                        borderRadius='12px',
                    )),
                ),
                className='w-full'
                # className='bg-[rgba(251, 252, 254, 1)] mx-10 sm:rounded-2xl flex items-center justify-center my-10 text-center inline-block flex-col w-[95%] border-dashed border-4 border-gray-400'
            )
        ],
            # className='container',
            className='bg-white shadow rounded-2xl flex items-start justify-center mb-5 text-center inline-block flex-col w-full h-96 mr-5 backdrop-blur-md bg-opacity-80 border border-gray-100',
        ),

        html.Video(src=path, id='video', controls=True,
                   className='h-96 rounded-2xl shadow'),
    ]

    return layout


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


# @memory_profiler.profile
def update_plots(save_pelvis_rotation, save_pelvis_tilt, save_pelvis_lift, save_pelvis_sway, save_pelvis_thrust,
                 save_thorax_lift, save_thorax_bend, save_thorax_sway, save_thorax_rotation, save_thorax_thrust,
                 save_thorax_tilt, save_spine_rotation, save_spine_tilt, save_head_rotation, save_head_tilt,
                 save_left_arm_length, save_wrist_angle, save_wrist_tilt, duration, filt=True):

    if filt:
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

    fig = go.Figure(data=go.Scatter(x=timeline, y=np.gradient(save_pelvis_rotation), name=f'Pelvis'))

    fig.add_trace(
        go.Scatter(
            x=timeline,
            y=np.gradient(save_thorax_rotation),
            name=f'Thorax',
            # legendrank=seq_sorted['Shoulder']
        )
    )

    fig.update_layout(
        title='Kinematic Sequence',
        title_x=0.5,
        font_size=12,
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
        font_size=12,
        yaxis_title='angle in °',
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
        font_size=12,
        yaxis_title='Displacement in m',
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
        font_size=12,
        yaxis_title='angle in °',
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
        font_size=12,
        yaxis_title='Displacement in m',
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
    )

    fig11 = go.Figure(data=go.Scatter(x=timeline, y=save_spine_tilt))

    fig11.update_layout(
        title='Tilt between pelvis and shoulder',
        title_x=0.5,
        font_size=12,
        yaxis_title='angle in °',
        xaxis_title="time in s",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
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
        font_size=12,
        yaxis_title='angle in °',
        xaxis_title="time in s",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
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
        font_size=12,
        yaxis_title='angle in °',
        xaxis_title="time in s",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
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
        font_size=12,
        yaxis_title='length in m',
        xaxis_title="time in s",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
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
        font_size=12,
        yaxis_title='angle in °',
        xaxis_title="time in s",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
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
        font_size=12,
        yaxis_title='angle in °',
        xaxis_title="time in s",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
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
    font_size=12,
    yaxis_title="Angular velocity in °/s",
    xaxis_title="time in s",
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    legend_orientation="h",
    legend=dict(y=1, yanchor="bottom"),
    margin=dict(
        l=80,
        r=50,
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
    font_size=12,
    yaxis_title='angle in °',
    xaxis_title="time in s",
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    legend_orientation="h",
    legend=dict(y=1, yanchor="bottom"),
    margin=dict(
        l=80,
        r=50,
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
    font_size=12,
    yaxis_title='Displacement in m',
    xaxis_title="time in s",
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    legend_orientation="h",
    legend=dict(y=1, yanchor="bottom"),
    margin=dict(
        l=80,
        r=50,
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
    font_size=12,
    yaxis_title='angle in °',
    xaxis_title="time in s",
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    legend_orientation="h",
    legend=dict(y=1, yanchor="bottom"),
    margin=dict(
        l=80,
        r=50,
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
    font_size=12,
    yaxis_title='Displacement in m',
    xaxis_title="time in s",
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    legend_orientation="h",
    legend=dict(y=1, yanchor="bottom"),
    margin=dict(
        l=80,
        r=50,
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
    font_size=12,
    yaxis_title='angle in °',
    xaxis_title="time in s",
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    margin=dict(
        l=80,
        r=50,
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
    font_size=12,
    yaxis_title='angle in °',
    xaxis_title="time in s",
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    margin=dict(
        l=80,
        r=50,
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
    font_size=12,
    yaxis_title='angle in °',
    xaxis_title="time in s",
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    margin=dict(
        l=80,
        r=50,
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
    font_size=12,
    yaxis_title='length in m',
    xaxis_title="time in s",
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    margin=dict(
        l=80,
        r=50,
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
    font_size=12,
    yaxis_title='angle in °',
    xaxis_title="time in s",
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    margin=dict(
        l=80,
        r=50,
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
    font_size=12,
    yaxis_title='angle in °',
    xaxis_title="time in s",
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    margin=dict(
        l=80,
        r=50,
    ),
    modebar=dict(
        bgcolor='rgba(0,0,0,0)',
        color='rgba(1,1,1,0.3)',
        activecolor='rgba(58, 73, 99, 1)'
    )
)


def render_files(files):
    if files is None:
        return []

    template = [html.A(href='# ', children=file, className='text-white text-sm') for file in files]
    print(template)
    return template


def init_dash(server):
    # Initialize the app
    app = Dash(__name__, server=server, url_base_pathname='/dashapp/',
               external_scripts=["https://tailwindcss.com/", {"src": "https://cdn.tailwindcss.com"}]
               )
    # app.css.config.serve_locally = False
    # app.css.append_css({'external_url': './assets/output.css'})
    # server = app.server
    app.app_context = server.app_context

    app.title = 'Swing Analysis'

    def serve_layout():
        disabled = True
        files = []

        if current_user != None:
            if current_user.is_authenticated:
                disabled = False if (current_user.n_analyses > 0 or current_user.unlimited) else True
                id = current_user.id
                if os.path.exists(f'assets/save_data/{id}'):
                    files = os.listdir(f'assets/save_data/{id}')
                    files = [file for file in files if not file.startswith('.')]
                    files.sort(reverse=True)

        layout = html.Div(

            # className="bg-[#F6F9FFFF] h-full",
            # className='bg-gradient-to-br from-amber-50 to-violet-100 h-full',

            children=[

                # navbar top
                html.Div(
                    id='navbar-top',
                    className='flex flex-row w-full h-12 items-center ml-4 lg:hidden z-20',
                    children=[
                        html.Button(
                            className='flex flex-row w-6 h-6 items-center',
                            id='menu-button',
                            children=[
                                html.Img(src=app.get_asset_url('menu_burger.svg'), className='h-4 w-4', id='menu-icon')
                            ]
                        )
                    ]
                ),

                # Sidebar
                html.Div(
                    id='sidebar',
                    className='flex flex-col bg-slate-600 fixed lg:left-5 top-5 bottom-5 w-60 z-10 rounded-2xl hidden lg:flex',
                    children=[
                        html.Div(
                            'HISTORY',
                            className='text-white text-xs font-medium mb-3 mt-12 lg:mt-5 px-4'
                        ),
                        html.Div(
                            className='flex flex-col mb-4 h-full overflow-y-auto border-b border-white',
                            children=[
                                        html.Button(
                                            children=[
                                                html.Div(
                                                    className='flex flex-row items-center',
                                                    children=[
                                                        html.Img(src=app.get_asset_url('graph_gray.svg'), className='w-6 h-6 mr-2'),
                                                        reformat_file(file),
                                                    ]),
                                                html.Button(html.Img(src=app.get_asset_url('delete.svg'), className='w-5 h-5'), id={'type': 'delete', 'index': file}, n_clicks=0, className='invisible', disabled=True
                                                            ),
                                                      ],
                                            id={'type': 'saved-button', 'index': f'{file}'},
                                            className='font-base max-w-full text-xs text-gray-200 flex flex-row hover:bg-slate-500 px-4 py-2 rounded-lg mb-2 mx-4 items-center justify-between h-12')
                                        for file in files],
                            id='file_list',
                        ),
                        html.Div(
                            className='flex flex-col gap-2 mx-4 mb-4 justify-end',
                            children=[
                                html.A(
                                    'HOME',
                                    href='/',
                                    className='font-medium text-xs text-amber-400 hover:border-amber-500 border-2 border-transparent hover:text-amber-500 items-center justify-center px-4 py-2 rounded-lg'
                                ),
                                html.A(
                                    'PROFILE',
                                    href='/profile',
                                    className='font-medium text-xs text-amber-400 hover:border-amber-500 border-2 border-transparent hover:text-amber-500 items-center justify-center px-4 py-2 rounded-lg'
                                ),
                                # html.A(
                                #     'HISTORY',
                                #     href='/history',
                                #     className='font-medium text-xs text-amber-400 hover:border-amber-500 border-2 border-transparent hover:text-amber-500 items-center justify-center px-4 py-2 rounded-2xl'
                                # ),
                                html.A(
                                    'DASHBOARD',
                                    href='/dash',
                                    className='font-medium text-xs text-amber-400 border-amber-400 hover:border-amber-500 border-2 hover:text-amber-500 items-center justify-center px-4 py-2 rounded-lg'
                                ),
                                html.A(
                                    'LOGOUT',
                                    href='/logout',
                                    className='inline-flex whitespace-nowrap rounded-lg border-2 border-transparent px-4 py-2 text-xs font-medium text-white hover:border-amber-500 hover:text-amber-500'
                                )
                            ]
                        )
                    ]
                ),

                html.Div(
                    id='body',
                    className='lg:mx-16 mx-4 lg:pl-60 mt-0',
                    children=[
                        html.Div(
                            id='upload-video',
                            className='flex flex-row justify-between mt-5',
                            children=[

                                html.Div(children=[
                                    html.Div(
                                        children=[
                                            html.Span(
                                                'Upload your video',
                                                className='text-lg font-medium text-[#3A4963FF] hover:text-gray-900 pt-4'
                                            ),
                                            html.Span(
                                                'as mp4, mov or avi – max. 20 MB',
                                                className='text-sm font-medium text-[#3A4963FF] hover:text-gray-900'
                                            )
                                        ],
                                        className='flex flex-col items-start mx-10 mb-4'
                                    ),
                                    html.Div(
                                        dcc.Upload(
                                            disabled=disabled,
                                            id='upload-data',
                                            children=html.Div(
                                                children=
                                                [
                                                    'Drop your video here or ',
                                                    html.A(' browse'),
                                                    ' ⛳️',
                                                ],
                                            ),
                                            # className='bg-[rgba(251, 252, 254, 1)] mx-10 rounded-xl flex items-center justify-center py-10 mb-5 text-center inline-block text-sm border-dashed border-4 border-gray-400 h-60',
                                            className='mx-10 rounded-xl flex items-center justify-center py-10 mb-5 text-center inline-block text-sm border-dashed border-4 border-gray-400 h-60',
                                            multiple=False,
                                            max_size=20e6,
                                            accept=['.mp4', '.mov', '.avi'],
                                            # className_active='bg-[rgba(230, 240, 250, 1)]',
                                            # className_active='bg-blue-50 mx-10 rounded-xl flex items-center justify-center py-10 mb-5 text-center inline-block text-sm border-dashed border-4 border-gray-400 h-60',
                                            # className_reject='bg-indigo-600'
                                            style_active=(dict(
                                                backgroundColor='rgba(230, 240, 250, 1)',
                                                borderColor='rgba(115, 165, 250, 1)',
                                                borderRadius='12px',
                                            )),
                                            style_reject=(dict(
                                                backgroundColor='bg-red-200',
                                                borderColor='bg-red-400',
                                                borderRadius='12px',
                                            )),
                                            # className='upload'
                                        ),
                                        className='w-full'
                                        # className='bg-[rgba(251, 252, 254, 1)] mx-10 sm:rounded-2xl flex items-center justify-center my-10 text-center inline-block flex-col w-[95%] border-dashed border-4 border-gray-400'
                                    )
                                ],
                                    # className='container',
                                    className='bg-white shadow rounded-2xl flex items-start justify-center mb-5 text-center inline-block flex-col w-full h-96 backdrop-blur-md bg-opacity-80 border border-gray-100',
                                ),
                            ]),

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
                                    # className='container'
                                    className='bg-white shadow rounded-2xl flex items-center justify-center mb-5 backdrop-blur-md bg-opacity-80 border border-gray-100'
                                )
                            ),
                        ),

                        html.Div(children=[

                            dcc.Graph(
                                id='pelvis_rotation',
                                figure=fig3,
                                config=config,
                                className='bg-white shadow rounded-2xl flex w-full backdrop-blur-md bg-opacity-80 border border-gray-100'
                            ),

                            dcc.Graph(
                                id='pelvis_displacement',
                                figure=fig4,
                                config=config,
                                className='bg-white shadow rounded-2xl flex w-full backdrop-blur-md bg-opacity-80 border border-gray-100'
                            ),
                        ],
                            className='flex justify-center mb-5 flex-col gap-5'
                        ),

                        html.Div(children=[

                            dcc.Graph(
                                id='thorax_rotation',
                                figure=fig5,
                                config=config,
                                className='bg-white shadow rounded-2xl backdrop-blur-md bg-opacity-80 border border-gray-100'
                            ),

                            dcc.Graph(
                                id='thorax_displacement',
                                figure=fig6,
                                config=config,
                                className='bg-white shadow rounded-2xl flex backdrop-blur-md bg-opacity-80 border border-gray-100'
                            ),
                        ],
                            className='flex justify-center mb-5 flex-col gap-5'
                        ),

                        html.Div(children=[

                            dcc.Graph(
                                id='h_tilt',
                                figure=fig12,
                                config=config,
                                # className='container_half_left'
                                className='bg-white shadow rounded-2xl backdrop-blur-md bg-opacity-80 border border-gray-100'
                            ),

                            dcc.Graph(
                                id='h_rotation',
                                figure=fig13,
                                config=config,
                                className='bg-white shadow rounded-2xl flex backdrop-blur-md bg-opacity-80 border border-gray-100'
                                # className='container_half_right'
                            ),
                        ],
                            className='flex justify-center mb-5 flex-col gap-5'
                        ),

                        html.Div(
                            dcc.Graph(
                                id='s_tilt',
                                figure=fig11,
                                config=config,
                                className='bg-white shadow rounded-2xl flex items-center justify-center mb-5 backdrop-blur-md bg-opacity-80 border border-gray-100'
                            )
                        ),

                        html.Div(
                            dcc.Graph(
                                id='arm_length',
                                figure=fig14,
                                config=config,
                                className='bg-white shadow rounded-2xl flex items-center justify-center mb-5 backdrop-blur-md bg-opacity-80 border border-gray-100'
                            )
                        ),

                        html.Div(
                            dcc.Graph(
                                id='spine_rotation',
                                figure=fig15,
                                config=config,
                                className='bg-white shadow rounded-2xl flex items-center justify-center mb-5 backdrop-blur-md bg-opacity-80 border border-gray-100'
                            )
                        ),

                        html.Div(
                            dcc.Graph(
                                id='wrist_angle',
                                figure=fig16,
                                config=config,
                                className='bg-white shadow rounded-2xl flex items-center justify-center mb-5 backdrop-blur-md bg-opacity-80 border border-gray-100'
                            )
                        ),
                        html.Script('assets/dash.js'),
                    ]
                ),

                # Footer
                # html.Div(
                #     html.Div(
                #         className='bg-indigo-700 h-20 flex items-center flex-row justify-end gap-20 rounded-t-2xl',
                #         children=[
                #             html.Span(
                #                 '© 2023 JL. All rights reserved.',
                #                 className='text-amber-400 text-xs'
                #             ),
                #             html.A(
                #                 'Privacy Policy',
                #                 href='#',
                #                 className='text-amber-400 text-xs hover:text-amber-500 font-normal'
                #             ),
                #             html.A(
                #                 'Contact',
                #                 href='#',
                #                 className='text-amber-400 text-xs hover:text-amber-500 font-normal md:mr-16 mr-4'
                #             )
                #         ]
                #     ),
                #     className='w-full',
                # ),
                # End Footer

            ]
        )

        return layout

    app.layout = serve_layout

    init_callbacks(app)

    return app


def create_folder(name):
    if not os.path.exists(name):
        os.makedirs(name)


def reformat_file(filename):
    print(filename)
    timestamp = datetime.datetime.strptime(filename, '%Y-%m-%d_%H-%M-%S')
    return timestamp.strftime('%d.%m.%Y, %H:%M')


def init_callbacks(app):

    # @app.callback(
    #     Output({'type': 'saved-button', 'index': ALL}, 'className'),
    #     Input({'type': 'saved-button', 'index': ALL}, 'n_clicks')
    # )
    # def update_saved_button(n_clicks):
    #     if n_clicks is None:
    #         print(n_clicks)
    #         return 'font-medium max-w-full text-xs text-amber-400 flex flex-row hover:bg-indigo-600 px-4 py-2 rounded-2xl mb-2 mx-4 items-center'
    #     else:
    #         return 'font-medium max-w-full text-xs text-amber-400 flex flex-row bg-indigo-600 px-4 py-2 rounded-2xl mb-2 mx-4 items-center'
    #
    # @app.callback(
    #     Output({'type': 'saved-button', 'index': MATCH}, 'className'),
    #     Input({'type': 'saved-button', 'index': MATCH}, 'n_clicks')
    # )
    # def update_saved_button(n_clicks):
    #     if n_clicks is None:
    #         return 'font-medium max-w-full text-xs text-amber-400 flex flex-row hover:bg-indigo-600 px-4 py-2 rounded-2xl mb-2 mx-4 items-center'
    #     else:
    #         return 'font-medium max-w-full text-xs text-amber-400 flex flex-row bg-indigo-600 px-4 py-2 rounded-2xl mb-2 mx-4 items-center'


    @app.callback(
        [Output('sequence', 'figure'), Output('pelvis_rotation', 'figure'), Output('pelvis_displacement', 'figure'),
         Output('thorax_rotation', 'figure'), Output('thorax_displacement', 'figure'), Output('s_tilt', 'figure'),
         Output('h_tilt', 'figure'),
         Output('h_rotation', 'figure'), Output('arm_length', 'figure'), Output('spine_rotation', 'figure'),
         Output('wrist_angle', 'figure'), Output('file_list', 'children'), Output('upload-video', 'children')],
        [Input('upload-data', 'contents'), Input('upload-data', 'filename'),
         Input({'type': 'saved-button', 'index': ALL}, 'n_clicks'), Input({'type': 'delete', 'index': ALL}, 'n_clicks')],
        [State('file_list', 'children')],
        prevent_initial_call=True
    )
    def process(contents, filename, n_clicks, clicks_delete, children):
        # Enable or Disable upload component
        disabled = False if (current_user.n_analyses > 0 or current_user.unlimited) else True

        # Check if button was pressed or a file was uploaded
        if ctx.triggered_id != 'upload-data':
            if ctx.triggered_id != ctx.triggered_id.type != 'delete':
                button_id = ctx.triggered_id.index
                file = f'{button_id}.parquet'
                data = pd.read_parquet(f'assets/save_data/{current_user.id}/{button_id}/{file}')
                duration = data['duration'][0]
                data_values = data.values
                save_pelvis_rotation = data_values[:, 0]
                save_pelvis_tilt = data_values[:, 1]
                save_pelvis_lift = data_values[:, 2]
                save_pelvis_sway = data_values[:, 3]
                save_pelvis_thrust = data_values[:, 4]
                save_thorax_lift = data_values[:, 5]
                save_thorax_bend = data_values[:, 6]
                save_thorax_sway = data_values[:, 7]
                save_thorax_rotation = data_values[:, 8]
                save_thorax_thrust = data_values[:, 9]
                save_thorax_tilt = data_values[:, 10]
                save_spine_rotation = data_values[:, 11]
                save_spine_tilt = data_values[:, 12]
                save_head_rotation = data_values[:, 13]
                save_head_tilt = data_values[:, 14]
                save_left_arm_length = data_values[:, 15]
                save_wrist_angle = data_values[:, 16]
                save_wrist_tilt = data_values[:, 17]

                # Get the video and update the video player
                vid_src = f'assets/save_data/{current_user.id}/{button_id}/motion.mp4'
                children_upload = upload_video(disabled, path=vid_src)

                # Change the background color of the pressed button and reset the previously pressed button
                for child in children:
                    if child['props']['id']['index'] == button_id:
                        child['props']['className'] = 'font-medium max-w-full text-xs text-gray-200 flex flex-row bg-slate-500 px-4 py-2 rounded-lg mb-2 mx-4 items-center justify-between h-12'
                        child['props']['disabled'] = True
                        # Enabling the delete button
                        child['props']['children'][1]['props']['disabled'] = False
                        child['props']['children'][1]['props']['className'] = 'visible hover:bg-red-300 rounded-full px-1 py-1 items-center justify-center'
                    else:
                        child['props']['className'] = 'font-medium max-w-full text-xs text-gray-200 flex flex-row hover:bg-slate-500 px-4 py-2 rounded-lg mb-2 mx-4 items-center justify-between h-12'
                        child['props']['disabled'] = False
                        # Disabling the delete button
                        child['props']['children'][1]['props']['disabled'] = True
                        child['props']['children'][1]['props']['className'] = 'invisible'

                fig, fig3, fig4, fig5, fig6, fig11, fig12, fig13, fig14, fig15, fig16 = update_plots(save_pelvis_rotation,
                                                                                                     save_pelvis_tilt,
                                                                                                     save_pelvis_lift,
                                                                                                     save_pelvis_sway,
                                                                                                     save_pelvis_thrust,
                                                                                                     save_thorax_lift,
                                                                                                     save_thorax_bend,
                                                                                                     save_thorax_sway,
                                                                                                     save_thorax_rotation,
                                                                                                     save_thorax_thrust,
                                                                                                     save_thorax_tilt,
                                                                                                     save_spine_rotation,
                                                                                                     save_spine_tilt,
                                                                                                     save_head_rotation,
                                                                                                     save_head_tilt,
                                                                                                     save_left_arm_length,
                                                                                                     save_wrist_angle,
                                                                                                     save_wrist_tilt,
                                                                                                     duration)

                return [fig, fig3, fig4, fig5, fig6, fig11, fig12, fig13, fig14, fig15, fig16, children, children_upload]

        # Delete was pressed
        if ctx.triggered_id != 'upload-data':
            if ctx.triggered_id.type == 'delete':
                button_id = ctx.triggered_id.index
                # file = f'{button_id}.parquet'
                for child in children:
                    if child['props']['id']['index'] == button_id:
                        children.remove(child)
                path = f'assets/save_data/{current_user.id}/{button_id}'
                shutil.rmtree(path)

                # Reset plots

                save_pelvis_rotation, save_pelvis_tilt, save_pelvis_lift, save_pelvis_sway, save_pelvis_thrust, \
                save_thorax_lift, save_thorax_bend, save_thorax_sway, save_thorax_rotation, save_thorax_thrust, \
                save_thorax_tilt, save_spine_rotation, save_spine_tilt, save_head_rotation, save_head_tilt, save_left_arm_length, \
                save_wrist_angle, save_wrist_tilt = rand(100, 18)

                duration = 10

                fig, fig3, fig4, fig5, fig6, fig11, fig12, fig13, fig14, fig15, fig16 = update_plots(save_pelvis_rotation, save_pelvis_tilt, save_pelvis_lift, save_pelvis_sway, save_pelvis_thrust, \
                save_thorax_lift, save_thorax_bend, save_thorax_sway, save_thorax_rotation, save_thorax_thrust, \
                save_thorax_tilt, save_spine_rotation, save_spine_tilt, save_head_rotation, save_head_tilt, save_left_arm_length, \
                save_wrist_angle, save_wrist_tilt, duration, filt=False)

                children_upload = [

                    html.Div(children=[
                        html.Div(
                            children=[
                                html.Span(
                                    'Upload your video',
                                    className='text-lg font-medium text-[#3A4963FF] hover:text-gray-900 pt-4'
                                ),
                                html.Span(
                                    'as mp4, mov or avi – max. 20 MB',
                                    className='text-sm font-medium text-[#3A4963FF] hover:text-gray-900'
                                )
                            ],
                            className='flex flex-col items-start mx-10 mb-4'
                        ),
                        html.Div(
                            dcc.Upload(
                                disabled=disabled,
                                id='upload-data',
                                children=html.Div(
                                    children=
                                    [
                                        'Drop your video here or ',
                                        html.A(' browse'),
                                        ' ⛳️',
                                    ],
                                ),
                                # className='bg-[rgba(251, 252, 254, 1)] mx-10 rounded-xl flex items-center justify-center py-10 mb-5 text-center inline-block text-sm border-dashed border-4 border-gray-400 h-60',
                                className='mx-10 rounded-xl flex items-center justify-center py-10 mb-5 text-center inline-block text-sm border-dashed border-4 border-gray-400 h-60',
                                multiple=False,
                                max_size=20e6,
                                accept=['.mp4', '.mov', '.avi'],
                                style_active=(dict(
                                    backgroundColor='rgba(230, 240, 250, 1)',
                                    borderColor='rgba(115, 165, 250, 1)',
                                    borderRadius='12px',
                                )),
                                style_reject=(dict(
                                    backgroundColor='bg-red-200',
                                    borderColor='bg-red-400',
                                    borderRadius='12px',
                                )),
                                # className='upload'
                            ),
                            className='w-full'
                            # className='bg-[rgba(251, 252, 254, 1)] mx-10 sm:rounded-2xl flex items-center justify-center my-10 text-center inline-block flex-col w-[95%] border-dashed border-4 border-gray-400'
                        )
                    ],
                        # className='container',
                        className='bg-white shadow rounded-2xl flex items-start justify-center mb-5 text-center inline-block flex-col w-full h-96 backdrop-blur-md bg-opacity-80 border border-gray-100',
                    ),
                ]

                return [fig, fig3, fig4, fig5, fig6, fig11, fig12, fig13, fig14, fig15, fig16, children, children_upload]

        # Check if folder was created and generate file name
        filename = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        create_folder(f'assets/save_data/{current_user.id}/' + filename)
        location = f'assets/save_data/{current_user.id}/' + filename

        # Extracting the motion data from the video
        save_pelvis_rotation, save_pelvis_tilt, save_pelvis_lift, save_pelvis_sway, save_pelvis_thrust, \
        save_thorax_lift, save_thorax_bend, save_thorax_sway, save_thorax_rotation, save_thorax_thrust, \
        save_thorax_tilt, save_spine_rotation, save_spine_tilt, save_head_rotation, save_head_tilt, save_left_arm_length, save_wrist_angle, save_wrist_tilt, duration = process_motion(
            contents, filename, location)

        # Get the video and update the video player
        vid_src = location + '/motion.mp4'
        children_upload = upload_video(disabled, path=vid_src)

        fig, fig3, fig4, fig5, fig6, fig11, fig12, fig13, fig14, fig15, fig16 = update_plots(save_pelvis_rotation,
                                                                                             save_pelvis_tilt,
                                                                                             save_pelvis_lift,
                                                                                             save_pelvis_sway,
                                                                                             save_pelvis_thrust,
                                                                                             save_thorax_lift,
                                                                                             save_thorax_bend,
                                                                                             save_thorax_sway,
                                                                                             save_thorax_rotation,
                                                                                             save_thorax_thrust,
                                                                                             save_thorax_tilt,
                                                                                             save_spine_rotation,
                                                                                             save_spine_tilt,
                                                                                             save_head_rotation,
                                                                                             save_head_tilt,
                                                                                             save_left_arm_length,
                                                                                             save_wrist_angle,
                                                                                             save_wrist_tilt,
                                                                                             duration)

        # Save the motion data to a parquet file
        df = pd.DataFrame(
            [save_pelvis_rotation, save_pelvis_tilt, save_pelvis_lift, save_pelvis_sway, save_pelvis_thrust,
             save_thorax_lift, save_thorax_bend, save_thorax_sway, save_thorax_rotation, save_thorax_thrust,
             save_thorax_tilt, save_spine_rotation, save_spine_tilt, save_head_rotation, save_head_tilt,
             save_left_arm_length, save_wrist_angle, save_wrist_tilt]).T
        df.columns = ['pelvis_rotation', 'pelvis_tilt', 'pelvis_lift', 'pelvis_sway', 'pelvis_thrust',
                      'thorax_lift', 'thorax_bend', 'thorax_sway', 'thorax_rotation', 'thorax_thrust',
                      'thorax_tilt', 'spine_rotation', 'spine_tilt', 'head_rotation', 'head_tilt', 'left_arm_length',
                      'wrist_angle', 'wrist_tilt']

        df['duration'] = duration

        df.to_parquet(f'assets/save_data/{current_user.id}/{filename}/{filename}.parquet')

        # Reset the background color of the buttons
        for child in children:
            child['props']['className'] = 'font-medium max-w-full text-xs text-gray-200 flex flex-row hover:bg-slate-500 px-4 py-2 rounded-lg mb-2 mx-4 items-center justify-between h-12'
            child['props']['disabled'] = False
            # Disabling the delete button
            child['props']['children'][1]['props']['disabled'] = True
            child['props']['children'][1]['props']['className'] = 'invisible'

        # Add a new button for the new motion data
        new_item = html.Button(
                                            disabled=True,
                                            children=[
                                                html.Div(
                                                    className='flex flex-row items-center',
                                                    children=[
                                                        html.Img(src=app.get_asset_url('graph_gray.svg'), className='w-6 h-6 mr-2'),
                                                        reformat_file(filename),
                                                    ]),
                                                html.Button(html.Img(src=app.get_asset_url('delete.svg'), className='w-5 h-5'), id={'type': 'delete', 'index': filename}, n_clicks=0, className='visible hover:bg-red-300 rounded-full px-1 py-1 items-center justify-center', disabled=False
                                                            ),
                                                      ],
                                            id={'type': 'saved-button', 'index': f'{filename}'},
                                            className='font-base max-w-full text-xs text-gray-200 flex flex-row bg-slate-500 px-4 py-2 rounded-lg mb-2 mx-4 items-center justify-between h-12')
        children.insert(0, new_item)

        if not current_user.unlimited:
            current_user.n_analyses -= 1
            db.session.commit()

        return [fig, fig3, fig4, fig5, fig6, fig11, fig12, fig13, fig14, fig15, fig16, children, children_upload]


    # Show navbar on click
    @app.callback(
        [Output('sidebar', 'className'), Output('menu-icon', 'src'), Output('navbar-top', 'className'), Output('body', 'className')],
        [Input('menu-button', 'n_clicks'), Input('navbar-top', 'className'), Input('body', 'className')],
        prevent_initial_call=True
    )
    def show_navbar(n_clicks, class_name, body_class):
        if n_clicks % 2 == 0:
            class_name = class_name.replace(' fixed', '')
            class_name = class_name.replace(' top-0', '')
            body_class = body_class.replace('mt-16', 'mt-0')
            return ['flex flex-col bg-slate-600 fixed left-5 top-5 bottom-5 w-60 z-10 rounded-2xl hidden lg:flex','assets/menu_burger.svg', class_name, body_class]

        else:
            class_name = class_name + ' fixed top-0'
            body_class = body_class.replace('mt-0', 'mt-16')
            return ['flex flex-col bg-slate-600 fixed top-0 bottom-0 w-60 z-10 lg:rounded-2xl lg:left-5 lg:top-5 lg:bottom-5', 'assets/menu_burger_white.svg', class_name, body_class]
