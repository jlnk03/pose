from dash import Dash, ctx, ALL, html, dcc, MATCH, ClientsideFunction

overlay = html.Div(
    className='w-full h-full z-50',
    children=[
        html.Button(id='hide_overlay', className='w-full h-32 bg-black bg-opacity-50'),
        html.Div(
            className='fixed top-24 w-full bottom-0 dark:bg-slate-700 bg-[#FAF7F5] rounded-t-3xl',
            children=[
                html.Div(
                    className='relative flex flex-col gap-4 mx-6 my-6 overflow-y-auto overflow-x-hidden h-full',
                    children=[
                        html.Div(
                            className='w-full h-fit flex flex-col gap-4',
                            children=[
                                html.Div('Report',
                                         className='text-3xl text-center font-bold mt-4 mb-10 text-gray-900 dark:text-gray-100'),

                                html.Div(className='flex flex-row',
                                         children=[
                                             html.Canvas(id='setup_frame', className='rounded-2xl'),
                                             html.Div(
                                                 className='flex flex-col ml-6',
                                                 children=[
                                                     html.Span('Setup',
                                                               className='text-2xl text-left font-bold mb-8 text-gray-900 dark:text-gray-100'),
                                                     html.Span('Pelvis',
                                                               className='text-xl text-left font-medium text-gray-900 dark:text-gray-100 mb-2'),
                                                     html.Span(id='pelvis_report_text', className='text-base text-left text-gray-900 dark:text-gray-100 mb-4'),
                                                     html.Span('Thorax',
                                                               className='text-xl text-left font-medium text-gray-900 dark:text-gray-100 mb-2'),
                                                    html.Span(id='thorax_report_text', className='text-base text-left text-gray-900 dark:text-gray-100 mb-4'),
                                                     html.Span('Head',
                                                               className='text-xl text-left font-medium text-gray-900 dark:text-gray-100 mb-2'),
                                                    html.Span(id='head_report_text', className='text-base text-left text-gray-900 dark:text-gray-100'),
                                                 ]
                                             )
                                         ]
                                         ),

                                html.Div(className='flex flex-row',
                                         children=[
                                             html.Canvas(id='top_frame', className='rounded-2xl'),
                                            html.Div(
                                                 className='flex flex-col ml-6',
                                                 children=[
                                                     html.Span('Top',
                                                               className='text-2xl text-left font-bold mb-4 text-gray-900 dark:text-gray-100 mb-8'),
                                                     html.Span('Pelvis',
                                                               className='text-xl text-left font-medium text-gray-900 dark:text-gray-100 mb-2'),
                                                    html.Span(id='pelvis_report_text_top', className='text-base text-left text-gray-900 dark:text-gray-100 mb-4'),
                                                     html.Span('Thorax',
                                                               className='text-xl text-left font-medium text-gray-900 dark:text-gray-100 mb-2'),
                                                    html.Span(id='thorax_report_text_top', className='text-base text-left text-gray-900 dark:text-gray-100 mb-4'),
                                                     html.Span('Head',
                                                               className='text-xl text-left font-medium text-gray-900 dark:text-gray-100 mb-2'),
                                                    html.Span(id='head_report_text_top', className='text-base text-left text-gray-900 dark:text-gray-100 mb-4'),
                                                 ]
                                             )
                                         ]
                                         ),

                                html.Div(className='flex flex-row gap-4',
                                         children=[
                                             html.Canvas(id='impact_frame', className='rounded-2xl'),
                                            html.Div(
                                                 className='flex flex-col gap-4 ml-6',
                                                 children=[
                                                     html.Span('Impact',
                                                               className='text-2xl text-left font-bold mb-4 text-gray-900 dark:text-gray-100'),
                                                     html.Span('Pelvis',
                                                               className='text-xl text-left font-medium text-gray-900 dark:text-gray-100'),
                                                     html.Span('Thorax',
                                                               className='text-xl text-left font-medium text-gray-900 dark:text-gray-100'),
                                                     html.Span('Head',
                                                               className='text-xl text-left font-medium text-gray-900 dark:text-gray-100'),
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
