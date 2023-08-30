import {GetObjectCommand, S3Client} from "@aws-sdk/client-s3";
import {getSignedUrl} from '@aws-sdk/s3-request-presigner';
import {NextResponse} from 'next/server';
import {prisma} from '@/lib/utils';

const s3Client = new S3Client({
    region: process.env.AWS_REGION,
    credentials: {
        accessKeyId: process.env.AWS_ACCESS_KEY_ID,
        secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY,
    },
});

const getVideoFromS3 = async (req, params) => {
    // Get the current user from the session
    // const session = await getServerSession(OPTIONS);
    // // console.log(session);
    // const user = await prisma.user.findUnique({
    //   where: { email: session.user.email },
    // });

    // console.log(params.params)

    try {
        const video = await prisma.video.findFirstOrThrow(
            {
                where: {
                    videoId: params.params.videoId
                },
                // orderBy: {
                //     createdAt: 'desc' // Sort by Date Added DESC
                // }
            }
        );

        // console.log(video);

        const videoName = video.name;

        const command = new GetObjectCommand({
            Bucket: process.env.AWS_S3_BUCKET_NAME,
            // Key: `${user.id}/${videoName}.mp4`,
            Key: `${videoName}.mp4`,
        });

        const url = await getSignedUrl(s3Client, command, {expiresIn: 3600});

        const commandJson = new GetObjectCommand({
            Bucket: process.env.AWS_S3_BUCKET_NAME,
            // Key: `${user.id}/${videoName}.json`,
            Key: `${videoName}.json`,
        });

        const urlJson = await getSignedUrl(s3Client, commandJson, {expiresIn: 3600});

        // get json file from s3
        const responseJson = await fetch(urlJson);
        const json = await responseJson.json();

        return NextResponse.json({
            url,
            json
        });
    } catch (error) {
        console.log(error);
        return NextResponse.error(new Error('Not Found'));
    }

};

export {getVideoFromS3 as GET}