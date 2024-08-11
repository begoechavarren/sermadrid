<div align="center">
  <h1>🚘 sermadrid</h1>
  <p><em>E2E project to search for public parking availability in Madrid SER zone</em></p>
  <p><a href="http://sermadrid.org">sermadrid.org</a></p> <!-- TODO: Add more examples -->

</div>

> [!WARNING]
> `sermadrid` is currently under active development.

`sermadrid` is an E2E Machine Learning project to search for public parking availability in Madrid SER zone.

The project results in the website [sermadrid.org](https://sermadrid.org/), which is publicly available, and allows users to search for parking availability based on their chosen date and address.

It uses Time Series models, with one model per neighborhood, to make the predictions. These models have been trained on four years of parking ticket data (2020 to 2024).

The project consists of several components, including the frontend (Node.js), backend (FastAPI), infrastructure (Digital Ocean & AWS, defined with Terraform), CI/CD deployment pipelines (Github Actions), MLOps framework server for training workflows orchestration (ZenML), and experiment tracking and model registry server (MLFlow).

<img src="assets/sermadrid.png" alt="sernadrid_screenshot" width="825" />

## 📥 Input data


## 🧩 Project Components
* Frontend: Node.js
* Backend: FastAPI
* Infrastructure: DigitalOcean & AWS, managed with Terraform
* CI/CD Pipelines: GitHub Actions
* MLOps Framework: ZenML for training workflow orchestration
* Experiment Tracking & Model Registry: MLFlow

## 📁 Project Structure

```
📂 sermadrid
├── 📂 .github              - GitHub Actions CI/CD pipelines
├── 📂 backend
|   ├── 📂 app              - FastAPI app 
|   └── 📂 sermadrid        - sermadrid python package
├── 📂 frontend             - Node.js app
├── 📂 infrastructure       - Terraform IaC resources
|   ├── 📂 backend          - Digital Ocean backend infrastructure
|   └── 📂 zenml            - AWS ZenML server and stack infrastructure
└── 📂 zenml                - ZenML training workflow pipelines 
```

## ➡️ Next steps

## ⚙️ Local deployment

1. Create `.env` file in the repository root with the following variables # TODO: Add include models

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
5. Create an AWS [access key](https://repost.aws/knowledge-center/create-access-key) # TODO: Add give user AmazonS3 permissions
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
