'use client'

import React, {useEffect, useState} from 'react';
import UploadSide from "@/app/[lang]/components/UploadSide";
import {Switch} from '@headlessui/react'
import {Button, Card} from "@tremor/react";
import Link from 'next/link';
import {useFileStorage, useVideoIdStorage} from '@/app/context/storage';
import {CSSTransition, TransitionGroup} from 'react-transition-group';


function Navbar({children, dictionary, lang}) {

    const {files, setFiles} = useFileStorage();
    const [disabled, setDisabled] = useState(false);
    const [expertMode, setExpertMode] = useState(false);
    const {videoId, setVideoId} = useVideoIdStorage();


    const toggleExpertMode = () => {
        setExpertMode(!expertMode);
    };


    useEffect(() => {
        fetch(`/api/storage`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            },
        })
            .then(response => response.json())
            .then(data => {
                setFiles(data['videos']);
            })
            .catch((error) => {
                console.error('Error:', error);
            });

        return () => {
            // cleanup
            setFiles([])
        }

    }, [])


    return (
        <>

            <Card
                id="sidebar"
                className="flex flex-col fixed lg:left-5 lg:top-5 lg:bottom-5 top-0 bottom-0 w-60 z-30 hidden lg:flex overflow-x-visible transition p-0 max-sm:rounded-l-none"
            >
                <button id="sidebar-header" className="flex-row items-center ml-4 lg:hidden">
                    {/* <img src={app.get_asset_url('menu_cross.svg')} className="h-4 w-4 mt-4 hidden" /> */}
                </button>

                <UploadSide disabled={disabled} dictionary={dictionary}/>

                <span className='text-black dark:text-gray-200 mx-2 mt-4 mb-2 font-medium'>
                    {dictionary['history']}
                </span>


                {/* history buttons */}
                <div
                    className="flex flex-col gap-2 pb-2 mx-2 h-full overflow-y-auto border-b border-gray-200 dark:border-gray-600">

                    <TransitionGroup component={null}>
                        {files.map((file, index) => (
                            <CSSTransition
                                key={index}
                                timeout={500}
                                classNames="item"
                            >
                                <Link href={{
                                    pathname: '/dashboard',
                                    query: {videoId: file.videoId}
                                }}
                                >
                                    <Button
                                        className={`relative w-full bg-white dark:bg-slate-800 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-slate-800 transition text-black ${videoId === file.videoId ? 'border-blue-700' : ' border-gray-200 dark:border-gray-600'}`}>
                                        {new Date(file.createdAt).toLocaleDateString(lang, {
                                            day: '2-digit',
                                            month: '2-digit',
                                            year: 'numeric'
                                        })}
                                    </Button>
                                </Link>
                            </CSSTransition>
                        ))}
                    </TransitionGroup>

                </div>

                <div
                    className="flex flex-col border-b border-gray-200 dark:border-gray-600 justify-center w-full px-8 py-2">
                    <label
                        className="inline-flex items-center cursor-pointer dark:text-gray-100 justify-between"
                        htmlFor="expert-mode"
                    >
                        <span className="font-normal text-xs">Expert Mode</span>
                        <span className="relative">

                            <Switch
                                checked={expertMode}
                                onChange={toggleExpertMode}
                                className={`${expertMode ? 'bg-blue-600' : 'bg-gray-200 dark:bg-gray-500'
                                } relative inline-flex h-6 w-11 items-center rounded-full`}
                            >
                                <span className="sr-only">Enable notifications</span>
                                <span
                                    className={`${expertMode ? 'translate-x-6' : 'translate-x-1'
                                    } inline-block h-4 w-4 transform rounded-full bg-white transition`}
                                />
                            </Switch>

                        </span>
                    </label>
                </div>

                <div className="flex flex-col gap-2 mx-4 my-4 justify-end">
                    <Link
                        href="/"
                        className="font-normal text-xs hover:bg-gray-100 dark:hover:bg-slate-800 items-center justify-center px-4 py-2 rounded-lg transition"
                    >
                        {dictionary['navigation']['home']}
                    </Link>
                    <Link
                        href="/profile"
                        className="font-normal text-xs hover:bg-gray-100 dark:hover:bg-slate-800 items-center justify-center px-4 py-2 rounded-lg transition"
                    >
                        {dictionary['navigation']['profile']}
                    </Link>
                    <Link
                        href="/dashboard"
                        className="font-normal text-xs bg-gray-100 dark:bg-slate-800 items-center justify-center px-4 py-2 rounded-lg transition"
                    >
                        {dictionary['navigation']['dashboard']}
                    </Link>
                    <Link
                        href="/logout"
                        className="font-normal text-xs dark:text-gray-200 text-gray-800 hover:bg-gray-100 dark:hover:bg-slate-800 items-center justify-center px-4 py-2 rounded-lg transition"
                    >
                        {dictionary['navigation']['logout']}
                    </Link>
                </div>
            </Card>
        </>
    );

}

export default Navbar;
