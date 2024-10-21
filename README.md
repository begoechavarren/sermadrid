<div align="center">
  <h1>🚘 sermadrid</h1>
  <p><em>E2E project to search for public parking availability in Madrid SER zone</em></p>
  <p><a href="http://sermadrid.org">sermadrid.org</a></p>

</div>

> [!WARNING]
> `sermadrid` is currently under active development.

`sermadrid` is an E2E Machine Learning project to search for public parking availability in Madrid SER zone.

The project results in the website [sermadrid.org](https://sermadrid.org/), which is publicly available, and allows users to search for parking availability based on their chosen date and address.

It uses Time Series models, with one model per neighbourhood, to make the predictions. These models have been trained on four years of parking ticket data (2020 to 2024).

The project consists of several components, including the frontend (Node.js), backend (FastAPI), infrastructure (Digital Ocean & AWS, defined with Terraform), CI/CD deployment pipelines (GitHub Actions), MLOps framework server for training workflows orchestration (ZenML), and experiment tracking and model registry server (MLFlow).

<img src="assets/sermadrid.png" alt="sernadrid_screenshot" width="825" />

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

## 🧩 Project Components

- **Frontend**: The frontend is developed using `Vue.js`, with `Mapbox` integrated to handle mapping and geospatial functionalities. It is served by an `nginx` web server, which is configured with SSL certificates for secure HTTPS communication, ensuring a smooth and secure user experience.

- **Backend**: The backend consists of a `FastAPI` application that serves the sermadrid Python package. This package is responsible for the core logic of predicting parking availability. The FastAPI app is designed to load machine learning models at startup, enabling efficient and responsive handling of user requests.

- **Infrastructure**: The project’s infrastructure is managed using `Terraform` and is hosted across `Digital Ocean` and `AWS`. Digital Ocean is used to host the application, including components like droplets, domain management, and firewall configurations. AWS is employed for the ZenML MLOps framework components.

- **CI/CD Pipelines**: `GitHub Actions` is utilized to manage CI/CD pipelines, with `Docker Compose` orchestrating the environment. Currently there are two pipelines: one for deploying the Digital Ocean infrastructure and another for deploying the sermadrid web application (frontend and backend). Next steps include building a CI/CD pipeline for deployment of ZenML infrastructure, server, and pipelines.

- **MLOps Framework**: `ZenML` is the chosen framework for orchestrating the machine learning training workflows. ZenML supports environment-agnostic execution, allowing the workflows to run both locally and on AWS. The AWS stack components are created through the Terraform scripts located in the *infrastructure/zenml* directory. The project relies on the two ZenML pipelines defined: "feature engineering" and "training", each of them containing multiple steps which process the raw data and train the Time Series models that power sermadrid.

- **Experiment Tracking & Model Registry**: `MLFlow` is integrated as part of the AWS infrastructure, with the setup of its server defined in the *infrastructure/zenml* directory. MLFlow handles experiment tracking and model registry. Next steps include including MLFlow into the ZenML pipelines to track experiments and register models, as well as enabling direct loading of models from MLFlow into the backend.

## 📥 Input Data

The project utilizes three primary data sources from the Madrid City Council: Regulated Parking Service (SER) Parking Tickets, SER Streets and Parking Spaces, and SER Area Map. These datasets are processed and combined to create `sermadrid`, with parking ticket data aggregated for Time Series features and geospatial data enabling map overlays and address-based searches.

### Dataset Details

| Dataset | Description | Source | Format | Update Frequency | Usage |
|---------|-------------|--------|--------|------------------|-------|
| [SER Parking Tickets](https://datos.madrid.es/portal/site/egob/menuitem.c05c1f754a33a9fbe4b2e4b284f1a5a0/?vgnextoid=67663c0a55e16710VgnVCM1000001d4a900aRCRD) | Data on parking tickets issued by the Regulated Parking Service (SER) from parking meters and mobile payment applications in Madrid. This dataset provides detailed information for each ticket, including parking meter ID, operation date, reservation start and end times, neighbourhood, zone type, permit type, reserved minutes, and amount paid. | [Madrid Open Data Portal](https://datos.madrid.es/portal/site/egob) | CSV | Quarterly | Training Time Series models per neighbourhood by processing & aggregating the data by time slots. |
| [SER Streets and Spaces](https://datos.madrid.es/portal/site/egob/menuitem.c05c1f754a33a9fbe4b2e4b284f1a5a0/?vgnextoid=4973b0dd4a872510VgnVCM1000000b205a0aRCRD) | Data on the number of parking spaces within the SER zone, broken down by neighbourhood. | [Madrid Open Data Portal](https://datos.madrid.es/portal/site/egob) | CSV | Quarterly | Enhancing predictions with additional parking information. |
| [SER Area Map](https://geoportal.madrid.es/IDEAM_WBGEOPORTAL/dataset.iam?id=9506daa5-e317-11ec-8359-60634c31c0aa) | Geospatial data of the Regulated Parking Service area, including the delimitation of the SER area and its subdivision into neighbourhoods. | [Madrid Geoportal](https://geoportal.madrid.es/) | Shapefile (SHP) | Last updated: 03/06/2022 | Frontend visualization, showing a mask in non-SER Madrid areas, and identifying the neighbourhood selected by the user. |

## 🔧 Technical Details

Other technical details include the use by `sermadrid` of:

* **[Ruff](https://github.com/astral-sh/ruff)**: A fast Python linter and formatter written in Rust.
* **[pre-commit](https://github.com/pre-commit/pre-commit)**: A tool that automates code quality checks before each commit.
* **[Poetry](https://python-poetry.org/)**: A tool for dependency management and packaging that builds a graph of dependencies and finds compatible package versions, avoiding incompatibility issues.


## ⚙️ Deployment

These are the guidelines to deploy the frontend and backend which compose the `sermadrid` web app, both locally and remotely.

### Local deployment

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

The app will then be available in http://localhost:80.

Afterwards, to stop all the running containers, run:
```
$ docker stop $(docker ps -a -q) 
```

### Remote deployment

**App Infrastructure**

1. Create a Digital Ocean account
2. Create a Digital Ocean [API key](https://docs.digitalocean.com/reference/api/create-personal-access-token/)
3. Create a Digital Ocean [SSH key](https://docs.digitalocean.com/reference/doctl/reference/compute/ssh-key/create/)
4. Create an AWS account
5. Create an AWS [access key](https://repost.aws/knowledge-center/create-access-key)
6. Register a valid website domain via a domain registrar and [point to Digital Ocean name servers](https://docs.digitalocean.com/products/networking/dns/getting-started/dns-registrars/) from it
7. Create the following GitHub Actions secret variables in the GitHub repository:
    - `DO_API_KEY_TOKEN`: Digital Ocean API key token
    - `DO_SSH_KEY_ID`: Digital Ocean SSH key ID
    - `DO_SSH_PRIVATE_KEY`: Digital Ocean SSH private key
    - `AWS_ACCESS_KEY_ID`: AWS access key ID
    - `AWS_SECRET_ACCESS_KEY`: AWS secret access key
8. Create the following GitHub Actions variables in the GitHub repository:
    - `AWS_S3_BUCKET_NAME`: Name to give to the AWS S3 bucket
    - `AWS_REGION`: Region to use for the AWS S3 bucket
    - `DOMAIN_NAME`: Registered website domain name
9. Run GitHub actions `deploy-infrastructure.yml` workflow to create the project's infrastructure

**App**

1. Retrieve the Digital Ocean droplet IP from the [Digital Ocean Control Panel](https://cloud.digitalocean.com/)
2. Create a [Mapbox](https://www.mapbox.com/) account and generate an access token
3. Create the following GitHub Actions secret variables in the GitHub repository:
    - `DO_DROPLET_IP`: Digital Ocean droplet IP
    - `DO_DROPLET_USER`: Digital Ocean droplet username (default username is *root*)
    - `MAPBOX TOKEN`: Mapbox access token
    - `CERTBOT_EMAIL`: Email to be used by Certbot to obtain the SSL certificate to enable HTTPS
4. Create the following GitHub Actions variables in the GitHub repository:
    - `BACKEND_CORS_ORIGINS`: A comma-separated list of origins allowed to access the backend to configure the CORS policy (in this case just the frontend: *["http://{DO_DROPLET_IP}", "http://{DOMAIN_NAME}", "http://www.{DOMAIN_NAME}"]*)
5. Run GitHub actions `deploy-app.yml` workflow to deploy the app

**ML Infrastructure**

1. Create the following GitHub Actions variables in the GitHub repository:
    - `AWS_S3_REMOTE_STATE_BUCKET_NAME`: Name to give to the AWS S3 bucket used for the Terraform remote state of this infrastructure stack
    - `AWS_S3_ZENML_BUCKET_NAME`
    - `AWS_S3_MLFLOW_BUCKET_NAME`
2. Create the following GitHub Actions secret variables in the GitHub repository:
    - `ZENML_USERNAME`: The username for the ZenML Server
    - `ZENML_PASSWORD`: The password for the ZenML Server
    - `MLFLOW_USERNAME`: The username for the MLflow Tracking Server
    - `MLFLOW_PASSWORD`: The password for the MLflow Tracking Server
    - `AWS_MLFLOW_ARTIFACT_S3_ACCESS_KEY`: The AWS access key for using S3 as MLflow artifact store
    - `AWS_MLFLOW_ARTIFACT_S3_SECRET_KEY`: The AWS secret key for using S3 as MLflow artifact store


TODO: Add for local deployment, create .tfvars and run terraform with it
TODO: Add comment about being able to create or destroy infrastructure with TF through the Github action pipelines

## ➡️ Next Steps

`sermadrid` is under active development, with the following next steps planned:

* **ZenML Infrastructure Deployment**: Implement a `GitHub Actions` pipeline to deploy the `ZenML` infrastructure on `AWS`, including the `MLFlow` server, utilizing the existing Terraform code in `infrastructure/zenml`.
* **ZenML Pipelines Deployment**: Create a GitHub Actions pipeline to register `ZenML` pipelines on the remote AWS server and automate their execution using AWS Lambda functions.
* **MLFlow ZenML Integration**: Integrate `MLFlow` for experiment tracking and model registry within the ZenML pipelines to streamline model management.
* **MLFlow Backend Integration**: Update the backend to load models on startup directly from the `MLFlow API` instead of the current S3 bucket, ensuring the use of the latest production models.
* **Model Monitoring**: Introduce model monitoring with `Evidently` and `Grafana` to track performance metrics over time.
* **Testing**: Develop unit and integration tests using `pytest` for both the FastAPI backend and the ZenML training pipelines to ensure code reliability and robustness.
