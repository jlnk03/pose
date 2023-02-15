import datetime
import shutil
import mediapipe as mp
import plotly.graph_objects as go
import plotly.io as pio
import plotly.express as px
from dash import Dash, ctx, ALL, Input, Output, State, html, dcc
import pandas as pd
from scipy import signal
from code_b.angles import *
from code_b.process_mem import process_motion
import os
from flask_login import current_user
from flask import url_for
from . import db
import requests
from itsdangerous import URLSafeTimedSerializer

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


def find_closest_zero_intersection_left_of_max(array):
    max_index = np.argmax(array)
    indices = np.where(np.diff(np.sign(array)))[0]
    zero_intersections = [i for i in indices if i < max_index]
    if zero_intersections:
        closest_intersection = zero_intersections[np.argmin(np.abs(np.array(zero_intersections) - max_index))]
        x1, x2 = closest_intersection, closest_intersection + 1
        y1, y2 = array[x1], array[x2]
        m = (y2 - y1) / (x2 - x1)
        b = y1 - m * x1
        x_intersection = -b / m
        return x_intersection
    else:
        return len(array)


def find_closest_zero_intersection_right_of_max(array):
    max_index = np.argmax(array)
    indices = np.where(np.diff(np.sign(array)))[0]
    zero_intersections = [i for i in indices if i > max_index]
    if zero_intersections:
        closest_intersection = zero_intersections[np.argmin(np.abs(np.array(zero_intersections) - max_index))]
        x1, x2 = closest_intersection, closest_intersection + 1
        y1, y2 = array[x1], array[x2]
        m = (y2 - y1) / (x2 - x1)
        b = y1 - m * x1
        x_intersection = -b / m
        return x_intersection
    else:
        return len(array)

    
def find_closest_zero_intersection_left_of_min(array):
    min_index = np.argmin(array)
    indices = np.where(np.diff(np.sign(array)))[0]
    zero_intersections = [i for i in indices if i < min_index]
    if zero_intersections:
        closest_intersection = zero_intersections[np.argmin(np.abs(np.array(zero_intersections) - min_index))]
        x1, x2 = closest_intersection, closest_intersection + 1
        y1, y2 = array[x1], array[x2]
        m = (y2 - y1) / (x2 - x1)
        b = y1 - m * x1
        x_intersection = -b / m
        return x_intersection
    else:
        return 0


