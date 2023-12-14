terraform {
  backend "s3" {
    endpoint   = "${local.do_region}.digitaloceanspaces.com"
    bucket     = [var.do_space_name]
    key        = "terraform.tfstate"
    region     = local.do_spaces_region
    access_key = var.do_spaces_access_key
    secret_key = var.do_spaces_secret_key

    # Set to "true" to enable S3 Transfer Acceleration
    skip_requesting_account_id  = true
    skip_credentials_validation = true
    skip_metadata_api_check     = true
    skip_region_validation      = true
  }
}
