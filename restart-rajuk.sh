git pull origin master
docker build -t rajuk-headmaster .
docker run -d --env-file .env --name rajuk-headmaster rajuk-headmaster