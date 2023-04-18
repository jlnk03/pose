from dash import html

overlay = html.Div(
    className='w-full h-full z-50',
    children=[
        html.Button(id='hide_overlay', className='w-full h-32 bg-black bg-opacity-50'),
        html.Div(
            className='fixed top-24 w-full bottom-0 dark:bg-slate-700 bg-[#FAF7F5] rounded-t-3xl justify-center flex flex-none',
            children=[
                html.Div(
                    className='relative h-full flex flex-col sm:mx-6 mx-2 py-6 max-w-8xl',
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
                                                html.Span('Pelvis',
                                                          className='sm:text-xl text-left font-medium text-gray-900 dark:text-gray-100 mb-2'),
                                                html.Span(id='pelvis_report_text',
                                                          className='sm:text-base text-sm text-left text-gray-900 dark:text-gray-100 mb-4'),

                                                html.Span(id='pelvis_report_text_tilt',
                                                          className='sm:text-base text-sm text-left text-gray-900 dark:text-gray-100 mb-4'),
                                            ]
                                        ),
                                        html.Div(
                                            className='flex flex-col bg-white dark:bg-gray-800 rounded-2xl p-4 w-56 grow flex-none snap-start',
                                            children=[
                                                html.Span('Thorax',
                                                          className='sm:text-xl text-left font-medium text-gray-900 dark:text-gray-100 mb-2'),
                                                html.Span(id='thorax_report_text',
                                                          className='sm:text-base text-sm text-left text-gray-900 dark:text-gray-100 mb-4'),

                                                html.Span(id='thorax_report_text_bend',
                                                          className='sm:text-base text-sm text-left text-gray-900 dark:text-gray-100 mb-4'),

                                            ]
                                        ),
                                        html.Div(
                                            className='flex flex-col w-56 grow flex-none bg-white dark:bg-gray-800 rounded-2xl p-4 snap-start',
                                            children=[
                                                html.Span('Head',
                                                          className='sm:text-xl text-left font-medium text-gray-900 dark:text-gray-100 mb-2'),
                                                html.Span(id='head_report_text',
                                                          className='sm:text-base text-sm text-left text-gray-900 dark:text-gray-100 mb-4'),

                                                html.Span(id='head_report_text_tilt',
                                                          className='sm:text-base text-sm text-left text-gray-900 dark:text-gray-100 mb-4'),
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
                                                html.Span('Pelvis',
                                                          className='sm:text-xl text-left font-medium text-gray-900 dark:text-gray-100 mb-2'),
                                                html.Span(id='pelvis_report_text_top',
                                                          className='sm:text-base text-sm text-left text-gray-900 dark:text-gray-100 mb-4'),

                                                html.Span(id='pelvis_report_text_tilt_top',
                                                          className='sm:text-base text-sm text-left text-gray-900 dark:text-gray-100 mb-4'),
                                            ]
                                        ),
                                        html.Div(
                                            className='flex flex-col bg-white dark:bg-gray-800 rounded-2xl p-4 w-56 grow flex-none snap-start',
                                            children=[
                                                html.Span('Thorax',
                                                          className='sm:text-xl text-left font-medium text-gray-900 dark:text-gray-100 mb-2'),
                                                html.Span(id='thorax_report_text_top',
                                                          className='sm:text-base text-sm text-left text-gray-900 dark:text-gray-100 mb-4'),

                                                html.Span(id='thorax_report_text_bend_top',
                                                          className='sm:text-base text-sm text-left text-gray-900 dark:text-gray-100 mb-4'),
                                            ]
                                        ),
                                        html.Div(
                                            className='flex flex-col bg-white dark:bg-gray-800 rounded-2xl p-4 w-56 grow flex-none snap-start',
                                            children=[
                                                html.Span('Head',
                                                          className='sm:text-xl text-left font-medium text-gray-900 dark:text-gray-100 mb-2'),
                                                html.Span(id='head_report_text_top',
                                                          className='sm:text-base text-sm text-left text-gray-900 dark:text-gray-100 mb-4'),

                                                html.Span(id='head_report_text_tilt_top',
                                                          className='sm:text-base text-sm text-left text-gray-900 dark:text-gray-100 mb-4'),
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
                                                html.Span('Pelvis',
                                                          className='sm:text-xl text-left font-medium text-gray-900 dark:text-gray-100 mb-2'),
                                                html.Span(id='pelvis_report_text_impact',
                                                          className='sm:text-base text-sm text-left text-gray-900 dark:text-gray-100 mb-4'),

                                                html.Span(id='pelvis_report_text_tilt_impact',
                                                          className='sm:text-base text-sm text-left text-gray-900 dark:text-gray-100 mb-4'),
                                            ]
                                        ),
                                        html.Div(
                                            className='flex flex-col bg-white dark:bg-gray-800 rounded-2xl p-4 w-56 grow flex-none snap-start',
                                            children=[
                                                html.Span('Thorax',
                                                          className='sm:text-xl text-left font-medium text-gray-900 dark:text-gray-100 mb-2'),
                                                html.Span(id='thorax_report_text_impact',
                                                          className='sm:text-base text-sm text-left text-gray-900 dark:text-gray-100 mb-4'),

                                                html.Span(id='thorax_report_text_bend_impact',
                                                          className='sm:text-base text-sm text-left text-gray-900 dark:text-gray-100 mb-4'),
                                            ]
                                        ),
                                        html.Div(
                                            className='flex flex-col bg-white dark:bg-gray-800 rounded-2xl p-4 w-56 grow flex-none snap-start',
                                            children=[
                                                html.Span('Head',
                                                          className='sm:text-xl text-left font-medium text-gray-900 dark:text-gray-100 mb-2'),
                                                html.Span(id='head_report_text_impact',
                                                          className='sm:text-base text-sm text-left text-gray-900 dark:text-gray-100 mb-4'),

                                                html.Span(id='head_report_text_tilt_impact',
                                                          className='sm:text-base text-sm text-left text-gray-900 dark:text-gray-100 mb-4'),
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
