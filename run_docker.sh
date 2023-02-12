docker system prune -f
git pull https://github.com/jlnk03/pose.git
docker-compose build
docker-compose up