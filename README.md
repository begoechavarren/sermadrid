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
2. Create an [API key](https://docs.digitalocean.com/reference/api/create-personal-access-token/)
3. Create an [SSH key](https://docs.digitalocean.com/reference/doctl/reference/compute/ssh-key/create/)
4. Create an [Spaces access Key](https://docs.digitalocean.com/products/spaces/how-to/manage-access/)
5. Create the following Github Actions secret variables in the Github repository:
    - `DO_TOKEN`: API key token
    - `SSH_FINGERPRINT`: SSH key # TODO: Rename
    - `DO_SPACES_ACCESS_KEY`: Spaces access key
    - `DO_SPACES_SECRET_KEY`: Spaces secret key
6. Run Github actions `deploy-infrastructure.yml` workflow to create the project's infrastructure