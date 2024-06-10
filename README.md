<div align="center">
  <h1>🚘 sermadrid</h1>
  <p><em>E2E app to search for public parking availability in Madrid SER zone</em></p>
  <p><a href="http://sermadrid.org">sermadrid.org</a></p>
</div>

> [!WARNING]
> `sermadrid` is currently under active development.


## ⚙️ Local deployment

1. Create `.env` file in the repository root with the following variables

    ```
    BACKEND_CORS_ORIGINS=["http://localhost","http://0.0.0.0"]
    # Mapbox token obtained from mapbox.com
    MAPBOX_TOKEN={MAPBOX_TOKEN}
    ```
2. Run the following commands to spin up the Docker containers
    
    ```
    $ docker-compose build --no-cache
    $ docker-compose up -d
    ```

TODO: Update this
The app will then be available in http://localhost:80. Some example variables to run it are:
- datetime: `2024-01-01T12:30:00`
- latitude: `40.416775`
- longitude: `-3.703790`

Afterwards, to stop all the running containers, run:
```
$ docker stop $(docker ps -a -q) 
```


## ⚙️ Remote deployment

### Infrastructure

1. Create a Digital Ocean account
2. Create a Digital Ocean [API key](https://docs.digitalocean.com/reference/api/create-personal-access-token/)
3. Create a Digital Ocean [SSH key](https://docs.digitalocean.com/reference/doctl/reference/compute/ssh-key/create/)
4. Create an AWS account
5. Create an AWS [access key](https://repost.aws/knowledge-center/create-access-key)
6. Register a valid website domain via a domain registrar and [point to Digital Ocean name servers](https://docs.digitalocean.com/products/networking/dns/getting-started/dns-registrars/) from it
7. Create the following Github Actions secret variables in the Github repository:
    - `DO_API_KEY_TOKEN`: Digital Ocean API key token
    - `DO_SSH_KEY_ID`: Digital Ocean SSH key ID
    - `DO_SSH_PRIVATE_KEY`: Digital Ocean SSH private key
    - `AWS_ACCESS_KEY_ID`: AWS access key ID
    - `AWS_SECRET_ACCESS_KEY`: AWS secret access key
8. Create the following Github Actions variables in the Github repository:
    - `AWS_S3_BUCKET_NAME`: Name to give to the AWS S3 bucket
    - `AWS_REGION`: Region to use for the AWS S3 bucket
    - `DOMAIN_NAME`: Registered website domain name
9. Run Github actions `deploy-infrastructure.yml` workflow to create the project's infrastructure

### App

1. Retrieve the Digital Ocean droplet IP from the [Digital Ocean Control Panel](https://cloud.digitalocean.com/)
2. Create a [Mapbox](https://www.mapbox.com/) account and generate an access token
3. Create the following Github Actions secret variables in the Github repository:
    - `DO_DROPLET_IP`: Digital Ocean droplet IP
    - `DO_DROPLET_USER`: Digital Ocean droplet username (default username is *root*)
    - `MAPBOX TOKEN`: Mapbox access token
    - `CERTBOT_EMAIL`: Email to be used by Certbot to obtain the SSL certificate to enable HTTPS
4. Create the following Github Actions variables in the Github repository:
    - `BACKEND_CORS_ORIGINS`: A comma-separated list of origins allowed to access the backend to configure the CORS policy (in this case just the frontend: *["http://{DO_DROPLET_IP}", "http://{DOMAIN_NAME}", "http://www.{DOMAIN_NAME}"]*)
5. Run Github actions `deploy-app.yml` workflow to deploy the app
