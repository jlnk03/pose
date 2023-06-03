import base64
import datetime
import os
import shutil
import sys
import tempfile
import urllib

import dash_player as dp
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
import replicate
from dash import ctx, ALL, html, dcc, MATCH, ClientsideFunction, no_update
from dash_extensions.enrich import Output, Input, State, NoOutputTransform, DashProxy
from flask_login import current_user
from scipy import signal

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from code_b.angles_2 import calculate_angles
from flask_wrapper import db
# from flask_wrapper.celery_app import celery_app
from flask_wrapper.loading_view import loader
from flask_wrapper.models import UserLikes
from flask_wrapper.overlay_view import overlay

# background_callback_manager = CeleryManager(celery_app)
# background_callback_manager = CeleryLongCallbackManager(celery_app)

# Set theme for dash
pio.templates.default = "plotly_white"

# Hide plotly logo
config = dict({'displaylogo': False, 'displayModeBar': False, 'scrollZoom': False})
config_3D = dict(
    {'displaylogo': False, 'displayModeBar': True, 'scrollZoom': False,
     'modeBarButtonsToRemove': ['zoom', 'pan', 'resetCameraDefault3d', 'orbitRotation', 'tableRotation', 'toImage']})


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


def over_the_top(hand_path_x, hand_path_z, setup, top, impact):
    hand_path_x = np.array(hand_path_x)
    hand_path_z = np.array(hand_path_z)
    back_z = hand_path_z[setup:top]
    down_z = hand_path_z[top:impact]
    half_height = 2 / 3 * (back_z[-1] - back_z[0]) + back_z[0]
    diff_back = np.abs(back_z - half_height)
    diff_down = np.abs(down_z - half_height)
    nearest = np.argmin(diff_back)
    nearest_down = np.argmin(diff_down)
    back_x = hand_path_x[setup:top][nearest]
    down_x = hand_path_x[top:impact][nearest_down]

    if back_x > down_x:
        return True

    return False


def add_vertical_line(fig):
    fig.add_vline(x=0, line_width=4, line_color="#818cf8")


# Return the video view
def upload_video(disabled=True, path=None):
    if path is not None:
        path += '#t=0.001'

    layout = [
        html.Div(
            id='video-view',
            className='flex flex-col sm:flex-row w-full h-full',
            children=[

                html.Button(
                    'Report',
                    id='show_overlay_mobile',
                    className='sm:hidden absolute -top-14 left-1/2 -translate-x-1/2 px-4 py-1 rounded-full bg-indigo-500 shadow-sm shadow-indigo-400 dark:shadow-slate-950 text-white font-bold text-xs disable-dbl-tap-zoom'
                ),

                html.Div(
                    className='flex flex-col-reverse sm:flex-row w-full h-full',
                    # Controls for the video player (top, impact, end)
                    children=[html.Div(
                        children=[
                            html.Div(
                                children=[
                                    html.Div(
                                        className='flex-row sm:flex flex-col flex-nowrap items-center sm:border-b max-sm:border-r border-gray-300 gap-2 sm:pb-2 pr-2 sm:pr-0 justify-between',
                                        children=[
                                            html.Button('Setup', id='setup_pos_button',
                                                        className='sm:w-24 px-4 py-2 rounded-full  bg-transparent hover:bg-indigo-600 hover:shadow-sm dark:hover:shadow-slate-800 hover:shadow-indigo-400 text-gray-400 hover:text-white font-bold text-xs'),
                                            html.Button('Top', id='top_pos_button',
                                                        className='sm:w-24 px-4 py-2 rounded-full bg-transparent hover:bg-indigo-600 hover:shadow-sm dark:hover:shadow-slate-800 hover:shadow-indigo-400 text-gray-400 hover:text-white font-bold text-xs'),
                                            html.Button('Impact', id='impact_pos_button',
                                                        className='sm:w-24 px-4 py-2 rounded-full bg-transparent hover:bg-indigo-600 hover:shadow-sm dark:hover:shadow-slate-800 hover:shadow-indigo-400 text-gray-400 hover:text-white font-bold text-xs'),
                                            html.Button('Finish', id='end_pos_button',
                                                        className='sm:w-24 px-4 py-2 rounded-full bg-transparent hover:bg-indigo-600 hover:shadow-sm dark:hover:shadow-slate-800 hover:shadow-indigo-400 text-gray-400 hover:text-white font-bold text-xs'),
                                        ]
                                    ),
                                    # Edit button
                                    html.Button('Edit', id='edit_positions',
                                                disabled=True,
                                                className='grow sm:w-24 px-4 py-2 rounded-full bg-indigo-300 dark:bg-indigo-800 text-white dark:text-gray-400 font-bold text-xs'),

                                    # Save new positions
                                    html.Div(
                                        id='edit_positions_div',
                                        className='absolute sm:bottom-0 sm:-right-24 bottom-16 right-0 z-20 flex flex-col gap-2 bg-indigo-100 dark:bg-indigo-900 rounded-3xl px-2 py-2 hidden',
                                        children=[
                                            html.Button('Reset', id='edit_positions_reset',
                                                        className='text-base py-2 px-4 rounded-full bg-indigo-500 hover:bg-indigo-600 hover:shadow-md dark:hover:shadow-slate-800 hover:shadow-indigo-400 text-white font-bold text-xs'),
                                            html.Button('Save', id='edit_positions_save',
                                                        className='text-base py-2 px-4 rounded-full bg-indigo-500 hover:bg-indigo-600 hover:shadow-md dark:hover:shadow-slate-800 hover:shadow-indigo-400 text-white font-bold text-xs'),
                                        ]
                                    ),
                                ],
                                className='relative flex flex-row sm:flex-col flex-nowrap sm:items-end sm:justify-center justify-between sm:mr-5 mt-2 sm:mt-0 gap-2 bg-indigo-100 dark:bg-indigo-900 shadow-sm shadow-indigo-200 dark:shadow-slate-950 rounded-full sm:rounded-3xl px-2 py-2'
                            ),

                            html.Div(
                                children=[
                                    html.Button('Frame +', id='plus_frame',
                                                className='w-24 px-4 py-2 rounded-full bg-indigo-500 hover:bg-indigo-600 hover:shadow-sm dark:hover:shadow-slate-800 hover:shadow-indigo-400 text-white font-bold text-xs hidden sm:block disable-dbl-tap-zoom'),
                                    html.Button('Frame -', id='minus_frame',
                                                className='w-24 px-4 py-2 rounded-full bg-indigo-500 hover:bg-indigo-600 hover:shadow-sm dark:hover:shadow-slate-800 hover:shadow-indigo-400 text-white font-bold text-xs hidden sm:block disable-dbl-tap-zoom'),
                                ],
                                className='hidden sm:flex flex-col sm:items-end sm:justify-center justify-between sm:mr-5 mt-2 sm:mt-0 gap-2 bg-indigo-100 dark:bg-indigo-900 shadow-sm shadow-indigo-200 dark:shadow-slate-950 rounded-full sm:rounded-3xl px-2 py-2 '
                            ),

                            html.Div(
                                html.Button(
                                    'Report',
                                    id='show_overlay',
                                    className='w-24 px-4 py-2 rounded-full bg-indigo-500 hover:bg-indigo-600 hover:shadow-sm dark:hover:shadow-slate-800 hover:shadow-indigo-400 text-white font-bold text-xs hidden sm:block disable-dbl-tap-zoom'
                                ),
                                className='mb-5 hidden sm:flex flex-col sm:items-end sm:justify-center justify-between sm:mr-5 mt-2 sm:mt-0 bg-indigo-100 dark:bg-indigo-900 shadow-sm shadow-indigo-200 dark:shadow-slate-950 rounded-full sm:rounded-3xl px-2 py-2 '

                            ),

                        ],
                        className='flex flex-col justify-between'
                    ),

                        # Video player
                        html.Div(
                            className="relative overflow-hidden sm:h-[29.5rem] h-96 w-full flex shadow rounded-2xl xl:mr-5 sm:mb-2 bg-white dark:bg-gray-700 dark:shadow-slate-950 dark:shadow-sm backdrop-blur-md bg-opacity-80 border border-gray-100 dark:border-gray-900",
                            children=[
                                # html.Video(src=f'{path}#t=0.001', id='video', controls=True,
                                #            className="h-full w-full object-cover"),

                                html.Button(id='heart', className='heart absolute top-4 left-4'),

                                # TODO: video

                                dp.DashPlayer(
                                    id='video',
                                    url=path,
                                    controls=True,
                                    playsinline=True,
                                    className="h-full w-full flex",
                                    width='100%',
                                    height='100%',
                                    intervalCurrentTime=70,
                                ),

                                # html.Div(
                                #     id='edit_positions_div',
                                #     className='absolute bottom-12 right-4 flex flex-col gap-2 bg-indigo-100 dark:bg-indigo-900 rounded-3xl px-2 py-2 hidden',
                                #     children=[
                                #         html.Button('Reset', id='edit_positions_reset',
                                #                     className='text-base py-2 px-4 rounded-full bg-indigo-500 hover:bg-indigo-600 hover:shadow-md dark:hover:shadow-slate-800 hover:shadow-indigo-400 text-white font-bold text-sm'),
                                #         html.Button('Save', id='edit_positions_save',
                                #                     className='text-base py-2 px-4 rounded-full bg-indigo-500 hover:bg-indigo-600 hover:shadow-md dark:hover:shadow-slate-800 hover:shadow-indigo-400 text-white font-bold text-sm'),
                                #     ]
                                # ),

                                # html.Button('⚙️', id='edit_positions',
                                #             className='text-base absolute bottom-4 right-4 hidden'),
                            ]
                        ), ]
                ),

                # Controls for the video player mobile (+, -)
                html.Div(
                    children=[
                        html.Button('Frame -', id='minus_frame_mobile',
                                    className='w-full h-fit px-4 py-2 rounded-full bg-indigo-500 text-white font-bold text-xs disable-dbl-tap-zoom sm:hidden'),
                        html.Button('Frame +', id='plus_frame_mobile',
                                    className='w-full h-fit px-4 py-2 rounded-full bg-indigo-500 text-white font-bold text-xs disable-dbl-tap-zoom sm:hidden'),
                    ],
                    className='flex flex-row justify-between mb-2 mt-2 gap-2 bg-indigo-100 dark:bg-indigo-900 shadow-sm shadow-indigo-200 dark:shadow-none rounded-full px-2 py-2 sm:hidden'
                ),
            ]),
    ]

    return layout


def slider_view(name, min_bound, max_bound, suffix='°'):
    layout = [
        html.Div(
            html.Div(
                className='absolute h-1.5 bottom-3 left-0 right-0 rounded-full',  # bg-red-600
                children=[
                    html.Div(
                        id=f'green_bar_{name}',
                        style=dict(
                            left='0%',
                            right='0%',
                        ),
                        # className='absolute h-2 bg-green-600 rounded-full'),
                        className='absolute h-1.5 gradient-slider-custom rounded-full'),
                    # Slider
                    html.Div(
                        id=f'slider_{name}',
                        style=dict(
                            left='50%',
                        ),
                        className='relative h-4 w-1 -translate-x-1/2 -translate-y-[5px] bg-gray-900 dark:bg-gray-100 rounded-full',
                    ),
                    html.Div(
                        f'{min_bound}{suffix}',
                        className='absolute left-0 bottom-3.5 text-xs text-gray-400',
                    ),
                    html.Div(
                        f'{max_bound}{suffix}',
                        className='absolute right-0 bottom-3.5 text-xs text-gray-400',
                    )
                ]
            ),
            className='absolute bottom-0 left-3 right-3 h-full overflow-x-hidden'
        )
    ]

    return layout


def gradient_slider_view(id, min, max):
    center = (max - min) / 2
    layout = [html.Div(
        id=f'{id}_gradient',
        children=[
            html.Div(
                style={'left': '50%'},
                id=id,
                className='rounded-full h-3 w-3 bg-slate-900 dark:bg-gray-100 border-2 border-white dark:border-gray-700 absolute -translate-x-1/2 top-1/2 transform -translate-y-1/2',
            ),
            html.Div(
                min,
                className='absolute left-0 bottom-3.5 text-xs text-gray-400',
            ),
            html.Div(
                center,
                className='absolute left-1/2 -translate-x-1/2 bottom-3.5 text-xs text-gray-400',
            ),
            html.Div(
                max,
                className='absolute right-0 bottom-3.5 text-xs text-gray-400',
            )
        ],
        className='absolute left-0 right-6 top-0 h-2 gradient-slider rounded-full'
    )]

    return layout


