'use client'

import React, {useEffect, useRef, useState} from 'react';
import {
    useFileStorage,
    useIsUploadingStorage,
    usePositionVideoStorage,
    useReplicateStorage,
    useVideoIdStorage,
    useVideoUrlStorage
} from "../../context/storage";
import Spinner from "./Spinner";

const UploadSide = ({
                        dictionary,
                        disabled,
                        className = 'h-32 flex-none mt-2 mx-2',
                        textSize,
                        svgSize = '1.5em',
                        tiltAngle = 10
                    }) => {
    const [isDragging, setIsDragging] = useState(false);
    const [isRejected, setIsRejected] = useState(false);
    const [borderColor, setBorderColor] = useState('border-slate-400');
    // const [uploading, setUploading] = useState(false);
    const {replicateOut, setReplicateOut} = useReplicateStorage();
    const {positionVideo, setPositionVideo} = usePositionVideoStorage();
    const {isUploading, setIsUploading} = useIsUploadingStorage();
    const {videoUrl, setVideoUrl} = useVideoUrlStorage();
    const {files, setFiles} = useFileStorage();
    const {videoId, setVideoId} = useVideoIdStorage();

    const blobRef = useRef(null);
    const fakeBlobRef = useRef(null);
    const cardRef = useRef(null);

    const handleDragEnter = () => {
        setIsDragging(true);
        setBorderColor('border-blue-700')
    }

    const handleDragLeave = () => {
        setIsDragging(false);
        setBorderColor('border-slate-400')
    }

    const sendToReplicate = async (file) => {
        setIsUploading(true);

        const formData = new FormData();
        formData.append('video', file);

        console.log('Sending video to Replicate...');
        fetch('/api/replicate', {method: 'POST', body: formData})
            .then(response => response.json())
            .then(data => {
                setReplicateOut(data);
                setPositionVideo([0, 0.25, data['impactRatio'], 1]);
                setVideoUrl(data['videoUrl']);
                setFiles([data['video'], ...files]);
                setVideoId(data['videoId']);
            })
            .catch(error => console.error('Error:', error))
            .finally(() => setIsUploading(false));
    };


    const handleFileChange = (event) => {
        const file = event.target.files[0];
        if (file && file.size > 20e6) {
            setIsRejected(true);
            setBorderColor('border-red-400');
        } else {
            setIsRejected(false);
            // setBorderColor('border-green-400');
            sendToReplicate(file); // send the video to Replicate
        }
        setIsDragging(false);
        setBorderColor('border-slate-400');
    };

    useEffect(() => {
        const card = cardRef.current;
        const handleMouseMove = (ev) => {
            const blob = blobRef.current;
            const fblob = fakeBlobRef.current;

            if (blob && fblob) {
                const rec = fblob.getBoundingClientRect();

                blob.style.transform = `translate(${ev.clientX - rec.left - (rec.width / 2)}px,${ev.clientY - rec.top - (rec.height / 2)}px)`;
            }

            if (card) {
                const x = ev.clientX - card.getBoundingClientRect().left;
                const y = ev.clientY - card.getBoundingClientRect().top;

                const xc = card.clientWidth / 2;
                const yc = card.clientHeight / 2;

                // offset from center of card in percentage
                const offsetX = (x - xc) / xc * tiltAngle;
                const offsetY = (y - yc) / yc * tiltAngle;

                console.log(offsetX, offsetY);

                card.style.setProperty('--rotate-x', `${-offsetY}deg`);
                card.style.setProperty('--rotate-y', `${offsetX}deg`);
            }
        };

        const handleMouseLeave = () => {
            const blob = blobRef.current;
            const fblob = fakeBlobRef.current;

            if (blob && fblob) {
                blob.style.transform = `translate(0px,0px)`;
            }

            if (card) {
                card.style.setProperty('--rotate-x', `0deg`);
                card.style.setProperty('--rotate-y', `0deg`);
            }
        };

        card.addEventListener('mouseleave', handleMouseLeave);

        card.addEventListener('mousemove', handleMouseMove);

        // Clean up the event listener when the component unmounts
        return () => {
            card.removeEventListener('mouseleave', handleMouseLeave);
            card.removeEventListener('mousemove', handleMouseMove);
        };
    }, []);


    return (
        <>
            <div ref={cardRef}
                 className={`card outline-4 dark:outline-blue-400 p-1 outline-indigo-500 -outline-offset-4 outline-dashed  rounded-lg relative dark:bg-blue-950 bg-indigo-700 dark:bg-opacity-20 bg-opacity-20 overflow-hidden ${className} `}>
                <div className='absolute inset-0 bg-opacity-20 z-[-2] bg-black'></div>
                <div
                    className="relative rounded-md flex flex-none items-center justify-center text-center inline-block text-sm border-dashed border-indigo-300 bg-indigo-100/40 dark:border-blue-300 dark:bg-blue-950/70 h-full dark:text-blue-300 text-indigo-700">
                    <input
                        disabled={isUploading}
                        type="file"
                        accept=".mp4, .mov, .avi"
                        onChange={handleFileChange}
                        className="grow h-full opacity-0 absolute inset-0 cursor-pointer z-30"
                    />

                    {isUploading && <Spinner/>} {/* render spinner when loading is true */}

                    {!isUploading && (
                        <span className='flex flex-col gap-2 items-center justify-center'>
                        <svg className='dark:fill-indigo-300 fill-indigo-700' xmlns="http://www.w3.org/2000/svg"
                             height={svgSize} viewBox="0 0 384 512"><path
                            d="M64 0C28.7 0 0 28.7 0 64V448c0 35.3 28.7 64 64 64H320c35.3 0 64-28.7 64-64V160H256c-17.7 0-32-14.3-32-32V0H64zM256 0V128H384L256 0zM64 288c0-17.7 14.3-32 32-32h96c17.7 0 32 14.3 32 32v96c0 17.7-14.3 32-32 32H96c-17.7 0-32-14.3-32-32V288zM300.9 397.9L256 368V304l44.9-29.9c2-1.3 4.4-2.1 6.8-2.1c6.8 0 12.3 5.5 12.3 12.3V387.7c0 6.8-5.5 12.3-12.3 12.3c-2.4 0-4.8-.7-6.8-2.1z"/></svg>
                        <span className={`font-bold ${textSize ? textSize : 'text-sm'}`}>
                            {dictionary['upload-video']}
                        </span>
                    </span>
                    )}

                </div>

                <div className='blob' ref={blobRef}></div>
                <div className='fakeblob' ref={fakeBlobRef}></div>

            </div>
        </>
    );
}

export default UploadSide;
