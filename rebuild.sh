docker-compose down
docker image remove poker_statistic-flask-app:latest
docker system prune -f --volumes
docker-compose up -d 