def hand_path_3d(x, y, z, start, end, top, fps):
    start = int(start)
    end = int(end)
    top = int(top)

    x = filter_data(x, fps)
    y = filter_data(y, fps)
    z = filter_data(z, fps)

    path_fig = go.Figure(
        data=go.Scatter3d(x=x[start:end],
                          y=y[start:end],
                          z=z[start:end],
                          mode='lines',
                          line=dict(color=np.linspace(0, 1, len(x))[start:end], width=6, colorscale='Viridis'),
                          name='Hand Path',
                          ),
    )

    start_point = [x[start], z[start]]
    end_point = [x[top], z[top]]
    # print(start_point, end_point)

    slope = (end_point[1] - start_point[1]) / (end_point[0] - start_point[0])
    angle = np.arctan(slope) * 180 / np.pi

    zero_intersect = start_point[1] - slope * start_point[0]

    plane_x = np.linspace(x[start], x[top], 10)
    plane_y = np.linspace(min(y), max(y), 10)
    plane_x, plane_y = np.meshgrid(plane_x, plane_y)
    plane_z = slope * plane_x + zero_intersect

    plane = go.Surface(x=plane_x, y=plane_y, z=plane_z, showscale=False, opacity=0.5, name='Swing Plane', )

    path_fig.add_trace(plane)

    path_fig.update_layout(
        scene=dict(
            xaxis_title='Down the line',
            yaxis_title='Face on',
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
        # showlegend=True,
        hovermode=False,
        modebar=dict(
            bgcolor='rgba(0,0,0,0)',
            color='#94a3b8',
            activecolor='#94a3b9',
        )
    )

    return path_fig, angle


def heart_navbar(file):
    like_row = UserLikes.query.filter_by(user_id=current_user.id, video_id=file).first()
    if like_row is not None:
        if like_row.like:
            return html.Div(className='-ml-4 -my-1 heart is-active', id=f'heart_{file}')

    return html.Div(className='-ml-4 -my-1 heart', id=f'heart_{file}')


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


def filter_data(data, fps):
    Wn = 4
    b, a = signal.butter(4, Wn, 'low', fs=fps)
    data = signal.filtfilt(b, a, data, method='gust')
    return data


# @memory_profiler.profile
def update_plots(save_pelvis_rotation, save_pelvis_tilt, save_pelvis_lift, save_pelvis_sway, save_pelvis_thrust,
                 save_thorax_lift, save_thorax_bend, save_thorax_sway, save_thorax_rotation, save_thorax_thrust,
                 save_thorax_tilt, save_spine_rotation, save_spine_tilt, save_head_rotation, save_head_tilt,
                 save_left_arm_length, save_wrist_angle, save_wrist_tilt, save_arm_rotation, save_arm_to_ground,
                 duration, fps=1,
                 filt=True):
    if filt:
        converted = [filter_data(np.array(name), fps) for name in
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
            y=np.gradient(save_arm_rotation, 1 / fps),
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
# path_fig = go.Figure(
#     data=go.Scatter3d(x=arm_position['x'], y=arm_position['y'],
#                       z=arm_position['z'], mode='lines',
#                       line=dict(color=arm_position['y'], width=6, colorscale='Viridis')))
#
# path_fig.update_layout(
#     scene=dict(
#         xaxis_title='Down the line',
#         # yaxis_title='Front on',
#         zaxis_title='Height',
#         xaxis_showticklabels=False,
#         yaxis_showticklabels=False,
#         zaxis_showticklabels=False,
#         camera=dict(
#             up=dict(x=0, y=0, z=1),
#             center=dict(x=0, y=0, z=-0.1),
#             eye=dict(x=-2.5, y=0.1, z=0.2)
#         ),
#     ),
#     font_color="#94a3b8",
#     margin=dict(r=10, b=10, l=10, t=10),
#     paper_bgcolor='rgba(0,0,0,0)',
# )
#
# fig = go.Figure(data=go.Scatter(x=timeline, y=save_pelvis_rotation, name=f'Pelvis'))
#
# fig.add_trace(
#     go.Scatter(
#         x=timeline,
#         y=save_thorax_rotation,
#         name=f'Thorax',
#         # legendrank=seq_sorted['Shoulder']
#     )
# )
#
# fig.add_trace(
#     go.Scatter(
#         x=timeline,
#         y=np.gradient(save_arm_rotation),
#         name=f'Arm',
#     )
# )
#
# add_vertical_line(fig)
#
# fig.update_layout(
#     # title='Angular velocity',
#     title_x=0.5,
#     font_size=12,
#     # yaxis_title="Angular velocity in °/s",
#     # xaxis_title="time in s",
#     yaxis_ticksuffix="°/s",
#     paper_bgcolor='rgba(0,0,0,0)',
#     plot_bgcolor='rgba(0,0,0,0)',
#     legend_orientation="h",
#     legend=dict(y=1, yanchor="bottom"),
#     margin=dict(
#         l=10,
#         r=10,
#         t=20,
#         pad=5
#     ),
#     modebar=dict(
#         bgcolor='rgba(0,0,0,0)',
#         color='rgba(1,1,1,0.3)',
#         activecolor='rgba(58, 73, 99, 1)'
#     )
# ),
#
# fig3 = go.Figure(data=go.Scatter(x=timeline, y=save_pelvis_tilt, name=f'Pelvis side bend'))
#
# fig3.add_trace(
#     go.Scatter(x=timeline, y=save_pelvis_rotation, name=f'Pelvis rotation')
# )
#
# add_vertical_line(fig3)
#
# fig3.update_layout(
#     # title='Pelvis angles',
#     title_x=0.5,
#     font_size=12,
#     # yaxis_title='angle in °',
#     # xaxis_title="time in s",
#     yaxis_ticksuffix="°",
#     paper_bgcolor='rgba(0,0,0,0)',
#     plot_bgcolor='rgba(0,0,0,0)',
#     legend_orientation="h",
#     legend=dict(y=1, yanchor="bottom"),
#     margin=dict(
#         l=10,
#         r=10,
#         t=20,
#         pad=5
#     ),
#     modebar=dict(
#         bgcolor='rgba(0,0,0,0)',
#         color='rgba(1,1,1,0.3)',
#         activecolor='rgba(58, 73, 99, 1)'
#     )
# )
#
# fig4 = go.Figure(data=go.Scatter(x=timeline, y=save_pelvis_lift, name=f'Pelvis lift'))
#
# fig4.add_trace(
#     go.Scatter(x=timeline, y=save_pelvis_sway, name=f'Pelvis sway')
# )
#
# fig4.add_trace(
#     go.Scatter(x=timeline, y=save_pelvis_thrust, name=f'Pelvis thrust')
# )
#
# add_vertical_line(fig4)
#
# fig4.update_layout(
#     # title='Pelvis displacement',
#     title_x=0.5,
#     font_size=12,
#     # yaxis_title='Displacement in m',
#     # xaxis_title="time in s",
#     yaxis_ticksuffix="m",
#     paper_bgcolor='rgba(0,0,0,0)',
#     plot_bgcolor='rgba(0,0,0,0)',
#     legend_orientation="h",
#     legend=dict(y=1, yanchor="bottom"),
#     margin=dict(
#         l=10,
#         r=10,
#         t=20,
#         pad=5
#     ),
#     modebar=dict(
#         bgcolor='rgba(0,0,0,0)',
#         color='rgba(1,1,1,0.3)',
#         activecolor='rgba(58, 73, 99, 1)'
#     )
# )
#
# fig5 = go.Figure(data=go.Scatter(x=timeline, y=save_thorax_rotation, name=f'Thorax rotation'))
#
# fig5.add_trace(
#     go.Scatter(x=timeline, y=save_thorax_bend, name=f'Thorax bend')
# )
#
# fig5.add_trace(
#     go.Scatter(x=timeline, y=save_thorax_tilt, name=f'Thorax tilt')
# )
#
# add_vertical_line(fig5)
#
# fig5.update_layout(
#     # title='Thorax angles',
#     title_x=0.5,
#     font_size=12,
#     # yaxis_title='angle in °',
#     # xaxis_title="time in s",
#     yaxis_ticksuffix="°",
#     paper_bgcolor='rgba(0,0,0,0)',
#     plot_bgcolor='rgba(0,0,0,0)',
#     legend_orientation="h",
#     legend=dict(y=1, yanchor="bottom"),
#     margin=dict(
#         l=10,
#         r=10,
#         t=20,
#         pad=5
#     ),
#     modebar=dict(
#         bgcolor='rgba(0,0,0,0)',
#         color='rgba(1,1,1,0.3)',
#         activecolor='rgba(58, 73, 99, 1)'
#     )
# )
#
# fig6 = go.Figure(data=go.Scatter(x=timeline, y=save_thorax_thrust, name=f'Thorax thrust'))
#
# fig6.add_trace(
#     go.Scatter(x=timeline, y=save_thorax_sway, name=f'Thorax sway')
# )
#
# fig6.add_trace(
#     go.Scatter(x=timeline, y=save_thorax_lift, name=f'Thorax lift')
# )
#
# add_vertical_line(fig6)
#
# fig6.update_layout(
#     # title='Thorax displacement',
#     title_x=0.5,
#     font_size=12,
#     # yaxis_title='Displacement in m',
#     # xaxis_title="time in s",
#     yaxis_ticksuffix="m",
#     paper_bgcolor='rgba(0,0,0,0)',
#     plot_bgcolor='rgba(0,0,0,0)',
#     legend_orientation="h",
#     legend=dict(y=1, yanchor="bottom"),
#     margin=dict(
#         l=10,
#         r=10,
#         t=20,
#         pad=5
#     ),
#     modebar=dict(
#         bgcolor='rgba(0,0,0,0)',
#         color='rgba(1,1,1,0.3)',
#         activecolor='rgba(58, 73, 99, 1)'
#     )
# )
#
# fig11 = go.Figure(data=go.Scatter(x=timeline, y=save_spine_tilt))
#
# add_vertical_line(fig11)
#
# fig11.update_layout(
#     # title='Tilt between pelvis and shoulder',
#     title_x=0.5,
#     font_size=12,
#     # yaxis_title='angle in °',
#     # xaxis_title="time in s",
#     yaxis_ticksuffix="°",
#     paper_bgcolor='rgba(0,0,0,0)',
#     plot_bgcolor='rgba(0,0,0,0)',
#     margin=dict(
#         l=10,
#         r=10,
#         t=20,
#         pad=5
#     ),
#     modebar=dict(
#         bgcolor='rgba(0,0,0,0)',
#         color='rgba(1,1,1,0.3)',
#         activecolor='rgba(58, 73, 99, 1)'
#     )
# )
#
# fig12 = go.Figure(data=go.Scatter(x=timeline, y=save_head_tilt))
#
# add_vertical_line(fig12)
#
# fig12.update_layout(
#     # title='Head tilt',
#     title_x=0.5,
#     font_size=12,
#     # yaxis_title='angle in °',
#     # xaxis_title="time in s",
#     yaxis_ticksuffix="°",
#     paper_bgcolor='rgba(0,0,0,0)',
#     plot_bgcolor='rgba(0,0,0,0)',
#     margin=dict(
#         l=10,
#         r=10,
#         t=20,
#         pad=5
#     ),
#     modebar=dict(
#         bgcolor='rgba(0,0,0,0)',
#         color='rgba(1,1,1,0.3)',
#         activecolor='rgba(58, 73, 99, 1)'
#     )
# )
#
# fig13 = go.Figure(data=go.Scatter(x=timeline, y=save_head_rotation))
#
# add_vertical_line(fig13)
#
# fig13.update_layout(
#     # title='Head rotation',
#     title_x=0.5,
#     font_size=12,
#     # yaxis_title='angle in °',
#     # xaxis_title="time in s",
#     yaxis_ticksuffix="°",
#     paper_bgcolor='rgba(0,0,0,0)',
#     plot_bgcolor='rgba(0,0,0,0)',
#     margin=dict(
#         l=10,
#         r=10,
#         t=20,
#         pad=5
#     ),
#     modebar=dict(
#         bgcolor='rgba(0,0,0,0)',
#         color='rgba(1,1,1,0.3)',
#         activecolor='rgba(58, 73, 99, 1)'
#     )
# )
#
# fig14 = go.Figure(data=go.Scatter(x=timeline, y=save_left_arm_length))
#
# add_vertical_line(fig14)
#
# fig14.update_layout(
#     # title='Left arm length',
#     title_x=0.5,
#     font_size=12,
#     # yaxis_title='length in m',
#     # xaxis_title="time in s",
#     yaxis_ticksuffix="m",
#     paper_bgcolor='rgba(0,0,0,0)',
#     plot_bgcolor='rgba(0,0,0,0)',
#     margin=dict(
#         l=10,
#         r=10,
#         t=20,
#         pad=5
#     ),
#     modebar=dict(
#         bgcolor='rgba(0,0,0,0)',
#         color='rgba(1,1,1,0.3)',
#         activecolor='rgba(58, 73, 99, 1)'
#     )
# )
#
# fig15 = go.Figure(data=go.Scatter(x=timeline, y=save_spine_rotation))
#
# add_vertical_line(fig15)
#
# fig15.update_layout(
#     # title='Spine rotation',
#     title_x=0.5,
#     font_size=12,
#     # yaxis_title='angle in °',
#     # xaxis_title="time in s",
#     yaxis_ticksuffix="°",
#     paper_bgcolor='rgba(0,0,0,0)',
#     plot_bgcolor='rgba(0,0,0,0)',
#     margin=dict(
#         l=10,
#         r=10,
#         t=20,
#         pad=5
#     ),
#     modebar=dict(
#         bgcolor='rgba(0,0,0,0)',
#         color='rgba(1,1,1,0.3)',
#         activecolor='rgba(58, 73, 99, 1)'
#     )
# )
#
# fig16 = go.Figure(data=go.Scatter(x=timeline, y=save_arm_rotation, name=f'Arm rotation'))
#
# fig16.add_trace(
#     go.Scatter(x=timeline, y=save_arm_to_ground, name=f'Arm to ground')
# )
#
# fig16.update_layout(
#     # title='Wrist angles',
#     title_x=0.5,
#     font_size=12,
#     # yaxis_title='angle in °',
#     # xaxis_title="time in s",
#     yaxis_ticksuffix="°",
#     paper_bgcolor='rgba(0,0,0,0)',
#     plot_bgcolor='rgba(0,0,0,0)',
#     margin=dict(
#         l=10,
#         r=10,
#         t=20,
#         pad=5
#     ),
#     modebar=dict(
#         bgcolor='rgba(0,0,0,0)',
#         color='rgba(1,1,1,0.3)',
#         activecolor='rgba(58, 73, 99, 1)'
#     )
# )


def render_files(files):
    if files is None:
        return []

    template = [html.A(href='# ', children=file, className='text-white text-sm') for file in files]
    return template


def init_dash(server):
    """
    Initialize the dash app

    :param server: Flask server to run the app on
    :return: Dash app
    """
    # Initialize the app
    app = DashProxy(__name__, server=server, url_base_pathname='/dashboard/',
                    external_scripts=["https://tailwindcss.com/", {"src": "https://cdn.tailwindcss.com"}],
                    transforms=[  # MultiplexerTransform(proxy_location=None),
                        NoOutputTransform()],
                    prevent_initial_callbacks=True,
                    # background_callback_manager=background_callback_manager
                    # long_callback_manager=background_callback_manager
                    )
    app.css.config.serve_locally = False
    app.css.append_css({'external_url': './assets/output.css'})
    # server = app.server
    app.app_context = server.app_context
    app._favicon = 'favicon.png'

    app.title = 'Analyze your swing – Swinglab'
    app.update_title = 'Analyze your swing – Swinglab'

    # Initialize the plots
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
        modebar=dict(
            bgcolor='rgba(0,0,0,0)',
            color='#94a3b8',
            activecolor='#94a3b9',
        )
    )

    def serve_layout():
        """
        Create the layout of the dash app

        :return: Layout of the dash app
        """

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

            id='main',

            children=[
                # html.Script(src='https://plausible.io/js/script.js', defer=True, **{'data-domain': 'swinglab.app'}),
                dcc.Location(id='url', refresh=False),

                # Loading state to show loading view
                html.Div(id='loading-state', className='hidden'),

                # Loader
                html.Div(
                    id='loader',
                    className='w-full z-50',
                    children=loader
                ),

                # overlay
                html.Div(
                    id='overlay',
                    className='w-full hidden z-50 fixed top-0 left-0 bottom-0 right-0',
                    children=overlay
                ),

                # Main wrapper
                html.Div(
                    className='flex w-full flex-col 2xl:items-center overflow-x-hidden hidden',
                    id='main_wrapper',
                    children=[

                        # navbar top
                        html.Div(
                            id='navbar-top',
                            className='flex flex-row w-full h-12 items-center ml-4 lg:hidden justify-between',
                            children=[
                                html.Button(
                                    className='flex flex-row w-6 h-6 items-center',
                                    id='menu-button',
                                    children=[
                                        html.Img(src=app.get_asset_url('menu_burger.svg'), className='h-4 w-4',
                                                 id='menu-icon')
                                    ]
                                ),
                                dcc.Upload(
                                    '+',
                                    id='add-button',
                                    disabled=disabled,
                                    multiple=False,
                                    max_size=20e6,
                                    accept=['.mp4', '.mov', '.avi'],
                                    className='flex flex-row w-6 h-6 items-center mr-8 text-gray-400 text-2xl lg:hidden',
                                )
                            ]
                        ),

                        html.Button(
                            id='navbar-mobile',
                            className='fixed z-10 top-0 left-0 w-full h-full bg-black bg-opacity-50 hidden cursor-default',
                        ),

                        # Sidebar
                        html.Div(
                            id='sidebar',
                            # className='flex flex-col bg-slate-600 dark:bg-gray-700 fixed lg:left-5 lg:top-5 lg:bottom-5 top-0 bottom-0 w-60 z-10 lg:rounded-2xl hidden lg:flex',
                            className='flex flex-col fixed lg:left-5 lg:top-5 lg:bottom-5 top-0 bottom-0 w-60 max-lg:z-30 hidden lg:flex overflow-x-visible bg-white dark:bg-gray-700 rounded-r-2xl lg:rounded-l-2xl shadow dark:shadow-slate-950',
                            # dark:bg - slate - 900
                            # bg - [  # FAF7F5
                            children=[
                                html.Button(
                                    id='sidebar-header',
                                    className='flex-row items-center ml-4 lg:hidden',
                                    children=[
                                        html.Img(src=app.get_asset_url('menu_cross.svg'),
                                                 className='h-4 w-4 mt-4 hidden')]
                                ),

                                # html.Div(
                                #     'HISTORY',
                                #     className='text-white text-xs font-medium mb-3 mt-5 px-4'
                                # ),

                                html.Div(
                                    dcc.Upload(
                                        disabled=disabled,
                                        id='upload-data',
                                        children=html.Div(
                                            className='text-gray-800 dark:text-gray-100',
                                            children=
                                            [
                                                '+  Upload your swing',
                                                ' ⛳️',
                                            ],
                                        ),
                                        className='absolute flex items-center justify-center text-center inline-block text-sm h-16 border border-slate-400 mx-2 rounded-2xl',
                                        multiple=False,
                                        max_size=20e6,
                                        accept=['.mp4', '.mov', '.avi'],
                                        style_active=(dict(
                                            backgroundColor='#64748b',
                                            borderColor='rgba(115, 165, 250, 1)',
                                            borderRadius='12px',
                                        )),
                                        style_reject=(dict(
                                            backgroundColor='bg-red-200',
                                            borderColor='bg-red-400',
                                            borderRadius='12px',
                                        )),
                                    ),
                                    className='relative h-28 mt-2 max-w-full'
                                ),

                                html.Div(
                                    className='flex flex-col mb-4 mt-1 h-full overflow-y-auto border-b border-gray-200 dark:border-gray-600',
                                    children=[
                                        html.Div(
                                            # disabled=True,
                                            children=[
                                                html.Button(
                                                    id={'type': 'saved-button', 'index': f'{file}'},
                                                    className='flex flex-row items-center',
                                                    children=[
                                                        # html.Img(src=app.get_asset_url('graph_gray.svg'),
                                                        #          className='w-6 h-6 mr-2'),
                                                        heart_navbar(file),
                                                        reformat_file(file),
                                                    ]),
                                                html.Button(
                                                    html.Img(src=app.get_asset_url('delete.svg'), className='w-5 h-5'),
                                                    id={'type': 'delete', 'index': file},
                                                    className='visible hover:bg-red-600 rounded-full px-1 py-1 absolute right-1',
                                                    disabled=False, n_clicks=0
                                                ),
                                            ],

                                            # className='relative font-base max-w-full text-xs text-gray-200 flex flex-row hover:bg-slate-500 px-4 py-2 rounded-lg mb-2 mx-4 items-center justify-between h-12 transition')
                                            className='relative font-base max-w-full text-xs text-gray-800 dark:text-gray-100 flex flex-row hover:bg-slate-200 dark:hover:bg-slate-500 hover:shadow-md dark:hover:shadow-slate-950 px-4 py-2 rounded-lg mb-2 mx-4 items-center justify-between h-12 transition')
                                        for file in files],
                                    id='file_list',
                                ),
                                html.Div(
                                    className='flex flex-col gap-2 mx-4 mb-4 justify-end',
                                    children=[
                                        html.A(
                                            'HOME',
                                            href='/',
                                            # className='font-normal text-xs text-amber-500 hover:border-amber-400 border-2 border-transparent hover:text-amber-400 items-center justify-center px-4 py-2 rounded-lg transition'
                                            className='font-normal text-xs text-amber-500 hover:bg-amber-100 dark:hover:bg-slate-800 items-center justify-center px-4 py-2 rounded-lg transition'
                                        ),
                                        html.A(
                                            'PROFILE',
                                            href='/profile',
                                            # className='font-normal text-xs text-amber-500 hover:border-amber-400 border-2 border-transparent hover:text-amber-400 items-center justify-center px-4 py-2 rounded-lg transition'
                                            className='font-normal text-xs text-amber-500 hover:bg-amber-100 dark:hover:bg-slate-800 items-center justify-center px-4 py-2 rounded-lg transition'
                                        ),
                                        html.A(
                                            'DASHBOARD',
                                            href='/dash',
                                            # className='font-normal text-xs text-amber-500 border-amber-500 hover:border-amber-400 border-2 hover:text-amber-400 items-center justify-center px-4 py-2 rounded-lg transition'
                                            className='font-normal text-xs text-amber-500 bg-amber-100 dark:bg-slate-800 items-center justify-center px-4 py-2 rounded-lg transition'
                                        ),
                                        html.A(
                                            'LOGOUT',
                                            href='/logout',
                                            # className='inline-flex whitespace-nowrap rounded-lg border-2 border-transparent px-4 py-2 text-xs font-normal text-white hover:border-gray-200 hover:text-gray-200 transition'
                                            # className='inline-flex whitespace-nowrap rounded-lg border-2 border-transparent px-4 py-2 text-xs font-normal text-gray-800 dark:text-gray-100 hover:border-gray-200 hover:text-gray-200 transition'
                                            className='font-normal text-xs dark:text-gray-200 text-gray-800 hover:bg-amber-100 dark:hover:bg-slate-800 items-center justify-center px-4 py-2 rounded-lg transition'
                                        )
                                    ]
                                )
                            ]
                        ),
                        # Sidebar end

                        html.Div(
                            id='body',
                            className='lg:mx-16 mx-4 lg:pl-60 mt-0 2xl:w-[90rem] ',
                            children=[

                                # Selection View background dismiss button
                                html.Button(
                                    id='selection-view-dismiss',
                                    className='fixed w-full h-full top-0 left-0 z-20 bg-black bg-opacity-50 backdrop-filter backdrop-blur-sm hidden',
                                ),

                                # Selection view in center of screen
                                html.Div(
                                    id='selection-view',
                                    className='hidden',
                                    children=[
                                        html.Div(
                                            className='fixed flex flex-col px-4 pt-14 pb-4 w-96 top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 bg-white dark:bg-gray-800 rounded-2xl shadow-lg z-30',
                                            children=[
                                                html.Div(
                                                    'New margins',
                                                    id='new_margins_title',
                                                    className='w-fit text-lg font-medium text-slate-900 dark:text-gray-100 pt-4 absolute top-6 transform -translate-x-1/2 left-1/2'
                                                ),

                                                html.Div(
                                                    'Setup',
                                                    className='relative justify-start text-sm font-medium text-slate-900 dark:text-gray-100 pt-4 flex flex-row'
                                                ),
                                                html.Div(
                                                    className='flex flex-row gap-2',
                                                    children=[
                                                        dcc.Input(
                                                            id='setup_low_new_margins',
                                                            # required=True,
                                                            type='number',
                                                            className='dark:bg-gray-600 relative block w-full my-2 p-3 appearance-none rounded-lg border border-gray-300 text-gray-900 dark:border-gray-500 dark:text-gray-100 placeholder-gray-300 dark:placeholder-gray-400 focus:z-10 focus:border-indigo-500 focus:outline-none focus:ring-indigo-500 text-sm',
                                                        ),
                                                        dcc.Input(
                                                            id='setup_high_new_margins',
                                                            type='number',
                                                            className='dark:bg-gray-600 relative block w-full my-2 p-3 appearance-none rounded-lg border border-gray-300 text-gray-900 dark:border-gray-500 dark:text-gray-100 placeholder-gray-300 dark:placeholder-gray-400 focus:z-10 focus:border-indigo-500 focus:outline-none focus:ring-indigo-500 text-sm',
                                                        ),
                                                    ]
                                                ),
                                                html.Div(
                                                    'Top',
                                                    className='relative justify-start text-sm font-medium text-slate-900 dark:text-gray-100 pt-2 flex flex-row'
                                                ),
                                                html.Div(
                                                    className='flex flex-row gap-2',
                                                    children=[
                                                        dcc.Input(
                                                            id='top_low_new_margins',
                                                            type='number',
                                                            className='dark:bg-gray-600 relative block w-full my-2 p-3 appearance-none rounded-lg border border-gray-300 text-gray-900 dark:border-gray-500 dark:text-gray-100 placeholder-gray-300 dark:placeholder-gray-400 focus:z-10 focus:border-indigo-500 focus:outline-none focus:ring-indigo-500 text-sm',
                                                        ),
                                                        dcc.Input(
                                                            id='top_high_new_margins',
                                                            type='number',
                                                            className='dark:bg-gray-600 relative block w-full my-2 p-3 appearance-none rounded-lg border border-gray-300 text-gray-900 dark:border-gray-500 dark:text-gray-100 placeholder-gray-300 dark:placeholder-gray-400 focus:z-10 focus:border-indigo-500 focus:outline-none focus:ring-indigo-500 text-sm',
                                                        ),
                                                    ]
                                                ),
                                                html.Div(
                                                    'Impact',
                                                    className='relative justify-start text-sm font-medium text-slate-900 dark:text-gray-100 pt-2 flex flex-row'
                                                ),
                                                html.Div(
                                                    className='flex flex-row gap-2',
                                                    children=[
                                                        dcc.Input(
                                                            id='impact_low_new_margins',
                                                            type='number',
                                                            className='dark:bg-gray-600 relative block w-full my-2 p-3 appearance-none rounded-lg border border-gray-300 text-gray-900 dark:border-gray-500 dark:text-gray-100 placeholder-gray-300 dark:placeholder-gray-400 focus:z-10 focus:border-indigo-500 focus:outline-none focus:ring-indigo-500 text-sm',
                                                        ),
                                                        dcc.Input(
                                                            id='impact_high_new_margins',
                                                            type='number',
                                                            className='dark:bg-gray-600 relative block w-full my-2 p-3 appearance-none rounded-lg border border-gray-300 text-gray-900 dark:border-gray-500 dark:text-gray-100 placeholder-gray-300 dark:placeholder-gray-400 focus:z-10 focus:border-indigo-500 focus:outline-none focus:ring-indigo-500 text-sm',
                                                        ),
                                                    ]
                                                ),
                                                html.Button(
                                                    'Save',
                                                    id='submit-new-margins',
                                                    className='relative justify-start text-sm font-medium text-gray-100 flex flex-row bg-indigo-500 hover:bg-indigo-600 rounded-lg items-center justify-center px-4 py-2 mt-2 w-fit',
                                                )
                                            ]
                                        )
                                    ]
                                ),
                                # End selection view

                                # region Delete file view
                                html.Div(
                                    id='delete-file-view',
                                    children=[
                                        html.Div(
                                            className='bg-white dark:bg-gray-800 rounded-lg shadow-lg p-4 w-fit fixed top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 items-center',
                                            children=[
                                                html.Div('Do you want to delete this swing?',
                                                         className='text-lg font-medium text-gray-900 dark:text-gray-100 pt-2 relative items-center w-full'),
                                                html.Div('',
                                                         className='text-sm font-medium text-gray-900 dark:text-gray-100 pt-2 relative items-center w-full',
                                                         id='delete-file-name'),
                                                html.Div(
                                                    className='flex flex-row justify-between mt-6',
                                                    children=[
                                                        html.Button('Delete',
                                                                    id='delete-file',
                                                                    className='text-sm font-medium text-gray-900 dark:text-gray-100 py-2 px-3 bg-red-200 dark:bg-red-800 rounded-lg w-24 items-center justify-center text-center'),
                                                        html.Button('Cancel',
                                                                    id='cancel-delete-file',
                                                                    className='text-sm font-medium text-gray-900 dark:text-gray-100 py-2 px-3 bg-gray-100 dark:bg-gray-600 rounded-lg w-24 items-center justify-center text-center')
                                                    ]
                                                )
                                            ]
                                        )
                                    ],
                                    className='fixed w-full h-full top-0 left-0 z-40 bg-black bg-opacity-50 backdrop-filter backdrop-blur-sm hidden',
                                ),
                                # endregion delete file view

                                # Start video view
                                html.Div(
                                    className='flex flex-col xl:flex-row justify-between',
                                    children=[

                                        html.Div(
                                            id='upload-video',
                                            className='relative w-full flex-row justify-between mt-5 hidden',
                                            children=upload_video()),

                                        # Upload component
                                        html.Div(
                                            id='upload-initial',
                                            className='relative w-full flex flex-row justify-between xl:mb-5 mt-5',
                                            children=[

                                                html.Div(children=[
                                                    html.Div(
                                                        children=[
                                                            html.Div(
                                                                children=[
                                                                    'New analysis',
                                                                    html.Div('BETA',
                                                                             className='ml-4 bg-gradient-to-br from-indigo-400 to-rose-600 dark:bg-gradient-to-b dark:from-amber-300 dark:to-orange-500 rounded-full px-2 py-1 w-fit font-bold text-sm text-gray-100 dark:text-gray-600')
                                                                ],
                                                                className='flex flex-row text-lg font-medium text-slate-900 dark:text-gray-100 pt-4'
                                                            ),
                                                            html.Span(
                                                                'mp4, mov or avi – max. 20 MB',
                                                                className='text-sm font-medium text-slate-900 dark:text-gray-100'
                                                            )
                                                        ],
                                                        className='flex flex-col items-start xl:mx-10 mx-4 mb-4'
                                                    ),
                                                    html.Div(
                                                        dcc.Upload(
                                                            disabled=disabled,
                                                            id='upload-data-initial',
                                                            children=html.Div(
                                                                className='text-slate-900 dark:text-gray-100',
                                                                children=
                                                                [
                                                                    'Upload your swing ⛳️',
                                                                ],
                                                            ),
                                                            className='bg-[rgba(251, 252, 254, 1)] xl:mx-10 mx-4 rounded-2xl flex items-center justify-center py-10 mb-5 text-center inline-block text-sm border-dashed border-4 border-gray-400 xl:h-80 h-20',
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
                                                    className='bg-white dark:bg-gray-700 shadow dark:shadow-slate-950 rounded-2xl flex items-start justify-center text-center inline-block flex-col w-full h-44 xl:h-full xl:mr-5 mb-2 xl:mb-0 backdrop-blur-md bg-opacity-80 border border-gray-100 dark:border-gray-900',
                                                ),

                                            ]),
                                        # End of upload component

                                        # region Live updating divs based on position in video
                                        html.Div(
                                            id='live-divs',
                                            className='flex flex-nowrap px-4 -mx-4 xl:mt-5 relative',
                                            children=[
                                                html.Div(
                                                    id='live-divs-container',
                                                    className='flex xl:mb-5 mb-2 gap-2 flex-col xl:flex-row w-fit relative max-xl:overflow-x-auto xl:h-[29.5rem] overflow-y-auto overflow-x-hidden px-2 -mx-2',
                                                    children=[
                                                        # First row
                                                        html.Div(
                                                            className='flex flex-row xl:flex-col w-full gap-2',
                                                            children=[
                                                                html.Div(
                                                                    children=[
                                                                        html.Div('Pelvis Rotation',
                                                                                 className='absolute w-fit left-1/2 -translate-x-1/2 top-2 text-base font-medium text-slate-900 dark:text-gray-100 text-left', ),
                                                                        html.Button(
                                                                            html.Img(src=app.get_asset_url('edit.svg'),
                                                                                     className='h-4 w-4'),
                                                                            id='pelvis_rot_btn',
                                                                            className='absolute right-3 w-fit h-fit top-3 z-10'),
                                                                        html.Div('- °', id='pelvis_rot_val',
                                                                                 className='mt-2'),
                                                                        # Slider bar
                                                                        html.Div(slider_view('pelvis_rot', -80, 160)),
                                                                        # End of slider bar
                                                                        # TODO: Pelvis rotation
                                                                        html.Div('-80, 160, -80, 160, -80, 160',
                                                                                 id='pelvis_rot_store',
                                                                                 className='hidden'),
                                                                    ],
                                                                    className='relative text-3xl font-medium text-slate-900 dark:text-gray-100 bg-white dark:bg-gray-700 shadow dark:shadow-slate-950 rounded-2xl flex flex-none flex-col items-center justify-center w-56 h-28 text-center'
                                                                ),
                                                                html.Div(
                                                                    children=[
                                                                        html.Div('Pelvis Tilt',
                                                                                 className='w-fit absolute left-1/2 -translate-x-1/2 top-2 text-base font-medium text-slate-900 dark:text-gray-100  text-left', ),
                                                                        html.Button(
                                                                            html.Img(src=app.get_asset_url('edit.svg'),
                                                                                     className='h-4 w-4'),
                                                                            id='pelvis_tilt_btn',
                                                                            className='absolute right-3 w-fit h-fit top-3 z-10'),
                                                                        html.Div('- °', id='pelvis_bend_val',
                                                                                 className='mt-2'),
                                                                        # Slider bar
                                                                        html.Div(slider_view('pelvis_bend', -30, 30)),
                                                                        # End of slider bar
                                                                        html.Div('-30, 30, -30, 30, -30, 30',
                                                                                 id='pelvis_bend_store',
                                                                                 className='hidden'),
                                                                    ],
                                                                    className='relative text-3xl font-medium text-slate-900 dark:text-gray-100 bg-white dark:bg-gray-700 shadow dark:shadow-slate-950 rounded-2xl flex flex-none flex-col items-center justify-center w-56 h-28 text-center'
                                                                ),
                                                                html.Div(
                                                                    children=[
                                                                        html.Div('Thorax Rotation',
                                                                                 className='w-fit absolute left-1/2 -translate-x-1/2 top-2 text-base font-medium text-slate-900 dark:text-gray-100 text-left', ),
                                                                        html.Button(
                                                                            html.Img(src=app.get_asset_url('edit.svg'),
                                                                                     className='h-4 w-4'),
                                                                            id='thorax_rot_btn',
                                                                            className='absolute right-3 w-fit h-fit top-3 z-10'),
                                                                        html.Div('- °', id='thorax_rot_val',
                                                                                 className='mt-2'),
                                                                        # Slider bar
                                                                        html.Div(slider_view('thorax_rot', -140, 140)),
                                                                        # End of slider bar
                                                                        html.Div('-140, 140, -140, 140, -140, 140',
                                                                                 id='thorax_rot_store',
                                                                                 className='hidden'),
                                                                    ],
                                                                    className='relative text-3xl font-medium text-slate-900 dark:text-gray-100 bg-white dark:bg-gray-700 shadow dark:shadow-slate-950 rounded-2xl flex flex-none flex-col items-center justify-center w-56 h-28 text-center'
                                                                ),
                                                                html.Div(
                                                                    children=[
                                                                        html.Div('Thorax Bend',
                                                                                 className='w-fit absolute left-1/2 -translate-x-1/2 top-2 text-base font-medium text-slate-900 dark:text-gray-100 text-left', ),
                                                                        html.Button(
                                                                            html.Img(src=app.get_asset_url('edit.svg'),
                                                                                     className='h-4 w-4'),
                                                                            id='thorax_tilt_btn',
                                                                            className='absolute right-3 w-fit h-fit top-3 z-10'),
                                                                        html.Div('- °', id='thorax_bend_val',
                                                                                 className='mt-2'),
                                                                        # Slider bar
                                                                        html.Div(slider_view('thorax_bend', -20, 60)),
                                                                        html.Div('-20, 60, -20, 60, -20, 60',
                                                                                 id='thorax_bend_store',
                                                                                 className='hidden'),
                                                                    ],
                                                                    className='relative text-3xl font-medium text-slate-900 dark:text-gray-100 bg-white dark:bg-gray-700 shadow dark:shadow-slate-950 rounded-2xl flex flex-none flex-col items-center justify-center w-56 h-28 text-center'
                                                                ),

                                                                # TODO Pelvis Tilt
                                                                # html.Div(
                                                                #     children=[
                                                                #         html.Div('Pelvis Tilt',
                                                                #                  className='w-fit absolute left-1/2 -translate-x-1/2 top-2 text-base font-medium text-slate-900 dark:text-gray-100 text-left', ),
                                                                #         # html.Button(
                                                                #         #     html.Img(src=app.get_asset_url('edit.svg'),
                                                                #         #              className='h-4 w-4'),
                                                                #         #     id='thorax_tilt_btn',
                                                                #         #     className='absolute right-3 w-fit h-fit top-3'),
                                                                #         html.Div('- °', id='pelvis_tilt_val',
                                                                #                  className='mt-2'),
                                                                #         # Slider bar
                                                                #         html.Div(slider_view('pelvis_tilt', -20, 60)),
                                                                #         html.Div('-20, 60, -20, 60, -20, 60',
                                                                #                  id='pelvis_tilt_store',
                                                                #                  className='hidden'),
                                                                #     ],
                                                                #     className='relative text-3xl font-medium text-slate-900 dark:text-gray-100 bg-white dark:bg-gray-700 shadow dark:shadow-slate-950 rounded-2xl flex flex-none flex-col items-center justify-center w-56 h-28 text-center'
                                                                # ),

                                                                html.Div(
                                                                    children=[
                                                                        html.Div('Pelvis Sway',
                                                                                 className='w-fit absolute left-1/2 -translate-x-1/2 top-2 text-base font-medium text-slate-900 dark:text-gray-100 text-left', ),
                                                                        # html.Button(
                                                                        #     html.Img(src=app.get_asset_url('edit.svg'),
                                                                        #              className='h-4 w-4'),
                                                                        #     id='thorax_tilt_btn',
                                                                        #     className='absolute right-3 w-fit h-fit top-3 z-10'),
                                                                        html.Div('- °', id='pelvis_sway_val',
                                                                                 className='mt-2'),
                                                                        # Slider bar
                                                                        html.Div(slider_view('pelvis_sway', -20, 60,
                                                                                             suffix='cm')),
                                                                        html.Div('-20, 60, -20, 60, -20, 60',
                                                                                 id='pelvis_sway_store',
                                                                                 className='hidden'),
                                                                    ],
                                                                    className='relative text-3xl font-medium text-slate-900 dark:text-gray-100 bg-white dark:bg-gray-700 shadow dark:shadow-slate-950 rounded-2xl flex flex-none flex-col items-center justify-center w-56 h-28 text-center'
                                                                ),
                                                            ]
                                                        ),
                                                        # End of first row

                                                        # Second row
                                                        html.Div(
                                                            className='flex flex-row xl:flex-col gap-2',
                                                            children=[
                                                                html.Div(
                                                                    children=[
                                                                        html.Div('Head Rotation',
                                                                                 className='w-fit absolute left-1/2 -translate-x-1/2 top-2 text-base font-medium text-slate-900 dark:text-gray-100 text-left', ),
                                                                        html.Button(
                                                                            html.Img(src=app.get_asset_url('edit.svg'),
                                                                                     className='h-4 w-4'),
                                                                            id='head_rot_btn',
                                                                            className='absolute right-3 w-fit h-fit top-3 z-10'),
                                                                        html.Div('- °', id='head_rot_val',
                                                                                 className='mt-2'),
                                                                        html.Div(slider_view('head_rot', -100, 100)),
                                                                        html.Div('-100, 100, -100, 100, -100, 100',
                                                                                 id='head_rot_store',
                                                                                 className='hidden'),
                                                                    ],
                                                                    className='relative text-3xl font-medium text-slate-900 dark:text-gray-100 bg-white dark:bg-gray-700 shadow dark:shadow-slate-950 rounded-2xl flex flex-none flex-col items-center justify-center w-56 h-28 text-center'
                                                                ),
                                                                html.Div(
                                                                    children=[
                                                                        html.Div('Head Tilt',
                                                                                 className='w-fit absolute left-1/2 -translate-x-1/2 top-2 text-base font-medium text-slate-900 dark:text-gray-100 text-left', ),
                                                                        html.Button(
                                                                            html.Img(src=app.get_asset_url('edit.svg'),
                                                                                     className='h-4 w-4'),
                                                                            id='head_tilt_btn',
                                                                            className='absolute right-3 w-fit h-fit top-3 z-10'),
                                                                        html.Div('- °', id='head_tilt_val',
                                                                                 className='mt-2'),
                                                                        html.Div(slider_view('head_tilt', -60, 60)),
                                                                        html.Div('-60, 60, -60, 60, -60, 60',
                                                                                 id='head_tilt_store',
                                                                                 className='hidden'),
                                                                    ],
                                                                    className='relative text-3xl font-medium text-slate-900 dark:text-gray-100 bg-white dark:bg-gray-700 shadow dark:shadow-slate-950 rounded-2xl flex flex-none flex-col items-center justify-center w-56 h-28 text-center'
                                                                ),
                                                                html.Div(
                                                                    children=[
                                                                        html.Div('Arm Rotation',
                                                                                 className='w-fit absolute left-1/2 -translate-x-1/2 top-2 text-base font-medium text-slate-900 dark:text-gray-100 text-left', ),
                                                                        html.Div('- °', id='arm_rot_val',
                                                                                 className='mt-2'),
                                                                        html.Div(slider_view('arm_rot', -240, 240)),
                                                                    ],
                                                                    className='relative text-3xl font-medium text-slate-900 dark:text-gray-100 bg-white dark:bg-gray-700 shadow  dark:shadow-slate-950 rounded-2xl flex flex-none flex-col items-center justify-center w-56 h-28 text-center'
                                                                ),
                                                                html.Div(
                                                                    children=[
                                                                        html.Div('Arm To Ground',
                                                                                 className='w-fit absolute left-1/2 -translate-x-1/2 top-2 text-base font-medium text-slate-900 dark:text-gray-100 text-left', ),
                                                                        html.Div('- °', id='arm_ground_val',
                                                                                 className='mt-2'),
                                                                        html.Div(slider_view('arm_ground', -90, 90)),
                                                                    ],
                                                                    className='relative text-3xl font-medium text-slate-900 dark:text-gray-100 bg-white dark:bg-gray-700 shadow dark:shadow-slate-950 rounded-2xl flex flex-none flex-col items-center justify-center w-56 h-28 text-center'
                                                                ),

                                                                # html.Div(
                                                                #     children=[
                                                                #         html.Div('Thorax Tilt',
                                                                #                  className='w-fit absolute left-1/2 -translate-x-1/2 top-2 text-base font-medium text-slate-900 dark:text-gray-100 text-left', ),
                                                                #         # html.Button(
                                                                #         #     html.Img(src=app.get_asset_url('edit.svg'),
                                                                #         #              className='h-4 w-4'),
                                                                #         #     id='thorax_tilt_btn',
                                                                #         #     className='absolute right-3 w-fit h-fit top-3 z-10'),
                                                                #         html.Div('- °', id='thorax_tilt_val',
                                                                #                  className='mt-2'),
                                                                #         # Slider bar
                                                                #         html.Div(slider_view('thorax_tilt', -20, 60)),
                                                                #         html.Div('-20, 60, -20, 60, -20, 60',
                                                                #                  id='thorax_tilt_store',
                                                                #                  className='hidden'),
                                                                #     ],
                                                                #     className='relative text-3xl font-medium text-slate-900 dark:text-gray-100 bg-white dark:bg-gray-700 shadow dark:shadow-slate-950 rounded-2xl flex flex-none flex-col items-center justify-center w-56 h-28 text-center'
                                                                # ),

                                                                html.Div(
                                                                    children=[
                                                                        html.Div('Thorax Sway',
                                                                                 className='w-fit absolute left-1/2 -translate-x-1/2 top-2 text-base font-medium text-slate-900 dark:text-gray-100 text-left', ),
                                                                        # html.Button(
                                                                        #     html.Img(src=app.get_asset_url('edit.svg'),
                                                                        #              className='h-4 w-4'),
                                                                        #     id='thorax_tilt_btn',
                                                                        #     className='absolute right-3 w-fit h-fit top-3 z-10'),
                                                                        html.Div('- °', id='thorax_sway_val',
                                                                                 className='mt-2'),
                                                                        # Slider bar
                                                                        html.Div(slider_view('thorax_sway', -20, 60,
                                                                                             suffix='cm')),
                                                                        html.Div('-20, 60, -20, 60, -20, 60',
                                                                                 id='thorax_sway_store',
                                                                                 className='hidden'),
                                                                    ],
                                                                    className='relative text-3xl font-medium text-slate-900 dark:text-gray-100 bg-white dark:bg-gray-700 shadow dark:shadow-slate-950 rounded-2xl flex flex-none flex-col items-center justify-center w-56 h-28 text-center'
                                                                ),

                                                            ]
                                                        ),
                                                        # End of second row
                                                    ]
                                                ),
                                            ]
                                        ),
                                        # endregion End of updating divs

                                    ]),
                                # End of video view

                                html.Div(
                                    className=('flex md:flex-row flex-col w-full h-full relative gap-2 mb-5'),
                                    children=[
                                        # Tempo divs
                                        html.Div(
                                            className='h-72 grid grid-cols-1 w-full gap-2 text-xl font-bold text-slate-900 dark:text-gray-100 bg-white dark:bg-gray-700 shadow dark:shadow-slate-950 rounded-2xl px-2',
                                            children=[
                                                html.Div(
                                                    id='position_divs',
                                                    children=[
                                                        html.Div('Backswing',
                                                                 className='text-base font-medium text-slate-900 dark:text-gray-100 dark:hover:text-gray-300'),
                                                        # TODO back text

                                                        html.Div('- s', id='backswing',
                                                                 className='mr-6'),
                                                        html.Div('0.5', id='top_pos', className='hidden'),
                                                        html.Div('0.5', id='impact_pos', className='hidden'),
                                                        html.Div('0.5', id='end_pos', className='hidden'),
                                                        html.Div('0.5', id='setup_pos', className='hidden'),
                                                        html.Div('60', id='fps_saved', className='hidden'),

                                                    ],
                                                    className='relative flex flex-col items-start w-full pl-2 sm:pl-8 pt-2 my-2'
                                                ),

                                                # Downswing div
                                                html.Div(
                                                    children=[
                                                        html.Div('Downswing',
                                                                 className='text-base font-medium text-slate-900 dark:text-gray-100 dark:hover:text-gray-300 top-6 left-6'),
                                                        # TODO down text

                                                        html.Div('- s', id='downswing',
                                                                 className='mr-6'),

                                                    ],
                                                    className='relative flex flex-col flex-none items-start w-full pl-2 sm:pl-8 md:pt-2 pt-0 my-2'
                                                ),

                                                # Tempo div
                                                html.Div(
                                                    children=[
                                                        html.Div('Tempo',
                                                                 className='text-base font-medium text-slate-900 dark:text-gray-100 dark:hover:text-gray-300 top-6 left-6 md:left-4 flex flex-col '),

                                                        html.Div(
                                                            className='flex flex-row w-full h-full justify-center relative',
                                                            children=[

                                                                html.Div(
                                                                    id='tempo_div',
                                                                    children=[
                                                                        html.Div('-', id='tempo'),
                                                                        html.Div(': 1', className=' ml-2')
                                                                    ],
                                                                    className='flex flex-row mr-6 w-1/3 '
                                                                ),

                                                                html.Div(
                                                                    className='relative  flex flex-col-reverse md:flex-col items-center w-2/3 px-2',
                                                                    children=[
                                                                        # TODO tempo text
                                                                        html.Div(
                                                                            id='tempo_text',
                                                                            className='text-sm text-gray-400 mx-6 w-full text-left h-full absolute font-normal top-8'
                                                                        ),

                                                                        html.Div(
                                                                            gradient_slider_view(id='tempo_slider',
                                                                                                 min=0,
                                                                                                 max=6),
                                                                        )
                                                                    ]
                                                                )

                                                            ]
                                                        ),

                                                    ],
                                                    className='relative flex flex-col flex-none md:justify-center w-full pl-2 sm:pl-8 h-24'
                                                ),
                                                # End of tempo div
                                            ]
                                        ),
                                        # End of tempo divs

                                        # Sequence div
                                        html.Div(
                                            children=[

                                                # Column for start sequence
                                                html.Div(
                                                    className='flex flex-col w-full sm:px-8 px-2',
                                                    children=[

                                                        html.Div(info_text('start_sequence'),
                                                                 className='relative w-full -mt-8 sm:-mx-8 -mx-2'),

                                                        html.Div(
                                                            className='flex flex-row items-center w-full px-2 pt-2',
                                                            children=[
                                                                html.Div(
                                                                    'Arms',
                                                                    className='text-sm font-medium text-gray-100 bg-[#2BC48C] rounded-full w-16 py-1 px-2 flex flex-none items-center justify-center border-[#2BC48C] border-4',
                                                                    id='start_sequence_first'
                                                                ),

                                                                html.Div(
                                                                    className='w-full h-1 bg-gray-300 dark:bg-gray-500 rounded-full mx-2'
                                                                ),
                                                                html.Div(
                                                                    'Thorax',
                                                                    className='text-sm font-medium text-gray-100 bg-[#E74D39] rounded-full w-16 py-1 px-2 flex flex-none items-center justify-center border-[#E74D39] border-4',
                                                                    id='start_sequence_second'
                                                                ),
                                                                html.Div(
                                                                    className='w-full h-1 bg-gray-300 dark:bg-gray-500 rounded-full mx-2'
                                                                ),

                                                                html.Div(
                                                                    'Hip',
                                                                    className='text-sm font-medium text-gray-100 bg-[#6266F6] rounded-full w-16 py-1 px-2 flex flex-none items-center justify-center border-[#6266F6] border-4',
                                                                    id='start_sequence_third'
                                                                ),
                                                                html.Div(
                                                                    '😍',
                                                                    className='text-lg font-medium ml-4',
                                                                    id='emoji-start'
                                                                )
                                                            ]
                                                        ),

                                                        html.Div(
                                                            'Ideally, you should start your swing with any body part but the pelvis.',
                                                            className='text-sm text-gray-400 w-full text-left mt-2 ml-2'
                                                        )

                                                    ]
                                                ),
                                                # Start sequence end

                                                # Column for transition sequence
                                                html.Div(
                                                    className='flex flex-col w-full sm:px-8 px-2 md:absolute md:bottom-6',
                                                    children=[

                                                        html.Div(info_text('transition_sequence'),
                                                                 className='relative w-full sm:-mx-8 -mx-2 -mt-4'),

                                                        html.Div(
                                                            className='flex flex-row items-center w-full px-2 pt-2 justify-between',
                                                            children=[
                                                                html.Div(
                                                                    'Hip',
                                                                    className='text-sm font-medium text-gray-100 bg-[#6266F6] rounded-full w-16 py-1 px-2 flex flex-none items-center justify-center border-[#6266F6] border-4',
                                                                    id='sequence_first'
                                                                ),
                                                                html.Div(
                                                                    className=' w-full h-1 bg-gray-300 dark:bg-gray-500 rounded-full mx-2'
                                                                ),
                                                                html.Div(
                                                                    'Thorax',
                                                                    className='text-sm font-medium text-gray-100 bg-[#E74D39] rounded-full w-16 py-1 px-2 flex flex-none items-center justify-center border-[#E74D39] border-4',
                                                                    id='sequence_second'
                                                                ),
                                                                html.Div(
                                                                    className='w-full h-1 bg-gray-300 dark:bg-gray-500 rounded-full mx-2'
                                                                ),
                                                                html.Div(
                                                                    'Arms',
                                                                    className='text-sm font-medium text-gray-100 bg-[#2BC48C] rounded-full w-16 py-1 px-2 flex flex-none items-center justify-center border-[#2BC48C] border-4',
                                                                    id='sequence_third'
                                                                ),
                                                                html.Div(
                                                                    '😍',
                                                                    className='text-lg font-medium ml-4',
                                                                    id='emoji-transition'
                                                                )
                                                            ]
                                                        ),

                                                        html.Div(
                                                            'The transition sequence should start with the pelvis and end with the arms.',
                                                            className='text-sm text-gray-400 w-full text-left mt-2 ml-2'
                                                        )

                                                    ]
                                                ),
                                                # Transition sequence end
                                            ],
                                            className='relative text-3xl text-slate-900 dark:text-gray-100 bg-white dark:bg-gray-700 shadow dark:shadow-slate-950 rounded-2xl flex flex-col justify-betwen w-full h-full md:h-72 text-center pb-4 pt-2'
                                        ),
                                        # End of sequence div

                                    ]),

                                html.Div(
                                    className='relative bg-white dark:bg-gray-700 shadow  dark:shadow-slate-950 rounded-2xl flex items-center justify-center mb-5 backdrop-blur-md bg-opacity-80 border border-gray-100 dark:border-gray-900 flex-col w-full',
                                    children=[

                                        html.Div(info_text('arm_path'), className='w-full'),

                                        html.Div(
                                            className='sm:grid sm:grid-cols-3 flex flex-col justify-between w-full flex-wrap relative',
                                            children=[
                                                html.Div(
                                                    className='flex flex-col',
                                                    children=[
                                                        html.Div(id='over_the_top',
                                                                 className='mx-4 sm:mx-10 sm:mt-20 mt-10 font-medium text-2xl dark:text-gray-100 text-slate-900 flex flex-col',
                                                                 children=[
                                                                     html.Div(
                                                                         children=[html.Div('Your transition is:',
                                                                                            className='text-base font-normal'),
                                                                                   'Perfect'])
                                                                 ]
                                                                 ),
                                                        html.Div(
                                                            id='swing_plane_angle',
                                                            className='mx-4 sm:mx-10 sm:mt-20 mt-10 font-medium text-2xl dark:text-gray-100 text-slate-900 flex flex-col',
                                                            children=[
                                                                html.Div(
                                                                    children=[html.Div('Swing Plane Angle:',
                                                                                       className='text-base font-normal'),
                                                                              '- °'])
                                                            ]
                                                        ),
                                                    ]
                                                ),
                                                html.Div(
                                                    # 3D arm path
                                                    id='arm_path',
                                                    children=[
                                                        dcc.Graph(
                                                            id='arm_path_3d',
                                                            figure=path_fig,
                                                            config=config_3D,
                                                            className='w-[350px] lg:w-[500px] xl:w-full h-fit relative',
                                                        )
                                                    ]),
                                            ]
                                        )
                                    ]
                                ),

                                html.Div(
                                    id='parent_sequence',
                                    className='hidden relative bg-white dark:bg-gray-700 shadow dark:shadow-slate-950 rounded-2xl flex items-center justify-center mb-5 backdrop-blur-md bg-opacity-80 border border-gray-100 dark:border-gray-900 flex-col w-full',
                                    children=[

                                        # Row for sequences
                                        html.Div(
                                            className='flex flex-row justify-between items-center w-full flex-wrap relative hidden',
                                            children=[

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
                                    className='relative bg-white dark:bg-gray-700 shadow dark:shadow-slate-950 rounded-2xl flex items-center justify-center mb-5 backdrop-blur-md bg-opacity-80 border border-gray-100 dark:border-gray-900 flex-col w-full',
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
                                    className='bg-white dark:bg-gray-700 shadow dark:shadow-slate-950 rounded-2xl flex items-center justify-center mb-5 backdrop-blur-md bg-opacity-80 border border-gray-100 dark:border-gray-900 flex-col w-full',
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
                                    className='bg-white dark:bg-gray-700 shadow dark:shadow-slate-950 rounded-2xl flex items-center justify-center mb-5 backdrop-blur-md bg-opacity-80 border border-gray-100 dark:border-gray-900 flex-col w-full',
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
                                    className='bg-white dark:bg-gray-700 shadow dark:shadow-slate-950 rounded-2xl flex items-center justify-center mb-5 backdrop-blur-md bg-opacity-80 border border-gray-100 dark:border-gray-900 flex-col w-full',
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
                                    className='bg-white dark:bg-gray-700 shadow dark:shadow-slate-950 rounded-2xl flex items-center justify-center mb-5 backdrop-blur-md bg-opacity-80 border border-gray-100 dark:border-gray-900 flex-col w-full',
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
                                    className='bg-white dark:bg-gray-700 shadow dark:shadow-slate-950 rounded-2xl flex items-center justify-center mb-5 backdrop-blur-md bg-opacity-80 border border-gray-100 dark:border-gray-900 flex-col w-full',
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
                                    className='bg-white dark:bg-gray-700 shadow dark:shadow-slate-950 rounded-2xl flex items-center justify-center mb-5 backdrop-blur-md bg-opacity-80 border border-gray-100 dark:border-gray-900 flex-col w-full',
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
                                    className='bg-white dark:bg-gray-700 shadow dark:shadow-slate-950 rounded-2xl flex items-center justify-center mb-5 backdrop-blur-md bg-opacity-80 border border-gray-100 dark:border-gray-900 flex-col w-full',
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
                                    className='bg-white dark:bg-gray-700 shadow dark:shadow-slate-950 rounded-2xl flex items-center justify-center mb-5 backdrop-blur-md bg-opacity-80 border border-gray-100 dark:border-gray-900 flex-col w-full',
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
                                    className='bg-white dark:bg-gray-700 shadow dark:shadow-slate-950 rounded-2xl flex items-center justify-center mb-5 backdrop-blur-md bg-opacity-80 border border-gray-100 dark:border-gray-900 flex-col w-full',
                                    children=[
                                        html.Div(
                                            className='text-base font-medium text-slate-900 dark:text-gray-100 pt-10 px-4 sm:px-10 w-full',
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
                            ]
                        ),
                    ]
                ),
            ]
        )

        return layout

    app.layout = serve_layout

    init_callbacks(app)

    app.register_celery_tasks()

    return app


def create_folder(name):
    """
    Create a folder if it does not exist
    :param name: Folder name
    :return: None
    """
    if not os.path.exists(name):
        os.makedirs(name)


def reformat_file(filename):
    """
    Reformat the filename to a more readable format
    :param filename: Filename to reformat (e.g. 2021-05-31_12-00-00)
    :return: Formatted filename (e.g. 31.05.2021, 12:00)
    """
    timestamp = datetime.datetime.strptime(filename, '%Y-%m-%d_%H-%M-%S')
    return timestamp.strftime('%d.%m.%Y, %H:%M')


def init_callbacks(app):
    """
    Initialize callbacks for the dash app
    :param app: dash app
    :return: None
    """

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
         Output('tempo', 'children', allow_duplicate=True), Output('backswing', 'children', allow_duplicate=True),
         Output('downswing', 'children', allow_duplicate=True),
         Output('top_pos', 'children', allow_duplicate=True), Output('impact_pos', 'children', allow_duplicate=True),
         Output('end_pos', 'children', allow_duplicate=True),
         Output('setup_pos', 'children', allow_duplicate=True), Output('fps_saved', 'children'),
         Output('arm_path', 'children', allow_duplicate=True), Output('over_the_top', 'children', allow_duplicate=True),
         Output('swing_plane_angle', 'children', allow_duplicate=True),
         Output('upload-data', 'disabled'), Output('add-button', 'disabled'), Output('upload-data-initial', 'disabled'),
         Output('upload-initial', 'className'), Output('upload-video', 'className'),
         Output('emoji-start', 'children'), Output('emoji-transition', 'children'), Output('loading-state', 'children'),
         Output('tempo_text', 'children'),
         # Output('backswing_text', 'children'), Output('downswing_text', 'children'),
         Output('url', 'pathname', allow_duplicate=True)
         ],
        [Input('upload-data', 'contents'), Input('add-button', 'contents'), Input('upload-data-initial', 'contents'),
         # Input('upload-data', 'filename'),
         # Input({'type': 'saved-button', 'index': ALL}, 'n_clicks'),
         Input('url', 'pathname'),
         Input('delete-file', 'n_clicks')
         # Input({'type': 'delete', 'index': ALL}, 'n_clicks')
         ],
        [State('file_list', 'children'), State('upload-initial', 'className'), State('upload-video', 'className'),
         State('delete-file-name', 'children')],
        # progress=Output('upload-progress', 'style'),
        prevent_initial_call=True,
        # background=True,
        # manager=background_callback_manager
    )
    def process(contents, contents_add, contents_initial, pathname,  # n_clicks,
                n_clicks_del, children, upload_initial_class,
                upload_video_class, del_file_name):
        """
        Process the uploaded video and extract motion data
        :param contents: Uploaded video from History page as base64 string
        :param contents_add: Uploaded video from plus button on mobile devices as base64 string
        :param contents_initial: Uploaded video from main page on first display as base64 string
        :param pathname: URL pathname of the current page (current video)
        :param n_clicks_del: Number of clicks on the delete button
        :param children: List of all files in the History
        :param upload_initial_class: Class of the upload component on the main page (will be changed to 'hidden' if a video is uploaded)
        :param upload_video_class: Class of the video view component on the main page (will be changed to visible if a video is uploaded)
        :param del_file_name: Name of the file to delete
        :return: Figures for the graphs, list of all files in the History, class of the upload component on the main page, class of the video view component on the main page
        """

        # Enable or Disable upload component
        disabled = False if (current_user.n_analyses > 0 or current_user.unlimited) else True

        # Check if file was uploaded
        if contents is None:
            if contents_initial is None:
                contents = contents_add
            else:
                contents = contents_initial

        # Check URL pathname
        if (pathname.split('/')[2] == '') and (contents is None) and (contents_add is None) and (
                contents_initial is None):
            return no_update

        # Check if file exists
        # if not os.path.exists(f'assets/save_data/{current_user.id}/{pathname.split("/")[2]}'):
        #     # print('File does not exist')
        #     # exit function
        #     return [no_update for _ in range(0, 51)] + ['/dashboard/']

        # Check if button was pressed or a file was uploaded
        if (ctx.triggered_id != 'upload-data') and (ctx.triggered_id != 'add-button') and (
                ctx.triggered_id != 'upload-data-initial'):
            if ctx.triggered_id != 'delete-file':
                # button_id = ctx.triggered_id.index
                button_id = pathname.split('/')[2]
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
                        modebar=dict(
                            bgcolor='rgba(0,0,0,0)',
                            color='#94a3b8',
                            activecolor='#94a3b9',
                        )
                    )

                    path = dcc.Graph(figure=path_fig, config=config_3D,
                                     className='w-[350px] lg:w-[500px] xl:w-full h-[500px] relative', )

                    # Reset sequence colors
                    sequence_first = 'text-base font-medium text-gray-100 bg-[#2BC48C] rounded-full w-16 py-1 px-2 flex fex-none items-center justify-center  bg-[#6266F6]',
                    sequence_second = 'text-base font-medium text-gray-100 bg-[#2BC48C] rounded-full w-16 py-1 px-2 flex fex-none items-center justify-center bg-[#E74D39]'
                    sequence_third = 'text-base font-medium text-gray-100 bg-[#2BC48C] rounded-full w-16 py-1 px-2 flex fex-none items-center justify-center bg-[#2BC48C]'

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

                    children_upload = []

                    return [fig, fig3, fig4, fig5, fig6, fig11, fig12, fig13, fig14, fig15, fig16, children,
                            children_upload, sequence_first, sequence_second, sequence_third,
                            sequence_first, sequence_second, sequence_third,
                            sequence_first, sequence_second, sequence_third,
                            sequence_first_text, sequence_second_text, sequence_third_text,
                            sequence_first_text, sequence_second_text, sequence_third_text,
                            sequence_first_text, sequence_second_text, sequence_third_text,
                            temp, time_back, time_down,
                            top_pos, impact_pos, end_pos, setup_pos, fps_saved,
                            [], [], [],
                            disabled, disabled, disabled,
                            upload_initial_class, upload_video_class,
                            '😍', '😍', '', '',  # '', ''
                            '/dashboard/'
                            ]

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

                try:
                    fps = data['fps'][0]
                except KeyError:
                    fps = len(save_wrist_angle) / duration

                # Get the kinematic transition  sequence
                sequence_first, sequence_second, sequence_third, first_bp, second_bp, third_bp, arm_index, emoji_transition = kinematic_sequence(
                    save_pelvis_rotation,
                    save_thorax_rotation,
                    save_arm_rotation, fps)

                # Get the kinematic start sequence
                sequence_first_start, sequence_second_start, sequence_third_start, first_bp_s, second_bp_s, third_bp_s, arm_index_s, emoji_start = kinematic_sequence_start(
                    save_pelvis_rotation, save_thorax_rotation, save_arm_rotation, fps)

                # Get the kinematic end sequence
                sequence_first_end, sequence_second_end, sequence_third_end, first_bp_e, second_bp_e, third_bp_e, arm_index_e = kinematic_sequence_end(
                    save_pelvis_rotation, save_thorax_rotation, save_arm_rotation, fps)

                # Get vid from db and check if custom values are set
                vid_row = UserLikes.query.filter_by(user_id=current_user.id, video_id=button_id).first()

                # Top of backswing
                if vid_row is None or vid_row.top is None:
                    top_pos = arm_index / len(save_wrist_angle)
                else:
                    top_pos = vid_row.top
                    arm_index = int(top_pos * len(save_wrist_angle))

                # Impact
                if vid_row is not None and vid_row.impact is not None:
                    impact_pos = vid_row.impact
                else:
                    if impact_ratio == -1:
                        impact_pos = (np.argmin(
                            filter_data(arm_z, fps)[int(arm_index):] / len(
                                save_wrist_angle)) + arm_index) / len(
                            save_wrist_angle)

                    else:
                        impact_pos = impact_ratio

                # End of swing
                if vid_row is None or vid_row.end is None:
                    end_pos = arm_index_e / len(save_wrist_angle)
                else:
                    end_pos = vid_row.end
                    arm_index_e = int(end_pos * len(save_wrist_angle))

                # Setup
                if vid_row is None or vid_row.setup is None:
                    setup_pos = arm_index_s / len(save_wrist_angle)
                else:
                    setup_pos = vid_row.setup
                    arm_index_s = int(setup_pos * len(save_wrist_angle))

                # Check if impact is before top
                if impact_pos < top_pos:
                    top_pos = (impact_pos - setup_pos) / 2 + setup_pos
                    arm_index = int(top_pos * len(save_wrist_angle))

                # Tempo
                temp, time_back, time_down = tempo(arm_index_s, arm_index, impact_pos * len(save_wrist_angle),
                                                   fps)

                # Get the tempo text
                tempo_text = get_tempo_text(temp)

                # Backswing text
                backswing_text = get_backswing_text(time_back)

                # Downswing text
                downswing_text = get_downswing_text(time_down)

                # Check if the swing is over the top
                over = over_the_top(arm_x, arm_z, int(arm_index_s), int(arm_index),
                                    int(impact_pos * len(save_wrist_angle)))
                if over:
                    over_text = [html.Div('Your transition is:', className='text-base font-normal'), 'Over the top']
                else:
                    over_text = [html.Div('Your transition is:', className='text-base font-normal'), 'Perfect']

                upload_initial_class = 'relative w-full flex-row justify-between xl:mb-5 mt-5 hidden'
                upload_video_class = 'relative w-full flex-row justify-between mt-5 flex'

                fps_saved = len(save_wrist_angle) / duration

                # Get the video and update the video player
                vid_src = f'assets/save_data/{current_user.id}/{button_id}/motion.mp4'
                children_upload = upload_video(disabled, path=vid_src)

                # Change the background color of the pressed button and reset the previously pressed button
                for child in children:
                    if child['props']['children'][0]['props']['id']['index'] == button_id:
                        child['props'][
                            'className'] = 'relative font-base max-w-full text-xs text-gray-800 dark:text-gray-100 flex flex-row bg-slate-200 dark:bg-slate-500 shadow-md dark:shadow-slate-950 px-4 py-2 rounded-lg mb-2 mx-4 items-center justify-between h-12 transition'
                        child['props']['children'][0]['props']['disabled'] = True

                    else:
                        child['props'][
                            'className'] = 'relative font-base max-w-full text-xs text-gray-800 dark:text-gray-100 flex flex-row hover:bg-slate-200 dark:hover:bg-slate-500 hover:shadow-md dark:hover:shadow-slate-950 px-4 py-2 rounded-lg mb-2 mx-4 items-center justify-between h-12 transition'
                        child['props']['children'][0]['props']['disabled'] = False

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
                    duration, fps)

                # Update the 3D plot
                path_fig, angle_swing_plane = hand_path_3d(arm_x, arm_y, arm_z, arm_index_s, arm_index_e, arm_index,
                                                           fps)

                angle_swing_plane_text = html.Div(
                    children=[html.Div('Swing Plane Angle:', className='text-base font-normal'),
                              f'{int(angle_swing_plane)}°'])

                path = dcc.Graph(figure=path_fig, config=config_3D,
                                 className='w-[350px] lg:w-[500px] xl:w-full h-[500px] relative', )

                return [fig, fig3, fig4, fig5, fig6, fig11, fig12, fig13, fig14, fig15, fig16, children,
                        children_upload, sequence_first, sequence_second, sequence_third,
                        sequence_first_start, sequence_second_start, sequence_third_start,
                        sequence_first_end, sequence_second_end, sequence_third_end, first_bp, second_bp, third_bp,
                        first_bp_s, second_bp_s, third_bp_s, first_bp_e, second_bp_e, third_bp_e,
                        temp, time_back, time_down,
                        top_pos, impact_pos, end_pos, setup_pos, fps_saved,
                        path, over_text, angle_swing_plane_text,
                        disabled, disabled, disabled,
                        upload_initial_class, upload_video_class,
                        emoji_start, emoji_transition, '', tempo_text,  # backswing_text, downswing_text,
                        f'/dashboard/{button_id}'
                        ]

        # Delete was pressed
        if (ctx.triggered_id != 'upload-data') and (ctx.triggered_id != 'add-button') and (
                ctx.triggered_id != 'upload-data-initial'):
            if ctx.triggered_id == 'delete-file':
                button_id = del_file_name
                # file = f'{button_id}.parquet'
                for child in children:
                    if child['props']['children'][0]['props']['id']['index'] == button_id:
                        children.remove(child)
                    else:
                        child['props'][
                            'className'] = 'relative font-base max-w-full text-xs text-gray-800 dark:text-gray-100 flex flex-row hover:bg-slate-200 dark:hover:bg-slate-500 hover:shadow-md dark:hover:shadow-slate-950 px-4 py-2 rounded-lg mb-2 mx-4 items-center justify-between h-12 transition'
                        child['props']['children'][0]['props']['disabled'] = False

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

                upload_initial_class = 'relative w-full flex-row justify-between xl:mb-5 mt-5 flex'
                upload_video_class = 'relative w-full flex-row justify-between mt-5 hidden'

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
                    modebar=dict(
                        bgcolor='rgba(0,0,0,0)',
                        color='#94a3b8',
                        activecolor='#94a3b9',
                    )
                )

                path = dcc.Graph(figure=path_fig, config=config_3D,
                                 className='w-[350px] lg:w-[500px] xl:w-full h-[500px] relative', )

                # Reset sequence colors
                sequence_first = 'text-base font-medium text-gray-100 bg-[#2BC48C] rounded-full w-16 py-1 px-2 flex fex-none items-center justify-center bg-[#6266F6]',
                sequence_second = 'text-base font-medium text-gray-100 bg-[#2BC48C] rounded-full w-16 py-1 px-2 flex fex-none items-center justify-center bg-[#E74D39]'
                sequence_third = 'text-base font-medium text-gray-100 bg-[#2BC48C] rounded-full w-16 py-1 px-2 flex fex-none items-center justify-center bg-[#2BC48C]'

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

                # children_upload = []
                children_upload = upload_video()

                # Remove video from like db
                like = UserLikes.query.filter_by(user_id=current_user.id, video_id=button_id).first()
                if like:
                    db.session.delete(like)
                    db.session.commit()

                return [fig, fig3, fig4, fig5, fig6, fig11, fig12, fig13, fig14, fig15, fig16, children,
                        children_upload, sequence_first, sequence_second, sequence_third,
                        sequence_first, sequence_second, sequence_third,
                        sequence_first, sequence_second, sequence_third, sequence_first_text,
                        sequence_second_text, sequence_third_text, sequence_first_text, sequence_second_text,
                        sequence_third_text, sequence_first_text, sequence_second_text, sequence_third_text,
                        temp, time_back, time_down,
                        top_pos, impact_pos, end_pos, setup_pos, fps_saved,
                        path, [], [],
                        disabled, disabled, disabled,
                        upload_initial_class, upload_video_class,
                        '😍', '😍', '', '',  # '', '',
                        '/dashboard/'
                        ]

        # TODO replicate

        # Write video to named tempfile
        content_type, content_string = contents.split(',')

        replicate.Client(api_token=os.getenv('REPLICATE_API_TOKEN'))

        content_string = base64.b64decode(content_string)

        # Create the directory if it doesn't exist
        directory = f"assets/{current_user.id}"
        if not os.path.exists(directory):
            os.makedirs(directory)

        # write video to temp file
        with tempfile.NamedTemporaryFile(suffix=".mp4", dir=f'assets/{current_user.id}') as temp:
            temp.write(content_string)
            print(tempfile.gettempdir())

            path = f'https://swinglab.app/dashboard/assets/{current_user.id}/{temp.name}'
            print(path)

            response = replicate.run(
                # "jlnk03/predict-pose:5f362416d56970a2e7e483fdddabd47778b54500724442be0bbb219e526fef76",
                "jlnk03/predict-pose:6d555b04c4e7032a1e20e5012d1babad7af6dfc12e392ebffb9d5af7bd067021",
                # input={"video": open(temp.name, "rb")},
                input={"video": path},
            )

        shoulder_l_s, shoulder_r_s, wrist_l_s, wrist_r_s, hip_l_s, hip_r_s, foot_l_s, eye_l_s, eye_r_s, pinky_l_s, index_l_s, arm_v, \
            duration, fps, impact_ratio, \
            out_path = response

        # yolo + motionBERT
        # content_string = base64.b64decode(content_string)
        # # write video to temp file
        # with tempfile.NamedTemporaryFile(suffix=".mp4") as temp:
        #     temp.write(content_string)
        #
        #     response = replicate.run(
        #         "jlnk03/pose3d:1fa7d2fa06f168febf0fba41e776a501c3e5df021ca298effcfa0287ce4a566b",
        #         input={"image": open(temp.name, "rb")},
        #     )
        #
        # shoulder_l_s, shoulder_r_s, wrist_l_s, wrist_r_s, hip_l_s, hip_r_s, foot_l_s, eye_l_s, eye_r_s, arm_v, \
        #     duration, fps, impact_ratio, \
        #     out_path = response
        #
        # # dummy pinky and index data
        # pinky_l_s = wrist_l_s
        # index_l_s = shoulder_l_s

        # Angles
        save_pelvis_rotation, save_pelvis_tilt, save_pelvis_sway, save_pelvis_thrust, save_pelvis_lift, \
            save_thorax_rotation, save_thorax_bend, save_thorax_tilt, save_thorax_sway, save_thorax_thrust, \
            save_thorax_lift, save_spine_rotation, save_spine_tilt, save_head_rotation, save_head_tilt, save_wrist_angle, \
            save_wrist_tilt, save_left_arm_length, save_arm_rotation, save_arm_to_ground, arm_position = \
            calculate_angles(shoulder_l_s, shoulder_r_s, wrist_l_s, wrist_r_s, hip_l_s, hip_r_s, foot_l_s, eye_l_s,
                             eye_r_s, pinky_l_s, index_l_s, arm_v, impact_ratio)

        # print(save_pelvis_rotation)

        # Check if folder was created and generate file name
        filename = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        create_folder(f'assets/save_data/{current_user.id}/' + filename)
        location = f'assets/save_data/{current_user.id}/' + filename

        # Get the video and update the video player
        urllib.request.urlretrieve(out_path, location + '/motion.mp4')

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
                                                                                             duration, fps)

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
        df['fps'] = fps

        df.to_parquet(f'assets/save_data/{current_user.id}/{filename}/{filename}.parquet')

        # Get the kinematic transition  sequence
        sequence_first, sequence_second, sequence_third, first_bp, second_bp, third_bp, arm_index, emoji_transition = kinematic_sequence(
            save_pelvis_rotation, save_thorax_rotation,
            save_arm_rotation, fps)

        # Get the kinematic start sequence
        sequence_first_start, sequence_second_start, sequence_third_start, first_bp_s, second_bp_s, third_bp_s, arm_index_s, emoji_start = kinematic_sequence_start(
            save_pelvis_rotation, save_thorax_rotation, save_arm_rotation, fps)

        # Get the kinematic end sequence
        sequence_first_end, sequence_second_end, sequence_third_end, first_bp_e, second_bp_e, third_bp_e, arm_index_e = kinematic_sequence_end(
            save_pelvis_rotation,
            save_thorax_rotation,
            save_arm_rotation,
            fps)

        # Top of backswing
        top_pos = arm_index / len(save_wrist_angle)

        # Impact
        if impact_ratio == -1:
            impact_pos = (np.argmin(
                filter_data(arm_position['z'], fps)[int(arm_index):] / len(
                    save_wrist_angle)) + arm_index) / len(
                save_wrist_angle)
        else:
            impact_pos = impact_ratio

        # End of swing
        end_pos = arm_index_e / len(save_wrist_angle)

        # Setup
        setup_pos = arm_index_s / len(save_wrist_angle)

        # Check if setup is before top
        if setup_pos > top_pos:
            setup_pos = 0
            arm_index_s = 0

        # Check if impact is before top
        if impact_pos < top_pos:
            top_pos = (impact_pos - setup_pos) / 2 + setup_pos
            arm_index = int(top_pos * len(save_wrist_angle))

        temp, time_back, time_down = tempo(arm_index_s, arm_index, impact_pos * len(save_wrist_angle),
                                           len(save_wrist_angle) / duration)

        # Get the tempo text
        tempo_text = get_tempo_text(temp)

        # Backswing text
        backswing_text = get_backswing_text(time_back)

        # Downswing text
        downswing_text = get_downswing_text(time_down)

        fps_saved = len(save_wrist_angle) / duration

        upload_initial_class = 'relative w-full flex-row justify-between xl:mb-5 mt-5 hidden'
        upload_video_class = 'relative w-full flex-row justify-between mt-5 flex'

        path_fig, angle_swing_plane = hand_path_3d(arm_position['x'], arm_position['y'], arm_position['z'], arm_index_s,
                                                   arm_index_e,
                                                   arm_index, fps)

        path = dcc.Graph(figure=path_fig, config=config_3D,
                         className='w-[350px] lg:w-[500px] xl:w-full h-[500px] relative', )

        angle_swing_plane_text = html.Div(children=[html.Div('Swing Plane Angle:', className='text-base font-normal'),
                                                    f'{int(angle_swing_plane)}°'])

        # Check if the swing is over the top
        over = over_the_top(arm_position['x'], arm_position['z'], int(arm_index_s), int(arm_index),
                            int(impact_pos * len(save_wrist_angle)))
        if over:
            over_text = [html.Div('Your transition is:', className='text-base font-normal'), 'Over the top']
        else:
            over_text = [html.Div('Your transition is:', className='text-base font-normal'), 'Perfect']

        # Reset the background color of the buttons
        for child in children:
            child['props'][
                'className'] = 'relative font-base max-w-full text-xs text-gray-800 dark:text-gray-100 flex flex-row hover:bg-slate-200 dark:hover:bg-slate-500 hover:shadow-md dark:hover:shadow-slate-950 px-4 py-2 rounded-lg mb-2 mx-4 items-center justify-between h-12 transition'
            child['props']['children'][0]['props']['disabled'] = False
            # Disabling the delete button
            # child['props']['children'][1]['props']['disabled'] = True
            # child['props']['children'][1]['props']['className'] = 'invisible'

        # Add a new button for the new motion data
        new_item = html.Div(
            # disabled=True,
            children=[
                html.Button(
                    id={'type': 'saved-button', 'index': f'{filename}'},
                    className='flex flex-row items-center',
                    children=[
                        # html.Img(src=app.get_asset_url('graph_gray.svg'),
                        #          className='w-6 h-6 mr-2'),
                        heart_navbar(filename),
                        reformat_file(filename),
                    ]),
                html.Button(
                    html.Img(src=app.get_asset_url('delete.svg'), className='w-5 h-5'),
                    id={'type': 'delete', 'index': filename},
                    className='visible hover:bg-red-600 rounded-full px-1 py-1 absolute right-1', disabled=False,
                    n_clicks=0
                ),
            ],

            # className='relative font-base max-w-full text-xs text-gray-200 flex flex-row hover:bg-slate-500 px-4 py-2 rounded-lg mb-2 mx-4 items-center justify-between h-12 transition')
            className='relative font-base max-w-full text-xs text-gray-800 dark:text-gray-100 flex flex-row bg-slate-200 dark:bg-slate-500 shadow-md dark:shadow-slate-950 px-4 py-2 rounded-lg mb-2 mx-4 items-center justify-between h-12 transition')
        children.insert(0, new_item)

        if not current_user.unlimited:
            current_user.n_analyses -= 1

        # Log number of analyses
        # Cant add value to None
        if current_user.analyzed is None:
            current_user.analyzed = 1
        else:
            current_user.analyzed += 1
        current_user.last_analyzed = datetime.datetime.now()
        db.session.commit()

        return [fig, fig3, fig4, fig5, fig6, fig11, fig12, fig13, fig14, fig15, fig16, children, children_upload,
                sequence_first, sequence_second, sequence_third,
                sequence_first_start, sequence_second_start, sequence_third_start,
                sequence_first_end, sequence_second_end, sequence_third_end,
                first_bp, second_bp, third_bp, first_bp_s, second_bp_s, third_bp_s, first_bp_e, second_bp_e, third_bp_e,
                temp, time_back, time_down,
                top_pos, impact_pos, end_pos, setup_pos, fps_saved,
                path, over_text, angle_swing_plane_text,
                disabled, disabled, disabled,
                upload_initial_class, upload_video_class,
                emoji_start, emoji_transition, '', tempo_text,  # backswing_text, downswing_text,
                f'/dashboard/{filename}'
                ]

    # Set pathname on button press
    @app.callback(
        Output('url', 'pathname', allow_duplicate=True),
        Input({'type': 'saved-button', 'index': ALL}, 'n_clicks'),
        State('url', 'pathname'),
        prevent_initial_call=False
    )
    def set_pathname_on_button_press(n_clicks, pathname):
        # print(pathname)

        if ctx.triggered[0]['value'] is None:
            return no_update

        if not os.path.exists(f'assets/save_data/{current_user.id}/{pathname.split("/")[2]}'):
            return '/dashboard/'

        pathname = ctx.triggered_id.index

        return f'/dashboard/{pathname}'

    # Save new margins to db
    @app.callback(
        Input('submit-new-margins', 'n_clicks'),
        [State('pelvis_rot_btn', 'n_clicks_timestamp'), State('pelvis_tilt_btn', 'n_clicks_timestamp'),
         State('thorax_rot_btn', 'n_clicks_timestamp'), State('thorax_tilt_btn', 'n_clicks_timestamp'),
         State('head_rot_btn', 'n_clicks_timestamp'), State('head_tilt_btn', 'n_clicks_timestamp'),
         State('setup_low_new_margins', 'value'), State('setup_high_new_margins', 'value'),
         State('top_low_new_margins', 'value'), State('top_high_new_margins', 'value'),
         State('impact_low_new_margins', 'value'), State('impact_high_new_margins', 'value'),
         ],
        prevent_initial_call=True
    )
    def save_new_margins(n_clicks, pelvis_rot_btn, pelvis_tilt_btn, thorax_rot_btn, thorax_tilt_btn, head_rot_btn,
                         head_tilt_btn, setup_low, setup_high, top_low, top_high, impact_low, impact_high):
        if n_clicks > 0:

            if pelvis_rot_btn is None:
                pelvis_rot_btn = 0
            if pelvis_tilt_btn is None:
                pelvis_tilt_btn = 0
            if thorax_rot_btn is None:
                thorax_rot_btn = 0
            if thorax_tilt_btn is None:
                thorax_tilt_btn = 0
            if head_rot_btn is None:
                head_rot_btn = 0
            if head_tilt_btn is None:
                head_tilt_btn = 0

            timestamp_dict = {'pelvis_rot_btn': pelvis_rot_btn, 'pelvis_tilt_btn': pelvis_tilt_btn,
                              'thorax_rot_btn': thorax_rot_btn, 'thorax_tilt_btn': thorax_tilt_btn,
                              'head_rot_btn': head_rot_btn, 'head_tilt_btn': head_tilt_btn}
            max_key = max(timestamp_dict, key=timestamp_dict.get)

            match max_key:
                case 'pelvis_rot_btn':
                    current_user.setup_low_pelvis_rot = setup_low
                    current_user.setup_high_pelvis_rot = setup_high
                    current_user.top_low_pelvis_rot = top_low
                    current_user.top_high_pelvis_rot = top_high
                    current_user.impact_low_pelvis_rot = impact_low
                    current_user.impact_high_pelvis_rot = impact_high
                case 'pelvis_tilt_btn':
                    current_user.setup_low_pelvis_tilt = setup_low
                    current_user.setup_high_pelvis_tilt = setup_high
                    current_user.top_low_pelvis_tilt = top_low
                    current_user.top_high_pelvis_tilt = top_high
                    current_user.impact_low_pelvis_tilt = impact_low
                    current_user.impact_high_pelvis_tilt = impact_high
                case 'thorax_rot_btn':
                    current_user.setup_low_thorax_rot = setup_low
                    current_user.setup_high_thorax_rot = setup_high
                    current_user.top_low_thorax_rot = top_low
                    current_user.top_high_thorax_rot = top_high
                    current_user.impact_low_thorax_rot = impact_low
                    current_user.impact_high_thorax_rot = impact_high
                case 'thorax_tilt_btn':
                    current_user.setup_low_thorax_tilt = setup_low
                    current_user.setup_high_thorax_tilt = setup_high
                    current_user.top_low_thorax_tilt = top_low
                    current_user.top_high_thorax_tilt = top_high
                    current_user.impact_low_thorax_tilt = impact_low
                    current_user.impact_high_thorax_tilt = impact_high
                case 'head_rot_btn':
                    current_user.setup_low_head_rot = setup_low
                    current_user.setup_high_head_rot = setup_high
                    current_user.top_low_head_rot = top_low
                    current_user.top_high_head_rot = top_high
                    current_user.impact_low_head_rot = impact_low
                    current_user.impact_high_head_rot = impact_high
                case 'head_tilt_btn':
                    current_user.setup_low_head_tilt = setup_low
                    current_user.setup_high_head_tilt = setup_high
                    current_user.top_low_head_tilt = top_low
                    current_user.top_high_head_tilt = top_high
                    current_user.impact_low_head_tilt = impact_low
                    current_user.impact_high_head_tilt = impact_high
                case _:
                    print('No match')

            db.session.commit()

    # Write margins to hidden div
    @app.callback(
        [Output('pelvis_rot_store', 'children'), Output('pelvis_bend_store', 'children'),
         Output('thorax_rot_store', 'children'), Output('thorax_bend_store', 'children'),
         Output('head_rot_store', 'children'), Output('head_tilt_store', 'children')
         ],
        [Input('pelvis_rot_store', 'children'), Input('pelvis_bend_store', 'children'),
         Input('thorax_rot_store', 'children'), Input('thorax_bend_store', 'children'),
         Input('head_rot_store', 'children'), Input('head_tilt_store', 'children')],
        prevent_initial_call=False
    )
    def update_margins(pelvis_rot, pelvis_tilt, thorax_rot, thorax_tilt, head_rot, head_tilt):

        setup_low_pelvis_rot = current_user.setup_low_pelvis_rot
        setup_high_pelvis_rot = current_user.setup_high_pelvis_rot
        top_low_pelvis_rot = current_user.top_low_pelvis_rot
        top_high_pelvis_rot = current_user.top_high_pelvis_rot
        impact_low_pelvis_rot = current_user.impact_low_pelvis_rot
        impact_high_pelvis_rot = current_user.impact_high_pelvis_rot

        setup_low_pelvis_tilt = current_user.setup_low_pelvis_tilt
        setup_high_pelvis_tilt = current_user.setup_high_pelvis_tilt
        top_low_pelvis_tilt = current_user.top_low_pelvis_tilt
        top_high_pelvis_tilt = current_user.top_high_pelvis_tilt
        impact_low_pelvis_tilt = current_user.impact_low_pelvis_tilt
        impact_high_pelvis_tilt = current_user.impact_high_pelvis_tilt

        setup_low_thorax_rot = current_user.setup_low_thorax_rot
        setup_high_thorax_rot = current_user.setup_high_thorax_rot
        top_low_thorax_rot = current_user.top_low_thorax_rot
        top_high_thorax_rot = current_user.top_high_thorax_rot
        impact_low_thorax_rot = current_user.impact_low_thorax_rot
        impact_high_thorax_rot = current_user.impact_high_thorax_rot

        setup_low_thorax_tilt = current_user.setup_low_thorax_tilt
        setup_high_thorax_tilt = current_user.setup_high_thorax_tilt
        top_low_thorax_tilt = current_user.top_low_thorax_tilt
        top_high_thorax_tilt = current_user.top_high_thorax_tilt
        impact_low_thorax_tilt = current_user.impact_low_thorax_tilt
        impact_high_thorax_tilt = current_user.impact_high_thorax_tilt

        setup_low_head_rot = current_user.setup_low_head_rot
        setup_high_head_rot = current_user.setup_high_head_rot
        top_low_head_rot = current_user.top_low_head_rot
        top_high_head_rot = current_user.top_high_head_rot
        impact_low_head_rot = current_user.impact_low_head_rot
        impact_high_head_rot = current_user.impact_high_head_rot

        setup_low_head_tilt = current_user.setup_low_head_tilt
        setup_high_head_tilt = current_user.setup_high_head_tilt
        top_low_head_tilt = current_user.top_low_head_tilt
        top_high_head_tilt = current_user.top_high_head_tilt
        impact_low_head_tilt = current_user.impact_low_head_tilt
        impact_high_head_tilt = current_user.impact_high_head_tilt

        positions = [setup_low_pelvis_rot, setup_high_pelvis_rot, top_low_pelvis_rot, top_high_pelvis_rot,
                     impact_low_pelvis_rot, impact_high_pelvis_rot,
                     setup_low_pelvis_tilt, setup_high_pelvis_tilt, top_low_pelvis_tilt, top_high_pelvis_tilt,
                     impact_low_pelvis_tilt, impact_high_pelvis_tilt,
                     setup_low_thorax_rot, setup_high_thorax_rot, top_low_thorax_rot, top_high_thorax_rot,
                     impact_low_thorax_rot, impact_high_thorax_rot,
                     setup_low_thorax_tilt, setup_high_thorax_tilt, top_low_thorax_tilt, top_high_thorax_tilt,
                     impact_low_thorax_tilt, impact_high_thorax_tilt,
                     setup_low_head_rot, setup_high_head_rot, top_low_head_rot, top_high_head_rot, impact_low_head_rot,
                     impact_high_head_rot,
                     setup_low_head_tilt, setup_high_head_tilt, top_low_head_tilt, top_high_head_tilt,
                     impact_low_head_tilt, impact_high_head_tilt
                     ]

        values = ['-3', '6', '-56', '-39', '29', '48', '-4', '6', '-14', '-6', '-2', '11', '7', '15', '-98', '-83',
                  '20', '37', '28', '40', '28', '40', '18', '30', '-6', '6', '-25', '-8', '-6', '15', '-3', '7', '-16',
                  '-3', '1', '18']

        result = [f'{pos}' if pos is not None else val for pos, val in zip(positions, values)]

        pelvis_rot_margins = f'{result[0]}, {result[1]}, {result[2]}, {result[3]}, {result[4]}, {result[5]}'
        pelvis_tilt_margins = f'{result[6]}, {result[7]}, {result[8]}, {result[9]}, {result[10]}, {result[11]}'
        thorax_rot_margins = f'{result[12]}, {result[13]}, {result[14]}, {result[15]}, {result[16]}, {result[17]}'
        thorax_tilt_margins = f'{result[18]}, {result[19]}, {result[20]}, {result[21]}, {result[22]}, {result[23]}'
        head_rot_margins = f'{result[24]}, {result[25]}, {result[26]}, {result[27]}, {result[28]}, {result[29]}'
        head_tilt_margins = f'{result[30]}, {result[31]}, {result[32]}, {result[33]}, {result[34]}, {result[35]}'

        return pelvis_rot_margins, pelvis_tilt_margins, thorax_rot_margins, thorax_tilt_margins, head_rot_margins, head_tilt_margins

    @app.callback(
        Input('heart', 'n_clicks'),
        [State('video', 'url')],
        prevent_initial_call=True
    )
    def heart(n_clicks, src):
        if n_clicks is not None:
            vid = src.split('/')[3]
            vid_row = UserLikes.query.filter_by(user_id=current_user.id, video_id=vid).first()

            if vid_row is None:
                like_row = UserLikes(user_id=current_user.id, video_id=vid, like=True)
                db.session.add(like_row)
            else:
                if vid_row.like:
                    vid_row.like = False
                else:
                    vid_row.like = True

            db.session.commit()

    @app.callback(
        Output('heart', 'className'),
        Input('video', 'url'),
        [State('heart', 'className')],
        prevent_initial_call=False
    )
    def heart_state(src, class_name):
        if src is not None:
            vid = src.split('/')[3]
            vid_row = UserLikes.query.filter_by(user_id=current_user.id, video_id=vid).first()
            if vid_row is None:
                return class_name
            else:
                if vid_row.like:
                    return class_name + ' is-active'
                else:
                    return class_name

    # TODO Save new positions
    @app.callback(
        Output('backswing', 'children', allow_duplicate=True), Output('downswing', 'children', allow_duplicate=True),
        Output('tempo', 'children', allow_duplicate=True),
        Output('arm_path', 'children', allow_duplicate=True),
        Output('swing_plane_angle', 'children', allow_duplicate=True),
        Output('setup_pos', 'children', allow_duplicate=True), Output('top_pos', 'children', allow_duplicate=True),
        Output('impact_pos', 'children', allow_duplicate=True),
        Output('end_pos', 'children', allow_duplicate=True),
        Input('edit_positions_save', 'n_clicks'),
        State('setup_pos_button', 'n_clicks_timestamp'), State('top_pos_button', 'n_clicks_timestamp'),
        State('impact_pos_button', 'n_clicks_timestamp'), State('end_pos_button', 'n_clicks_timestamp'),
        State('video', 'currentTime'), State('video', 'duration'), State('fps_saved', 'children'),
        State('video', 'url'),
        State('setup_pos', 'children'), State('top_pos', 'children'), State('impact_pos', 'children'),
        State('end_pos', 'children'), State('arm_path', 'children'), State('swing_plane_angle', 'children'),
        State('backswing', 'children'), State('downswing', 'children'), State('tempo', 'children'),

        prevent_initial_call=True
    )
    def save_new_positions(n_clicks, setup_time, top_time, impact_time, end_time, current_time, duration, fps, url,
                           setup_pos, top_pos, impact_pos, end_pos, fig, angle_text, time_back, time_down, temp):

        if n_clicks is not None:
            if n_clicks > 0:
                setup_time = 0 if setup_time is None else setup_time
                top_time = 0 if top_time is None else top_time
                impact_time = 0 if impact_time is None else impact_time
                end_time = 0 if end_time is None else end_time

                timestamp_dict = {'setup': setup_time, 'top': top_time, 'impact': impact_time, 'end': end_time}
                max_key = max(timestamp_dict, key=timestamp_dict.get)

                ratio = current_time / duration

                vid = url.split('/')[3]
                vid_row = UserLikes.query.filter_by(user_id=current_user.id, video_id=vid).first()

                if vid_row is None:
                    db.session.add(UserLikes(user_id=current_user.id, video_id=vid))
                    db.session.commit()

                vid_row = UserLikes.query.filter_by(user_id=current_user.id, video_id=vid).first()

                # Read data from parquet file
                data = pd.read_parquet(f'assets/save_data/{current_user.id}/{vid}/{vid}.parquet')
                x = data['arm_x']
                y = data['arm_y']
                z = data['arm_z']

                length = len(x)

                match max_key:
                    case 'setup':
                        vid_row.setup = ratio
                        vid_row.setup_calc = setup_pos
                        setup_pos = ratio

                        # Tempo
                        temp, time_back, time_down = tempo(setup_pos * length, top_pos * length, impact_pos * length,
                                                           fps)

                    case 'top':
                        vid_row.top = ratio
                        vid_row.top_calc = top_pos
                        top_pos = ratio

                        # Tempo
                        temp, time_back, time_down = tempo(setup_pos * length, top_pos * length, impact_pos * length,
                                                           fps)

                    case 'impact':
                        vid_row.impact = ratio
                        vid_row.impact_calc = impact_pos
                        impact_pos = ratio

                        # Tempo
                        temp, time_back, time_down = tempo(setup_pos * length, top_pos * length, impact_pos * length,
                                                           fps)

                    case 'end':
                        vid_row.end = ratio
                        vid_row.end_calc = end_pos
                        end_pos = ratio

                        # Tempo
                        temp, time_back, time_down = tempo(setup_pos * length, top_pos * length, impact_pos * length,
                                                           fps)

                    case _:
                        print('Error: No position selected')
                        temp = '-'
                        time_back = '- s'
                        time_down = '- s'

                # 3D plot
                path, angle = hand_path_3d(x, y, z, int(setup_pos * length), int(end_pos * length),
                                           int(top_pos * length),
                                           fps)

                angle_text = html.Div(
                    children=[html.Div('Swing Plane Angle:', className='text-base font-normal'),
                              f'{int(angle)}°'])

                fig = dcc.Graph(
                    id='arm_path_3d',
                    figure=path,
                    config=config_3D,
                    className='w-[350px] lg:w-[500px] xl:w-full h-fit relative',
                )

                db.session.commit()

        return time_back, time_down, temp, fig, angle_text, setup_pos, top_pos, impact_pos, end_pos

    # Reset positions
    @app.callback(
        Output('backswing', 'children'), Output('downswing', 'children'), Output('tempo', 'children'),
        Output('arm_path', 'children'), Output('swing_plane_angle', 'children'),
        Output('setup_pos', 'children'), Output('top_pos', 'children'), Output('impact_pos', 'children'),
        Output('end_pos', 'children'),
        Input('edit_positions_reset', 'n_clicks'),
        State('setup_pos_button', 'n_clicks_timestamp'), State('top_pos_button', 'n_clicks_timestamp'),
        State('impact_pos_button', 'n_clicks_timestamp'), State('end_pos_button', 'n_clicks_timestamp'),
        State('video', 'currentTime'), State('video', 'duration'), State('fps_saved', 'children'),
        State('video', 'url'),
        State('setup_pos', 'children'), State('top_pos', 'children'), State('impact_pos', 'children'),
        State('end_pos', 'children'), State('arm_path', 'children'), State('swing_plane_angle', 'children'),
        State('backswing', 'children'), State('downswing', 'children'), State('tempo', 'children'),

        prevent_initial_call=True
    )
    def reset_positions(n_clicks, setup_time, top_time, impact_time, end_time, current_time, duration, fps, url,
                        setup_pos, top_pos, impact_pos, end_pos, fig, angle_text, time_back, time_down, temp):

        if n_clicks is not None:
            if n_clicks > 0:
                setup_time = 0 if setup_time is None else setup_time
                top_time = 0 if top_time is None else top_time
                impact_time = 0 if impact_time is None else impact_time
                end_time = 0 if end_time is None else end_time

                timestamp_dict = {'setup': setup_time, 'top': top_time, 'impact': impact_time, 'end': end_time}
                max_key = max(timestamp_dict, key=timestamp_dict.get)

                vid = url.split('/')[3]
                vid_row = UserLikes.query.filter_by(user_id=current_user.id, video_id=vid).first()

                if vid_row is None:
                    db.session.add(UserLikes(user_id=current_user.id, video_id=vid))
                    db.session.commit()

                vid_row = UserLikes.query.filter_by(user_id=current_user.id, video_id=vid).first()

                # Read data from parquet file
                data = pd.read_parquet(f'assets/save_data/{current_user.id}/{vid}/{vid}.parquet')
                x = data['arm_x']
                y = data['arm_y']
                z = data['arm_z']

                length = len(x)

                match max_key:
                    case 'setup':
                        vid_row.setup = None

                        setup_pos = vid_row.setup_calc

                        if vid_row.top is not None:
                            top_pos = vid_row.top
                        if vid_row.impact is not None:
                            impact_pos = vid_row.impact

                        # Tempo
                        temp, time_back, time_down = tempo(setup_pos * length, top_pos * length, impact_pos * length,
                                                           fps)

                    case 'top':
                        vid_row.top = None
                        top_pos = vid_row.top_calc

                        if vid_row.setup is not None:
                            setup_pos = vid_row.setup
                        if vid_row.impact is not None:
                            impact_pos = vid_row.impact

                        temp, time_back, time_down = tempo(setup_pos * length, top_pos * length, impact_pos * length,
                                                           fps)

                    case 'impact':
                        vid_row.impact = None
                        impact_pos = vid_row.impact_calc

                        if vid_row.setup is not None:
                            setup_pos = vid_row.setup
                        if vid_row.top is not None:
                            top_pos = vid_row.top

                        temp, time_back, time_down = tempo(setup_pos * length, top_pos * length, impact_pos * length,
                                                           fps)

                    case 'end':
                        vid_row.end = None
                        end_pos = vid_row.end_calc

                        temp, time_back, time_down = tempo(setup_pos * length, top_pos * length, impact_pos * length,
                                                           fps)

                    case _:
                        print('Error: No position selected')

                        temp, time_back, time_down = tempo(setup_pos * length, top_pos * length, impact_pos * length,
                                                           fps)

                # 3D plot
                path, angle = hand_path_3d(x, y, z, int(setup_pos * length), int(end_pos * length),
                                           int(top_pos * length),
                                           fps)

                angle_text = html.Div(
                    children=[html.Div('Swing Plane Angle:', className='text-base font-normal'),
                              f'{int(angle)}°'])

                fig = dcc.Graph(
                    id='arm_path_3d',
                    figure=path,
                    config=config_3D,
                    className='w-[350px] lg:w-[500px] xl:w-full h-fit relative',
                )

                db.session.commit()

        return time_back, time_down, temp, fig, angle_text, setup_pos, top_pos, impact_pos, end_pos

    # Hide selection view with save
    app.clientside_callback(
        ClientsideFunction(
            namespace='clientside',
            function_name='hideSelectionView'
        ),
        Input('submit-new-margins', 'n_clicks'),
        prevent_initial_call=True
    )

    # Hide selection view without save
    app.clientside_callback(
        ClientsideFunction(
            namespace='clientside',
            function_name='hideSelectionViewCross'
        ),
        Input('selection-view-dismiss', 'n_clicks'),
        prevent_initial_call=True
    )

    # Show selection view
    app.clientside_callback(
        ClientsideFunction(
            namespace='clientside',
            function_name='showSelectionView'
        ),
        [
            Output('setup_low_new_margins', 'value'), Output('setup_high_new_margins', 'value'),
            Output('top_low_new_margins', 'value'), Output('top_high_new_margins', 'value'),
            Output('impact_low_new_margins', 'value'), Output('impact_high_new_margins', 'value'),
        ],
        [Input('pelvis_rot_btn', 'n_clicks'), Input('pelvis_tilt_btn', 'n_clicks'),
         Input('thorax_rot_btn', 'n_clicks'), Input('thorax_tilt_btn', 'n_clicks'),
         Input('head_rot_btn', 'n_clicks'), Input('head_tilt_btn', 'n_clicks'),
         ],
        # State('selection-view', 'className'),
        prevent_initial_call=True
    )

    # Show navbar on click
    app.clientside_callback(
        ClientsideFunction(
            namespace='clientside',
            function_name='showNavbar'
        ),
        [Output('sidebar', 'className'), Output('navbar-mobile', 'className')],
        [Input('menu-button', 'n_clicks'), Input('sidebar-header', 'n_clicks'), Input('navbar-mobile', 'n_clicks')],
        [State('sidebar', 'className'), State('navbar-mobile', 'className'), ],
        prevent_initial_call=True
    )

    # Help box on click
    app.clientside_callback(
        '''
        function showHelp(n_clicks, help_class) {
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

        Output('video', 'seekTo'), Output('edit_positions', 'disabled'),
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
         Output('pelvis_sway_val', 'children'), Output('thorax_sway_val', 'children'),
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

    # Tempo slider position
    app.clientside_callback(
        ClientsideFunction(
            namespace='clientside',
            function_name='tempoSlider'
        ),
        Output('tempo_slider', 'style'),
        Input('tempo', 'children'),
    )

    # Show heart
    app.clientside_callback(
        ClientsideFunction(
            namespace='clientside',
            function_name='toggleHeart'
        ),
        Input('heart', 'n_clicks'),
        State('video', 'url'),
        prevent_initial_call=True
    )

    # Show delete view file
    # Should be called before toggleDeleteView
    app.clientside_callback(
        ClientsideFunction(
            namespace='clientside',
            function_name='deleteViewFile'
        ),
        [Output('delete-file-name', 'children')],
        Input({'type': 'delete', 'index': ALL}, 'n_clicks'),
        prevent_initial_call=True
    )

    # Show delete view
    app.clientside_callback(
        ClientsideFunction(
            namespace='clientside',
            function_name='toggleDeleteView'
        ),
        Output({'type': 'delete', 'index': MATCH}, 'n_clicks'),
        Input({'type': 'delete', 'index': MATCH}, 'n_clicks'),
        prevent_initial_call=True
    )

    # Hide delete view
    app.clientside_callback(
        ClientsideFunction(
            namespace='clientside',
            function_name='hideDeleteView'
        ),
        Input('delete-file', 'n_clicks'), Input('cancel-delete-file', 'n_clicks'),
        prevent_initial_call=True
    )

    # TODO Show edit positions save button
    app.clientside_callback(
        ClientsideFunction(
            namespace='clientside',
            function_name='showEditPositionsSaveButton'
        ),
        Input('edit_positions', 'n_clicks'), Input('edit_positions_save', 'n_clicks'),
        Input('edit_positions_reset', 'n_clicks'),
        prevent_initial_call=True
    )

    # Show video frames
    app.clientside_callback(
        ClientsideFunction(
            namespace='clientside',
            function_name='showVideoFrames'
        ),
        Input('show_overlay', 'n_clicks'), Input('show_overlay_mobile', 'n_clicks'),
        State('setup_pos', 'children'), State('impact_pos', 'children'), State('top_pos', 'children'),
        prevent_initial_call=True
    )

    # Show report text
    app.clientside_callback(
        ClientsideFunction(
            namespace='clientside',
            function_name='reportText'
        ),
        Input('show_overlay', 'n_clicks'), Input('show_overlay_mobile', 'n_clicks'),
        State('sequence', 'figure'), State('pelvis_rotation', 'figure'), State('pelvis_displacement', 'figure'),
        State('thorax_rotation', 'figure'), State('thorax_displacement', 'figure'), State('s_tilt', 'figure'),
        State('h_tilt', 'figure'), State('h_rotation', 'figure'), State('arm_length', 'figure'),
        State('spine_rotation', 'figure'), State('arm_angle', 'figure'),
        State('setup_pos', 'children'), State('impact_pos', 'children'), State('top_pos', 'children'),
        prevent_initial_call=True
    )

    # TODO overlay
    # Show overlay
    app.clientside_callback(
        ClientsideFunction(
            namespace='clientside',
            function_name='showOverlay'
        ),
        Input('show_overlay', 'n_clicks'), Input('show_overlay_mobile', 'n_clicks'), Input('hide_overlay', 'n_clicks'),
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
                ),
                className='w-full'
            )
        ],
            className='bg-white dark:bg-gray-700 shadow dark:shadow-slate-950 rounded-2xl flex items-start justify-center mb-5 text-center inline-block flex-col w-full h-96 backdrop-blur-md bg-opacity-80 border border-gray-100 dark:border-gray-900',
        ),
    ]

    return [fig, fig3, fig4, fig5, fig6, fig11, fig12, fig13, fig14, fig15, fig16, children, children_upload, []]


def kinematic_sequence(pelvis_rotation, thorax_rotation, arm_rotation, fps):
    # Get the kinematic transition sequence
    hip_index = find_closest_zero_intersection_left_of_max(
        np.gradient(filter_data(pelvis_rotation, fps)))
    thorax_index = find_closest_zero_intersection_left_of_max(
        np.gradient(filter_data(thorax_rotation, fps)))
    arm_index = find_closest_zero_intersection_left_of_max(
        -np.gradient(filter_data(arm_rotation, fps)))

    # print(hip_index, thorax_index, arm_index)

    # Colors for hip, thorax and arm
    sequence = {'bg-[#6266F6]': hip_index, 'bg-[#E74D39]': thorax_index, 'bg-[#2BC48C]': arm_index}

    # Colors sorted by index
    sequence = sorted(sequence.items(), key=lambda item: item[1])

    # Body parrt sorted by index
    body_part = {'Pelvis': hip_index, 'Thorax': thorax_index, 'Arm': arm_index}
    body_part = sorted(body_part.items(), key=lambda item: item[1])
    body_part = [body_part[0][0], body_part[1][0], body_part[2][0]]

    # Update colors
    sequence_first = f'text-sm font-medium text-gray-100  rounded-full w-16 py-1 px-2 flex flex-none items-center justify-center border-4 border-[#6266F6] {sequence[0][0]}'
    sequence_second = f'text-sm font-medium text-gray-100  rounded-full w-16 py-1 px-2 flex flex-none items-center justify-center border-4 border-[#E74D39] {sequence[1][0]}'
    sequence_third = f'text-sm font-medium text-gray-100 rounded-full w-16 py-1 px-2 flex flex-none items-center justify-center border-4 border-[#2BC48C] {sequence[2][0]}'

    emoji_transition = '😍' if body_part == ['Pelvis', 'Thorax', 'Arm'] else '🧐'

    return sequence_first, sequence_second, sequence_third, body_part[0], body_part[1], body_part[2], \
        thorax_index, emoji_transition


def kinematic_sequence_start(pelvis_rotation, thorax_rotation, arm_rotation, fps):
    # Get the kinematic start sequence
    argmax = np.argmax(arm_rotation)
    hip_index = find_closest_zero_intersection_left_of_min(
        np.gradient(filter_data(pelvis_rotation[:argmax], fps)))
    thorax_index = find_closest_zero_intersection_left_of_min(
        np.gradient(filter_data(thorax_rotation[:argmax], fps)))
    arm_index = find_closest_zero_intersection_left_of_min(
        np.gradient(filter_data(arm_rotation[:argmax], fps)))

    # Colors for hip, thorax and arm
    sequence = {'bg-[#6266F6]': hip_index, 'bg-[#E74D39]': thorax_index, 'bg-[#2BC48C]': arm_index}

    # Colors sorted by index
    sequence = sorted(sequence.items(), key=lambda item: item[1])

    # Body part sorted by index
    body_part = {'Pelvis': hip_index, 'Thorax': thorax_index, 'Arm': arm_index}
    body_part = sorted(body_part.items(), key=lambda item: item[1])

    # Update colors
    sequence_first = f'text-sm font-medium text-gray-100 rounded-full w-16 py-2 px-4 flex flex-none items-center justify-center {sequence[0][0]}'
    sequence_second = f'text-sm font-medium text-gray-100 rounded-full w-16 py-2 px-4 flex flex-none items-center justify-center {sequence[1][0]}'
    sequence_third = f'text-sm font-medium text-gray-100 rounded-full w-16 py-2 px-4 flex flex-none items-center justify-center {sequence[2][0]}'

    sequence_start_emoji = ' 😍' if body_part[0][0] != 'Pelvis' else '🧐'

    return sequence_first, sequence_second, sequence_third, body_part[0][0], body_part[1][0], body_part[2][
        0], thorax_index, sequence_start_emoji


def kinematic_sequence_end(pelvis_rotation, thorax_rotation, arm_rotation, fps):
    # Get the kinematic end sequence
    hip_index = find_closest_zero_intersection_right_of_max(
        np.gradient(filter_data(pelvis_rotation, fps)))
    thorax_index = find_closest_zero_intersection_right_of_max(
        np.gradient(filter_data(thorax_rotation, fps)))
    arm_index = find_closest_zero_intersection_right_of_max(
        np.gradient(filter_data(arm_rotation, fps)))

    # Colors for hip, thorax and arm
    sequence = {'bg-[#6266F6]': hip_index, 'bg-[#E74D39]': thorax_index, 'bg-[#2BC48C]': arm_index}

    # Colors sorted by index
    sequence = sorted(sequence.items(), key=lambda item: item[1])

    # Body part sorted by index
    body_part = {'Pelvis': hip_index, 'Thorax': thorax_index, 'Arm': arm_index}
    body_part = sorted(body_part.items(), key=lambda item: item[1])

    # Update colors
    sequence_first = f'text-sm font-medium text-gray-100 bg-[#2BC48C] rounded-full w-18 py-1 px-2 flex flex-none items-center justify-center {sequence[0][0]}'
    sequence_second = f'text-sm font-medium text-gray-100 bg-[#2BC48C] rounded-full w-18 py-1 px-2 flex flex-none items-center justify-center {sequence[1][0]}'
    sequence_third = f'text-sm font-medium text-gray-100 bg-[#2BC48C] rounded-full w-18 py-1 px-2 flex flex-none items-center justify-center {sequence[2][0]}'

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
            title = '3D Hand Path and Swing Plane'

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
                    className='text-base font-medium text-slate-900 hover:text-gray-600 dark:text-gray-100 dark:hover:text-gray-300 mt-10 mx-4 sm:mx-10 relative text-left',
                    children=[
                        title
                    ]
                ),
            ]
        ),
        html.Div(
            # id=f'{plot_type}_help',
            id={'type': 'help_box', 'index': plot_type},
            className='absolute top-20 right-3 left-4 sm:left-10 sm:w-96 bg-gray-200 border border-opacity-30 border-gray-400 shadow-sm rounded-2xl backdrop-blur-md bg-opacity-80 hidden z-10',
            children=[
                html.Div(
                    className='flex flex-row px-4 py-4 text-sm text-gray-900 text-justify',
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
        className="relative h-[500px] bg-white dark:bg-gray-700 shadow dark:shadow-slate-950 rounded-2xl flex items-center justify-center mb-5 backdrop-blur-md bg-opacity-80 border border-gray-100 dark:border-gray-900 flex-col w-full",
    ),


def get_tempo_text(tempo):
    tempo = float(tempo)
    if tempo < 2.4:
        return 'Relax, your swing is a bit hectic'
    elif tempo > 3.6:
        return 'Your tempo is a bit slow'
    else:
        return 'Your tempo is good'


def get_backswing_text(backswing):
    backswing = float(backswing.split(' ')[0])
    if backswing < 0.6:
        return 'Try to swing a bit slower, your backswing is too short'
    elif backswing > 0.9:
        return 'Try to swing a bit faster, your backswing is too long'
    else:
        return 'Your backswing is good'


def get_downswing_text(downswing):
    return ''
    downswing = float(downswing.split(' ')[0])
    if downswing < 0.2:
        return 'Relax, your downsing is a bit fast'
    elif downswing > 0.30:
        return 'Try to swing a bit faster, your downswing is too slow'
    else:
        return 'Your downswing is good'


if __name__ == '__main__':
    pass
