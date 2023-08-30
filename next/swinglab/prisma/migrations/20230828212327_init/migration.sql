/*
  Warnings:

  - Added the required column `videoId` to the `video` table without a default value. This is not possible if the table is not empty.

*/
-- AlterTable
ALTER TABLE "video"
    ADD COLUMN "videoId" VARCHAR(255) NOT NULL;
