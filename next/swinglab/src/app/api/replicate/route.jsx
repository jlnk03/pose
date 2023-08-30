// import {v4 as uuid} from "uuid";
import {DeleteObjectCommand, GetObjectCommand, PutObjectCommand, S3Client} from "@aws-sdk/client-s3";
import {getSignedUrl} from '@aws-sdk/s3-request-presigner';
import Replicate from 'replicate';
import {NextResponse} from 'next/server';
import {prisma} from '@/lib/utils';


const s3Client = new S3Client({
    region: process.env.AWS_REGION,
    credentials: {
        accessKeyId: process.env.AWS_ACCESS_KEY_ID,
        secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY,
    },
});

const replicate = new Replicate({
    auth: process.env.REPLICATE_API_TOKEN,
});

async function uploadVideoToS3(file, fileName, type) {
    // console.log("Uploading video to S3...");
    // console.log(process.env.AWS_S3_BUCKET_NAME)
    const fileKey = `${Date.now()}-${fileName}`;

    const params = {
        Bucket: process.env.AWS_S3_BUCKET_NAME,
        Key: fileKey,
        Body: file,
        ContentType: type,
    };

    await s3Client.send(new PutObjectCommand(params));

    const url = await getSignedUrl(s3Client, new GetObjectCommand(params), {expiresIn: 3600});

    // console.log("Video uploaded to S3:", url);

    return {url, fileKey};
}

const ProcessVideo = async (request) => {
    try {
        // console.log("Processing video...")
        const formData = await request.formData();
        // console.log("Form data:", formData)
        const file = formData.get("video");
        // console.log("File:", file)

        if (!file) {
            return {status: 400, body: {error: "File blob is required."}};
        }

        const mimeType = file.type;
        const fileExtension = mimeType.split("/")[1];

        const buffer = Buffer.from(await file.arrayBuffer());
        const {url, fileKey} = await uploadVideoToS3(buffer, `video-${crypto.randomUUID()}.${fileExtension}`, mimeType);

        // console.log("Running Replicate...");

        const replicateOutput = await replicate.run(
            "jlnk03/predict-pose:40e95a0ce71067bffcf81a826da74aa039d52213e2af9157ddc2702e6a257df3",
            {
                input: {
                    video: url,
                    calc_angles: true
                }
            }
        );

        // console.log("Replicate output:", replicateOutput);

        // Deleting video from S3 after processing
        const deleteParams = {
            Bucket: process.env.AWS_S3_BUCKET_NAME,
            Key: fileKey
        };

        await s3Client.send(new DeleteObjectCommand(deleteParams));

        let [
            angles,
            armV,
            duration,
            fps,
            impactRatio,
            outPath
        ] = replicateOutput;

        // get output
        const outputToUpload = {
            'angles': angles,
            'armV': armV,
            'duration': duration,
            'fps': fps,
            'impactRatio': impactRatio
        };

        const response = await fetch(outPath);

        if (!response.ok) {
            throw new Error('Failed to fetch the video.');
        }

        const videoBuffer = await response.arrayBuffer();

        const date = Date.now();
        const id = crypto.randomUUID();

        // upload video to s3 specified in outpath
        const videoKey = `${date}-${id}.mp4`;
        const videoParams = {
            Bucket: process.env.AWS_S3_BUCKET_NAME,
            Key: videoKey,
            Body: Buffer.from(videoBuffer),
            ContentType: 'video/mp4',
        };

        // upload to s3
        const outputKey = `${date}-${id}.json`;
        const outputParams = {
            Bucket: process.env.AWS_S3_BUCKET_NAME,
            Key: outputKey,
            Body: JSON.stringify(outputToUpload),
        };

        await s3Client.send(new PutObjectCommand(videoParams));

        await s3Client.send(new PutObjectCommand(outputParams));

        // save to db
        await prisma.video.create({
            data: {
                name: `${date}-${id}`,
                videoId: id,
            }
        });

        // get object from db
        const video = await prisma.video.findUnique({
            where: {
                videoId: id,
            }
        });

        // get signed url
        const videoUrl = await getSignedUrl(s3Client, new GetObjectCommand(videoParams), {expiresIn: 3600});
        console.log("Video uploaded to S3:", videoUrl);

        return NextResponse.json({
            success: true,
            angles,
            duration,
            fps,
            impactRatio,
            videoUrl,
            video: video,
            videoId: id
        });
    } catch (error) {
        console.error("Error processing video:", error);
        return NextResponse.error(new Error('Error processing video.'));
    }
}

export {ProcessVideo as POST};

