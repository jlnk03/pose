from dash import Dash, ctx, ALL, html, dcc, MATCH, ClientsideFunction

overlay = html.Div(
    className='w-full h-full z-50',
    children=[
        html.Button(id='hide_overlay', className='w-full h-32 bg-black bg-opacity-50'),
        html.Div(
            className='fixed top-24 w-full bottom-0 dark:bg-slate-700 bg-[#FAF7F5] rounded-t-3xl',
            children=[
                html.Div(
                    className='relative h-full flex flex-col gap-4 ml-6 py-6 overflow-x-hidden',
                    children=[
                        html.Div(
                            className='w-full h-full flex flex-col gap-4 overflow-y-auto',
                            children=[
                                html.Div('Report',
                                         className='sm:text-3xl text-xl text-left font-bold mt-4 sm:mb-10 mb-6 text-gray-900 dark:text-gray-100'),

                                html.Div(className='flex flex-row',
                                         children=[
                                             html.Canvas(id='setup_frame', className='rounded-2xl max-h-56 sm:max-h-96'),
                                             html.Div(
                                                 className='flex flex-col ml-6',
                                                 children=[
                                                     html.Span('Setup',
                                                               className='sm:text-2xl text-lg text-left font-bold mb-4 text-gray-900 dark:text-gray-100 sm:mb-8 mb-6'),
                                                     html.Span('Pelvis',
                                                               className='sm:text-xl text-left font-medium text-gray-900 dark:text-gray-100 mb-2'),
                                                     html.Span(id='pelvis_report_text',
                                                               className='sm:text-base text-sm text-left text-gray-900 dark:text-gray-100 mb-4'),
                                                     html.Span('Thorax',
                                                               className='sm:text-xl text-left font-medium text-gray-900 dark:text-gray-100 mb-2'),
                                                     html.Span(id='thorax_report_text',
                                                               className='sm:text-base text-sm text-left text-gray-900 dark:text-gray-100 mb-4'),
                                                     html.Span('Head',
                                                               className='sm:text-xl text-left font-medium text-gray-900 dark:text-gray-100 mb-2'),
                                                     html.Span(id='head_report_text',
                                                               className='sm:text-base text-sm text-left text-gray-900 dark:text-gray-100 mb-4'),
                                                 ]
                                             )
                                         ]
                                         ),

                                html.Div(className='flex flex-row',
                                         children=[
                                             html.Canvas(id='top_frame', className='rounded-2xl max-h-56 sm:max-h-96'),
                                             html.Div(
                                                 className='flex flex-col ml-6',
                                                 children=[
                                                     html.Span('Top',
                                                               className='sm:text-2xl text-lg text-left font-bold mb-4 text-gray-900 dark:text-gray-100 sm:mb-8 mb-6'),
                                                     html.Span('Pelvis',
                                                               className='sm:text-xl text-left font-medium text-gray-900 dark:text-gray-100 mb-2'),
                                                     html.Span(id='pelvis_report_text_top',
                                                               className='sm:text-base text-sm text-left text-gray-900 dark:text-gray-100 mb-4'),
                                                     html.Span('Thorax',
                                                               className='sm:text-xl text-left font-medium text-gray-900 dark:text-gray-100 mb-2'),
                                                     html.Span(id='thorax_report_text_top',
                                                               className='sm:text-base text-sm text-left text-gray-900 dark:text-gray-100 mb-4'),
                                                     html.Span('Head',
                                                               className='sm:text-xl text-left font-medium text-gray-900 dark:text-gray-100 mb-2'),
                                                     html.Span(id='head_report_text_top',
                                                               className='sm:text-base text-sm text-left text-gray-900 dark:text-gray-100 mb-4'),
                                                 ]
                                             )
                                         ]
                                         ),

                                html.Div(className='flex flex-row',
                                         children=[
                                             html.Canvas(id='impact_frame', className='rounded-2xl max-h-56 sm:max-h-96'),
                                             html.Div(
                                                 className='flex flex-col ml-6',
                                                 children=[
                                                     html.Span('Impact',
                                                               className='sm:text-2xl text-lg text-left font-bold mb-4 text-gray-900 dark:text-gray-100 sm:mb-8 mb-6'),
                                                     html.Span('Pelvis',
                                                               className='sm:text-xl text-left font-medium text-gray-900 dark:text-gray-100 mb-2'),
                                                     html.Span(id='pelvis_report_text_impact',
                                                               className='sm:text-base text-sm text-left text-gray-900 dark:text-gray-100 mb-4'),
                                                     html.Span('Thorax',
                                                               className='sm:text-xl text-left font-medium text-gray-900 dark:text-gray-100 mb-2'),
                                                     html.Span(id='thorax_report_text_impact',
                                                               className='sm:text-base text-sm text-left text-gray-900 dark:text-gray-100 mb-4'),
                                                     html.Span('Head',
                                                               className='sm:text-xl text-left font-medium text-gray-900 dark:text-gray-100 mb-2'),
                                                     html.Span(id='head_report_text_impact',
                                                               className='sm:text-base text-sm text-left text-gray-900 dark:text-gray-100 mb-4'),
                                                 ]
                                             )
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
