provider "digitalocean" {
  token = var.do_api_key_token
}

resource "digitalocean_project" "project" {
  name = "sermadrid"
  resources = [
    digitalocean_droplet.droplet.urn,
    digitalocean_domain.default.urn,
  ]
}
resource "digitalocean_droplet" "droplet" {
  image      = "ubuntu-24-10-x64"
  name       = "ubuntu-s-1vcpu-2gb-ams3-01"
  region     = local.do_region
  size       = "s-1vcpu-2gb-intel"
  ssh_keys   = [var.do_ssh_key_fingerprint]
  vpc_uuid   = local.do_vpc_uuid
}


resource "digitalocean_domain" "default" {
  name = var.domain_name
}

resource "digitalocean_record" "www_record" {
  domain = digitalocean_domain.default.id
  type   = "A"
  name   = "www"
  value  = digitalocean_droplet.droplet.ipv4_address
}

resource "digitalocean_record" "apex_record" {
  domain = digitalocean_domain.default.id
  type   = "A"
  name   = "@"
  value  = digitalocean_droplet.droplet.ipv4_address
}

resource "digitalocean_firewall" "web_firewall" {
  name = "sermadrid-firewall"

  droplet_ids = [
    digitalocean_droplet.droplet.id,
  ]

  inbound_rule {
    protocol         = "tcp"
    port_range       = "80"
    source_addresses = ["0.0.0.0/0", "::/0"]
  }

  inbound_rule {
    protocol         = "tcp"
    port_range       = "443"
    source_addresses = ["0.0.0.0/0", "::/0"]
  }

  inbound_rule {
    protocol         = "tcp"
    port_range       = "8080"
    source_addresses = [digitalocean_droplet.droplet.ipv4_address]
  }

  inbound_rule {
    protocol         = "tcp"
    port_range       = "22"
    source_addresses = ["0.0.0.0/0", "::/0"]
  }

  outbound_rule {
    protocol              = "udp"
    port_range            = "53"
    destination_addresses = ["0.0.0.0/0", "::/0"]
  }

  outbound_rule {
    protocol              = "tcp"
    port_range            = "53"
    destination_addresses = ["0.0.0.0/0", "::/0"]
  }

  outbound_rule {
    protocol              = "tcp"
    port_range            = "1-65535"
    destination_addresses = ["0.0.0.0/0", "::/0"]
  }
}
