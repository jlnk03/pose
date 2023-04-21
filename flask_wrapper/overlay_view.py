from dash import html


def report_text_view(id1, id2, img1, img2):
    layout = html.Div(
        className='flex flex-col justify-center w-full h-full gap-4',
        children=[
            html.Div(
                className='flex flex-row sm:text-base text-sm text-left text-gray-900 dark:text-gray-100 mb-4 gap-2',
                children=[
                    html.Img(src='assets/' + img1,
                             className='dark:border-indigo-400 border-indigo-600 border-2 rounded-full h-8 w-8 text-center flex flex-none items-center justify-center'),
                    html.Span(id=id1,
                              className='sm:text-base text-sm text-left text-gray-900 dark:text-gray-100 mb-4'),
                ]
            ),
            html.Div(
                className='flex flex-row sm:text-base text-sm text-left text-gray-900 dark:text-gray-100 mb-4 gap-2',
                children=[
                    html.Img(src='assets/' + img2,
                             className='dark:border-indigo-400 border-indigo-600 border-2 rounded-full h-8 w-8 text-center flex flex-none items-center justify-center'),
                    html.Span(id=id2,
                              className='sm:text-base text-sm text-left text-gray-900 dark:text-gray-100 mb-4'),
                ]
            ),
        ]
    )

    return layout


def report_focus_view(id1, id2):
    layout = html.Div(
        className='flex flex-col justify-center w-full h-full gap-4',
        children=[
            html.Div(
                className='flex flex-row sm:text-base text-sm text-left text-gray-900 dark:text-gray-100 mb-4 gap-2',
                children=[
                    html.Span('1',
                              className='dark:border-indigo-400 border-indigo-600 border-2 rounded-full h-8 w-8 text-center flex-none flex items-center justify-center'),
                    html.Span(id=id1,
                              className='flex justify-center items-center')
                ]
            ),
            html.Div(
                className='flex flex-row sm:text-base text-sm text-left text-gray-900 dark:text-gray-100 mb-4 gap-2',
                children=[
                    html.Span('2',
                              className='dark:border-indigo-400 border-indigo-600 border-2 rounded-full h-8 w-8 text-center flex flex-none items-center justify-center'),
                    html.Span(id=id2,
                              className='flex justify-center items-center')
                ]
            ),

        ]
    ),

    return layout