# Return the video view
def upload_video(disabled=True, path=None):
    layout = [
        html.Div(
            id='video-view',
            className='flex flex-col sm:flex-row w-full h-full',
            children=[
                html.Div(children=[
                    html.Div(
                        children=[
                            html.Span(
                                'Upload your video',
                                className='text-lg font-medium text-slate-900 dark:text-gray-100 pt-4'
                            ),
                            html.Span(
                                'as mp4, mov or avi – max. 20 MB',
                                className='text-sm font-medium text-slate-900 dark:text-gray-100'
                            )
                        ],
                        className='flex flex-col items-start sm:mx-10 mx-4 mb-4'
                    ),
                    html.Div(
                        dcc.Upload(
                            disabled=disabled,
                            id='upload-data',
                            children=html.Div(
                                className='text-slate-900 dark:text-gray-100',
                                children=
                                [
                                    'Drop your video here or ',
                                    html.A(' browse'),
                                    ' ⛳️',
                                ],
                            ),
                            className='bg-[rgba(251, 252, 254, 1)] sm:mx-10 mx-4 rounded-2xl flex items-center justify-center py-10 mb-5 text-center inline-block text-sm border-dashed border-4 border-gray-400 sm:h-60 h-20',
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
                    className='bg-white dark:bg-gray-700 shadow rounded-2xl flex items-start justify-center mb-5 text-center inline-block flex-col w-full h-44 sm:h-96 sm:mr-5 backdrop-blur-md bg-opacity-80 border border-gray-100 dark:border-gray-900',
                ),

                html.Div(
                    className="sm:hidden relative overflow-hidden h-96 w-full shadow rounded-2xl mb-5 bg-white dark:bg-gray-700 backdrop-blur-md bg-opacity-80 border border-gray-100 dark:border-gray-900",
                    children=[
                        html.Video(src=f'{path}#t=0.001', id='video', controls=True,
                                   className="h-full w-full object-cover"),
                    ]
                ),
                html.Video(src=f'{path}#t=0.001', id='video', controls=True,
                           className="h-96 rounded-2xl mb-5 sm:block hidden"),
            ])
    ]

    return layout


# Random inititalization for data
def rand(length, size):
    full = [np.full(length, np.random.randint(0, 30)) for _ in range(size)]
    return full


save_pelvis_rotation, save_pelvis_tilt, save_pelvis_lift, save_pelvis_sway, save_pelvis_thrust, \
    save_thorax_lift, save_thorax_bend, save_thorax_sway, save_thorax_rotation, save_thorax_thrust, \
    save_thorax_tilt, save_spine_rotation, save_spine_tilt, save_head_rotation, save_head_tilt, save_left_arm_length, \
    save_wrist_angle, save_wrist_tilt, save_arm_rotation = rand(100, 19)

duration = 10
timeline = np.linspace(0, duration, len(save_pelvis_rotation))


def filter_data(data, duration):
    sample_rate = len(data) / duration
    Wn = 2
    b, a = signal.butter(3, Wn / (sample_rate / 2), 'low')
    data = signal.filtfilt(b, a, data)
    return data


# @memory_profiler.profile
def update_plots(save_pelvis_rotation, save_pelvis_tilt, save_pelvis_lift, save_pelvis_sway, save_pelvis_thrust,
                 save_thorax_lift, save_thorax_bend, save_thorax_sway, save_thorax_rotation, save_thorax_thrust,
                 save_thorax_tilt, save_spine_rotation, save_spine_tilt, save_head_rotation, save_head_tilt,
                 save_left_arm_length, save_wrist_angle, save_wrist_tilt, save_arm_rotation, duration, filt=True):
    if filt:
        converted = [filter_data(np.array(name), duration) for name in
                     [save_pelvis_rotation, save_pelvis_tilt, save_pelvis_lift, save_pelvis_sway, save_pelvis_thrust,
                      save_thorax_lift, save_thorax_bend, save_thorax_sway, save_thorax_rotation, save_thorax_thrust,
                      save_thorax_tilt, save_spine_rotation, save_spine_tilt, save_head_rotation, save_head_tilt,
                      save_left_arm_length, save_wrist_angle, save_wrist_tilt, save_arm_rotation]]

        save_pelvis_rotation, save_pelvis_tilt, save_pelvis_lift, save_pelvis_sway, save_pelvis_thrust, \
        save_thorax_lift, save_thorax_bend, save_thorax_sway, save_thorax_rotation, save_thorax_thrust, \
        save_thorax_tilt, save_spine_rotation, save_spine_tilt, save_head_rotation, save_head_tilt, save_left_arm_length, save_wrist_angle, save_wrist_tilt, save_arm_rotation = converted

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
        )
    )

    fig.add_trace(
        go.Scatter(
            x=timeline,
            y=np.gradient(save_arm_rotation),
            name=f'Arm',
        )
    )

    fig.update_layout(
        # title='Angular velocity',
        title_x=0.5,
        font_size=12,
        yaxis_title="Angular velocity in °/s",
        # xaxis_title="time in s",
        xaxis_ticksuffix="s",
        yaxis_ticksuffix="°/s",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        legend_orientation="h",
        legend=dict(y=1, yanchor="bottom"),
        margin=dict(
            l=10,
            r=10,
            t=20,
            pad=5
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
        # title='Pelvis angles',
        title_x=0.5,
        font_size=12,
        # yaxis_title='angle in °',
        # xaxis_title="time in s",
        yaxis_ticksuffix="°",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        legend_orientation="h",
        # legend=dict(y=1, yanchor="bottom"),
        margin=dict(
            l=10,
            r=10,
            t=20,
            pad=5
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
        # title='Pelvis displacement',
        title_x=0.5,
        font_size=12,
        yaxis_title='Displacement in m',
        # xaxis_title="time in s",
        yaxis_ticksuffix="m",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        legend_orientation="h",
        legend=dict(y=1, yanchor="bottom"),
        margin=dict(
            l=10,
            r=10,
            t=20,
            pad=5
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
        # title='Thorax angles',
        title_x=0.5,
        font_size=12,
        yaxis_title='angle in °',
        # xaxis_title="time in s",
        yaxis_ticksuffix="°",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        legend_orientation="h",
        legend=dict(y=1, yanchor="bottom"),
        margin=dict(
            l=10,
            r=10,
            t=20,
            pad=5
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
        # title='Thorax displacement',
        title_x=0.5,
        font_size=12,
        yaxis_title='Displacement in m',
        # xaxis_title="time in s",
        yaxis_ticksuffix="m",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        legend_orientation="h",
        legend=dict(y=1, yanchor="bottom"),
        margin=dict(
            l=10,
            r=10,
            t=20,
            pad=5
        ),
        modebar=dict(
            bgcolor='rgba(0,0,0,0)',
            color='rgba(1,1,1,0.3)',
            activecolor='rgba(58, 73, 99, 1)'
        )
    )

    fig11 = go.Figure(data=go.Scatter(x=timeline, y=save_spine_tilt))

    fig11.update_layout(
        # title='Tilt between pelvis and shoulder',
        title_x=0.5,
        font_size=12,
        yaxis_title='angle in °',
        # xaxis_title="time in s",
        yaxis_ticksuffix="°",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(
            l=10,
            r=10,
            t=20,
            pad=5
        ),
        modebar=dict(
            bgcolor='rgba(0,0,0,0)',
            color='rgba(1,1,1,0.3)',
            activecolor='rgba(58, 73, 99, 1)'
        )
    )

    fig12 = go.Figure(data=go.Scatter(x=timeline, y=save_head_tilt))

    fig12.update_layout(
        # title='Head tilt',
        title_x=0.5,
        font_size=12,
        yaxis_title='angle in °',
        # xaxis_title="time in s",
        yaxis_ticksuffix="°",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(
            l=10,
            r=10,
            t=20,
            pad=5
        ),
        modebar=dict(
            bgcolor='rgba(0,0,0,0)',
            color='rgba(1,1,1,0.3)',
            activecolor='rgba(58, 73, 99, 1)'
        )
    )

    fig13 = go.Figure(data=go.Scatter(x=timeline, y=save_head_rotation))

    fig13.update_layout(
        # title='Head rotation',
        title_x=0.5,
        font_size=12,
        yaxis_title='angle in °',
        # xaxis_title="time in s",
        yaxis_ticksuffix="°",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(
            l=10,
            r=10,
            t=20,
            pad=5
        ),
        modebar=dict(
            bgcolor='rgba(0,0,0,0)',
            color='rgba(1,1,1,0.3)',
            activecolor='rgba(58, 73, 99, 1)'
        )
    )

    fig14 = go.Figure(data=go.Scatter(x=timeline, y=save_left_arm_length))

    fig14.update_layout(
        # title='Left arm length',
        title_x=0.5,
        font_size=12,
        yaxis_title='length in m',
        # xaxis_title="time in s",
        yaxis_ticksuffix="m",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(
            l=10,
            r=10,
            t=20,
            pad=5
        ),
        modebar=dict(
            bgcolor='rgba(0,0,0,0)',
            color='rgba(1,1,1,0.3)',
            activecolor='rgba(58, 73, 99, 1)'
        )
    )

    fig15 = go.Figure(data=go.Scatter(x=timeline, y=save_spine_rotation))

    fig15.update_layout(
        # title='Spine rotation',
        title_x=0.5,
        font_size=12,
        yaxis_title='angle in °',
        # xaxis_title="time in s",
        yaxis_ticksuffix="°",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(
            l=10,
            r=10,
            t=20,
            pad=5
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
        # title='Wrist angle',
        title_x=0.5,
        font_size=12,
        yaxis_title='angle in °',
        # xaxis_title="time in s",
        yaxis_ticksuffix="°",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(
            l=10,
            r=10,
            t=20,
            pad=5
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

fig.add_trace(
    go.Scatter(
        x=timeline,
        y=np.gradient(save_arm_rotation),
        name=f'Arm',
    )
)

fig.update_layout(
    # title='Angular velocity',
    title_x=0.5,
    font_size=12,
    yaxis_title="Angular velocity in °/s",
    # xaxis_title="time in s",
    yaxis_ticksuffix="°/s",
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    legend_orientation="h",
    legend=dict(y=1, yanchor="bottom"),
    margin=dict(
        l=10,
        r=10,
        t=20,
        pad=5
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
    # title='Pelvis angles',
    title_x=0.5,
    font_size=12,
    yaxis_title='angle in °',
    # xaxis_title="time in s",
    yaxis_ticksuffix="°",
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    legend_orientation="h",
    legend=dict(y=1, yanchor="bottom"),
    margin=dict(
        l=10,
        r=10,
        t=20,
        pad=5
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
    # title='Pelvis displacement',
    title_x=0.5,
    font_size=12,
    yaxis_title='Displacement in m',
    # xaxis_title="time in s",
    yaxis_ticksuffix="m",
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    legend_orientation="h",
    legend=dict(y=1, yanchor="bottom"),
    margin=dict(
        l=10,
        r=10,
        t=20,
        pad=5
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
    # title='Thorax angles',
    title_x=0.5,
    font_size=12,
    yaxis_title='angle in °',
    # xaxis_title="time in s",
    yaxis_ticksuffix="°",
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    legend_orientation="h",
    legend=dict(y=1, yanchor="bottom"),
    margin=dict(
        l=10,
        r=10,
        t=20,
        pad=5
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
    # title='Thorax displacement',
    title_x=0.5,
    font_size=12,
    yaxis_title='Displacement in m',
    # xaxis_title="time in s",
    yaxis_ticksuffix="m",
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    legend_orientation="h",
    legend=dict(y=1, yanchor="bottom"),
    margin=dict(
        l=10,
        r=10,
        t=20,
        pad=5
    ),
    modebar=dict(
        bgcolor='rgba(0,0,0,0)',
        color='rgba(1,1,1,0.3)',
        activecolor='rgba(58, 73, 99, 1)'
    )
)

fig11 = go.Figure(data=go.Scatter(x=timeline, y=save_spine_tilt))

fig11.update_layout(
    # title='Tilt between pelvis and shoulder',
    title_x=0.5,
    font_size=12,
    yaxis_title='angle in °',
    # xaxis_title="time in s",
    yaxis_ticksuffix="°",
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    margin=dict(
        l=10,
        r=10,
        t=20,
        pad=5
    ),
    modebar=dict(
        bgcolor='rgba(0,0,0,0)',
        color='rgba(1,1,1,0.3)',
        activecolor='rgba(58, 73, 99, 1)'
    )
)

fig12 = go.Figure(data=go.Scatter(x=timeline, y=save_head_tilt))

fig12.update_layout(
    # title='Head tilt',
    title_x=0.5,
    font_size=12,
    yaxis_title='angle in °',
    # xaxis_title="time in s",
    yaxis_ticksuffix="°",
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    margin=dict(
        l=10,
        r=10,
        t=20,
        pad=5
    ),
    modebar=dict(
        bgcolor='rgba(0,0,0,0)',
        color='rgba(1,1,1,0.3)',
        activecolor='rgba(58, 73, 99, 1)'
    )
)

fig13 = go.Figure(data=go.Scatter(x=timeline, y=save_head_rotation))

fig13.update_layout(
    # title='Head rotation',
    title_x=0.5,
    font_size=12,
    yaxis_title='angle in °',
    # xaxis_title="time in s",
    yaxis_ticksuffix="°",
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    margin=dict(
        l=10,
        r=10,
        t=20,
        pad=5
    ),
    modebar=dict(
        bgcolor='rgba(0,0,0,0)',
        color='rgba(1,1,1,0.3)',
        activecolor='rgba(58, 73, 99, 1)'
    )
)

fig14 = go.Figure(data=go.Scatter(x=timeline, y=save_left_arm_length))

fig14.update_layout(
    # title='Left arm length',
    title_x=0.5,
    font_size=12,
    yaxis_title='length in m',
    # xaxis_title="time in s",
    yaxis_ticksuffix="m",
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    margin=dict(
        l=10,
        r=10,
        t=20,
        pad=5
    ),
    modebar=dict(
        bgcolor='rgba(0,0,0,0)',
        color='rgba(1,1,1,0.3)',
        activecolor='rgba(58, 73, 99, 1)'
    )
)

fig15 = go.Figure(data=go.Scatter(x=timeline, y=save_spine_rotation))

fig15.update_layout(
    # title='Spine rotation',
    title_x=0.5,
    font_size=12,
    yaxis_title='angle in °',
    # xaxis_title="time in s",
    yaxis_ticksuffix="°",
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    margin=dict(
        l=10,
        r=10,
        t=20,
        pad=5
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
    # title='Wrist angles',
    title_x=0.5,
    font_size=12,
    yaxis_title='angle in °',
    # xaxis_title="time in s",
    yaxis_ticksuffix="°",
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    margin=dict(
        l=10,
        r=10,
        t=20,
        pad=5
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
    app = Dash(__name__, server=server, url_base_pathname='/dashboard/',
               external_scripts=["https://tailwindcss.com/", {"src": "https://cdn.tailwindcss.com"}]
               )
    app.css.config.serve_locally = False
    app.css.append_css({'external_url': './assets/output.css'})
    # server = app.server
    app.app_context = server.app_context
    # app._favicon = './assets/favicon.png'

    app.title = 'Analyze your swing – Swinglab'

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
                    className='flex flex-col bg-slate-600 dark:bg-gray-700 fixed lg:left-5 top-5 bottom-5 w-60 z-10 rounded-2xl hidden lg:flex',
                    children=[
                        html.Button(
                            id='sidebar-header',
                            className='flex-row items-center ml-4 hidden',
                            children=[html.Img(src=app.get_asset_url('menu_cross.svg'), className='h-4 w-4 mt-4')]
                        ),
                        html.Div(
                            'HISTORY',
                            className='text-white text-xs font-medium mb-3 mt-5 px-4'
                        ),
                        html.Div(
                            className='flex flex-col mb-4 h-full overflow-y-auto border-b border-white',
                            children=[
                                html.Button(
                                    children=[
                                        html.Div(
                                            className='flex flex-row items-center',
                                            children=[
                                                html.Img(src=app.get_asset_url('graph_gray.svg'),
                                                         className='w-6 h-6 mr-2'),
                                                reformat_file(file),
                                            ]),
                                        html.Button(html.Img(src=app.get_asset_url('delete.svg'), className='w-5 h-5'),
                                                    id={'type': 'delete', 'index': file}, n_clicks=0,
                                                    className='invisible', disabled=True
                                                    ),
                                    ],
                                    id={'type': 'saved-button', 'index': f'{file}'},
                                    className='font-base max-w-full text-xs text-gray-200 flex flex-row hover:bg-slate-500 px-4 py-2 rounded-lg mb-2 mx-4 items-center justify-between h-12 transition')
                                for file in files],
                            id='file_list',
                        ),
                        html.Div(
                            className='flex flex-col gap-2 mx-4 mb-4 justify-end',
                            children=[
                                html.A(
                                    'HOME',
                                    href='/',
                                    className='font-medium text-xs text-amber-500 hover:border-amber-400 border-2 border-transparent hover:text-amber-400 items-center justify-center px-4 py-2 rounded-lg transition'
                                ),
                                html.A(
                                    'PROFILE',
                                    href='/profile',
                                    className='font-medium text-xs text-amber-500 hover:border-amber-400 border-2 border-transparent hover:text-amber-400 items-center justify-center px-4 py-2 rounded-lg transition'
                                ),
                                # html.A(
                                #     'HISTORY',
                                #     href='/history',
                                #     className='font-medium text-xs text-amber-400 hover:border-amber-500 border-2 border-transparent hover:text-amber-500 items-center justify-center px-4 py-2 rounded-2xl'
                                # ),
                                html.A(
                                    'DASHBOARD',
                                    href='/dash',
                                    className='font-medium text-xs text-amber-500 border-amber-500 hover:border-amber-400 border-2 hover:text-amber-400 items-center justify-center px-4 py-2 rounded-lg transition'
                                ),
                                html.A(
                                    'LOGOUT',
                                    href='/logout',
                                    className='inline-flex whitespace-nowrap rounded-lg border-2 border-transparent px-4 py-2 text-xs font-medium text-white hover:border-gray-200 hover:text-gray-200 transition'
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
                                                className='text-lg font-medium text-slate-900 dark:text-gray-100 pt-4'
                                            ),
                                            html.Span(
                                                'as mp4, mov or avi – max. 20 MB',
                                                className='text-sm font-medium text-slate-900 dark:text-gray-100'
                                            )
                                        ],
                                        className='flex flex-col items-start mx-4 sm:mx-10 mb-4'
                                    ),
                                    html.Div(
                                        dcc.Upload(
                                            disabled=disabled,
                                            id='upload-data',
                                            children=html.Div(
                                                className='text-slate-900 dark:text-gray-100',
                                                children=
                                                [
                                                    'Drop your video here or ',
                                                    html.A(' browse'),
                                                    ' ⛳️',
                                                ],
                                            ),
                                            # className='bg-[rgba(251, 252, 254, 1)] mx-10 rounded-xl flex items-center justify-center py-10 mb-5 text-center inline-block text-sm border-dashed border-4 border-gray-400 h-60',
                                            className='mx-4 sm:mx-10 rounded-xl flex items-center justify-center py-10 mb-5 text-center inline-block text-sm border-dashed border-4 border-gray-400 h-20 sm:h-60',
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
                                    className='bg-white dark:bg-gray-700 shadow rounded-2xl flex items-start justify-center mb-5 text-center inline-block flex-col w-full h-44 sm:h-96 backdrop-blur-md bg-opacity-80 border border-gray-100 dark:border-gray-900',
                                ),
                            ]),

                        dcc.Loading(
                            id='loading',
                            type='graph',
                            fullscreen=True,
                            # parent_className="dark:bg-slate-600 bg-[#FAF7F5]",
                            children=
                            html.Div(
                                className='bg-white dark:bg-gray-700 shadow rounded-2xl flex items-center justify-center mb-5 backdrop-blur-md bg-opacity-80 border border-gray-100 dark:border-gray-900 flex-col w-full',
                                children=[

                                    # Row for sequences
                                    html.Div(
                                        className='flex flex-row justify-between items-center w-full flex-wrap',
                                        children=[
                                            # Column for sequence
                                            html.Div(
                                                className='flex flex-col',
                                                children=[
                                                    html.Div(
                                                        className='text-lg font-medium text-slate-900 dark:text-gray-100 pt-10 px-4 sm:px-10 w-full',
                                                        children=[
                                                            'Transition Sequence',
                                                        ]
                                                    ),
                                                    html.Div(
                                                        className='flex flex-row items-center w-full px-4 sm:px-10 py-10',
                                                        children=[
                                                            html.Div(
                                                                '1',
                                                                className='text-2xl font-medium text-gray-100 bg-[#6266F6] rounded-full w-8 h-8 flex items-center justify-center',
                                                                id='sequence_first'
                                                            ),
                                                            html.Div(
                                                                className='sm:w-24 w-10 h-1 bg-gray-300 dark:bg-gray-500 rounded-full mx-2'
                                                            ),
                                                            html.Div(
                                                                '2',
                                                                className='text-2xl font-medium text-gray-100 bg-[#E74D39] rounded-full w-8 h-8 flex items-center justify-center',
                                                                id='sequence_second'
                                                            ),
                                                            html.Div(
                                                                className='sm:w-24 w-10 h-1 bg-gray-300 dark:bg-gray-500 rounded-full mx-2'
                                                            ),
                                                            html.Div(
                                                                '3',
                                                                className='text-2xl font-medium text-gray-100 bg-[#2BC48C] rounded-full w-8 h-8 flex items-center justify-center',
                                                                id='sequence_third'
                                                            )
                                                        ]
                                                    ),
                                                ]
                                            ),

                                            # Column for sequence
                                            html.Div(
                                                className='flex flex-col',
                                                children=[
                                                    html.Div(
                                                        className='text-lg font-medium text-slate-900 dark:text-gray-100 pt-10 px-4 sm:px-10 w-full',
                                                        children=[
                                                            'Start Sequence',
                                                        ]
                                                    ),
                                                    html.Div(
                                                        className='flex flex-row items-center w-full px-4 sm:px-10 py-10',
                                                        children=[
                                                            html.Div(
                                                                '1',
                                                                className='text-2xl font-medium text-gray-100 bg-[#6266F6] rounded-full w-8 h-8 flex items-center justify-center',
                                                                id='start_sequence_first'
                                                            ),
                                                            html.Div(
                                                                className='sm:w-24 w-10 h-1 bg-gray-300 dark:bg-gray-500 rounded-full mx-2'
                                                            ),
                                                            html.Div(
                                                                '2',
                                                                className='text-2xl font-medium text-gray-100 bg-[#E74D39] rounded-full w-8 h-8 flex items-center justify-center',
                                                                id='start_sequence_second'
                                                            ),
                                                            html.Div(
                                                                className='sm:w-24 w-10 h-1 bg-gray-300 dark:bg-gray-500 rounded-full mx-2'
                                                            ),
                                                            html.Div(
                                                                '3',
                                                                className='text-2xl font-medium text-gray-100 bg-[#2BC48C] rounded-full w-8 h-8 flex items-center justify-center',
                                                                id='start_sequence_third'
                                                            )
                                                        ]
                                                    ),
                                                ]
                                            ),

                                            # Column for sequence
                                            html.Div(
                                                className='flex flex-col',
                                                children=[
                                                    html.Div(
                                                        className='text-lg font-medium text-slate-900 dark:text-gray-100 pt-10 px-4 sm:px-10 w-full',
                                                        children=[
                                                            'Finish Sequence',
                                                        ]
                                                    ),
                                                    html.Div(
                                                        className='flex flex-row items-center w-full px-4 sm:px-10 py-10',
                                                        children=[
                                                            html.Div(
                                                                '1',
                                                                className='text-2xl font-medium text-gray-100 bg-[#6266F6] rounded-full w-8 h-8 flex items-center justify-center',
                                                                id='end_sequence_first'
                                                            ),
                                                            html.Div(
                                                                className='sm:w-24 w-10 h-1 bg-gray-300 dark:bg-gray-500 rounded-full mx-2'
                                                            ),
                                                            html.Div(
                                                                '2',
                                                                className='text-2xl font-medium text-gray-100 bg-[#E74D39] rounded-full w-8 h-8 flex items-center justify-center',
                                                                id='end_sequence_second'
                                                            ),
                                                            html.Div(
                                                                className='sm:w-24 w-10 h-1 bg-gray-300 dark:bg-gray-500 rounded-full mx-2'
                                                            ),
                                                            html.Div(
                                                                '3',
                                                                className='text-2xl font-medium text-gray-100 bg-[#2BC48C] rounded-full w-8 h-8 flex items-center justify-center',
                                                                id='end_sequence_third'
                                                            )
                                                        ]
                                                    ),
                                                ]
                                            ),
                                        ]
                                    ),

                                    html.Div(
                                        className='text-lg font-medium text-slate-900 dark:text-gray-100 pt-10 px-4 sm:px-10 w-full',
                                        children=[
                                            'Angular Velocity',
                                        ]
                                    ),

                                    dcc.Graph(
                                        id='sequence',
                                        figure=fig,
                                        config=config,
                                        className='h-[500px] w-full'
                                    ),
                                ]
                            ),
                        ),

                        html.Div(
                            className='bg-white dark:bg-gray-700 shadow rounded-2xl flex items-center justify-center mb-5 backdrop-blur-md bg-opacity-80 border border-gray-100 dark:border-gray-900 flex-col w-full',
                            children=[
                                html.Div(
                                    className='text-lg font-medium text-slate-900 dark:text-gray-100 pt-10 px-4 sm:px-10 w-full',
                                    children=[
                                        'Pelvis Angles',
                                    ]
                                ),

                                dcc.Graph(
                                    id='pelvis_rotation',
                                    figure=fig3,
                                    config=config,
                                    className='w-full h-[500px]'
                                ),
                            ]),

                        html.Div(
                            className='bg-white dark:bg-gray-700 shadow rounded-2xl flex items-center justify-center mb-5 backdrop-blur-md bg-opacity-80 border border-gray-100 dark:border-gray-900 flex-col w-full',
                            children=[
                                html.Div(
                                    className='text-lg font-medium text-slate-900 dark:text-gray-100 pt-10 px-4 sm:px-10 w-full',
                                    children=[
                                        'Pelvis Displacement',
                                    ]
                                ),

                                dcc.Graph(
                                    id='pelvis_displacement',
                                    figure=fig4,
                                    config=config,
                                    className='w-full h-[500px]'
                                ),
                            ]),

                        html.Div(
                            className='bg-white dark:bg-gray-700 shadow rounded-2xl flex items-center justify-center mb-5 backdrop-blur-md bg-opacity-80 border border-gray-100 dark:border-gray-900 flex-col w-full',
                            children=[
                                html.Div(
                                    className='text-lg font-medium text-slate-900 dark:text-gray-100 pt-10 px-4 sm:px-10 w-full',
                                    children=[
                                        'Thorax Angles',
                                    ]
                                ),

                                dcc.Graph(
                                    id='thorax_rotation',
                                    figure=fig5,
                                    config=config,
                                    className='w-full h-[500px]'
                                ),
                            ]),

                        html.Div(
                            className='bg-white dark:bg-gray-700 shadow rounded-2xl flex items-center justify-center mb-5 backdrop-blur-md bg-opacity-80 border border-gray-100 dark:border-gray-900 flex-col w-full',
                            children=[
                                html.Div(
                                    className='text-lg font-medium text-slate-900 dark:text-gray-100 pt-10 px-4 sm:px-10 w-full',
                                    children=[
                                        'Thorax Displacement',
                                    ]
                                ),

                                dcc.Graph(
                                    id='thorax_displacement',
                                    figure=fig6,
                                    config=config,
                                    className='w-full h-[500px]'
                                ),
                            ]),

                        html.Div(
                            className='bg-white dark:bg-gray-700 shadow rounded-2xl flex items-center justify-center mb-5 backdrop-blur-md bg-opacity-80 border border-gray-100 dark:border-gray-900 flex-col w-full',
                            children=[
                                html.Div(
                                    className='text-lg font-medium text-slate-900 dark:text-gray-100 pt-10 px-4 sm:px-10 w-full',
                                    children=[
                                        'Head Tilt',
                                    ]
                                ),

                                dcc.Graph(
                                    id='h_tilt',
                                    figure=fig12,
                                    config=config,
                                    className='w-full h-[500px]'
                                ),
                            ]),

                        html.Div(
                            className='bg-white dark:bg-gray-700 shadow rounded-2xl flex items-center justify-center mb-5 backdrop-blur-md bg-opacity-80 border border-gray-100 dark:border-gray-900 flex-col w-full',
                            children=[
                                html.Div(
                                    className='text-lg font-medium text-slate-900 dark:text-gray-100 pt-10 px-4 sm:px-10 w-full',
                                    children=[
                                        'Head Rotation',
                                    ]
                                ),

                                dcc.Graph(
                                    id='h_rotation',
                                    figure=fig13,
                                    config=config,
                                    className='w-full h-[500px]'
                                ),
                            ]),

                        html.Div(
                            className='bg-white dark:bg-gray-700 shadow rounded-2xl flex items-center justify-center mb-5 backdrop-blur-md bg-opacity-80 border border-gray-100 dark:border-gray-900 flex-col w-full',
                            children=[
                                html.Div(
                                    className='text-lg font-medium text-slate-900 dark:text-gray-100 pt-10 px-4 sm:px-10 w-full',
                                    children=[
                                        'Spine Tilt',
                                    ]
                                ),

                                dcc.Graph(
                                    id='s_tilt',
                                    figure=fig11,
                                    config=config,
                                    className='w-full h-[500px]'
                                )
                            ]),

                        html.Div(
                            className='bg-white dark:bg-gray-700 shadow rounded-2xl flex items-center justify-center mb-5 backdrop-blur-md bg-opacity-80 border border-gray-100 dark:border-gray-900 flex-col w-full',
                            children=[
                                html.Div(
                                    className='text-lg font-medium text-slate-900 dark:text-gray-100 pt-10 px-4 sm:px-10 w-full',
                                    children=[
                                        'Left Arm Length'
                                    ]
                                ),

                                dcc.Graph(
                                    id='arm_length',
                                    figure=fig14,
                                    config=config,
                                    className='w-full h-[500px]'
                                )
                            ]),

                        html.Div(
                            className='bg-white dark:bg-gray-700 shadow rounded-2xl flex items-center justify-center mb-5 backdrop-blur-md bg-opacity-80 border border-gray-100 dark:border-gray-900 flex-col w-full',
                            children=[
                                html.Div(
                                    className='text-lg font-medium text-slate-900 dark:text-gray-100 pt-10 px-4 sm:px-10 w-full',
                                    children=[
                                        'Spine Rotation'
                                    ]
                                ),

                                dcc.Graph(
                                    id='spine_rotation',
                                    figure=fig15,
                                    config=config,
                                    className='w-full h-[500px]'
                                )
                            ]),

                        html.Div(
                            className='bg-white dark:bg-gray-700 shadow rounded-2xl flex items-center justify-center mb-5 backdrop-blur-md bg-opacity-80 border border-gray-100 dark:border-gray-900 flex-col w-full',
                            children=[
                                html.Div(
                                    className='text-lg font-medium text-slate-900 dark:text-gray-100 pt-10 px-4 sm:px-10 w-full',
                                    children=[
                                        'Wrist Angles'
                                    ]
                                ),

                                dcc.Graph(
                                    id='wrist_angle',
                                    figure=fig16,
                                    config=config,
                                    className='w-full h-[500px]'
                                )
                            ]),

                        html.Script('assets/dash.js'),
                    ]
                ),
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
    # print(filename)
    timestamp = datetime.datetime.strptime(filename, '%Y-%m-%d_%H-%M-%S')
    return timestamp.strftime('%d.%m.%Y, %H:%M')


def init_callbacks(app):

    @app.callback(
        [Output('sequence', 'figure'), Output('pelvis_rotation', 'figure'), Output('pelvis_displacement', 'figure'),
         Output('thorax_rotation', 'figure'), Output('thorax_displacement', 'figure'), Output('s_tilt', 'figure'),
         Output('h_tilt', 'figure'),
         Output('h_rotation', 'figure'), Output('arm_length', 'figure'), Output('spine_rotation', 'figure'),
         Output('wrist_angle', 'figure'), Output('file_list', 'children'), Output('upload-video', 'children'),
         Output('sequence_first', 'className'), Output('sequence_second', 'className'), Output('sequence_third', 'className'),
         Output('start_sequence_first', 'className'), Output('start_sequence_second', 'className'), Output('start_sequence_third', 'className'),
         Output('end_sequence_first', 'className'), Output('end_sequence_second', 'className'), Output('end_sequence_third', 'className')
         ],
        [Input('upload-data', 'contents'), Input('upload-data', 'filename'),
         Input({'type': 'saved-button', 'index': ALL}, 'n_clicks'),
         Input({'type': 'delete', 'index': ALL}, 'n_clicks')],
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

                if not os.path.exists(f'assets/save_data/{current_user.id}/{button_id}/{file}'):
                    fig, fig3, fig4, fig5, fig6, fig11, fig12, fig13, fig14, fig15, fig16, children, children_upload = reset_plots(
                        children, button_id, disabled)

                    sequence_first = 'text-2xl font-medium text-gray-100 bg-[#6266F6] rounded-full w-8 h-8 flex items-center justify-center',
                    sequence_second = 'text-2xl font-medium text-gray-100 bg-[#E74D39] rounded-full w-8 h-8 flex items-center justify-center'
                    sequence_third = 'text-2xl font-medium text-gray-100 bg-[#2BC48C] rounded-full w-8 h-8 flex items-center justify-center'

                    return [fig, fig3, fig4, fig5, fig6, fig11, fig12, fig13, fig14, fig15, fig16, children,
                            children_upload, sequence_first, sequence_second, sequence_third]

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
                try:
                    save_arm_rotation = data_values[:, 18]
                except:
                    save_arm_rotation = np.zeros(len(save_wrist_angle))

                # Get the kinematic transition  sequence
                sequence_first, sequence_second, sequence_third = kinematic_sequence(save_pelvis_rotation, save_thorax_rotation, save_arm_rotation, duration)

                # Get the kinematic start sequence
                sequence_first_start, sequence_second_start, sequence_third_start = kinematic_sequence_start(save_pelvis_rotation, save_thorax_rotation, save_arm_rotation, duration)

                # Get the kinematic end sequence
                sequence_first_end, sequence_second_end, sequence_third_end = kinematic_sequence_end(save_pelvis_rotation, save_thorax_rotation, save_arm_rotation, duration)


                # Get the video and update the video player
                vid_src = f'assets/save_data/{current_user.id}/{button_id}/motion.mp4'
                children_upload = upload_video(disabled, path=vid_src)

                # Change the background color of the pressed button and reset the previously pressed button
                for child in children:
                    if child['props']['id']['index'] == button_id:
                        child['props'][
                            'className'] = 'font-medium max-w-full text-xs text-gray-200 flex flex-row bg-slate-500 px-4 py-2 rounded-lg mb-2 mx-4 items-center justify-between h-12 transition'
                        child['props']['disabled'] = True
                        # Enabling the delete button
                        child['props']['children'][1]['props']['disabled'] = False
                        child['props']['children'][1]['props'][
                            'className'] = 'visible hover:bg-red-300 rounded-full px-1 py-1 items-center justify-center'
                    else:
                        child['props'][
                            'className'] = 'font-medium max-w-full text-xs text-gray-200 flex flex-row hover:bg-slate-500 px-4 py-2 rounded-lg mb-2 mx-4 items-center justify-between h-12 transition'
                        child['props']['disabled'] = False
                        # Disabling the delete button
                        child['props']['children'][1]['props']['disabled'] = True
                        child['props']['children'][1]['props']['className'] = 'invisible'

                fig, fig3, fig4, fig5, fig6, fig11, fig12, fig13, fig14, fig15, fig16 = update_plots(
                    save_pelvis_rotation,
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
                    save_arm_rotation,
                    duration)

                return [fig, fig3, fig4, fig5, fig6, fig11, fig12, fig13, fig14, fig15, fig16, children,
                        children_upload, sequence_first, sequence_second, sequence_third,
                        sequence_first_start, sequence_second_start, sequence_third_start,
                        sequence_first_end, sequence_second_end, sequence_third_end
                        ]

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
                    save_wrist_angle, save_wrist_tilt, save_arm_rotation = rand(100, 19)

                duration = 10

                fig, fig3, fig4, fig5, fig6, fig11, fig12, fig13, fig14, fig15, fig16 = update_plots(
                    save_pelvis_rotation, save_pelvis_tilt, save_pelvis_lift, save_pelvis_sway, save_pelvis_thrust, \
                    save_thorax_lift, save_thorax_bend, save_thorax_sway, save_thorax_rotation, save_thorax_thrust, \
                    save_thorax_tilt, save_spine_rotation, save_spine_tilt, save_head_rotation, save_head_tilt,
                    save_left_arm_length, \
                    save_wrist_angle, save_wrist_tilt, save_arm_rotation, duration, filt=False)

                # Reset sequence colors
                sequence_first = 'text-2xl font-medium text-gray-100 bg-[#6266F6] rounded-full w-8 h-8 flex items-center justify-center',
                sequence_second = 'text-2xl font-medium text-gray-100 bg-[#E74D39] rounded-full w-8 h-8 flex items-center justify-center'
                sequence_third = 'text-2xl font-medium text-gray-100 bg-[#2BC48C] rounded-full w-8 h-8 flex items-center justify-center'

                sequence_first_start = 'text-2xl font-medium text-gray-100 bg-[#6266F6] rounded-full w-8 h-8 flex items-center justify-center',
                sequence_second_start = 'text-2xl font-medium text-gray-100 bg-[#E74D39] rounded-full w-8 h-8 flex items-center justify-center'
                sequence_third_start = 'text-2xl font-medium text-gray-100 bg-[#2BC48C] rounded-full w-8 h-8 flex items-center justify-center'

                sequence_first_end = 'text-2xl font-medium text-gray-100 bg-[#6266F6] rounded-full w-8 h-8 flex items-center justify-center',
                sequence_second_end = 'text-2xl font-medium text-gray-100 bg-[#E74D39] rounded-full w-8 h-8 flex items-center justify-center'
                sequence_third_end = 'text-2xl font-medium text-gray-100 bg-[#2BC48C] rounded-full w-8 h-8 flex items-center justify-center'

                children_upload = [

                    html.Div(children=[
                        html.Div(
                            children=[
                                html.Span(
                                    'Upload your video',
                                    className='text-lg font-medium text-slate-900 dark:text-gray-100 pt-4'
                                ),
                                html.Span(
                                    'as mp4, mov or avi – max. 20 MB',
                                    className='text-sm font-medium text-slate-900 dark:text-gray-100'
                                )
                            ],
                            className='flex flex-col items-start mx-10 mb-4'
                        ),
                        html.Div(
                            dcc.Upload(
                                disabled=disabled,
                                id='upload-data',
                                children=html.Div(
                                    className='text-slate-900 dark:text-gray-100',
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
                        className='bg-white dark:bg-gray-700 shadow rounded-2xl flex items-start justify-center mb-5 text-center inline-block flex-col w-full h-96 backdrop-blur-md bg-opacity-80 border border-gray-100 dark:border-gray-900',
                    ),
                ]

                return [fig, fig3, fig4, fig5, fig6, fig11, fig12, fig13, fig14, fig15, fig16, children,
                        children_upload, sequence_first, sequence_second, sequence_third,
                        sequence_first_start, sequence_second_start, sequence_third_start,
                        sequence_first_end, sequence_second_end, sequence_third_end]

        # Check if folder was created and generate file name
        filename = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        create_folder(f'assets/save_data/{current_user.id}/' + filename)
        location = f'assets/save_data/{current_user.id}/' + filename

        # Send the video to the server and extract motion data
        # Send token to server to verify user
        email = current_user.email
        ts = URLSafeTimedSerializer('key')
        token = ts.dumps(email, salt='verification-key')

        response = requests.post(url_for('main.predict', token=token, _external=True, _scheme='https'), json={'contents': contents, 'filename': filename, 'location': location})
        # response = requests.post(url_for('main.predict', token=token, _external=True, _scheme='http'), json={'contents': contents, 'filename': filename, 'location': location})

        if response.status_code == 200:
            save_pelvis_rotation, save_pelvis_tilt, save_pelvis_lift, save_pelvis_sway, save_pelvis_thrust, \
            save_thorax_lift, save_thorax_bend, save_thorax_sway, save_thorax_rotation, save_thorax_thrust, \
            save_thorax_tilt, save_spine_rotation, save_spine_tilt, save_head_rotation, save_head_tilt, save_left_arm_length, save_wrist_angle, save_wrist_tilt, save_arm_rotation, duration = response.json().values()

        else:
            save_pelvis_rotation, save_pelvis_tilt, save_pelvis_lift, save_pelvis_sway, save_pelvis_thrust, \
            save_thorax_lift, save_thorax_bend, save_thorax_sway, save_thorax_rotation, save_thorax_thrust, \
            save_thorax_tilt, save_spine_rotation, save_spine_tilt, save_head_rotation, save_head_tilt, save_left_arm_length, save_wrist_angle, save_wrist_tilt, save_arm_rotation = rand(100, 19)
            duration = 10

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
                                                                                             save_arm_rotation,
                                                                                             duration)

        # Save the motion data to a parquet file
        df = pd.DataFrame(
            [save_pelvis_rotation, save_pelvis_tilt, save_pelvis_lift, save_pelvis_sway, save_pelvis_thrust,
             save_thorax_lift, save_thorax_bend, save_thorax_sway, save_thorax_rotation, save_thorax_thrust,
             save_thorax_tilt, save_spine_rotation, save_spine_tilt, save_head_rotation, save_head_tilt,
             save_left_arm_length, save_wrist_angle, save_wrist_tilt, save_arm_rotation]).T
        df.columns = ['pelvis_rotation', 'pelvis_tilt', 'pelvis_lift', 'pelvis_sway', 'pelvis_thrust',
                      'thorax_lift', 'thorax_bend', 'thorax_sway', 'thorax_rotation', 'thorax_thrust',
                      'thorax_tilt', 'spine_rotation', 'spine_tilt', 'head_rotation', 'head_tilt', 'left_arm_length',
                      'wrist_angle', 'wrist_tilt', 'arm_rotation']

        df['duration'] = duration

        df.to_parquet(f'assets/save_data/{current_user.id}/{filename}/{filename}.parquet')

        # Get the kinematic transition  sequence
        sequence_first, sequence_second, sequence_third = kinematic_sequence(save_pelvis_rotation, save_thorax_rotation,
                                                                             save_arm_rotation, duration)

        # Get the kinematic start sequence
        sequence_first_start, sequence_second_start, sequence_third_start = kinematic_sequence_start(
            save_pelvis_rotation, save_thorax_rotation, save_arm_rotation, duration)

        # Get the kinematic end sequence
        sequence_first_end, sequence_second_end, sequence_third_end = kinematic_sequence_end(save_pelvis_rotation,
                                                                                             save_thorax_rotation,
                                                                                             save_arm_rotation,
                                                                                             duration)

        # Reset the background color of the buttons
        for child in children:
            child['props'][
                'className'] = 'font-medium max-w-full text-xs text-gray-200 flex flex-row hover:bg-slate-500 px-4 py-2 rounded-lg mb-2 mx-4 items-center justify-between h-12'
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
                html.Button(html.Img(src=app.get_asset_url('delete.svg'), className='w-5 h-5'),
                            id={'type': 'delete', 'index': filename}, n_clicks=0,
                            className='visible hover:bg-red-300 rounded-full px-1 py-1 items-center justify-center',
                            disabled=False
                            ),
            ],
            id={'type': 'saved-button', 'index': f'{filename}'},
            className='font-base max-w-full text-xs text-gray-200 flex flex-row bg-slate-500 px-4 py-2 rounded-lg mb-2 mx-4 items-center justify-between h-12 transition')
        children.insert(0, new_item)

        if not current_user.unlimited:
            current_user.n_analyses -= 1
            db.session.commit()

        return [fig, fig3, fig4, fig5, fig6, fig11, fig12, fig13, fig14, fig15, fig16, children, children_upload,
                sequence_first, sequence_second, sequence_third,
                sequence_first_start, sequence_second_start, sequence_third_start,
                sequence_first_end, sequence_second_end, sequence_third_end,]

    # Show navbar on click
    @app.callback(
        [Output('sidebar', 'className'), Output('sidebar-header', 'className')],
        [Input('menu-button', 'n_clicks'), Input('body', 'className'), Input('sidebar-header', 'n_clicks')],
        prevent_initial_call=True
    )
    def show_navbar(n_clicks, body_class, header_clicks):
        if ctx.triggered_id != 'menu-button':
            body_class = body_class.replace('hidden', 'flex')
            return [
                'flex flex-col bg-slate-600 dark:bg-gray-700 fixed left-5 top-5 bottom-5 w-60 z-10 rounded-2xl hidden lg:flex',
                body_class]

        else:
            body_class = body_class.replace('flex', 'hidden')
            return [
                'flex flex-col bg-slate-600 dark:bg-gray-700 fixed top-0 bottom-0 w-60 z-10 lg:rounded-2xl lg:left-5 lg:top-5 lg:bottom-5',
                body_class]


# Reset plots
def reset_plots(children, button_id, disabled):
    for child in children:
        if child['props']['id']['index'] == button_id:
            children.remove(child)
    path = f'assets/save_data/{current_user.id}/{button_id}'
    shutil.rmtree(path)

    # Reset plots
    save_pelvis_rotation, save_pelvis_tilt, save_pelvis_lift, save_pelvis_sway, save_pelvis_thrust, \
    save_thorax_lift, save_thorax_bend, save_thorax_sway, save_thorax_rotation, save_thorax_thrust, \
    save_thorax_tilt, save_spine_rotation, save_spine_tilt, save_head_rotation, save_head_tilt, save_left_arm_length, \
    save_wrist_angle, save_wrist_tilt, save_arm_rotation = rand(100, 19)

    duration = 10

    fig, fig3, fig4, fig5, fig6, fig11, fig12, fig13, fig14, fig15, fig16 = update_plots(save_pelvis_rotation,
                                                                                         save_pelvis_tilt,
                                                                                         save_pelvis_lift,
                                                                                         save_pelvis_sway,
                                                                                         save_pelvis_thrust, \
                                                                                         save_thorax_lift,
                                                                                         save_thorax_bend,
                                                                                         save_thorax_sway,
                                                                                         save_thorax_rotation,
                                                                                         save_thorax_thrust, \
                                                                                         save_thorax_tilt,
                                                                                         save_spine_rotation,
                                                                                         save_spine_tilt,
                                                                                         save_head_rotation,
                                                                                         save_head_tilt,
                                                                                         save_left_arm_length, \
                                                                                         save_wrist_angle,
                                                                                         save_wrist_tilt,
                                                                                         save_arm_rotation,
                                                                                         duration,
                                                                                         filt=False)

    children_upload = [

        html.Div(children=[
            html.Div(
                children=[
                    html.Span(
                        'Upload your video',
                        className='text-lg font-medium text-slate-900 dark:text-gray-100 pt-4'
                    ),
                    html.Span(
                        'as mp4, mov or avi – max. 20 MB',
                        className='text-sm font-medium text-slate-900 dark:text-gray-100'
                    )
                ],
                className='flex flex-col items-start mx-10 mb-4'
            ),
            html.Div(
                dcc.Upload(
                    disabled=disabled,
                    id='upload-data',
                    children=html.Div(
                        className='text-slate-900 dark:text-gray-100',
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
            className='bg-white dark:bg-gray-700 shadow rounded-2xl flex items-start justify-center mb-5 text-center inline-block flex-col w-full h-96 backdrop-blur-md bg-opacity-80 border border-gray-100 dark:border-gray-900',
        ),
    ]

    return [fig, fig3, fig4, fig5, fig6, fig11, fig12, fig13, fig14, fig15, fig16, children, children_upload]


def kinematic_sequence(pelvis_rotation, thorax_rotation, arm_rotation, duration):
    # Get the kinematic transition  sequence
    hip_index = find_closest_zero_intersection_left_of_max(
        np.gradient(filter_data(pelvis_rotation, duration)))
    thorax_index = find_closest_zero_intersection_left_of_max(
        np.gradient(filter_data(thorax_rotation, duration)))
    arm_index = find_closest_zero_intersection_left_of_max(
        np.gradient(filter_data(arm_rotation, duration)))

    # Colors for hip, thorax and arm
    sequence = {'bg-[#6266F6]': hip_index, 'bg-[#E74D39]': thorax_index, 'bg-[#2BC48C]': arm_index}

    # Colors sorted by index
    sequence = sorted(sequence.items(), key=lambda item: item[1])

    # Update colors
    sequence_first = f'text-2xl font-medium text-gray-100 rounded-full w-8 h-8 flex items-center justify-center {sequence[0][0]}'
    sequence_second = f'text-2xl font-medium text-gray-100 rounded-full w-8 h-8 flex items-center justify-center {sequence[1][0]}'
    sequence_third = f'text-2xl font-medium text-gray-100 rounded-full w-8 h-8 flex items-center justify-center {sequence[2][0]}'

    return sequence_first, sequence_second, sequence_third


def kinematic_sequence_start(pelvis_rotation, thorax_rotation, arm_rotation, duration):
    # Get the kinematic transition  sequence
    hip_index = find_closest_zero_intersection_left_of_min(
        np.gradient(filter_data(pelvis_rotation, duration)))
    thorax_index = find_closest_zero_intersection_left_of_min(
        np.gradient(filter_data(thorax_rotation, duration)))
    arm_index = find_closest_zero_intersection_left_of_min(
        np.gradient(filter_data(arm_rotation, duration)))

    # Colors for hip, thorax and arm
    sequence = {'bg-[#6266F6]': hip_index, 'bg-[#E74D39]': thorax_index, 'bg-[#2BC48C]': arm_index}

    # Colors sorted by index
    sequence = sorted(sequence.items(), key=lambda item: item[1])

    # Update colors
    sequence_first = f'text-2xl font-medium text-gray-100 rounded-full w-8 h-8 flex items-center justify-center {sequence[0][0]}'
    sequence_second = f'text-2xl font-medium text-gray-100 rounded-full w-8 h-8 flex items-center justify-center {sequence[1][0]}'
    sequence_third = f'text-2xl font-medium text-gray-100 rounded-full w-8 h-8 flex items-center justify-center {sequence[2][0]}'

    return sequence_first, sequence_second, sequence_third


def kinematic_sequence_end(pelvis_rotation, thorax_rotation, arm_rotation, duration):
    # Get the kinematic transition  sequence
    hip_index = find_closest_zero_intersection_right_of_max(
        np.gradient(filter_data(pelvis_rotation, duration)))
    thorax_index = find_closest_zero_intersection_right_of_max(
        np.gradient(filter_data(thorax_rotation, duration)))
    arm_index = find_closest_zero_intersection_right_of_max(
        np.gradient(filter_data(arm_rotation, duration)))

    # Colors for hip, thorax and arm
    sequence = {'bg-[#6266F6]': hip_index, 'bg-[#E74D39]': thorax_index, 'bg-[#2BC48C]': arm_index}

    # Colors sorted by index
    sequence = sorted(sequence.items(), key=lambda item: item[1])

    # Update colors
    sequence_first = f'text-2xl font-medium text-gray-100 rounded-full w-8 h-8 flex items-center justify-center {sequence[0][0]}'
    sequence_second = f'text-2xl font-medium text-gray-100 rounded-full w-8 h-8 flex items-center justify-center {sequence[1][0]}'
    sequence_third = f'text-2xl font-medium text-gray-100 rounded-full w-8 h-8 flex items-center justify-center {sequence[2][0]}'

    return sequence_first, sequence_second, sequence_third
