from dash import html


def report_text_view(id1, id2, img1, img2):
    layout = html.Div(
        className='flex flex-col justify-end w-full h-full gap-4',
        children=[
            html.Div(
                className='flex flex-row sm:text-base text-sm text-left text-gray-900 dark:text-gray-100 mb-4 gap-2',
                children=[
                    html.Img(src='assets/' + img1,
                             className='rounded-full h-8 w-8 text-center flex flex-none items-center justify-center'),
                    html.Span(id=id1,
                              className='flex justify-center items-center'),
                ]
            ),
            html.Div(
                className='flex flex-row sm:text-base text-sm text-left text-gray-900 dark:text-gray-100 mb-2 gap-2',
                children=[
                    html.Img(src='assets/' + img2,
                             className='rounded-full h-8 w-8 text-center flex flex-none items-center justify-center'),
                    html.Span(id=id2,
                              className='flex justify-center items-center'),
                ]
            ),
        ]
    )

    return layout


def report_focus_view(id1, id2):
    layout = html.Div(
        className='flex flex-col justify-end w-full h-full gap-4',
        children=[
            html.Div(
                className='flex flex-row sm:text-base text-sm text-left text-gray-900 dark:text-gray-100 mb-4 gap-2',
                children=[
                    html.Span('1',
                              className='h-8 w-8 text-center flex-none flex items-center justify-center text-gray-500 font-bold text-xl'),
                    html.Span(id=id1,
                              className='flex justify-center items-center')
                ]
            ),
            html.Div(
                className='flex flex-row sm:text-base text-sm text-left text-gray-900 dark:text-gray-100 mb-2 gap-2',
                children=[
                    html.Span('2',
                              className='h-8 w-8 text-center flex-none flex items-center justify-center text-gray-500 font-bold text-xl'),
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
                    className='relative h-full flex flex-col  w-full',
                    children=[
                        html.Div(
                            className='w-full h-full flex flex-col overflow-y-auto relative sm:px-6 px-2 py-6',
                            children=[
                                html.Div('Report',
                                         className='sm:text-3xl text-xl text-left font-bold mt-4 sm:mb-10 mb-6 text-gray-900 dark:text-gray-100'),

                                html.Span('Setup',
                                          className='sm:text-2xl text-lg text-left font-bold text-gray-900 dark:text-gray-100 mb-1'),

                                html.Div(
                                    className='flex flex-row gap-4 w-full',
                                    children=[
                                        html.Canvas(id='setup_frame',
                                                    className='rounded-2xl max-h-56 max-w-56 sm:max-h-96 sm:max-w-96'),

                                        html.Div(
                                            className='flex flex-row bg-white dark:bg-gray-800 sm:h-96 h-56 overflow-x-auto grow rounded-2xl snap-x snap-mandatory  gap-4 pr-4 py-4',
                                            children=[

                                                html.Div(
                                                    className='flex flex-col p-4 w-56 grow flex-none snap-start border-r-2 border-gray-200 dark:border-gray-600',
                                                    children=[
                                                        html.Span('Focus',
                                                                  className='sm:text-xl text-left font-medium text-gray-900 dark:text-gray-100 mb-2'),

                                                        html.Div(
                                                            report_focus_view('focus_report_text',
                                                                              'focus_report_text_2'),
                                                            className='w-full h-full'
                                                        )
                                                    ]
                                                ),

                                                html.Div(
                                                    className='flex flex-col p-4 w-56 grow flex-none snap-start border-r-2 border-gray-200 dark:border-gray-600',
                                                    children=[
                                                        html.Span('Pelvis',
                                                                  className='sm:text-xl text-left font-medium text-gray-900 dark:text-gray-100 mb-2'),

                                                        html.Div(
                                                            report_text_view('pelvis_report_text',
                                                                             'pelvis_report_text_tilt',
                                                                             'rotation.png', 'tilt.png'),
                                                            className='w-full h-full'
                                                        )
                                                    ]
                                                ),
                                                html.Div(
                                                    className='flex flex-col  p-4 w-56 grow flex-none snap-start border-r-2 border-gray-200 dark:border-gray-600',
                                                    children=[
                                                        html.Span('Thorax',
                                                                  className='sm:text-xl text-left font-medium text-gray-900 dark:text-gray-100 mb-2'),

                                                        html.Div(
                                                            report_text_view('thorax_report_text',
                                                                             'thorax_report_text_bend',
                                                                             'rotation.png', 'bend.png'),
                                                            className='w-full h-full'
                                                        )

                                                    ]
                                                ),
                                                html.Div(
                                                    className='flex flex-col w-56 grow flex-none p-4 snap-start ',
                                                    children=[
                                                        html.Span('Head',
                                                                  className='sm:text-xl text-left font-medium text-gray-900 dark:text-gray-100 mb-2'),

                                                        html.Div(
                                                            report_text_view('head_report_text',
                                                                             'head_report_text_tilt',
                                                                             'rotation.png', 'tilt.png'),
                                                            className='w-full h-full'
                                                        )

                                                    ]
                                                ),
                                            ]
                                        ),
                                    ]
                                ),

                                html.Span('Top',
                                          className='sm:text-2xl text-lg text-left font-bold text-gray-900 dark:text-gray-100 mb-1 mt-6'),
                                html.Div(
                                    className='flex flex-row gap-4 w-full',
                                    children=[
                                        html.Canvas(id='top_frame',
                                                    className='rounded-2xl max-h-56 max-w-56 sm:max-h-96 sm:max-w-96 snap-start'),

                                        html.Div(
                                            className='flex flex-row sm:h-96 h-56 overflow-x-auto grow snap-x snap-mandatory gap-4 bg-white dark:bg-gray-800 rounded-2xl pr-4 py-4',
                                            children=[

                                                html.Div(
                                                    className='flex flex-col  p-4 w-56 grow flex-none snap-start border-r-2 border-gray-200 dark:border-gray-600',
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
                                                    className='flex flex-col p-4 w-56 grow flex-none snap-start border-r-2 border-gray-200 dark:border-gray-600',
                                                    children=[
                                                        html.Span('Pelvis',
                                                                  className='sm:text-xl text-left font-medium text-gray-900 dark:text-gray-100 mb-2'),

                                                        html.Div(
                                                            report_text_view('pelvis_report_text_top',
                                                                             'pelvis_report_text_tilt_top',
                                                                             'rotation.png',
                                                                             'tilt.png'),
                                                            className='w-full h-full'),
                                                    ]
                                                ),
                                                html.Div(
                                                    className='flex flex-col p-4 w-56 grow flex-none snap-start border-r-2 border-gray-200 dark:border-gray-600',
                                                    children=[
                                                        html.Span('Thorax',
                                                                  className='sm:text-xl text-left font-medium text-gray-900 dark:text-gray-100 mb-2'),

                                                        html.Div(
                                                            report_text_view('thorax_report_text_top',
                                                                             'thorax_report_text_bend_top',
                                                                             'rotation.png',
                                                                             'bend.png'),
                                                            className='w-full h-full'
                                                        )

                                                    ]
                                                ),
                                                html.Div(
                                                    className='flex flex-col p-4 w-56 grow flex-none snap-start',
                                                    children=[
                                                        html.Span('Head',
                                                                  className='sm:text-xl text-left font-medium text-gray-900 dark:text-gray-100 mb-2'),

                                                        html.Div(
                                                            report_text_view('head_report_text_top',
                                                                             'head_report_text_tilt_top',
                                                                             'rotation.png',
                                                                             'tilt.png'),
                                                            className='w-full h-full'
                                                        )

                                                    ]
                                                ),

                                            ]
                                        ),
                                    ]
                                ),

                                html.Span('Impact',
                                          className='sm:text-2xl text-lg text-left font-bold text-gray-900 dark:text-gray-100 mb-1 mt-6'),

                                html.Div(
                                    className='flex flex-row gap-4 w-full',
                                    children=[
                                        html.Canvas(id='impact_frame',
                                                    className=' rounded-2xl max-h-56 max-w-56 sm:max-h-96 sm:max-w-96 snap-start'),

                                        html.Div(
                                            className='flex flex-row sm:h-96 h-56 overflow-x-auto w-full snap-x snap-mandatory gap-4 bg-white dark:bg-gray-800 rounded-2xl pr-4 py-4',
                                            children=[

                                                html.Div(
                                                    className='flex flex-col p-4 w-56 grow flex-none snap-start border-r-2 border-gray-200 dark:border-gray-600',
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
                                                    className='flex flex-col p-4 w-56 grow flex-none snap-start border-r-2 border-gray-200 dark:border-gray-600',
                                                    children=[
                                                        html.Span('Pelvis',
                                                                  className='sm:text-xl text-left font-medium text-gray-900 dark:text-gray-100 mb-2'),

                                                        html.Div(
                                                            report_text_view('pelvis_report_text_impact',
                                                                             'pelvis_report_text_tilt_impact',
                                                                             'rotation.png',
                                                                             'tilt.png'),
                                                            className='w-full h-full'
                                                        )
                                                    ]
                                                ),
                                                html.Div(
                                                    className='flex flex-col p-4 w-56 grow flex-none snap-start border-r-2 border-gray-200 dark:border-gray-600',
                                                    children=[
                                                        html.Span('Thorax',
                                                                  className='sm:text-xl text-left font-medium text-gray-900 dark:text-gray-100 mb-2'),

                                                        html.Div(
                                                            report_text_view('thorax_report_text_impact',
                                                                             'thorax_report_text_bend_impact',
                                                                             'rotation.png',
                                                                             'bend.png'),
                                                            className='w-full h-full'
                                                        )
                                                    ]
                                                ),
                                                html.Div(
                                                    className='flex flex-col bg-white dark:bg-gray-800 p-4 w-56 grow flex-none snap-start',
                                                    children=[
                                                        html.Span('Head',
                                                                  className='sm:text-xl text-left font-medium text-gray-900 dark:text-gray-100 mb-2'),

                                                        html.Div(
                                                            report_text_view('head_report_text_impact',
                                                                             'head_report_text_tilt_impact',
                                                                             'rotation.png',
                                                                             'tilt.png'),
                                                            className='w-full h-full'
                                                        )
                                                    ]
                                                ),
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

report_view = html.Div(
    # className='flex flex-col mt-5 mb-10',
    className='grid md:grid-cols-2 grid-cols-1 mt-14 mb-10 gap-5',
    children=[

        html.Div(
            className='flex flex-col relative ',
            children=[
                html.Canvas(id='setup_frame',
                            className='rounded-2xl max-h-40 max-w-40 bg-gray-200 dark:bg-gray-800 absolute top-0 right-0 z-30 transform -translate-x-1/2 -translate-y-1/4'),

                html.Img(src='assets/page_dots.png',
                         className='absolute bottom-0 right-1/2 transform translate-x-1/2 z-20 h-10 w-10'),

                html.Span('Setup',
                          className='sm:text-xl text-lg text-left font-bold text-gray-900 dark:text-gray-100 mb-1'),

                html.Div(
                    id='setup_report',
                    className='flex flex-row h-60 gap-4 overflow-x-auto snap-x snap-mandatory  w-full relative',
                    children=[

                        html.Div(
                            className='flex flex-col p-4  w-full bg-white dark:bg-gray-700 rounded-2xl flex-none snap-start',
                            children=[
                                html.Span('Focus',
                                          className='sm:text-xl text-left font-medium text-gray-900 dark:text-gray-100 mb-2'),

                                html.Div(
                                    report_focus_view('focus_report_text',
                                                      'focus_report_text_2'),
                                    className='w-full h-full'
                                )
                            ]
                        ),

                        html.Div(
                            className='flex flex-col p-4  w-full bg-white dark:bg-gray-700 rounded-2xl flex-none snap-start',
                            children=[
                                html.Span('Pelvis',
                                          className='sm:text-xl text-left font-medium text-gray-900 dark:text-gray-100 mb-2'),

                                html.Div(
                                    report_text_view('pelvis_report_text',
                                                     'pelvis_report_text_tilt',
                                                     'rotation.png', 'tilt.png'),
                                    className='w-full h-full'
                                )
                            ]
                        ),
                        html.Div(
                            className='flex flex-col p-4  w-full bg-white dark:bg-gray-700 rounded-2xl flex-none  snap-start',
                            children=[
                                html.Span('Thorax',
                                          className='sm:text-xl text-left font-medium text-gray-900 dark:text-gray-100 mb-2'),

                                html.Div(
                                    report_text_view('thorax_report_text',
                                                     'thorax_report_text_bend',
                                                     'rotation.png', 'bend.png'),
                                    className='w-full h-full'
                                )

                            ]
                        ),
                        html.Div(
                            className='flex flex-col p-4  w-full bg-white dark:bg-gray-700 rounded-2xl flex-none snap-start',
                            children=[
                                html.Span('Head',
                                          className='sm:text-xl text-left font-medium text-gray-900 dark:text-gray-100 mb-2'),

                                html.Div(
                                    report_text_view('head_report_text',
                                                     'head_report_text_tilt',
                                                     'rotation.png', 'tilt.png'),
                                    className='w-full h-full'
                                )

                            ]
                        ),
                    ]
                ),
            ]
        ),

        html.Div(
            className='flex flex-col relative md:mt-0 mt-14 ',
            children=[
                html.Canvas(id='top_frame',
                            className='rounded-2xl max-h-40 max-w-40 bg-gray-200 dark:bg-gray-800 absolute top-0 right-0 z-30 transform -translate-x-1/2 -translate-y-1/4'),

                html.Img(src='assets/page_dots.png',
                         className='absolute bottom-0 right-1/2 transform translate-x-1/2 z-20 h-10 w-10'),

                html.Span('Top',
                          className='sm:text-xl text-lg text-left font-bold text-gray-900 dark:text-gray-100 mb-1'),

                html.Div(
                    id='top_report',
                    className='flex flex-row h-60 gap-4 overflow-x-auto snap-x snap-mandatory  w-full relative',
                    children=[

                        html.Div(
                            className='flex flex-col p-4  w-full bg-white dark:bg-gray-700 rounded-2xl flex-none snap-start',
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
                            className='flex flex-col p-4  w-full bg-white dark:bg-gray-700 rounded-2xl flex-none snap-start',
                            children=[
                                html.Span('Pelvis',
                                          className='sm:text-xl text-left font-medium text-gray-900 dark:text-gray-100 mb-2'),

                                html.Div(
                                    report_text_view('pelvis_report_text_top',
                                                     'pelvis_report_text_tilt_top',
                                                     'rotation.png',
                                                     'tilt.png'),
                                    className='w-full h-full'),
                            ]
                        ),
                        html.Div(
                            className='flex flex-col p-4  w-full bg-white dark:bg-gray-700 rounded-2xl flex-none snap-start',
                            children=[
                                html.Span('Thorax',
                                          className='sm:text-xl text-left font-medium text-gray-900 dark:text-gray-100 mb-2'),

                                html.Div(
                                    report_text_view('thorax_report_text_top',
                                                     'thorax_report_text_bend_top',
                                                     'rotation.png',
                                                     'bend.png'),
                                    className='w-full h-full'
                                )

                            ]
                        ),
                        html.Div(
                            className='flex flex-col p-4  w-full bg-white dark:bg-gray-700 rounded-2xl flex-none snap-start',
                            children=[
                                html.Span('Head',
                                          className='sm:text-xl text-left font-medium text-gray-900 dark:text-gray-100 mb-2'),

                                html.Div(
                                    report_text_view('head_report_text_top',
                                                     'head_report_text_tilt_top',
                                                     'rotation.png',
                                                     'tilt.png'),
                                    className='w-full h-full'
                                )

                            ]
                        ),

                    ]
                ),
            ]
        ),

        html.Div(
            className='flex flex-col relative mt-14 ',
            children=[
                html.Canvas(id='impact_frame',
                            className='rounded-2xl max-h-40 max-w-40 bg-gray-200 dark:bg-gray-800 absolute top-0 right-0 z-30 transform -translate-x-1/2 -translate-y-1/4'),

                html.Img(src='assets/page_dots.png',
                         className='absolute bottom-0 right-1/2 transform translate-x-1/2 z-20 h-10 w-10'),

                html.Span('Impact',
                          className='sm:text-xl text-lg text-left font-bold text-gray-900 dark:text-gray-100 mb-1'),

                html.Div(
                    id='impact_report',
                    className='flex flex-row h-60 gap-4 overflow-x-auto snap-x snap-mandatory  w-full relative',
                    children=[

                        html.Div(
                            className='flex flex-col p-4  w-full bg-white dark:bg-gray-700 rounded-2xl flex-none snap-start',
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
                            className='flex flex-col p-4  w-full bg-white dark:bg-gray-700 rounded-2xl flex-none snap-start',
                            children=[
                                html.Span('Pelvis',
                                          className='sm:text-xl text-left font-medium text-gray-900 dark:text-gray-100 mb-2'),

                                html.Div(
                                    report_text_view('pelvis_report_text_impact',
                                                     'pelvis_report_text_tilt_impact',
                                                     'rotation.png',
                                                     'tilt.png'),
                                    className='w-full h-full'
                                )
                            ]
                        ),
                        html.Div(
                            className='flex flex-col p-4  w-full bg-white dark:bg-gray-700 rounded-2xl flex-none snap-start',
                            children=[
                                html.Span('Thorax',
                                          className='sm:text-xl text-left font-medium text-gray-900 dark:text-gray-100 mb-2'),

                                html.Div(
                                    report_text_view('thorax_report_text_impact',
                                                     'thorax_report_text_bend_impact',
                                                     'rotation.png',
                                                     'bend.png'),
                                    className='w-full h-full'
                                )
                            ]
                        ),
                        html.Div(
                            className='flex flex-col p-4  w-full bg-white dark:bg-gray-700 rounded-2xl flex-none snap-start',
                            children=[
                                html.Span('Head',
                                          className='sm:text-xl text-left font-medium text-gray-900 dark:text-gray-100 mb-2'),

                                html.Div(
                                    report_text_view('head_report_text_impact',
                                                     'head_report_text_tilt_impact',
                                                     'rotation.png',
                                                     'tilt.png'),
                                    className='w-full h-full'
                                )
                            ]
                        ),
                    ]
                ),
            ]
        ),
    ]
)