overlay = html.Div(
    className='w-full h-full z-50',
    children=[
        html.Button(id='hide_overlay', className='w-full h-32 bg-black bg-opacity-50'),
        html.Div(
            className='fixed top-24 w-full bottom-0 dark:bg-slate-700 bg-[#FAF7F5] rounded-t-3xl justify-center flex flex-none',
            children=[
                html.Div(
                    className='relative h-full flex flex-col sm:px-6 px-2 py-6 w-full',
                    children=[
                        html.Div(
                            className='w-full h-full flex flex-col overflow-y-auto relative',
                            children=[
                                html.Div('Report',
                                         className='sm:text-3xl text-xl text-left font-bold mt-4 sm:mb-10 mb-6 text-gray-900 dark:text-gray-100'),

                                html.Span('Setup',
                                          className='sm:text-2xl text-lg text-left font-bold text-gray-900 dark:text-gray-100 mb-1'),

                                html.Div(
                                    className='flex flex-row flex-none sm:h-96 h-56 overflow-x-auto w-full snap-x snap-mandatory  gap-4',
                                    children=[
                                        html.Canvas(id='setup_frame',
                                                    className='rounded-2xl max-h-56 max-w-56 sm:max-h-96 sm:max-w-96 snap-start'),

                                        html.Div(
                                            className='flex flex-col bg-white dark:bg-gray-800 rounded-2xl p-4 w-56 grow flex-none snap-start',
                                            children=[
                                                html.Span('Focus',
                                                          className='sm:text-xl text-left font-medium text-gray-900 dark:text-gray-100 mb-2'),

                                                html.Div(
                                                    report_focus_view('focus_report_text', 'focus_report_text_2'),
                                                    className='w-full h-full'
                                                )

                                            ]
                                        ),

                                        html.Div(
                                            className='flex flex-col bg-white dark:bg-gray-800 rounded-2xl p-4 w-56 grow flex-none snap-start',
                                            children=[
                                                html.Span('Pelvis',
                                                          className='sm:text-xl text-left font-medium text-gray-900 dark:text-gray-100 mb-2'),

                                                html.Div(
                                                    className='flex flex-col justify-center w-full h-full gap-4',
                                                    children=[

                                                        html.Div(
                                                            className='flex flex-row sm:text-base text-sm text-left text-gray-900 dark:text-gray-100 mb-4 gap-2',
                                                            children=[
                                                                html.Img(src='assets/rotation.png',
                                                                         className='dark:border-indigo-400 border-indigo-600 border-2 rounded-full h-8 w-8 text-center flex flex-none items-center justify-center'),
                                                                html.Span(id='pelvis_report_text',
                                                                          className='flex justify-center items-center'),
                                                            ]
                                                        ),

                                                        html.Div(
                                                            className='flex flex-row sm:text-base text-sm text-left text-gray-900 dark:text-gray-100 mb-4 gap-2',
                                                            children=[
                                                                html.Img(src='assets/tilt.png',
                                                                         className='dark:border-indigo-400 border-indigo-600 border-2 rounded-full h-8 w-8 text-center flex flex-none items-center justify-center'),
                                                                html.Span(id='pelvis_report_text_tilt',
                                                                          className='flex justify-center items-center'),
                                                            ]
                                                        ),
                                                    ]
                                                )
                                            ]
                                        ),
                                        html.Div(
                                            className='flex flex-col bg-white dark:bg-gray-800 rounded-2xl p-4 w-56 grow flex-none snap-start',
                                            children=[
                                                html.Span('Thorax',
                                                          className='sm:text-xl text-left font-medium text-gray-900 dark:text-gray-100 mb-2'),

                                                html.Div(
                                                    className='flex flex-col justify-center w-full h-full gap-4',
                                                    children=[

                                                        html.Div(
                                                            className='flex flex-row sm:text-base text-sm text-left text-gray-900 dark:text-gray-100 mb-4 gap-2',
                                                            children=[
                                                                html.Img(src='assets/rotation.png',
                                                                         className='dark:border-indigo-400 border-indigo-600 border-2 rounded-full h-8 w-8 text-center flex flex-none items-center justify-center'),
                                                                html.Span(id='thorax_report_text',
                                                                          className='sm:text-base text-sm text-left text-gray-900 dark:text-gray-100 mb-4'),
                                                            ]
                                                        ),

                                                        html.Div(
                                                            className='flex flex-row sm:text-base text-sm text-left text-gray-900 dark:text-gray-100 mb-4 gap-2',
                                                            children=[
                                                                html.Img(src='assets/bend.png',
                                                                         className='dark:border-indigo-400 border-indigo-600 border-2 rounded-full h-8 w-8 text-center flex flex-none items-center justify-center'),
                                                                html.Span(id='thorax_report_text_bend',
                                                                          className='sm:text-base text-sm text-left text-gray-900 dark:text-gray-100 mb-4'),
                                                            ]
                                                        )
                                                    ]
                                                )

                                            ]
                                        ),
                                        html.Div(
                                            className='flex flex-col w-56 grow flex-none bg-white dark:bg-gray-800 rounded-2xl p-4 snap-start',
                                            children=[
                                                html.Span('Head',
                                                          className='sm:text-xl text-left font-medium text-gray-900 dark:text-gray-100 mb-2'),

                                                html.Div(
                                                    className='flex flex-col justify-center w-full h-full gap-4',
                                                    children=[
                                                        html.Div(
                                                            className='flex flex-row sm:text-base text-sm text-left text-gray-900 dark:text-gray-100 mb-4 gap-2',
                                                            children=[
                                                                html.Img(src='assets/rotation.png',
                                                                         className='dark:border-indigo-400 border-indigo-600 border-2 rounded-full h-8 w-8 text-center flex flex-none items-center justify-center'),
                                                                html.Span(id='head_report_text',
                                                                          className='sm:text-base text-sm text-left text-gray-900 dark:text-gray-100 mb-4'),
                                                            ]
                                                        ),
                                                        html.Div(
                                                            className='flex flex-row sm:text-base text-sm text-left text-gray-900 dark:text-gray-100 mb-4 gap-2',
                                                            children=[
                                                                html.Img(src='assets/tilt.png',
                                                                         className='dark:border-indigo-400 border-indigo-600 border-2 rounded-full h-8 w-8 text-center flex flex-none items-center justify-center'),
                                                                html.Span(id='head_report_text_tilt',
                                                                          className='sm:text-base text-sm text-left text-gray-900 dark:text-gray-100 mb-4'),
                                                            ]
                                                        ),
                                                    ]
                                                )
                                            ]
                                        ),
                                    ]
                                ),

                                html.Span('Top',
                                          className='sm:text-2xl text-lg text-left font-bold text-gray-900 dark:text-gray-100 mb-1 mt-6'),
                                html.Div(
                                    className='flex flex-row flex-none sm:h-96 h-56 overflow-x-auto w-full snap-x snap-mandatory gap-4',
                                    children=[
                                        html.Canvas(id='top_frame',
                                                    className='rounded-2xl max-h-56 max-w-56 sm:max-h-96 sm:max-w-96 snap-start'),

                                        html.Div(
                                            className='flex flex-col bg-white dark:bg-gray-800 rounded-2xl p-4 w-56 grow flex-none snap-start',
                                            children=[
                                                html.Span('Focus',
                                                          className='sm:text-xl text-left font-medium text-gray-900 dark:text-gray-100 mb-2'),

                                                html.Div(
                                                    report_focus_view('focus_report_text_top',
                                                                      'focus_report_text_2_top'),
                                                    className='w-full h-full'
                                                )

                                            ]
                                        ),

                                        html.Div(
                                            className='flex flex-col bg-white dark:bg-gray-800 rounded-2xl p-4 w-56 grow flex-none snap-start',
                                            children=[
                                                html.Span('Pelvis',
                                                          className='sm:text-xl text-left font-medium text-gray-900 dark:text-gray-100 mb-2'),

                                                html.Div(
                                                    report_text_view('pelvis_report_text_top',
                                                                     'pelvis_report_text_tilt_top', 'rotation.png',
                                                                     'tilt.png'),
                                                    className='w-full h-full'),
                                            ]
                                        ),
                                        html.Div(
                                            className='flex flex-col bg-white dark:bg-gray-800 rounded-2xl p-4 w-56 grow flex-none snap-start',
                                            children=[
                                                html.Span('Thorax',
                                                          className='sm:text-xl text-left font-medium text-gray-900 dark:text-gray-100 mb-2'),

                                                html.Div(
                                                    report_text_view('thorax_report_text_top',
                                                                     'thorax_report_text_bend_top', 'rotation.png',
                                                                     'bend.png'),
                                                    className='w-full h-full'
                                                )

                                            ]
                                        ),
                                        html.Div(
                                            className='flex flex-col bg-white dark:bg-gray-800 rounded-2xl p-4 w-56 grow flex-none snap-start',
                                            children=[
                                                html.Span('Head',
                                                          className='sm:text-xl text-left font-medium text-gray-900 dark:text-gray-100 mb-2'),

                                                html.Div(
                                                    report_text_view('head_report_text_top',
                                                                     'head_report_text_tilt_top', 'rotation.png',
                                                                     'tilt.png'),
                                                    className='w-full h-full'
                                                )

                                            ]
                                        ),

                                    ]
                                ),

                                html.Span('Impact',
                                          className='sm:text-2xl text-lg text-left font-bold text-gray-900 dark:text-gray-100 mb-1 mt-6'),
                                html.Div(
                                    className='flex flex-row flex-none sm:h-96 h-56 overflow-x-auto w-full snap-x snap-mandatory gap-4',
                                    children=[
                                        html.Canvas(id='impact_frame',
                                                    className='rounded-2xl max-h-56 max-w-56 sm:max-h-96 sm:max-w-96 snap-start'),

                                        html.Div(
                                            className='flex flex-col bg-white dark:bg-gray-800 rounded-2xl p-4 w-56 grow flex-none snap-start',
                                            children=[
                                                html.Span('Focus',
                                                          className='sm:text-xl text-left font-medium text-gray-900 dark:text-gray-100 mb-2'),

                                                html.Div(
                                                    report_focus_view('focus_report_text_impact',
                                                                      'focus_report_text_2_impact'),
                                                    className='w-full h-full'
                                                )

                                            ]
                                        ),

                                        html.Div(
                                            className='flex flex-col bg-white dark:bg-gray-800 rounded-2xl p-4 w-56 grow flex-none snap-start',
                                            children=[
                                                html.Span('Pelvis',
                                                          className='sm:text-xl text-left font-medium text-gray-900 dark:text-gray-100 mb-2'),

                                                html.Div(
                                                    report_text_view('pelvis_report_text_impact',
                                                                     'pelvis_report_text_tilt_impact', 'rotation.png',
                                                                     'tilt.png'),
                                                    className='w-full h-full'
                                                )
                                            ]
                                        ),
                                        html.Div(
                                            className='flex flex-col bg-white dark:bg-gray-800 rounded-2xl p-4 w-56 grow flex-none snap-start',
                                            children=[
                                                html.Span('Thorax',
                                                          className='sm:text-xl text-left font-medium text-gray-900 dark:text-gray-100 mb-2'),

                                                html.Div(
                                                    report_text_view('thorax_report_text_impact',
                                                                     'thorax_report_text_bend_impact', 'rotation.png',
                                                                     'bend.png'),
                                                    className='w-full h-full'
                                                )
                                            ]
                                        ),
                                        html.Div(
                                            className='flex flex-col bg-white dark:bg-gray-800 rounded-2xl p-4 w-56 grow flex-none snap-start',
                                            children=[
                                                html.Span('Head',
                                                          className='sm:text-xl text-left font-medium text-gray-900 dark:text-gray-100 mb-2'),

                                                html.Div(
                                                    report_text_view('head_report_text_impact',
                                                                     'head_report_text_tilt_impact', 'rotation.png',
                                                                     'tilt.png'),
                                                    className='w-full h-full'
                                                )
                                            ]
                                        ),
                                    ]
                                ),

                                html.Div(className='w-full h-96')
                            ]
                        )
                    ]
                )
            ]
        )
    ]
)
