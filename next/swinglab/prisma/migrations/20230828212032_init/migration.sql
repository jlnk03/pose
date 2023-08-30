-- CreateTable
CREATE TABLE "video"
(
    "id"        SERIAL       NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,
    "name"      VARCHAR(255) NOT NULL,

    CONSTRAINT "video_pkey" PRIMARY KEY ("id")
);
