/*
  Warnings:

  - A unique constraint covering the columns `[videoId]` on the table `video` will be added. If there are existing duplicate values, this will fail.

*/
-- CreateIndex
CREATE UNIQUE INDEX "video_videoId_key" ON "video" ("videoId");
