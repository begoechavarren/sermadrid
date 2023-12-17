# SERMadrid

```
$ docker-compose build --no-cache
$ docker-compose up -d
```

http://localhost:80

- datetime: `2024-01-01T12:30:00`
- latitude: `40.416775`
- longitude: `-3.703790`

## ⚙️ Installation & Setup

### Infrastructure

1. Create Digital Ocean account
2. Create a Digital Ocean [API key](https://docs.digitalocean.com/reference/api/create-personal-access-token/)
3. Create a Digital Ocean [SSH key](https://docs.digitalocean.com/reference/doctl/reference/compute/ssh-key/create/)
4. Create an AWS account
5. Create an AWS [access key](https://repost.aws/knowledge-center/create-access-key)
6. Create the following Github Actions secret variables in the Github repository:
    - `DO_TOKEN`: Digital Ocean API key token
    - `SSH_PRIVATE_KEY`: Digital ocean SSH private key
    - `SSH_FINGERPRINT`: Digital Ocean SSH key fingerprint # TODO: Rename
    - `AWS_ACCESS_KEY_ID`: AWS access key ID
    - `AWS_SECRET_ACCESS_KEY`: AWS secret access key
    # TODO: Add others
7. Create the following Github Actions variables in the Github repository:
    - `AWS_S3_BUCKET_NAME`: Name to give to the AWS S3 bucket
    - `AWS_REGION`: Region to use for the AWS S3 bucket
    # TODO: Add others
8. Run Github actions `deploy-infrastructure.yml` workflow to create the project's infrastructure