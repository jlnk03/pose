'use client'

import React, {useEffect, useRef, useState} from 'react';
import PositionSelection from "./PositionSelection";


function VideoPlayer({src, disabled}) {
    const videoRef = useRef(null);
    const [playing, setPlaying] = useState(false);
    const [progress, setProgress] = useState(0);
    // Step 1: Set up component state
    const [isActive, setIsActive] = useState(false);

    const togglePlayback = () => {
        if (playing) {
            videoRef.current.pause();
        } else {
            videoRef.current.play();
        }
        setPlaying(!playing);
    };

    const updateProgress = () => {
        const {currentTime, duration} = videoRef.current;
        setProgress((currentTime / duration) * 100);
        if (currentTime === duration) {
            setPlaying(false);
        }
    };

    const skipFrame = (direction) => {
        const skipTime = 1 / 30; // Assuming 30 FPS
        videoRef.current.currentTime += direction === 'forward' ? skipTime : -skipTime;
        updateProgress();
    };

    const skipToPercentage = (percentage) => {
        videoRef.current.currentTime = percentage * videoRef.current.duration;
        updateProgress();
    }

    useEffect(() => {
        videoRef.current.addEventListener('timeupdate', updateProgress);

        return () => {
            if (videoRef.current) {
                videoRef.current.removeEventListener('timeupdate', updateProgress);
            }
        };
    }, []);

    // Format time to mm:ss
    const formatTime = (time) => {
        const minutes = Math.floor(time / 60);
        const seconds = Math.floor(time % 60);
        return `${minutes}:${seconds.toString().padStart(2, '0')}`;
    }

    const handleSliderChange = (e) => {
        const currentTime = (e.target.value / 100) * videoRef.current.duration;
        videoRef.current.currentTime = currentTime;
        updateProgress();
    };

    // Step 2: Implement the toggle function
    const toggleActive = () => {
        setIsActive(!isActive);
    };


    return (
        <div className="relative flex flex-col w-full items-center">
            <div className='items-center justify-center flex relative w-fit overflow-clip rounded-2xl'>

                <video ref={videoRef} className="max-h-[calc(100dvh-10rem)] min-h-96 rounded-2xl" src={src}
                       onClick={togglePlayback}>
                </video>

                <div
                    className="absolute bottom-0 left-0 w-full bg-gradient-to-t from-black/80 to-transparent mask-gradient-to-t"
                >

                    <div className="flex flex-row w-full gap-4 justify-center p-1">

                        <button
                            onClick={toggleActive}
                            className={`heart rounded-full flex justify-center items-center absolute left-3 ${isActive ? 'is-active' : ''}`}>
                        </button>

                        <button onClick={() => skipFrame('backward')} className="p-2 rounded focus:outline-none">
                            <svg width="18" height="18" viewBox="0 0 32 32" fill="none"
                                 xmlns="http://www.w3.org/2000/svg">
                                <path
                                    d="M26 7C26 5.76393 24.5889 5.05836 23.6 5.8L11.6 14.8C10.8 15.4 10.8 16.6 11.6 17.2L23.6 26.2C24.5889 26.9416 26 26.2361 26 25V7Z"
                                    fill="#94A3B8" stroke="#94A3B8" strokeWidth="2" strokeLinejoin="round"></path>
                                <path d="M6 5L6 27" stroke="#94A3B8" strokeWidth="2" strokeLinecap="round"
                                      strokeLinejoin="round"></path>
                            </svg>
                        </button>

                        <div
                            className="flex items-center justify-center"
                            onClick={togglePlayback}
                        >
                            <button className="rounded-full focus:outline-none">
                                <div
                                    className="cursor-pointer w-12 h-12 rounded-full flex items-center justify-center">
                                    {!playing && (
                                        <svg id="play-icon" className="ml-[5px]" width="15.5" height="18.5"
                                             viewBox="0 0 31 37"
                                             fill="none" xmlns="http://www.w3.org/2000/svg">
                                            <path fillRule="evenodd" clipRule="evenodd"
                                                  d="M29.6901 16.6608L4.00209 0.747111C2.12875 -0.476923 0.599998 0.421814 0.599998 2.75545V33.643C0.599998 35.9728 2.12747 36.8805 4.00209 35.6514L29.6901 19.7402C29.6901 19.7402 30.6043 19.0973 30.6043 18.2012C30.6043 17.3024 29.6901 16.6608 29.6901 16.6608Z"
                                                  className="fill-slate-200"></path>
                                        </svg>
                                    )}

                                    {playing && (
                                        <svg id="pause-icon" width="12" height="18" viewBox="0 0 24 36" fill="none"
                                             xmlns="http://www.w3.org/2000/svg">
                                            <rect width="6" height="36" rx="3"
                                                  className="fill-slate-200"></rect>
                                            <rect x="18" width="6" height="36" rx="3"
                                                  className="fill-slate-200"></rect>
                                        </svg>
                                    )}
                                </div>
                            </button>
                        </div>

                        <button onClick={() => skipFrame('forward')} className="p-2 rounded focus:outline-none">
                            <svg width="18" height="18" viewBox="0 0 32 32" fill="none"
                                 xmlns="http://www.w3.org/2000/svg">
                                <path
                                    d="M6 7C6 5.76393 7.41115 5.05836 8.4 5.8L20.4 14.8C21.2 15.4 21.2 16.6 20.4 17.2L8.4 26.2C7.41115 26.9416 6 26.2361 6 25V7Z"
                                    fill="#94A3B8" stroke="#94A3B8" strokeWidth="2" strokeLinejoin="round"></path>
                                <path d="M26 5L26 27" stroke="#94A3B8" strokeWidth="2" strokeLinecap="round"
                                      strokeLinejoin="round"></path>
                            </svg>
                        </button>
                    </div>


                </div>
            </div>

            {/*slider*/}
            <div className="w-full flex flex-col z-10 my-3">
                <div className="relative w-full h-1.5 bg-gray-300 dark:bg-gray-500 rounded-full mb-3 cursor-pointer">
                    <input
                        type="range"
                        id="song-percentage-played"
                        className="appearance-none w-full h-full opacity-0 absolute inset-0 z-10"
                        step=".1"
                        value={progress}
                        onChange={handleSliderChange}
                        style={{
                            background: `linear-gradient(to right, #EF4444 0%, #EF4444 ${progress}%, #D1D5DB ${progress}%, #D1D5DB 100%)`
                        }}
                    />
                    <div className="absolute top-0 left-0 h-full rounded-full"
                         style={{width: `${progress}%`, background: '#EF4444'}}></div>
                    <div
                        className="absolute top-1/2 transform -translate-y-1/2 -translate-x-1/2 h-4 w-4 bg-red-500 rounded-full shadow"
                        style={{left: `${progress}%`}}></div>
                </div>

                <div className="flex w-full justify-between">
                    <span
                        className="amplitude-current-time text-xs font-sans tracking-wide font-medium text-red-500">
                        {formatTime(videoRef.current ? videoRef.current.currentTime : 0)}
                    </span>
                    <span className="amplitude-duration-time text-xs font-sans tracking-wide font-medium text-gray-500">
                        {formatTime(videoRef.current ? videoRef.current.duration : 0)}
                    </span>
                </div>
            </div>


            <PositionSelection skipToPercentage={skipToPercentage}/>

        </div>
    );
}

export default VideoPlayer;
