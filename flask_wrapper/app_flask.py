import datetime
import shutil
import mediapipe as mp
import numpy as np
import plotly.graph_objects as go
import plotly.io as pio
import plotly.express as px
from dash import Dash, ctx, ALL, html, dcc, MATCH, ClientsideFunction
from dash_extensions.enrich import DashProxy, MultiplexerTransform, NoOutputTransform, Output, Input, State
import dash_player as dp
import pandas as pd
from scipy import signal
from code_b.angles import *
# from code_b.process_mem import process_motion
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
config = dict({'displaylogo': False, 'displayModeBar': False, 'scrollZoom': False})

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


def add_vertical_line(fig):
    fig.add_vline(x=0, line_width=4, line_color="#818cf8")


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
                            html.Div(
                                children=[
                                    'Upload your video',
                                    html.Div('BETA',
                                             className='ml-4 bg-gradient-to-br from-indigo-400 to-rose-600 dark:bg-gradient-to-b dark:from-amber-300 dark:to-orange-500 rounded-full px-2 py-1 w-fit font-bold text-sm text-gray-100 dark:text-gray-600')
                                ],
                                className='flex flex-row text-lg font-medium text-slate-900 dark:text-gray-100 pt-4'
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

                # Controls for the video player (top, impact, end)
                html.Div(
                    children=[
                        html.Button('Setup', id='setup_pos_button',
                                    className='w-24 px-4 py-2 rounded-lg bg-indigo-500 text-white font-bold text-sm'),
                        html.Button('Top', id='top_pos_button',
                                    className='w-24 px-4 py-2 rounded-lg bg-indigo-500 text-white font-bold text-sm'),
                        html.Button('Impact', id='impact_pos_button',
                                    className='w-24 px-4 py-2 rounded-lg bg-indigo-500 text-white font-bold text-sm'),
                        html.Button('Finish', id='end_pos_button',
                                    className='w-24 px-4 py-2 rounded-lg bg-indigo-500 text-white font-bold text-sm'),
                        html.Button('Frame +', id='plus_frame',
                                    className='w-24 px-4 py-2 rounded-lg bg-indigo-500 text-white font-bold text-sm hidden sm:block'),
                        html.Button('Frame -', id='minus_frame',
                                    className='w-24 px-4 py-2 rounded-lg bg-indigo-500 text-white font-bold text-sm hidden sm:block'),
                    ],
                    className='flex flex-row sm:flex-col sm:items-end sm:justify-center justify-between sm:mr-2 mb-2 sm:mb-5 gap-2 sm:gap-5'
                ),

                # Video player
                html.Div(
                    className=" relative overflow-hidden h-96 w-full shadow rounded-2xl sm:mb-5 bg-white dark:bg-gray-700 backdrop-blur-md bg-opacity-80 border border-gray-100 dark:border-gray-900",
                    children=[
                        # html.Video(src=f'{path}#t=0.001', id='video', controls=True,
                        #            className="h-full w-full object-cover"),

                        dp.DashPlayer(
                            id='video',
                            url=f'{path}#t=0.001',
                            controls=True,
                            playsinline=True,
                            className="h-full w-full object-cover",
                            width='100%',
                            height='100%',
                            intervalCurrentTime=70,
                        )
                    ]
                ),

                # Controls for the video player mobile (+, -)
                html.Div(
                    children=[
                        html.Button('Frame -', id='minus_frame_mobile',
                                    className='w-full h-fit px-4 py-2 rounded-lg bg-indigo-500 text-white font-bold text-sm disable-dbl-tap-zoom sm:hidden'),
                        html.Button('Frame +', id='plus_frame_mobile',
                                    className='w-full h-fit px-4 py-2 rounded-lg bg-indigo-500 text-white font-bold text-sm disable-dbl-tap-zoom sm:hidden'),
                    ],
                    className='flex flex-row justify-between mb-5 mt-2 gap-2'
                ),
            ]),
    ]

    return layout


def slider_view(name, min_bound, max_bound):
    layout = [
        html.Div(
            className='absolute h-2 bottom-3 left-3 right-3 bg-red-600 rounded-full',
            children=[
                html.Div(
                    id=f'green_bar_{name}',
                    style=dict(
                        left='0%',
                        right='0%',
                    ),
                    className='absolute h-2 bg-green-600 rounded-full'),
                # Slider
                html.Div(
                    id=f'slider_{name}',
                    style=dict(
                        left='50%',
                    ),
                    className='absolute h-6 w-1 -translate-x-1/2 -translate-y-2 bg-gray-900 dark:bg-gray-100 rounded-full',
                ),
                html.Div(
                    f'{min_bound}°',
                    className='absolute left-0 bottom-3.5 text-xs text-gray-400',
                ),
                html.Div(
                    f'{max_bound}°',
                    className='absolute right-0 bottom-3.5 text-xs text-gray-400',
                )
            ]
        ),
    ]

    return layout


def hand_path_3d(x, y, z, start, end, top, duration):
    start = int(start)
    end = int(end)
    top = int(top)

    x = filter_data(x, duration * 2)
    y = filter_data(y, duration * 2)
    z = filter_data(z, duration * 2)

    path_fig = go.Figure(
        data=go.Scatter3d(x=x[start:end],
                          y=y[start:end],
                          z=z[start:end],
                          mode='lines',
                          line=dict(color=np.linspace(0, 1, len(x))[start:end], width=6, colorscale='Viridis')))

    start_point = [x[start], y[start]]
    end_point = [x[top], y[top]]
    # print(start_point, end_point)

    slope = (end_point[1] - start_point[1]) / (end_point[0] - start_point[0])
    # slope = -1 / slope

    zero_intersect = start_point[1] - slope * start_point[0]

    plane_x = np.linspace(-0.5, 0.5, 100)
    plane_y = np.linspace(-0.5, 0.5, 100)
    plane_x, plane_y = np.meshgrid(plane_x, plane_y)
    plane_z = slope * plane_x + zero_intersect

    # plane = go.Surface(x=plane_x, y=plane_y, z=plane_z, showscale=False, opacity=0.5)

    # path_fig.add_trace(plane)

    path_fig.update_layout(
        scene=dict(
            xaxis_title='Down the line',
            # yaxis_title='Front on',
            zaxis_title='Height',
            # xaxis_showticklabels=False,
            # yaxis_showticklabels=False,
            # zaxis_showticklabels=False,
            camera=dict(
                up=dict(x=0, y=0, z=1),
                center=dict(x=0, y=0, z=-0.1),
                eye=dict(x=-2.5, y=0.1, z=0.2)
            ),
        ),
        font_color="#94a3b8",
        margin=dict(r=10, b=10, l=10, t=10),
        paper_bgcolor='rgba(0,0,0,0)',
    )

    return path_fig


# Random initialization for data
def rand(length, size):
    full = [np.full(length, np.random.randint(0, 30)) for _ in range(size)]
    return full


save_pelvis_rotation, save_pelvis_tilt, save_pelvis_lift, save_pelvis_sway, save_pelvis_thrust, \
    save_thorax_lift, save_thorax_bend, save_thorax_sway, save_thorax_rotation, save_thorax_thrust, \
    save_thorax_tilt, save_spine_rotation, save_spine_tilt, save_head_rotation, save_head_tilt, save_left_arm_length, \
    save_wrist_angle, save_wrist_tilt, save_arm_rotation, save_arm_to_ground = rand(100, 20)

