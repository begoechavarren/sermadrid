resource "random_string" "unique" {
  length  = 4
  special = false
  upper   = false
}

locals {
  prefix = "zenml"

  eks = {
    cluster_name        = "mycluster-zenml"
    cluster_version     = "1.29"
    workloads_namespace = "zenml"
  }
  vpc = {
    name = "vpc-${random_string.unique.result}"
  }

  ecr = {
    name = var.repo_name == "" ? "container-registry-${random_string.unique.result}" : var.repo_name
  }

  s3 = {
    name = var.bucket_name == "" ? "store-${random_string.unique.result}" : var.bucket_name
  }

  cert_manager = {
    version = "1.9.1"
  }

  istio = {
    version = "1.12.0"
  }

  nginx_ingress = {
    version = "4.4.0"
  }


  kubeflow = {
    version             = "1.8.3"
    ingress_host_prefix = "kubeflow"
  }

  tekton = {
    version             = "0.40.2"
    dashboard_version   = "0.31.0"
    ingress_host_prefix = "tekton"
    workloads_namespace = "zenml-workloads-tekton"
  }

  mlflow = {
    chart_version           = "0.7.13"
    image_version           = "v2.17.0"
    artifact_Proxied_Access = "false"
    artifact_S3             = "true"

    ingress_host_prefix = "mlflow"
  }

  seldon = {
    version              = "1.15.0"
    name                 = "seldon"
    namespace            = "seldon-system"
    workloads_namespace  = "zenml-workloads-seldon"
    service_account_name = "seldon"
  }

  zenml = {
    version                         = "0.66.0"
    database_ssl_ca                 = ""
    database_ssl_cert               = ""
    database_ssl_key                = ""
    database_ssl_verify_server_cert = false
    ingress_host_prefix             = "zenml"
    ingress_tls                     = true
    image_tag                       = ""
    service_account_name            = "sermadrid"
    stacks = {
      sermadrid =  "sermadrid"
    }
    
  }

  common_tags = {
    "managedBy"   = "terraform"
    "application" = local.prefix
  }
}