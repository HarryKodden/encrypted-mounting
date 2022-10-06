// cloudfare.tf

variable "cloudflare_api_token" {
  description = "API token for Cloudfare"
  type        = string
}

variable "cloudflare_zone_name" {
  description = "Zone Name for Cloudfare"
  type        = string
}

variable "domain" {
  description = "DNS Domain for Cloudfare"
  type        = string
}

terraform {
  required_providers {
    cloudflare = {
      source  = "cloudflare/cloudflare"
      version = "~> 3.0"
    }
  }
}

provider "cloudflare" {
  api_token = var.cloudflare_api_token
}

data "cloudflare_zones" "zone" {
  filter {
    name = var.cloudflare_zone_name
  }
}

resource "cloudflare_record" "my_main_domain" {
  zone_id         = data.cloudflare_zones.zone.zones[0].id
  name            = var.domain
  value           = aws_eip.my_eip.public_ip
  type            = "A"
  ttl             = 3600
  allow_overwrite = true
}

resource "cloudflare_record" "my_sub_domains" {  
  zone_id         = data.cloudflare_zones.zone.zones[0].id
  name            = "*.${var.domain}"
  value           = aws_eip.my_eip.public_ip
  type            = "A"
  ttl             = 3600
  allow_overwrite = true
}
