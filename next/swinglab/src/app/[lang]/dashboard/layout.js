import {
    FileStorageContextProvider,
    IsUploadingStorageContextProvider,
    PositionVideoStorageContextProvider,
    ReplicateStorageContextProvider,
    VideoIdStorageContextProvider,
    VideoUrlStorageContextProvider
} from "@/app/context/storage";


export default function DashboardLayout({children}) {
    return (
        <section>
            <ReplicateStorageContextProvider>
                <PositionVideoStorageContextProvider>
                    <IsUploadingStorageContextProvider>
                        <VideoUrlStorageContextProvider>
                            <VideoIdStorageContextProvider>
                                <FileStorageContextProvider>
                                    {children}
                                </FileStorageContextProvider>
                            </VideoIdStorageContextProvider>
                        </VideoUrlStorageContextProvider>
                    </IsUploadingStorageContextProvider>
                </PositionVideoStorageContextProvider>
            </ReplicateStorageContextProvider>
        </section>
    )
}