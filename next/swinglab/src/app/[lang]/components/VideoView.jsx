import React from 'react';
import VideoPlayer from "./VideoPlayer";

function VideoComponent({disabled, path}) {
    if (path) {
        path += '#t=0.001';
    }

    return (
        <div
            className="items-center flex items-start justify-center mb-5 text-center inline-block flex-col">
            <VideoPlayer src={path} disabled={disabled}/>
        </div>
    );
}

export default VideoComponent;
