import {NextResponse} from 'next/server';
import {prisma} from '@/lib/utils';


const getVideos = async (req, params) => {
    // Get the current user from the session
    // const session = await getServerSession(OPTIONS);
    // // console.log(session);
    // const user = await prisma.user.findUnique({
    //   where: { email: session.user.email },
    // });

    try {
        const videos = await prisma.video.findMany(
            {
                // where: {
                //     videoId: params.params.videoId
                // },
                orderBy: {
                    createdAt: 'desc' // Sort by Date Added DESC
                }
            }
        );

        return NextResponse.json({videos});
    } catch (error) {
        console.log(error);
        return NextResponse.error(new Error('Not Found'));
    }

};

export {getVideos as GET}
