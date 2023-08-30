'use client'

import AnalysisView from "@/app/[lang]/components/AnalysisView";
import {
    usePositionVideoStorage,
    useReplicateStorage,
    useVideoIdStorage,
    useVideoUrlStorage
} from "../../context/storage";
import UploadComponent from "@/app/[lang]/components/UploadComponent";
import {useSearchParams} from 'next/navigation'
import {useEffect} from "react";

// import { SheetDemo } from './Navbar';

function Dashboard({dictionary}) {

    const {replicateOut, setReplicateOut} = useReplicateStorage();
    const {videoUrl, setVideoUrl} = useVideoUrlStorage();
    const {videoId, setVideoId} = useVideoIdStorage();
    const {positionVideo, setPositionVideo} = usePositionVideoStorage();

    const searchParams = useSearchParams()
    let videoIdSearch = searchParams.get('videoId')
    // console.log('videoId', videoId)

    useEffect(() => {
        if (videoIdSearch) {
            // console.log('videoId is not null')
            fetch(`/api/storage/${videoIdSearch}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                },
            })
                .then(response => response.json())
                .then(data => {
                    // console.log('data', data)
                    setReplicateOut(data['json']);
                    setVideoUrl(data['url']);
                    setPositionVideo([0, 0.25, data['json']['impactRatio'], 1]);
                    setVideoId(videoIdSearch);
                })
                .catch((error) => {
                    console.error('Error:', error);
                });
        }

        return () => {
            // cleanup
            setReplicateOut([])
            setVideoUrl('')
        }

    }, [videoIdSearch])


    if (replicateOut.length === 0) {

        return (
            <>
                {/* <SheetDemo /> */}
                <div
                    id="body"
                    className="lg:mx-16 mx-4 lg:pl-60 pt-5 2xl:w-[90rem] h-full relative flex flex-col justify-center items-center"
                >
                    <span>{videoIdSearch}</span>
                    <UploadComponent dictionary={dictionary}/>

                </div>
            </>
        )
    }

    return (
        <div>
            <div
                id="body"
                className="lg:mx-16 mx-4 lg:pl-60 pt-5 2xl:w-[90rem] h-full grow"
            >
                <AnalysisView dictionary={dictionary} path={videoUrl}/>
            </div>
        </div>
    );
}

export default Dashboard;