arm_position = {'x': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9], 'y': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
                'z': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]}

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
                 save_left_arm_length, save_wrist_angle, save_wrist_tilt, save_arm_rotation, save_arm_to_ground,
                 duration, fps=1,
                 filt=True):
    if filt:
        converted = [filter_data(np.array(name), duration) for name in
                     [save_pelvis_rotation, save_pelvis_tilt, save_pelvis_lift, save_pelvis_sway, save_pelvis_thrust,
                      save_thorax_lift, save_thorax_bend, save_thorax_sway, save_thorax_rotation, save_thorax_thrust,
                      save_thorax_tilt, save_spine_rotation, save_spine_tilt, save_head_rotation, save_head_tilt,
                      save_left_arm_length, save_wrist_angle, save_wrist_tilt, save_arm_rotation, save_arm_to_ground]]

        save_pelvis_rotation, save_pelvis_tilt, save_pelvis_lift, save_pelvis_sway, save_pelvis_thrust, \
            save_thorax_lift, save_thorax_bend, save_thorax_sway, save_thorax_rotation, save_thorax_thrust, \
            save_thorax_tilt, save_spine_rotation, save_spine_tilt, save_head_rotation, save_head_tilt, \
            save_left_arm_length, save_wrist_angle, save_wrist_tilt, save_arm_rotation, save_arm_to_ground = converted

    timeline = np.linspace(0, duration, len(save_pelvis_rotation))

    save_pelvis_lift = save_pelvis_lift - save_pelvis_lift[0]
    save_pelvis_sway = save_pelvis_sway - save_pelvis_sway[0]
    save_pelvis_thrust = save_pelvis_thrust - save_pelvis_thrust[0]
    save_thorax_lift = save_thorax_lift - save_thorax_lift[0]
    save_thorax_sway = save_thorax_sway - save_thorax_sway[0]
    save_thorax_thrust = save_thorax_thrust - save_thorax_thrust[0]

    fig = go.Figure(data=go.Scatter(x=timeline, y=np.gradient(save_pelvis_rotation, 1 / fps), name=f'Pelvis'))

    fig.add_trace(
        go.Scatter(
            x=timeline,
            y=np.gradient(save_thorax_rotation, 1 / fps),
            name=f'Thorax',
        )
    )

    fig.add_trace(
        go.Scatter(
            x=timeline,
            y=-np.gradient(save_arm_rotation, 1 / fps),
            name=f'Arm',
        )
    )

    add_vertical_line(fig)

    fig.update_layout(
        # title='Angular velocity',
        title_x=0.5,
        font_size=12,
        # yaxis_title="Angular velocity in °/s",
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

    add_vertical_line(fig3)

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
        go.Scatter(x=timeline, y=save_pelvis_sway, name=f'Pelvis sway')
    )

    fig4.add_trace(
        go.Scatter(x=timeline, y=save_pelvis_thrust, name=f'Pelvis thrust')
    )

    add_vertical_line(fig4)

    fig4.update_layout(
        # title='Pelvis displacement',
        title_x=0.5,
        font_size=12,
        # yaxis_title='Displacement in m',
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

    add_vertical_line(fig5)

    fig5.update_layout(
        # title='Thorax angles',
        title_x=0.5,
        font_size=12,
        # yaxis_title='angle in °',
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

    add_vertical_line(fig6)

    fig6.update_layout(
        # title='Thorax displacement',
        title_x=0.5,
        font_size=12,
        # yaxis_title='Displacement in m',
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

    add_vertical_line(fig11)

    fig11.update_layout(
        # title='Tilt between pelvis and shoulder',
        title_x=0.5,
        font_size=12,
        # yaxis_title='angle in °',
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

    add_vertical_line(fig12)

    fig12.update_layout(
        # title='Head tilt',
        title_x=0.5,
        font_size=12,
        # yaxis_title='angle in °',
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

    add_vertical_line(fig13)

    fig13.update_layout(
        # title='Head rotation',
        title_x=0.5,
        font_size=12,
        # yaxis_title='angle in °',
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

    add_vertical_line(fig14)

    fig14.update_layout(
        # title='Left arm length',
        title_x=0.5,
        font_size=12,
        # yaxis_title='length in m',
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

    add_vertical_line(fig15)

    fig15.update_layout(
        # title='Spine rotation',
        title_x=0.5,
        font_size=12,
        # yaxis_title='angle in °',
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

    fig16 = go.Figure(data=go.Scatter(x=timeline, y=save_arm_rotation, name=f'Arm rotation'))

    fig16.add_trace(
        go.Scatter(x=timeline, y=save_arm_to_ground, name=f'Arm to ground')
    )

    fig16.update_layout(
        # title='Wrist angle',
        title_x=0.5,
        font_size=12,
        # yaxis_title='angle in °',
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
path_fig = go.Figure(
    data=go.Scatter3d(x=arm_position['x'], y=arm_position['y'],
                      z=arm_position['z'], mode='lines',
                      line=dict(color=arm_position['y'], width=6, colorscale='Viridis')))

path_fig.update_layout(
    scene=dict(
        xaxis_title='Down the line',
        # yaxis_title='Front on',
        zaxis_title='Height',
        xaxis_showticklabels=False,
        yaxis_showticklabels=False,
        zaxis_showticklabels=False,
        camera=dict(
            up=dict(x=0, y=0, z=1),
            center=dict(x=0, y=0, z=-0.1),
            eye=dict(x=-2.5, y=0.1, z=0.2)
        ),
    ),
    font_color="#94a3b8",
    margin=dict(r=10, b=10, l=10, t=10),
    paper_bgcolor='rgba(0,0,0,0)',
)

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

add_vertical_line(fig)

fig.update_layout(
    # title='Angular velocity',
    title_x=0.5,
    font_size=12,
    # yaxis_title="Angular velocity in °/s",
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

add_vertical_line(fig3)

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
    go.Scatter(x=timeline, y=save_pelvis_sway, name=f'Pelvis sway')
)

fig4.add_trace(
    go.Scatter(x=timeline, y=save_pelvis_thrust, name=f'Pelvis thrust')
)

add_vertical_line(fig4)

fig4.update_layout(
    # title='Pelvis displacement',
    title_x=0.5,
    font_size=12,
    # yaxis_title='Displacement in m',
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

add_vertical_line(fig5)

fig5.update_layout(
    # title='Thorax angles',
    title_x=0.5,
    font_size=12,
    # yaxis_title='angle in °',
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

add_vertical_line(fig6)

fig6.update_layout(
    # title='Thorax displacement',
    title_x=0.5,
    font_size=12,
    # yaxis_title='Displacement in m',
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

add_vertical_line(fig11)

fig11.update_layout(
    # title='Tilt between pelvis and shoulder',
    title_x=0.5,
    font_size=12,
    # yaxis_title='angle in °',
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

add_vertical_line(fig12)

fig12.update_layout(
    # title='Head tilt',
    title_x=0.5,
    font_size=12,
    # yaxis_title='angle in °',
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

add_vertical_line(fig13)

fig13.update_layout(
    # title='Head rotation',
    title_x=0.5,
    font_size=12,
    # yaxis_title='angle in °',
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

add_vertical_line(fig14)

fig14.update_layout(
    # title='Left arm length',
    title_x=0.5,
    font_size=12,
    # yaxis_title='length in m',
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

add_vertical_line(fig15)

fig15.update_layout(
    # title='Spine rotation',
    title_x=0.5,
    font_size=12,
    # yaxis_title='angle in °',
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

fig16 = go.Figure(data=go.Scatter(x=timeline, y=save_arm_rotation, name=f'Arm rotation'))

fig16.add_trace(
    go.Scatter(x=timeline, y=save_arm_to_ground, name=f'Arm to ground')
)

fig16.update_layout(
    # title='Wrist angles',
    title_x=0.5,
    font_size=12,
    # yaxis_title='angle in °',
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
    app = DashProxy(__name__, server=server, url_base_pathname='/dashboard/',
                    external_scripts=["https://tailwindcss.com/", {"src": "https://cdn.tailwindcss.com"}],
                    transforms=[MultiplexerTransform(), NoOutputTransform()]
                    )
    app.css.config.serve_locally = False
    app.css.append_css({'external_url': './assets/output.css'})
    # server = app.server
    app.app_context = server.app_context
    app._favicon = 'favicon.png'

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

            # className='flex w-full',

            children=[

                # Loader
                html.Div(
                    id='loader',
                    className='hidden w-full',
                    children=loader
                ),

                # Main wrapper
                html.Div(
                    className='flex w-full flex-col',
                    id='main_wrapper',
                    children=[

                        # navbar top
                        html.Div(
                            id='navbar-top',
                            className='flex flex-row w-full h-12 items-center ml-4 lg:hidden',
                            children=[
                                html.Button(
                                    className='flex flex-row w-6 h-6 items-center',
                                    id='menu-button',
                                    children=[
                                        html.Img(src=app.get_asset_url('menu_burger.svg'), className='h-4 w-4',
                                                 id='menu-icon')
                                    ]
                                )
                            ]
                        ),

                        # Sidebar
                        html.Div(
                            id='sidebar',
                            className='flex flex-col bg-slate-600 dark:bg-gray-700 fixed lg:left-5 lg:top-5 lg:bottom-5 top-0 bottom-0 w-60 z-10 lg:rounded-2xl hidden lg:flex',
                            children=[
                                html.Button(
                                    id='sidebar-header',
                                    className='flex-row items-center ml-4 lg:hidden',
                                    children=[
                                        html.Img(src=app.get_asset_url('menu_cross.svg'), className='h-4 w-4 mt-4')]
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
                                                html.Button(
                                                    html.Img(src=app.get_asset_url('delete.svg'), className='w-5 h-5'),
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
                        # Sidebar end

                        html.Div(
                            id='body',
                            className='lg:mx-16 mx-4 lg:pl-60 mt-0',
                            children=[

                                # Selection view in center of screen
                                html.Div(
                                    className='fixed w-full h-full top-0 left-0 z-20 bg-black bg-opacity-50 backdrop-filter backdrop-blur-sm hidden',
                                    children=[
                                        html.Div(
                                            className='fixed flex flex-col p-14 w-96 top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 bg-white dark:bg-gray-800 rounded-2xl shadow-lg z-30',
                                            children=[
                                                html.Div(
                                                    'New margins',
                                                    className='text-lg font-medium text-slate-900 dark:text-gray-100 pt-4 flex flex-row items-center absolute top-4 left-1/2 transform -translate-x-1/2'
                                                ),
                                                html.Form(
                                                    children=[
                                                    html.Div(
                                                        'Setup',
                                                        className='relative justify-start text-sm font-medium text-slate-900 dark:text-gray-100 pt-4 flex flex-row'
                                                    ),
                                                    dcc.Input(
                                                        id='setup_new_margins',
                                                        className='dark:bg-gray-600 relative block w-full my-2 p-3 appearance-none rounded-lg border border-gray-300 text-gray-900 dark:border-gray-500 dark:text-gray-100 placeholder-gray-300 dark:placeholder-gray-400 focus:z-10 focus:border-indigo-500 focus:outline-none focus:ring-indigo-500 text-sm',
                                                    ),
                                                    html.Div(
                                                        'Impact',
                                                        className='relative justify-start text-sm font-medium text-slate-900 dark:text-gray-100 pt-2 flex flex-row'
                                                    ),
                                                    dcc.Input(
                                                        id='impact_new_margins',
                                                        className='dark:bg-gray-600 relative block w-full my-2 p-3 appearance-none rounded-lg border border-gray-300 text-gray-900 dark:border-gray-500 dark:text-gray-100 placeholder-gray-300 dark:placeholder-gray-400 focus:z-10 focus:border-indigo-500 focus:outline-none focus:ring-indigo-500 text-sm',
                                                    ),
                                                    html.Div(
                                                        'Finish',
                                                        className='relative justify-start text-sm font-medium text-slate-900 dark:text-gray-100 pt-2 flex flex-row'
                                                    ),
                                                    dcc.Input(
                                                        id='finish_new_margins',
                                                        className='dark:bg-gray-600 relative block w-full my-2 p-3 appearance-none rounded-lg border border-gray-300 text-gray-900 dark:border-gray-500 dark:text-gray-100 placeholder-gray-300 dark:placeholder-gray-400 focus:z-10 focus:border-indigo-500 focus:outline-none focus:ring-indigo-500 text-sm',
                                                    ),
                                                    html.Button(
                                                        'Save',
                                                        className='relative justify-start text-sm font-medium text-slate-900 dark:text-gray-100 flex flex-row bg-indigo-500 hover:bg-indigo-600 rounded-lg items-center justify-center px-4 py-2 mt-2 w-fit',
                                                    )
                                                    ]
                                                )
                                            ]
                                        )
                                    ]
                                ),
                                # End selection view

                                # Upload component
                                html.Div(
                                    id='upload-video',
                                    className='flex flex-row justify-between mt-5',
                                    children=[

                                        html.Div(children=[
                                            html.Div(
                                                children=[
                                                    html.Div(
                                                        children=[
                                                            'Upload your video',
                                                            html.Div('BETA',
                                                                     className='ml-4 bg-gradient-to-br from-indigo-400 to-rose-600 dark:bg-gradient-to-b dark:from-amber-300 dark:to-orange-500 rounded-full px-2 py-1 w-fit font-bold text-sm text-gray-100 dark:text-gray-600')
                                                        ],

                                                        className='text-lg font-medium text-slate-900 dark:text-gray-100 pt-4 flex flex-row items-center justify-between'
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
                                                ),
                                                className='w-full'
                                                # className='bg-[rgba(251, 252, 254, 1)] mx-10 sm:rounded-2xl flex items-center justify-center my-10 text-center inline-block flex-col w-[95%] border-dashed border-4 border-gray-400'
                                            )
                                        ],
                                            className='bg-white dark:bg-gray-700 shadow rounded-2xl flex items-start justify-center mb-5 text-center inline-block flex-col w-full h-44 sm:h-96 backdrop-blur-md bg-opacity-80 border border-gray-100 dark:border-gray-900',
                                        ),
                                    ]),
                                # End of upload component

                                # Live updating divs based on position in video
                                html.Div(
                                    className='flex flex-nowrap overflow-x-auto px-4 -mx-4',
                                    children=[
                                        html.Div(
                                            className='flex mb-5 gap-2 flex-col',
                                            children=[
                                                # First row
                                                html.Div(
                                                    className='flex flex-row w-full gap-2',
                                                    children=[
                                                        html.Div(
                                                            children=[
                                                                html.Div('Pelvis Rot.',
                                                                         className='absolute left-1/2 -translate-x-1/2 top-2 sm:text-lg text-sm font-medium text-slate-900 hover:text-gray-600 dark:text-gray-100 dark:hover:text-gray-300 text-left', ),
                                                                html.Div('- °', id='pelvis_rot_val', className='mt-2'),
                                                                # Slider bar
                                                                html.Div(slider_view('pelvis_rot', -80, 160))
                                                                # End of slider bar
                                                            ],
                                                            className='relative text-3xl font-medium text-slate-900 dark:text-gray-100 bg-white dark:bg-gray-700 shadow rounded-2xl flex flex-col items-center justify-center w-56 h-28 text-center'
                                                        ),
                                                        html.Div(
                                                            children=[
                                                                html.Div('Pelvis Tilt',
                                                                         className='absolute left-1/2 -translate-x-1/2 top-2 sm:text-lg text-sm font-medium text-slate-900 hover:text-gray-600 dark:text-gray-100 dark:hover:text-gray-300 text-left', ),
                                                                html.Div('- °', id='pelvis_bend_val', className='mt-2'),
                                                                # Slider bar
                                                                html.Div(slider_view('pelvis_bend', -30, 30))
                                                                # End of slider bar
                                                            ],
                                                            className='relative text-3xl font-medium text-slate-900 dark:text-gray-100 bg-white dark:bg-gray-700 shadow rounded-2xl flex flex-col items-center justify-center w-56 h-28 text-center'
                                                        ),
                                                        html.Div(
                                                            children=[
                                                                html.Div('Thorax Rot.',
                                                                         className='absolute left-1/2 -translate-x-1/2 top-2 sm:text-lg text-sm font-medium text-slate-900 hover:text-gray-600 dark:text-gray-100 dark:hover:text-gray-300 text-left', ),
                                                                html.Div('- °', id='thorax_rot_val', className='mt-2'),
                                                                # Slider bar
                                                                html.Div(slider_view('thorax_rot', -140, 140)),
                                                                # End of slider bar
                                                            ],
                                                            className='relative text-3xl font-medium text-slate-900 dark:text-gray-100 bg-white dark:bg-gray-700 shadow rounded-2xl flex flex-col items-center justify-center w-56 h-28 text-center'
                                                        ),
                                                        html.Div(
                                                            children=[
                                                                html.Div('Thorax Tilt',
                                                                         className='absolute left-1/2 -translate-x-1/2 top-2 sm:text-lg text-sm font-medium text-slate-900 hover:text-gray-600 dark:text-gray-100 dark:hover:text-gray-300 text-left', ),
                                                                html.Div('- °', id='thorax_bend_val', className='mt-2'),
                                                                # Slider bar
                                                                html.Div(slider_view('thorax_bend', -20, 60)),
                                                                # End of slider bar
                                                            ],
                                                            className='relative text-3xl font-medium text-slate-900 dark:text-gray-100 bg-white dark:bg-gray-700 shadow rounded-2xl flex flex-col items-center justify-center w-56 h-28 text-center'
                                                        ),
                                                    ]
                                                ),
                                                # End of first row

                                                # Second row
                                                html.Div(
                                                    className='flex flex-row gap-2',
                                                    children=[
                                                        html.Div(
                                                            children=[
                                                                html.Div('Head Rot.',
                                                                         className='absolute left-1/2 -translate-x-1/2 top-2 sm:text-lg text-sm font-medium text-slate-900 hover:text-gray-600 dark:text-gray-100 dark:hover:text-gray-300 text-left', ),
                                                                html.Div('- °', id='head_rot_val', className='mt-2'),
                                                                html.Div(slider_view('head_rot', -100, 100)),
                                                            ],
                                                            className='relative text-3xl font-medium text-slate-900 dark:text-gray-100 bg-white dark:bg-gray-700 shadow rounded-2xl flex flex-col items-center justify-center w-56 h-28 text-center'
                                                        ),
                                                        html.Div(
                                                            children=[
                                                                html.Div('Head Tilt',
                                                                         className='absolute left-1/2 -translate-x-1/2 top-2 sm:text-lg text-sm font-medium text-slate-900 hover:text-gray-600 dark:text-gray-100 dark:hover:text-gray-300 text-left', ),
                                                                html.Div('- °', id='head_tilt_val', className='mt-2'),
                                                                html.Div(slider_view('head_tilt', -60, 60)),
                                                            ],
                                                            className='relative text-3xl font-medium text-slate-900 dark:text-gray-100 bg-white dark:bg-gray-700 shadow rounded-2xl flex flex-col items-center justify-center w-56 h-28 text-center'
                                                        ),
                                                        html.Div(
                                                            children=[
                                                                html.Div('Arm Rot.',
                                                                         className='absolute left-1/2 -translate-x-1/2 top-2 sm:text-lg text-sm font-medium text-slate-900 hover:text-gray-600 dark:text-gray-100 dark:hover:text-gray-300 text-left', ),
                                                                html.Div('- °', id='arm_rot_val', className='mt-2'),
                                                                html.Div(slider_view('arm_rot', -240, 240)),
                                                            ],
                                                            className='relative text-3xl font-medium text-slate-900 dark:text-gray-100 bg-white dark:bg-gray-700 shadow rounded-2xl flex flex-col items-center justify-center w-56 h-28 text-center'
                                                        ),
                                                        html.Div(
                                                            children=[
                                                                html.Div('Arm Ground',
                                                                         className='absolute left-1/2 -translate-x-1/2 top-2 sm:text-lg text-sm font-medium text-slate-900 hover:text-gray-600 dark:text-gray-100 dark:hover:text-gray-300 text-left', ),
                                                                html.Div('- °', id='arm_ground_val', className='mt-2'),
                                                                html.Div(slider_view('arm_ground', -90, 90)),
                                                            ],
                                                            className='relative text-3xl font-medium text-slate-900 dark:text-gray-100 bg-white dark:bg-gray-700 shadow rounded-2xl flex flex-col items-center justify-center w-56 h-28 text-center'
                                                        ),
                                                    ]
                                                ),
                                                # End of second row
                                            ]
                                        ),
                                    ]
                                ),
                                # End of updating divs

                                # Tempo divs
                                html.Div(
                                    className='flex flex-row w-full justify-between mb-5 sm:gap-5 gap-2',
                                    children=[
                                        html.Div(
                                            id='position_divs',
                                            children=[
                                                html.Div('Backswing',
                                                         className='sm:text-lg text-sm font-medium text-slate-900 hover:text-gray-600 dark:text-gray-100 dark:hover:text-gray-300 mx-4 sm:mx-10 relative text-left', ),
                                                html.Div('- s', id='backswing', className='mt-2'),
                                                html.Div('0.5', id='top_pos', className='hidden'),
                                                html.Div('0.5', id='impact_pos', className='hidden'),
                                                html.Div('0.5', id='end_pos', className='hidden'),
                                                html.Div('0.5', id='setup_pos', className='hidden'),
                                                html.Div('60', id='fps_saved', className='hidden'),
                                            ],
                                            className='text-3xl font-medium text-slate-900 dark:text-gray-100 bg-white dark:bg-gray-700 shadow rounded-2xl flex flex-col items-center justify-center w-full h-28 text-center'
                                        ),
                                        html.Div(
                                            children=[
                                                html.Div('Downswing',
                                                         className='sm:text-lg text-sm font-medium text-slate-900 hover:text-gray-600 dark:text-gray-100 dark:hover:text-gray-300 mx-4 sm:mx-10 relative text-left', ),
                                                html.Div('- s', id='downswing', className='mt-2')
                                            ],
                                            className='text-3xl font-medium text-slate-900 dark:text-gray-100 bg-white dark:bg-gray-700 shadow rounded-2xl flex flex-col items-center justify-center w-full h-28 text-center'
                                        ),
                                        html.Div(
                                            children=[
                                                html.Div('Tempo',
                                                         className='sm:text-lg text-sm font-medium text-slate-900 hover:text-gray-600 dark:text-gray-100 dark:hover:text-gray-300 mx-4 sm:mx-10 relative text-left', ),
                                                html.Div(
                                                    children=[
                                                        html.Div('-', id='tempo', className='mt-2'),
                                                        html.Div(': 1', className='mt-2 ml-2')
                                                    ],
                                                    className='flex flex-row items-center justify-center'
                                                )
                                            ],
                                            className='text-3xl font-medium text-slate-900 dark:text-gray-100 bg-white dark:bg-gray-700 shadow rounded-2xl flex flex-col items-center justify-center w-full h-28 text-center'
                                        ),
                                    ]
                                ),
                                # End of tempo divs

                                html.Div(
                                    className='relative bg-white dark:bg-gray-700 shadow rounded-2xl flex items-center justify-center mb-5 backdrop-blur-md bg-opacity-80 border border-gray-100 dark:border-gray-900 flex-col w-full',
                                    children=[

                                        html.Div(info_text('arm_path'), className='w-full'),

                                        html.Div(
                                            # 3D arm path
                                            id='arm_path',
                                            children=[
                                                dcc.Graph(
                                                    id='arm_path_3d',
                                                    figure=path_fig,
                                                    config=config,
                                                    className='w-[350px] lg:w-[500px] xl:w-full h-[500px] relative',
                                                )
                                            ]),
                                    ]
                                ),

                                html.Div(
                                    id='parent_sequence',
                                    className='relative bg-white dark:bg-gray-700 shadow rounded-2xl flex items-center justify-center mb-5 backdrop-blur-md bg-opacity-80 border border-gray-100 dark:border-gray-900 flex-col w-full',
                                    children=[

                                        # Row for sequences
                                        html.Div(
                                            className='flex flex-row justify-between items-center w-full flex-wrap relative',
                                            children=[

                                                # Column for sequence
                                                html.Div(
                                                    className='flex flex-col',
                                                    children=[
                                                        html.Div(info_text('start_sequence'),
                                                                 className='relative w-full'),
                                                        html.Div(
                                                            className='flex flex-row items-center w-full px-4 sm:px-10 py-10',
                                                            children=[
                                                                html.Div(
                                                                    'Hip',
                                                                    className='text-lg font-medium text-gray-100 bg-[#6266F6] rounded-lg py-2 px-2 flex items-center justify-center',
                                                                    id='start_sequence_first'
                                                                ),
                                                                html.Div(
                                                                    className='sm:w-16 w-10 h-1 bg-gray-300 dark:bg-gray-500 rounded-full mx-2'
                                                                ),
                                                                html.Div(
                                                                    'Thorax',
                                                                    className='text-lg font-medium text-gray-100 bg-[#E74D39] rounded-lg py-2 px-2 flex items-center justify-center',
                                                                    id='start_sequence_second'
                                                                ),
                                                                html.Div(
                                                                    className='sm:w-16 w-10 h-1 bg-gray-300 dark:bg-gray-500 rounded-full mx-2'
                                                                ),
                                                                html.Div(
                                                                    'Arms',
                                                                    className='text-lg font-medium text-gray-100 bg-[#2BC48C] rounded-lg py-2 px-2 flex items-center justify-center',
                                                                    id='start_sequence_third'
                                                                )
                                                            ]
                                                        ),
                                                    ]
                                                ),

                                                html.Div(
                                                    className='flex flex-col',
                                                    children=[
                                                        html.Div(info_text('transition_sequence'),
                                                                 className='relative w-full'),
                                                        html.Div(
                                                            className='flex flex-row items-center w-full px-4 sm:px-10 py-10',
                                                            children=[
                                                                html.Div(
                                                                    'Hip',
                                                                    className='text-lg font-medium text-gray-100 bg-[#6266F6] rounded-lg py-2 px-2 flex items-center justify-center',
                                                                    id='sequence_first'
                                                                ),
                                                                html.Div(
                                                                    className='sm:w-16 w-10 h-1 bg-gray-300 dark:bg-gray-500 rounded-full mx-2'
                                                                ),
                                                                html.Div(
                                                                    'Thorax',
                                                                    className='text-lg font-medium text-gray-100 bg-[#E74D39] rounded-lg py-2 px-2 flex items-center justify-center',
                                                                    id='sequence_second'
                                                                ),
                                                                html.Div(
                                                                    className='sm:w-16 w-10 h-1 bg-gray-300 dark:bg-gray-500 rounded-full mx-2'
                                                                ),
                                                                html.Div(
                                                                    'Arms',
                                                                    className='text-lg font-medium text-gray-100 bg-[#2BC48C] rounded-lg py-2 px-2 flex items-center justify-center',
                                                                    id='sequence_third'
                                                                )
                                                            ]
                                                        ),
                                                    ]
                                                ),

                                                # Column for sequence
                                                html.Div(
                                                    className='relative flex flex-col',
                                                    children=[
                                                        html.Div(info_text('finish_sequence'),
                                                                 className=' relative w-full'),
                                                        html.Div(
                                                            className='flex flex-row items-center w-full px-4 sm:px-10 py-10',
                                                            children=[
                                                                html.Div(
                                                                    'Hip',
                                                                    className='text-lg font-medium text-gray-100 bg-[#6266F6] rounded-lg py-2 px-2 flex items-center justify-center',
                                                                    id='end_sequence_first'
                                                                ),
                                                                html.Div(
                                                                    className='sm:w-16 w-10 h-1 bg-gray-300 dark:bg-gray-500 rounded-full mx-2'
                                                                ),
                                                                html.Div(
                                                                    'Thorax',
                                                                    className='text-lg font-medium text-gray-100 bg-[#E74D39] rounded-lg py-2 px-2 flex items-center justify-center',
                                                                    id='end_sequence_second'
                                                                ),
                                                                html.Div(
                                                                    className='sm:w-16 w-10 h-1 bg-gray-300 dark:bg-gray-500 rounded-full mx-2'
                                                                ),
                                                                html.Div(
                                                                    'Arms',
                                                                    className='text-lg font-medium text-gray-100 bg-[#2BC48C] rounded-lg py-2 px-2 flex items-center justify-center',
                                                                    id='end_sequence_third'
                                                                )
                                                            ]
                                                        ),
                                                    ]
                                                ),
                                            ]
                                        ),

                                        html.Div(info_text('angular_velocity'), className=' relative w-full'),

                                        dcc.Graph(
                                            id='sequence',
                                            figure=fig,
                                            config=config,
                                            className='h-[500px] w-full relative',
                                        ),
                                    ]
                                ),

                                html.Div(
                                    className='relative bg-white dark:bg-gray-700 shadow rounded-2xl flex items-center justify-center mb-5 backdrop-blur-md bg-opacity-80 border border-gray-100 dark:border-gray-900 flex-col w-full',
                                    children=[
                                        html.Div(info_text('pelvis_rotation'), className='relative w-full'),

                                        dcc.Graph(
                                            id='pelvis_rotation',
                                            figure=fig3,
                                            config=config,
                                            className='w-full h-[500px]',
                                        ),
                                    ]),

                                html.Div(
                                    className='bg-white dark:bg-gray-700 shadow rounded-2xl flex items-center justify-center mb-5 backdrop-blur-md bg-opacity-80 border border-gray-100 dark:border-gray-900 flex-col w-full',
                                    children=[
                                        html.Div(info_text('pelvis_displacement'), className=' relative w-full'),

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
                                        html.Div(info_text('thorax_angles'), className=' relative w-full'),

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
                                        html.Div(info_text('thorax_displacement'), className=' relative w-full'),

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
                                        html.Div(info_text('head_tilt'), className=' relative w-full'),

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
                                        html.Div(info_text('head_rotation'), className=' relative w-full'),

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
                                        html.Div(info_text('spine_tilt'), className=' relative w-full'),

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
                                        html.Div(info_text('left_arm'), className=' relative w-full'),

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
                                        html.Div(info_text('spine_rotation'), className=' relative w-full'),

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
                                                'Arm Angles'
                                            ]
                                        ),

                                        dcc.Graph(
                                            id='arm_angle',
                                            figure=fig16,
                                            config=config,
                                            className='w-full h-[500px]'
                                        )
                                    ]),

                                html.Script('assets/dash.js'),
                                # html.Script(src='video_update.js')
                            ]
                        ),

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
         Output('arm_angle', 'figure'), Output('file_list', 'children'), Output('upload-video', 'children'),
         Output('sequence_first', 'className'), Output('sequence_second', 'className'),
         Output('sequence_third', 'className'),
         Output('start_sequence_first', 'className'), Output('start_sequence_second', 'className'),
         Output('start_sequence_third', 'className'),
         Output('end_sequence_first', 'className'), Output('end_sequence_second', 'className'),
         Output('end_sequence_third', 'className'),
         Output('sequence_first', 'children'), Output('sequence_second', 'children'),
         Output('sequence_third', 'children'),
         Output('start_sequence_first', 'children'), Output('start_sequence_second', 'children'),
         Output('start_sequence_third', 'children'),
         Output('end_sequence_first', 'children'), Output('end_sequence_second', 'children'),
         Output('end_sequence_third', 'children'),
         Output('tempo', 'children'), Output('backswing', 'children'), Output('downswing', 'children'),
         Output('top_pos', 'children'), Output('impact_pos', 'children'), Output('end_pos', 'children'),
         Output('setup_pos', 'children'), Output('fps_saved', 'children'),
         Output('arm_path', 'children')
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

                # Check if file exists and delete otherwise
                if (not os.path.exists(f'assets/save_data/{current_user.id}/{button_id}/{file}')) or (
                        not os.path.exists(f'assets/save_data/{current_user.id}/{button_id}/motion.mp4')):
                    fig, fig3, fig4, fig5, fig6, fig11, fig12, fig13, fig14, fig15, fig16, children, children_upload = reset_plots(
                        children, button_id, disabled)

                    # Reset plots
                    save_pelvis_rotation, save_pelvis_tilt, save_pelvis_lift, save_pelvis_sway, save_pelvis_thrust, \
                        save_thorax_lift, save_thorax_bend, save_thorax_sway, save_thorax_rotation, save_thorax_thrust, \
                        save_thorax_tilt, save_spine_rotation, save_spine_tilt, save_head_rotation, save_head_tilt, save_left_arm_length, \
                        save_wrist_angle, save_wrist_tilt, save_arm_rotation, save_arm_to_ground = rand(100, 20)

                    arm_position = {'x': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9], 'y': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
                                    'z': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]}

                    duration = 10

                    fig, fig3, fig4, fig5, fig6, fig11, fig12, fig13, fig14, fig15, fig16 = update_plots(
                        save_pelvis_rotation, save_pelvis_tilt, save_pelvis_lift, save_pelvis_sway, save_pelvis_thrust,
                        save_thorax_lift, save_thorax_bend, save_thorax_sway, save_thorax_rotation, save_thorax_thrust,
                        save_thorax_tilt, save_spine_rotation, save_spine_tilt, save_head_rotation, save_head_tilt,
                        save_left_arm_length, save_wrist_angle, save_wrist_tilt, save_arm_rotation, save_arm_to_ground,
                        duration, filt=False)

                    path_fig = go.Figure(data=go.Scatter3d(x=arm_position['x'],
                                                           y=arm_position['y'],
                                                           z=arm_position['z'], mode='lines',
                                                           line=dict(color=np.linspace(0, 1, len(arm_position['x'])),
                                                                     width=6, colorscale='Viridis')))

                    path_fig.update_layout(
                        scene=dict(
                            xaxis_title='Down the line',
                            yaxis_title='Front on',
                            zaxis_title='Height',
                            xaxis_showticklabels=False,
                            yaxis_showticklabels=False,
                            zaxis_showticklabels=False,
                            camera=dict(
                                up=dict(x=0, y=0, z=1),
                                center=dict(x=0, y=0, z=-0.1),
                                eye=dict(x=-2.5, y=0.1, z=0.2)
                            ),
                        ),
                        font_color="#94a3b8",
                        margin=dict(r=10, b=10, l=10, t=10),
                        paper_bgcolor='rgba(0,0,0,0)',
                    )

                    path = dcc.Graph(figure=path_fig, config=config,
                                     className='w-[350px] lg:w-[500px] xl:w-full h-[500px] relative', )

                    # Reset sequence colors
                    sequence_first = 'text-lg font-medium text-gray-100 rounded-lg py-2 px-2 flex items-center justify-center  bg-[#6266F6]',
                    sequence_second = 'text-lg font-medium text-gray-100 rounded-lg py-2 px-2 flex items-center justify-center  bg-[#E74D39]'
                    sequence_third = 'text-lg font-medium text-gray-100 rounded-lg py-2 px-2 flex items-center justify-center  bg-[#2BC48C]'

                    # Reset sequence text
                    sequence_first_text = 'Hip'
                    sequence_second_text = 'Thorax'
                    sequence_third_text = 'Arm'

                    # Tempo
                    temp, time_back, time_down = ('-', '- s', '- s')

                    # Top backswing
                    top_pos = 0.5

                    # Impact
                    impact_pos = 0.5

                    # End of swing
                    end_pos = 0.5

                    # Setup
                    setup_pos = 0.5

                    fps_saved = 60

                    children_upload = [

                        html.Div(children=[
                            html.Div(
                                children=[
                                    html.Div(
                                        children=[
                                            'Upload your video',
                                            html.Div('BETA',
                                                     className='ml-4 bg-gradient-to-br from-indigo-400 to-rose-600 dark:bg-gradient-to-b dark:from-amber-300 dark:to-orange-500 rounded-full px-2 py-1 w-fit font-bold text-sm text-gray-100 dark:text-gray-600')
                                        ],
                                        className='flex flex-row text-lg font-medium text-slate-900 dark:text-gray-100 pt-4'
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
                            sequence_first, sequence_second, sequence_third,
                            sequence_first, sequence_second, sequence_third,
                            sequence_first_text, sequence_second_text, sequence_third_text,
                            sequence_first_text, sequence_second_text, sequence_third_text,
                            sequence_first_text, sequence_second_text, sequence_third_text,
                            temp, time_back, time_down,
                            top_pos, impact_pos, end_pos, setup_pos, fps_saved,
                            []]

                # Read data from parquet file
                data = pd.read_parquet(f'assets/save_data/{current_user.id}/{button_id}/{file}')
                duration = data['duration'][0]
                # data = data.values
                save_pelvis_rotation = data['pelvis_rotation']
                save_pelvis_tilt = data['pelvis_tilt']
                save_pelvis_lift = data['pelvis_lift']
                save_pelvis_sway = data['pelvis_sway']
                save_pelvis_thrust = data['pelvis_thrust']
                save_thorax_lift = data['thorax_lift']
                save_thorax_bend = data['thorax_bend']
                save_thorax_sway = data['thorax_sway']
                save_thorax_rotation = data['thorax_rotation']
                save_thorax_thrust = data['thorax_thrust']
                save_thorax_tilt = data['thorax_tilt']
                save_spine_rotation = data['spine_rotation']
                save_spine_tilt = data['spine_tilt']
                save_head_rotation = data['head_rotation']
                save_head_tilt = data['head_tilt']
                save_left_arm_length = data['left_arm_length']
                save_wrist_angle = data['wrist_angle']
                save_wrist_tilt = data['wrist_tilt']
                try:
                    save_arm_rotation = data['arm_rotation']
                    arm_x = data['arm_x']
                    arm_y = data['arm_y']
                    arm_z = data['arm_z']

                except KeyError:
                    save_arm_rotation = np.zeros(len(save_wrist_angle))
                    arm_x = np.linspace(0, 9, len(save_wrist_angle))
                    arm_y = np.linspace(0, 9, len(save_wrist_angle))
                    arm_z = np.linspace(0, 9, len(save_wrist_angle))

                try:
                    impact_ratio = data['impact_ratio'][0]
                except KeyError:
                    impact_ratio = -1

                try:
                    save_arm_to_ground = data['arm_to_ground']
                except KeyError:
                    save_arm_to_ground = np.zeros(len(save_wrist_angle))

                # Get the kinematic transition  sequence
                sequence_first, sequence_second, sequence_third, first_bp, second_bp, third_bp, arm_index = kinematic_sequence(
                    save_pelvis_rotation,
                    save_thorax_rotation,
                    save_arm_rotation, duration)

                # Get the kinematic start sequence
                sequence_first_start, sequence_second_start, sequence_third_start, first_bp_s, second_bp_s, third_bp_s, arm_index_s = kinematic_sequence_start(
                    save_pelvis_rotation, save_thorax_rotation, save_arm_rotation, duration)

                # Get the kinematic end sequence
                sequence_first_end, sequence_second_end, sequence_third_end, first_bp_e, second_bp_e, third_bp_e, arm_index_e = kinematic_sequence_end(
                    save_pelvis_rotation, save_thorax_rotation, save_arm_rotation, duration)

                # Top of backswing
                top_pos = arm_index / len(save_wrist_angle)

                # Impact
                if impact_ratio == -1:
                    impact_pos = (np.argmin(
                        filter_data(arm_z, duration * 2)[int(arm_index):] / len(
                            save_wrist_angle)) + arm_index) / len(
                        save_wrist_angle)

                else:
                    impact_pos = impact_ratio

                # End of swing
                end_pos = arm_index_e / len(save_wrist_angle)

                # Setup
                setup_pos = arm_index_s / len(save_wrist_angle)

                # Tempo
                temp, time_back, time_down = tempo(arm_index_s, arm_index, impact_pos * len(save_wrist_angle),
                                                   len(save_wrist_angle) / duration)

                fps_saved = len(save_wrist_angle) / duration

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
                    save_arm_to_ground,
                    duration)

                # Update the 3D plot
                path_fig = hand_path_3d(arm_x, arm_y, arm_z, arm_index_s, arm_index_e, arm_index, duration)

                path = dcc.Graph(figure=path_fig, config=config,
                                 className='w-[350px] lg:w-[500px] xl:w-full h-[500px] relative', )

                return [fig, fig3, fig4, fig5, fig6, fig11, fig12, fig13, fig14, fig15, fig16, children,
                        children_upload, sequence_first, sequence_second, sequence_third,
                        sequence_first_start, sequence_second_start, sequence_third_start,
                        sequence_first_end, sequence_second_end, sequence_third_end, first_bp, second_bp, third_bp,
                        first_bp_s, second_bp_s, third_bp_s, first_bp_e, second_bp_e, third_bp_e,
                        temp, time_back, time_down,
                        top_pos, impact_pos, end_pos, setup_pos, fps_saved,
                        path
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
                    save_wrist_angle, save_wrist_tilt, save_arm_rotation, save_arm_to_ground = rand(100, 20)

                arm_position = {'x': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9], 'y': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
                                'z': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]}

                duration = 10

                fps_saved = 60

                fig, fig3, fig4, fig5, fig6, fig11, fig12, fig13, fig14, fig15, fig16 = update_plots(
                    save_pelvis_rotation, save_pelvis_tilt, save_pelvis_lift, save_pelvis_sway, save_pelvis_thrust,
                    save_thorax_lift, save_thorax_bend, save_thorax_sway, save_thorax_rotation, save_thorax_thrust,
                    save_thorax_tilt, save_spine_rotation, save_spine_tilt, save_head_rotation, save_head_tilt,
                    save_left_arm_length, save_wrist_angle, save_wrist_tilt, save_arm_rotation, save_arm_to_ground,
                    duration, filt=False)

                path_fig = go.Figure(data=go.Scatter3d(x=arm_position['x'],
                                                       y=arm_position['y'],
                                                       z=arm_position['z'], mode='lines',
                                                       line=dict(color=np.linspace(0, 1, len(arm_position['x'])),
                                                                 width=6, colorscale='Viridis')))

                path_fig.update_layout(
                    scene=dict(
                        xaxis_title='Down the line',
                        yaxis_title='Front on',
                        zaxis_title='Height',
                        xaxis_showticklabels=False,
                        yaxis_showticklabels=False,
                        zaxis_showticklabels=False,
                        camera=dict(
                            up=dict(x=0, y=0, z=1),
                            center=dict(x=0, y=0, z=-0.1),
                            eye=dict(x=-2.5, y=0.1, z=0.2)
                        ),
                    ),
                    font_color="#94a3b8",
                    margin=dict(r=10, b=10, l=10, t=10),
                    paper_bgcolor='rgba(0,0,0,0)',
                )

                path = dcc.Graph(figure=path_fig, config=config,
                                 className='w-[350px] lg:w-[500px] xl:w-full h-[500px] relative', )

                # Reset sequence colors
                sequence_first = 'text-lg font-medium text-gray-100 rounded-lg py-2 px-2 flex items-center justify-center  bg-[#6266F6]',
                sequence_second = 'text-lg font-medium text-gray-100 rounded-lg py-2 px-2 flex items-center justify-center  bg-[#E74D39]'
                sequence_third = 'text-lg font-medium text-gray-100 rounded-lg py-2 px-2 flex items-center justify-center  bg-[#2BC48C]'

                # Reset sequence text
                sequence_first_text = 'Hip'
                sequence_second_text = 'Thorax'
                sequence_third_text = 'Arm'

                # Tempo
                temp, time_back, time_down = ('-', '- s', '- s')

                # Top backswing
                top_pos = 0.5

                # Impact
                impact_pos = 0.5

                # End of swing
                end_pos = 0.5

                # Setup
                setup_pos = 0.5

                children_upload = [

                    html.Div(children=[
                        html.Div(
                            children=[
                                html.Div(
                                    children=[
                                        'Upload your video',
                                        html.Div('BETA',
                                                 className='ml-4 bg-gradient-to-br from-indigo-400 to-rose-600 dark:bg-gradient-to-b dark:from-amber-300 dark:to-orange-500 rounded-full px-2 py-1 w-fit font-bold text-sm text-gray-100 dark:text-gray-600')
                                    ],
                                    className='flex flex-row text-lg font-medium text-slate-900 dark:text-gray-100 pt-4'
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
                        sequence_first, sequence_second, sequence_third,
                        sequence_first, sequence_second, sequence_third, sequence_first_text,
                        sequence_second_text, sequence_third_text, sequence_first_text, sequence_second_text,
                        sequence_third_text, sequence_first_text, sequence_second_text, sequence_third_text,
                        temp, time_back, time_down,
                        top_pos, impact_pos, end_pos, setup_pos, fps_saved,
                        path
                        ]

        # Check if folder was created and generate file name
        filename = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        create_folder(f'assets/save_data/{current_user.id}/' + filename)
        location = f'assets/save_data/{current_user.id}/' + filename

        # Send the video to the server and extract motion data
        # Send token to server to verify user
        email = current_user.email
        ts = URLSafeTimedSerializer('key')
        token = ts.dumps(email, salt='verification-key')

        response = requests.post(url_for('main.predict', token=token, _external=True, _scheme='https'),
                                 json={'contents': contents, 'filename': filename, 'location': location})
        # response = requests.post(url_for('main.predict', token=token, _external=True, _scheme='http'),  json={'contents': contents, 'filename': filename, 'location': location})

        if response.status_code == 200:
            save_pelvis_rotation, save_pelvis_tilt, save_pelvis_lift, save_pelvis_sway, save_pelvis_thrust, \
                save_thorax_lift, save_thorax_bend, save_thorax_sway, save_thorax_rotation, save_thorax_thrust, \
                save_thorax_tilt, save_spine_rotation, save_spine_tilt, save_head_rotation, save_head_tilt, save_left_arm_length, \
                save_wrist_angle, save_wrist_tilt, save_arm_rotation, save_arm_to_ground, arm_position, duration, fps, impact_ratio = response.json().values()

        else:
            if response.status_code == 413:
                message = 'Video is too long. Please upload a shorter video.'
            save_pelvis_rotation, save_pelvis_tilt, save_pelvis_lift, save_pelvis_sway, save_pelvis_thrust, \
                save_thorax_lift, save_thorax_bend, save_thorax_sway, save_thorax_rotation, save_thorax_thrust, \
                save_thorax_tilt, save_spine_rotation, save_spine_tilt, save_head_rotation, save_head_tilt, save_left_arm_length, \
                save_wrist_angle, save_wrist_tilt, save_arm_rotation, save_arm_to_ground = rand(
                100, 20)
            duration = 10
            impact_ratio = 0.5
            arm_position = {'x': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9], 'y': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
                            'z': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]}

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
                                                                                             save_arm_to_ground,
                                                                                             duration)

        # Save the motion data to a parquet file
        df = pd.DataFrame(
            [save_pelvis_rotation, save_pelvis_tilt, save_pelvis_lift, save_pelvis_sway, save_pelvis_thrust,
             save_thorax_lift, save_thorax_bend, save_thorax_sway, save_thorax_rotation, save_thorax_thrust,
             save_thorax_tilt, save_spine_rotation, save_spine_tilt, save_head_rotation, save_head_tilt,
             save_left_arm_length, save_wrist_angle, save_wrist_tilt, save_arm_rotation, save_arm_to_ground,
             arm_position['x'], arm_position['y'], arm_position['z']]).T
        df.columns = ['pelvis_rotation', 'pelvis_tilt', 'pelvis_lift', 'pelvis_sway', 'pelvis_thrust',
                      'thorax_lift', 'thorax_bend', 'thorax_sway', 'thorax_rotation', 'thorax_thrust',
                      'thorax_tilt', 'spine_rotation', 'spine_tilt', 'head_rotation', 'head_tilt', 'left_arm_length',
                      'wrist_angle', 'wrist_tilt', 'arm_rotation', 'arm_to_ground', 'arm_x', 'arm_y', 'arm_z']

        df['duration'] = duration
        df['impact_ratio'] = impact_ratio

        df.to_parquet(f'assets/save_data/{current_user.id}/{filename}/{filename}.parquet')

        # Get the kinematic transition  sequence
        sequence_first, sequence_second, sequence_third, first_bp, second_bp, third_bp, arm_index = kinematic_sequence(
            save_pelvis_rotation, save_thorax_rotation,
            save_arm_rotation, duration)

        # Get the kinematic start sequence
        sequence_first_start, sequence_second_start, sequence_third_start, first_bp_s, second_bp_s, third_bp_s, arm_index_s = kinematic_sequence_start(
            save_pelvis_rotation, save_thorax_rotation, save_arm_rotation, duration)

        # Get the kinematic end sequence
        sequence_first_end, sequence_second_end, sequence_third_end, first_bp_e, second_bp_e, third_bp_e, arm_index_e = kinematic_sequence_end(
            save_pelvis_rotation,
            save_thorax_rotation,
            save_arm_rotation,
            duration)

        # Top of backswing
        top_pos = arm_index / len(save_wrist_angle)

        # Impact
        if impact_ratio == -1:
            impact_pos = (np.argmin(
                filter_data(arm_position['z'], duration * 2)[int(arm_index):] / len(
                    save_wrist_angle)) + arm_index) / len(
                save_wrist_angle)
        else:
            impact_pos = impact_ratio

        # End of swing
        end_pos = arm_index_e / len(save_wrist_angle)

        # Setup
        setup_pos = arm_index_s / len(save_wrist_angle)

        temp, time_back, time_down = tempo(arm_index_s, arm_index, impact_pos * len(save_wrist_angle),
                                           len(save_wrist_angle) / duration)

        fps_saved = len(save_wrist_angle) / duration

        path_fig = hand_path_3d(arm_position['x'], arm_position['y'], arm_position['z'], arm_index_s, arm_index_e, arm_index, duration)

        path = dcc.Graph(figure=path_fig, config=config,
                         className='w-[350px] lg:w-[500px] xl:w-full h-[500px] relative', )

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

        # Log number of analyses
        current_user.analyzed += 1
        db.session.commit()
        return [fig, fig3, fig4, fig5, fig6, fig11, fig12, fig13, fig14, fig15, fig16, children, children_upload,
                sequence_first, sequence_second, sequence_third,
                sequence_first_start, sequence_second_start, sequence_third_start,
                sequence_first_end, sequence_second_end, sequence_third_end,
                first_bp, second_bp, third_bp, first_bp_s, second_bp_s, third_bp_s, first_bp_e, second_bp_e, third_bp_e,
                temp, time_back, time_down,
                top_pos, impact_pos, end_pos, setup_pos, fps_saved,
                path
                ]

    # Show navbar on click
    app.clientside_callback(
        ClientsideFunction(
            namespace='clientside',
            function_name='showNavbar'
        ),
        [Output('sidebar', 'className')],
        [Input('menu-button', 'n_clicks'), Input('sidebar-header', 'n_clicks')],
        State('sidebar', 'className'),
        prevent_initial_call=True
    )

    # Help box on click
    app.clientside_callback(
        '''
        function(n_clicks, help_class) {
            if (n_clicks % 2 == 1) {
                return help_class.replace('hidden', 'flex');
            } else {
                return help_class.replace('flex', 'hidden');
            }
        }
        ''',
        Output({'type': 'help_box', 'index': MATCH}, 'className'),
        [Input({'type': 'info_button', 'index': MATCH}, 'n_clicks'),
         Input({'type': 'help_box', 'index': MATCH}, 'className')],
        prevent_initial_call=True
    )

    # Jump to position in video on click
    app.clientside_callback(
        ClientsideFunction(
            namespace='clientside',
            function_name='positionUpdate'
        ),

        Output('video', 'seekTo'),
        [Input('top_pos_button', 'n_clicks'), Input('impact_pos_button', 'n_clicks'),
         Input('end_pos_button', 'n_clicks'), Input('setup_pos_button', 'n_clicks'),
         Input('minus_frame', 'n_clicks'), Input('plus_frame', 'n_clicks'),
         Input('minus_frame_mobile', 'n_clicks'), Input('plus_frame_mobile', 'n_clicks'),
         ],
        [State('video', 'currentTime'), State('video', 'duration')],
        prevent_initial_call=True
    )

    # Vertical moving line synced with video
    app.clientside_callback(
        ClientsideFunction(
            namespace='clientside',
            function_name='drawVerticalLine'
        ),

        # Output('sequence', 'figure'),
        Input('video', 'currentTime'),
        State('sequence', 'figure'), State('pelvis_rotation', 'figure'), State('pelvis_displacement', 'figure'),
        State('thorax_rotation', 'figure'), State('thorax_displacement', 'figure'), State('s_tilt', 'figure'),
        State('h_tilt', 'figure'), State('h_rotation', 'figure'), State('arm_length', 'figure'),
        State('spine_rotation', 'figure'),
        prevent_initial_call=True
    )

    # Value divs when video is playing
    app.clientside_callback(
        ClientsideFunction(
            namespace='clientside',
            function_name='updateValues'
        ),

        # Output('sequence', 'figure'),
        [Output('pelvis_rot_val', 'children'), Output('pelvis_bend_val', 'children'),
         Output('thorax_rot_val', 'children'), Output('thorax_bend_val', 'children'),
         Output('head_rot_val', 'children'), Output('head_tilt_val', 'children'),
         Output('arm_rot_val', 'children'), Output('arm_ground_val', 'children'),
         ],
        [Input('video', 'currentTime'), Input('video', 'duration')],
        State('sequence', 'figure'), State('pelvis_rotation', 'figure'), State('pelvis_displacement', 'figure'),
        State('thorax_rotation', 'figure'), State('thorax_displacement', 'figure'), State('s_tilt', 'figure'),
        State('h_tilt', 'figure'), State('h_rotation', 'figure'), State('arm_length', 'figure'),
        State('spine_rotation', 'figure'), State('arm_angle', 'figure'),
        State('impact_pos_button', 'n_clicks_timestamp'), State('top_pos_button', 'n_clicks_timestamp'),
        State('end_pos_button', 'n_clicks_timestamp'), State('setup_pos_button', 'n_clicks_timestamp'),
        prevent_initial_call=True
    )


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
        save_wrist_angle, save_wrist_tilt, save_arm_rotation, save_arm_to_ground = rand(100, 20)

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
                                                                                         save_arm_to_ground,
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

    return [fig, fig3, fig4, fig5, fig6, fig11, fig12, fig13, fig14, fig15, fig16, children, children_upload, []]


def kinematic_sequence(pelvis_rotation, thorax_rotation, arm_rotation, duration):
    # Get the kinematic transition sequence
    hip_index = find_closest_zero_intersection_left_of_max(
        np.gradient(filter_data(pelvis_rotation, duration)))
    thorax_index = find_closest_zero_intersection_left_of_max(
        np.gradient(filter_data(thorax_rotation, duration)))
    arm_index = find_closest_zero_intersection_left_of_max(
        -np.gradient(filter_data(arm_rotation, duration)))

    # print(hip_index, thorax_index, arm_index)

    # Colors for hip, thorax and arm
    sequence = {'bg-[#6266F6]': hip_index, 'bg-[#E74D39]': thorax_index, 'bg-[#2BC48C]': arm_index}

    # Colors sorted by index
    sequence = sorted(sequence.items(), key=lambda item: item[1])

    # Body parrt sorted by index
    body_part = {'Pelvis': hip_index, 'Thorax': thorax_index, 'Arm': arm_index}
    body_part = sorted(body_part.items(), key=lambda item: item[1])

    # Update colors
    sequence_first = f'text-lg font-medium text-gray-100 rounded-lg py-2 px-2 flex items-center justify-center {sequence[0][0]}'
    sequence_second = f'text-lg font-medium text-gray-100 rounded-lg py-2 px-2 flex items-center justify-center {sequence[1][0]}'
    sequence_third = f'text-lg font-medium text-gray-100 rounded-lg py-2 px-2 flex items-center justify-center {sequence[2][0]}'

    return sequence_first, sequence_second, sequence_third, body_part[0][0], body_part[1][0], body_part[2][
        0], thorax_index


def kinematic_sequence_start(pelvis_rotation, thorax_rotation, arm_rotation, duration):
    # Get the kinematic start sequence
    argmax = np.argmax(arm_rotation)
    hip_index = find_closest_zero_intersection_left_of_min(
        np.gradient(filter_data(pelvis_rotation[:argmax], duration)))
    thorax_index = find_closest_zero_intersection_left_of_min(
        np.gradient(filter_data(thorax_rotation[:argmax], duration)))
    arm_index = find_closest_zero_intersection_left_of_min(
        np.gradient(filter_data(arm_rotation[:argmax], duration)))

    # Colors for hip, thorax and arm
    sequence = {'bg-[#6266F6]': hip_index, 'bg-[#E74D39]': thorax_index, 'bg-[#2BC48C]': arm_index}

    # Colors sorted by index
    sequence = sorted(sequence.items(), key=lambda item: item[1])

    # Body parrt sorted by index
    body_part = {'Pelvis': hip_index, 'Thorax': thorax_index, 'Arm': arm_index}
    body_part = sorted(body_part.items(), key=lambda item: item[1])

    # Update colors
    sequence_first = f'text-lg font-medium text-gray-100 rounded-lg py-2 px-2 flex items-center justify-center {sequence[0][0]}'
    sequence_second = f'text-lg font-medium text-gray-100 rounded-lg py-2 px-2 flex items-center justify-center {sequence[1][0]}'
    sequence_third = f'text-lg font-medium text-gray-100 rounded-lg py-2 px-2 flex items-center justify-center {sequence[2][0]}'

    return sequence_first, sequence_second, sequence_third, body_part[0][0], body_part[1][0], body_part[2][
        0], thorax_index


def kinematic_sequence_end(pelvis_rotation, thorax_rotation, arm_rotation, duration):
    # Get the kinematic end sequence
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

    # Body parrt sorted by index
    body_part = {'Pelvis': hip_index, 'Thorax': thorax_index, 'Arm': arm_index}
    body_part = sorted(body_part.items(), key=lambda item: item[1])

    # Update colors
    sequence_first = f'text-lg font-medium text-gray-100 rounded-lg py-2 px-2 flex items-center justify-center {sequence[0][0]}'
    sequence_second = f'text-lg font-medium text-gray-100 rounded-lg py-2 px-2 flex items-center justify-center {sequence[1][0]}'
    sequence_third = f'text-lg font-medium text-gray-100 rounded-lg py-2 px-2 flex items-center justify-center {sequence[2][0]}'

    return sequence_first, sequence_second, sequence_third, body_part[0][0], body_part[1][0], body_part[2][
        0], thorax_index


def tempo(start, back, end, fps):
    # Get the tempo of the swing
    time_back = (back - start) / fps
    time_down = (end - back) / fps
    temp = time_back / time_down
    temp = f'{round(temp, 2)}'

    time_back = f'{round(time_back, 2)} s'
    time_down = f'{round(time_down, 2)} s'

    return temp, time_back, time_down


def velocity(path):
    # Get the velocity of the path
    # print(np.shape(path))
    velocity = np.gradient(path, axis=1)
    # print(np.shape(velocity))
    speed = np.sqrt(velocity[0] ** 2 + velocity[1] ** 2 + velocity[2] ** 2)
    # print(np.shape(speed))

    return speed


def info_text(plot_type):
    # Get the info text for the plot
    match plot_type:
        case 'arm_path':
            text = '''
                        The 3D line shows the trace of the hands while the color of the line represents the beginning and end of the swing.
                        This visualization can help you to understand the movement of your arms and hands. For example you can see how steep or shallow your backswing is and in which direction you transition on the downswing.
                        Front on is the view facing the player. Down the line is the view in direction of the target.
            '''
            title = '3D Hand Path'

        case 'transition_sequence':
            text = '''
                            The transition sequence shows the order of the body parts that initiate the downswing. The color of the circle represents the body part and the order of the circles represents the order of the body parts.
                '''
            title = 'Transition Sequence'

        case 'start_sequence':
            text = '''
                            The start sequence shows the order of the body parts that initiate the backswing. The color of the circle represents the body part and the order of the circles represents the order of the body parts.
                '''
            title = 'Start Sequence'

        case 'finish_sequence':
            text = '''
                            The finish sequence shows the order of the body parts that finish the swing. The color of the circle represents the body part and the order of the circles represents the order of the body parts.
                '''
            title = 'Stabilization Sequence'

        case 'pelvis_rotation':
            text = '''
                            The pelvis rotation shows the rotation of the pelvis around the x-axis. The rotation is measured in degrees and the color of the line represents the beginning and end of the swing.
                '''
            title = 'Pelvis Rotation'

        case 'angular_velocity':
            text = '''
                            The angular velocity shows the angular velocity of the pelvis around the x-axis. The angular velocity is measured in degrees per second and the color of the line represents the beginning and end of the swing.
                '''

            title = 'Angular Velocity'

        case 'pelvis_displacement':
            text = '''
                            The pelvis displacement shows the displacement of the pelvis in the x-direction. The displacement is measured in meters and the color of the line represents the beginning and end of the swing.
                '''

            title = 'Pelvis Displacement'

        case 'thorax_angles':
            text = '''
                            The thorax rotation shows the rotation of the thorax around the x-axis. The rotation is measured in degrees and the color of the line represents the beginning and end of the swing.
                '''

            title = 'Thorax Angles'

        case 'thorax_displacement':
            text = '''
                            The thorax displacement shows the displacement of the thorax in the x-direction. The displacement is measured in meters and the color of the line represents the beginning and end of the swing.
                '''

            title = 'Thorax Displacement'

        case 'head_tilt':
            text = '''
                            The head tilt shows the tilt of the head around the y-axis. The tilt is measured in degrees and the color of the line represents the beginning and end of the swing.
                '''

            title = 'Head Tilt'

        case 'head_rotation':
            text = '''
                            The head rotation shows the rotation of the head around the z-axis. The rotation is measured in degrees and the color of the line represents the beginning and end of the swing.
                '''

            title = 'Head Rotation'

        case 'spine_rotation':
            text = '''
                            The spine rotation shows the rotation of the spine around the x-axis. The rotation is measured in degrees and the color of the line represents the beginning and end of the swing.
                '''

            title = 'Spine Rotation'

        case 'spine_tilt':
            text = '''
                            The spine tilt shows the tilt of the spine around the y-axis. The tilt is measured in degrees and the color of the line represents the beginning and end of the swing.
                '''

            title = 'Spine Tilt'

        case 'left_arm':
            text = '''
                            The left arm shows the rotation of the left arm around the x-axis. The rotation is measured in degrees and the color of the line represents the beginning and end of the swing.
                '''

            title = 'Left Arm Length'

        case 'backswing':

            text = 'Duration of the backswing in seconds'
            title = 'Backswing'

        case 'downswing':

            text = 'Duration of the downswing in seconds'
            title = 'Downswing'

        case _:  # default
            text = ''
            title = ''

    layout = [
        html.Div(
            className='flex flex-row w-full justify-start',
            children=[
                html.Button(
                    # id=f'{plot_type}_title',
                    id={'type': 'info_button', 'index': plot_type},
                    className='text-lg font-medium text-slate-900 hover:text-gray-600 dark:text-gray-100 dark:hover:text-gray-300 mt-10 mx-4 sm:mx-10 relative text-left',
                    children=[
                        title
                    ]
                ),
            ]
        ),
        html.Div(
            # id=f'{plot_type}_help',
            id={'type': 'help_box', 'index': plot_type},
            className='absolute top-20 right-3 left-4 sm:left-10 sm:w-96 bg-gray-300 rounded-2xl backdrop-blur-md bg-opacity-80 hidden z-10',
            children=[
                html.Div(
                    className='flex flex-row px-4 py-4 text-sm text-gray-900',
                    children=[text]
                )
            ]
        ),
    ]

    return layout


def content_box():
    return html.Div(
        [
            html.Div(
                className="bg-slate-200 w-28 h-8 rounded-lg left-4 top-8 absolute animate-pulse"
            ),
            html.Div(
                className="bg-slate-200 rounded-lg top-24 left-4 right-4 bottom-10 animate-pulse absolute"
            ),
        ],
        className="relative h-[500px] bg-white dark:bg-gray-700 shadow rounded-2xl flex items-center justify-center mb-5 backdrop-blur-md bg-opacity-80 border border-gray-100 dark:border-gray-900 flex-col w-full",
    ),


loader = html.Div(
    children=[
        # Sidebar
        html.Div(
            [
                html.Div(
                    className="bg-slate-200 dark:bg-slate-500 w-28 h-4 rounded-lg ml-4 mt-4 animate-pulse mb-4"
                ),
                html.Div(
                    [html.Div(className="bg-slate-200 dark:bg-slate-500 h-10 rounded-lg mx-4 mt-2 animate-pulse") for _
                     in range(5)],
                    className="relative overflow-hidden",
                ),
                html.Div(
                    [html.Div(className="bg-orange-200 dark:bg-orange-300 h-8 rounded-lg mt-2 animate-pulse") for _ in
                     range(4)],
                    className="absolute bottom-4 left-4 right-4 bg-slate-600 dark:bg-gray-700",
                ),
            ],
            className="flex flex-col bg-slate-600 dark:bg-gray-700 fixed lg:left-5 top-5 bottom-5 w-60 z-10 rounded-2xl hidden lg:flex",
        ),

        # Content
        html.Div(
            [

                html.Div(
                    className='flex sm:flex-row flex-col w-full',
                    children=[
                        # Upload loader
                        html.Div(
                            [
                                html.Div(
                                    className="bg-slate-200 dark:bg-slate-500 w-28 h-8 rounded-lg left-4 sm:top-8 top-3 absolute animate-pulse"
                                ),
                                html.Div(
                                    className="bg-slate-200 dark:bg-slate-500 rounded-lg sm:top-24 top-12 left-4 right-4 sm:bottom-10 bottom-4 animate-pulse absolute flex-col items-center justify-center",
                                    children=[
                                        html.Div(
                                            className='dark:text-gray-100 text-gray-800 md:text-xl sm:text-md text-sm font-medium text-left flex flex flex-col animate-none justify-center items-center flex-col w-full h-full',
                                            children=[
                                                html.Div(
                                                    id='quote',
                                                    className='animate-none',
                                                    children=[
                                                        html.Div('No matter how good you get',
                                                                 className='animate-none'),
                                                        html.Div('you can always get better', className='animate-none'),
                                                        html.Div('and that\'s the exciting part.',
                                                                 className='animate-none'),
                                                        html.Div('— Tiger Woods',
                                                                 className='font-normal text-xs sm:text-sm'),
                                                        html.Div('Extracting motion data...',
                                                                 className='animate-none text-gray-800 text-xs font-medium mt-1 sm:mt-4'),
                                                    ])
                                            ]
                                        ),
                                    ]
                                ),
                            ],
                            className="relative bg-white dark:bg-gray-700 shadow rounded-2xl flex items-center justify-center mb-5 backdrop-blur-md bg-opacity-80 border border-gray-100 dark:border-gray-900 flex-col w-full h-44 sm:h-96 sm:mt-0 mt-12",
                        ),

                        # Video loader
                        html.Div(
                            className="bg-slate-400 sm:w-96 h-96 rounded-2xl sm:ml-4 relative mb-5",
                            children=[
                                # Play button
                                html.Div(
                                    className='bg-gray-600 w-14 h-14 rounded-full absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 animate-pulse',
                                )
                            ]
                        )

                    ]
                ),

                html.Div(
                    [
                        html.Div(
                            className="bg-slate-200 dark:bg-slate-500 w-28 h-8 rounded-lg left-4 top-8 absolute animate-pulse"
                        ),
                        html.Div(
                            className="bg-slate-200 dark:bg-slate-500 rounded-lg top-24 left-4 right-4 bottom-10 animate-pulse absolute"
                        ),
                    ],
                    className="relative h-[570px] bg-white dark:bg-gray-700 shadow rounded-2xl flex items-center justify-center mb-5 backdrop-blur-md bg-opacity-80 border border-gray-100 dark:border-gray-900 flex-col w-full",
                ),

                html.Div(
                    [
                        html.Div(
                            className="bg-slate-200 dark:bg-slate-500 w-28 h-8 rounded-lg left-4 top-8 absolute animate-pulse"
                        ),
                        html.Div(
                            className="bg-slate-200 dark:bg-slate-500 rounded-lg top-24 left-4 right-4 bottom-10 animate-pulse absolute"
                        ),
                    ],
                    className="relative h-[750px] bg-white dark:bg-gray-700 shadow rounded-2xl flex items-center justify-center mb-5 backdrop-blur-md bg-opacity-80 border border-gray-100 dark:border-gray-900 flex-col w-full",
                ),

                html.Div(
                    children=[html.Div(
                        [
                            html.Div(
                                className="bg-slate-200 dark:bg-slate-500 w-28 h-8 rounded-lg left-4 top-8 absolute animate-pulse"
                            ),
                            html.Div(
                                className="bg-slate-200 dark:bg-slate-500 rounded-lg top-24 left-4 right-4 bottom-10 animate-pulse absolute"
                            ),
                        ],
                        className="relative h-[570px] bg-white dark:bg-gray-700 shadow rounded-2xl flex items-center justify-center mb-5 backdrop-blur-md bg-opacity-80 border border-gray-100 dark:border-gray-900 flex-col w-full",
                    ) for _ in range(10)],
                )

            ],

            className="lg:mx-16 mx-4 lg:pl-60 mt-5 relative",
        )

    ]
)

if __name__ == '__main__':
    pass
