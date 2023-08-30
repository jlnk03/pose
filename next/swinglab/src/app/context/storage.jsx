'use client'

import {createContext, useContext, useState} from "react"

const StorageContext = createContext(
    {
        replicateOut: [],
        setReplicateOut: () => {
        }
    }
)

export const ReplicateStorageContextProvider = ({children}) => {

    const [replicateOut, setReplicateOut] = useState([]);

    return (
        <StorageContext.Provider value={{replicateOut, setReplicateOut}}>
            {children}
        </StorageContext.Provider>
    )
}

const positionVideoStorage = createContext(
    {
        positionVideo: [],
        setPositionVideo: () => {
        }
    }
)

export const PositionVideoStorageContextProvider = ({children}) => {

    const [positionVideo, setPositionVideo] = useState([]);

    return (
        <positionVideoStorage.Provider value={{positionVideo, setPositionVideo}}>
            {children}
        </positionVideoStorage.Provider>
    )
}

const isUploadingStorage = createContext(
    {
        isUploading: false,
        setIsUploading: () => {
        }
    }
)

export const IsUploadingStorageContextProvider = ({children}) => {

    const [isUploading, setIsUploading] = useState(false);

    return (
        <isUploadingStorage.Provider value={{isUploading, setIsUploading}}>
            {children}
        </isUploadingStorage.Provider>
    )
}

const videoUrlStorage = createContext(
    {
        videoUrl: '',
        setVideoUrl: () => {
        }
    }
)

export const VideoUrlStorageContextProvider = ({children}) => {

    const [videoUrl, setVideoUrl] = useState('');

    return (
        <videoUrlStorage.Provider value={{videoUrl, setVideoUrl}}>
            {children}
        </videoUrlStorage.Provider>
    )
}

const videoIdStorage = createContext(
    {
        videoId: '',
        setVideoId: () => {
        }
    }
)

export const VideoIdStorageContextProvider = ({children}) => {

    const [videoId, setVideoId] = useState('');

    return (
        <videoIdStorage.Provider value={{videoId, setVideoId}}>
            {children}
        </videoIdStorage.Provider>
    )
}

const fileStorage = createContext(
    {
        files: [],
        setFiles: () => {
        }
    }
)

export const FileStorageContextProvider = ({children}) => {

    const [files, setFiles] = useState([]);

    return (
        <fileStorage.Provider value={{files, setFiles}}>
            {children}
        </fileStorage.Provider>
    )
}

export const useReplicateStorage = () => useContext(StorageContext)

export const usePositionVideoStorage = () => useContext(positionVideoStorage)

export const useIsUploadingStorage = () => useContext(isUploadingStorage)

export const useVideoUrlStorage = () => useContext(videoUrlStorage)

export const useVideoIdStorage = () => useContext(videoIdStorage)

export const useFileStorage = () => useContext(fileStorage)