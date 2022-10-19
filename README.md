#Readme
## Deploy
```shell
# install latest version of Docker first
git clone git@github.com:alfredhot/reserv_hwadam.git

cd reserv_hwadam

echo "TOKEN={YOUR_BOT_TOKEN_HERE}" > .env

# docker-compose build or
docker compose build

# docker-compose up -d
docker compose up -d

``` 

## In your bot
Just send '$hello' to start your session