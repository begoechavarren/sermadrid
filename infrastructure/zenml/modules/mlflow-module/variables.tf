variable "namespace" {
  type    = string
  default = "mlflow"
}

variable "chart_version" {
  type    = string
  default = "0.7.13"
}

variable "image_version" {
  type    = string
  default = "v2.17.0"
}

variable "htpasswd" {}

variable "ingress_host" {
  type    = string
  default = ""
}

variable "tls_enabled" {
  type    = bool
  default = true
}

variable "artifact_Proxied_Access" {
  type    = bool
  default = false
}

variable "artifact_S3" {
  type    = bool
  default = false
}
variable "artifact_S3_Bucket" {
  type    = string
  default = ""
}
variable "artifact_S3_Access_Key" {
  type    = string
  default = ""
}
variable "artifact_S3_Secret_Key" {
  type    = string
  default = ""
}
variable "artifact_S3_Endpoint_URL" {
  type    = string
  default = ""
}

variable "artifact_Azure" {
  type    = bool
  default = false
}
variable "artifact_Azure_Storage_Account_Name" {
  type    = string
  default = ""
}
variable "artifact_Azure_Container" {
  type    = string
  default = ""
}
variable "artifact_Azure_Access_Key" {
  type    = string
  default = ""
}

variable "artifact_GCS" {
  type    = bool
  default = false
}
variable "artifact_GCS_Bucket" {
  type    = string
  default = ""
}
variable "istio_enabled" {
  type    = bool
  default = false
}