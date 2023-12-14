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
4. Create the following Github Actions secret variables in the Github repository:
    - `TF_VAR_do_token`: API key token
    - `TF_VAR_ssh_fingerprint`: SSH key
5. Run Github actions `deploy-infrastructure.yml` workflow to create the project's infrastructure