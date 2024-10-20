# enable services
variable "enable_artifact_store" {
  description = "Enable S3 deployment"
  default     = true
}
variable "enable_container_registry" {
  description = "Enable ECR deployment"
  default     = true
}
variable "enable_orchestrator_kubeflow" {
  description = "Enable Kubeflow deployment"
  default     = false
}
variable "enable_orchestrator_tekton" {
  description = "Enable Tekton deployment"
  default     = false
}
variable "enable_orchestrator_kubernetes" {
  description = "Enable Kubernetes deployment"
  default     = true
}
variable "enable_orchestrator_skypilot" {
  description = "Enable SkyPilot orchestrator deployment"
  default     = false
}
variable "enable_orchestrator_sagemaker" {
  description = "Enable SageMaker as orchestrator"
  default     = false
}
variable "enable_experiment_tracker_mlflow" {
  description = "Enable MLflow deployment"
  default     = true
}
variable "enable_model_deployer_seldon" {
  description = "Enable Seldon deployment"
  default     = false
}
variable "enable_step_operator_sagemaker" {
  description = "Enable SageMaker as step operator"
  default     = false
}
variable "enable_zenml" {
  description = "Enable ZenML deployment"
  default     = true
}

variable "repo_name" {
  description = "The name of the container repository"
  default     = "zenml"
}
variable "bucket_name" {
  description = "The name of the S3 bucket"
}
variable "region" {
  description = "The region to deploy resources to"
}

# variables for the MLflow tracking server
variable "mlflow-artifact-S3-access-key" {
  description = "Your AWS access key for using S3 as MLflow artifact store"
  type        = string
}
variable "mlflow-artifact-S3-secret-key" {
  description = "Your AWS secret key for using S3 as MLflow artifact store"
  type        = string
}
variable "mlflow-username" {
  description = "The username for the MLflow Tracking Server"
  type        = string
}
variable "mlflow-password" {
  description = "The password for the MLflow Tracking Server"
  type        = string
}
variable "mlflow_bucket" {
  description = "The name of the S3 bucket to use for MLflow artifact store"
  default     = "mlflow"
}

# variables for creating a ZenML stack configuration file
variable "zenml-version" {
  description = "The version of ZenML being used"
  default     = "0.55.2"
  type        = string
}

variable "zenml-username" {
  description = "The username for the ZenML Server"
  type        = string
}
variable "zenml-password" {
  description = "The password for the ZenML Server"
  type        = string
}
variable "zenml-database-url" {
  description = "The ZenML Server database URL"
  type        = string
  default     = ""
}

# additional tags defined via CLI
variable "additional_tags" {
  default     = {}
  description = "Additional resource tags"
  type        = map(string)
}