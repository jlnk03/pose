from dash import html

loader = html.Div(
    children=[
        # Moving gradient loading indicator
        html.Div(className='gradient-box fixed top-0 left-0 z-50'),
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
            className="flex flex-col bg-slate-600 dark:bg-gray-700 fixed lg:left-5 top-5 bottom-5 w-60 z-10 rounded-3xl hidden lg:flex",
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
                                    className="bg-slate-200 dark:bg-slate-500 rounded-lg sm:top-24 top-12 left-4 right-4 sm:bottom-10 bottom-4 absolute flex-col items-center justify-center",
                                    children=[
                                        # html.Div(
                                        #     id='upload-progress',
                                        #     className="absolute bg-slate-400 dark:bg-slate-700 w-full h-full rounded-lg",
                                        #     style={'width': '45%'},
                                        # ),
                                        html.Div(
                                            className='relative dark:text-gray-100 text-gray-800 md:text-xl sm:text-md text-sm font-medium text-left flex flex flex-col animate-none justify-center items-center flex-col w-full h-full',
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
                            className="relative bg-white dark:bg-gray-700 shadow rounded-3xl flex items-center justify-center mb-5 backdrop-blur-md bg-opacity-80 border border-gray-100 dark:border-gray-900 flex-col w-full h-44 sm:h-96 sm:mt-0 mt-12",
                        ),

                        # Video loader
                        html.Div(
                            className="bg-slate-400 sm:w-96 h-96 rounded-3xl sm:ml-4 relative mb-5",
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
                    className="relative h-[570px] bg-white dark:bg-gray-700 shadow rounded-3xl flex items-center justify-center mb-5 backdrop-blur-md bg-opacity-80 border border-gray-100 dark:border-gray-900 flex-col w-full",
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
                    className="relative h-[750px] bg-white dark:bg-gray-700 shadow rounded-3xl flex items-center justify-center mb-5 backdrop-blur-md bg-opacity-80 border border-gray-100 dark:border-gray-900 flex-col w-full",
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
                        className="relative h-[570px] bg-white dark:bg-gray-700 shadow rounded-3xl flex items-center justify-center mb-5 backdrop-blur-md bg-opacity-80 border border-gray-100 dark:border-gray-900 flex-col w-full",
                    ) for _ in range(10)],
                )

            ],

            className="lg:mx-16 mx-4 lg:pl-60 mt-5 relative",
        )

    ]
)