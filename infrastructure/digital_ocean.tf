provider "digitalocean" {
  token = var.do_token
}

resource "digitalocean_droplet" "droplet" {
  image    = "ubuntu-23-10-x64"
  name     = "ubuntu-s-1vcpu-512mb-10gb-ams3-01"
  region   = "ams3"
  size     = "s-1vcpu-512mb-10gb"
  ssh_keys = [var.ssh_fingerprint]
}

resource "digitalocean_project" "project" {
  name      = "sermadrid"
  resources = [digitalocean_droplet.droplet.urn]
}