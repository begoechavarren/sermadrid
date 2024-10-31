locals {
  component_configs = {
    # Artifact Store
    artifact_store = {
      enabled      = var.enable_artifact_store
      id          = var.enable_artifact_store ? uuid() : ""
      flavor      = var.enable_artifact_store ? "s3" : ""
      name        = var.enable_artifact_store ? "s3_artifact_store_${random_string.unique.result}" : ""
      config      = var.enable_artifact_store ? jsonencode({
        path = "s3://${aws_s3_bucket.zenml-artifact-store[0].bucket}"
      }) : ""
    }

    # Container Registry
    container_registry = {
      enabled      = var.enable_container_registry
      id          = var.enable_container_registry ? uuid() : ""
      flavor      = var.enable_container_registry ? "aws" : ""
      name        = var.enable_container_registry ? "aws_container_registry_${random_string.unique.result}" : ""
      config      = var.enable_container_registry ? jsonencode({
        uri = "${data.aws_caller_identity.current.account_id}.dkr.ecr.${var.region}.amazonaws.com"
      }) : ""
    }

    # Orchestrator
    orchestrator = {
      enabled = (
        var.enable_orchestrator_kubernetes || 
        var.enable_orchestrator_kubeflow || 
        var.enable_orchestrator_tekton || 
        var.enable_orchestrator_sagemaker
      )
      id      = coalesce(
        var.enable_orchestrator_kubernetes ? uuid() : "",
        var.enable_orchestrator_kubeflow ? uuid() : "",
        var.enable_orchestrator_tekton ? uuid() : "",
        var.enable_orchestrator_sagemaker ? uuid() : "",
        ""
      )
      flavor  = coalesce(
        var.enable_orchestrator_kubernetes ? "kubernetes" : "",
        var.enable_orchestrator_kubeflow ? "kubeflow" : "",
        var.enable_orchestrator_tekton ? "tekton" : "",
        var.enable_orchestrator_sagemaker ? "sagemaker" : "",
        ""
      )
      name    = coalesce(
        var.enable_orchestrator_kubernetes ? "eks_kubernetes_orchestrator_${random_string.unique.result}" : "",
        var.enable_orchestrator_kubeflow ? "eks_kubeflow_orchestrator_${random_string.unique.result}" : "",
        var.enable_orchestrator_tekton ? "eks_tekton_orchestrator_${random_string.unique.result}" : "",
        var.enable_orchestrator_sagemaker ? "sagemaker_orchestrator_${random_string.unique.result}" : "",
        ""
      )
      config  = coalesce(
        var.enable_orchestrator_kubernetes ? jsonencode({
          kubernetes_context = "${aws_eks_cluster.cluster[0].arn}"
          synchronous       = true
        }) : "",
        var.enable_orchestrator_kubeflow ? jsonencode({
          kubernetes_context = "${aws_eks_cluster.cluster[0].arn}"
          synchronous       = true
        }) : "",
        var.enable_orchestrator_tekton ? jsonencode({
          kubernetes_context = "${aws_eks_cluster.cluster[0].arn}"
        }) : "",
        var.enable_orchestrator_sagemaker ? jsonencode({
          execution_role = "${aws_iam_role.sagemaker_role[0].arn}"
        }) : "",
        ""
      )
    }

    # Experiment Tracker
    experiment_tracker = {
      enabled = var.enable_experiment_tracker_mlflow
      id      = var.enable_experiment_tracker_mlflow ? uuid() : ""
      flavor  = var.enable_experiment_tracker_mlflow ? "mlflow" : ""
      name    = var.enable_experiment_tracker_mlflow ? "eks_mlflow_experiment_tracker_${random_string.unique.result}" : ""
      config  = var.enable_experiment_tracker_mlflow ? jsonencode({
        tracking_uri      = module.mlflow[0].mlflow-tracking-URL
        tracking_username = var.mlflow-username
        tracking_password = var.mlflow-password
      }) : ""
    }
  }
}

output "artifact_store_id" {
  value = local.component_configs.artifact_store.id
}

output "artifact_store_flavor" {
  value = local.component_configs.artifact_store.flavor
}

output "artifact_store_name" {
  value = local.component_configs.artifact_store.name
}

output "artifact_store_configuration" {
  value = local.component_configs.artifact_store.config
}

output "container_registry_id" {
  value = local.component_configs.container_registry.id
}

output "container_registry_flavor" {
  value = local.component_configs.container_registry.flavor
}

output "container_registry_name" {
  value = local.component_configs.container_registry.name
}

output "container_registry_configuration" {
  value = local.component_configs.container_registry.config
}

output "orchestrator_id" {
  value = local.component_configs.orchestrator.id
}

output "orchestrator_flavor" {
  value = local.component_configs.orchestrator.flavor
}

output "orchestrator_name" {
  value = local.component_configs.orchestrator.name
}

output "orchestrator_configuration" {
  value = local.component_configs.orchestrator.config
}

output "experiment_tracker_id" {
  value = local.component_configs.experiment_tracker.id
}

output "experiment_tracker_flavor" {
  value = local.component_configs.experiment_tracker.flavor
}

output "experiment_tracker_name" {
  value = local.component_configs.experiment_tracker.name
}

output "experiment_tracker_configuration" {
  value = local.component_configs.experiment_tracker.config
}

# Infrastructure-related outputs
output "eks-cluster-name" {
  value = local.enable_eks ? "${local.prefix}-${local.eks.cluster_name}" : ""
}

output "ingress-controller-host" {
  value = length(module.nginx-ingress) > 0 ? module.nginx-ingress[0].ingress-hostname : null
}

output "ingress-controller-ip" {
  value = length(module.nginx-ingress) > 0 ? module.nginx-ingress[0].ingress-ip-address-aws : null
}

output "nginx-ingress-hostname" {
  value = length(module.nginx-ingress) > 0 ? module.nginx-ingress[0].ingress-hostname : null
}

output "istio-ingress-hostname" {
  value = length(module.istio) > 0 ? module.istio[0].ingress-hostname : null
}

output "kubeflow-pipelines-ui-URL" {
  value = var.enable_orchestrator_kubeflow ? module.kubeflow-pipelines[0].pipelines-ui-URL : null
}

output "tekton-pipelines-ui-URL" {
  value = var.enable_orchestrator_tekton ? module.tekton-pipelines[0].pipelines-ui-URL : null
}

output "mlflow-tracking-URL" {
  value = var.enable_experiment_tracker_mlflow ? module.mlflow[0].mlflow-tracking-URL : null
}

output "mlflow-bucket" {
  value = var.mlflow_bucket
}

output "seldon-workload-namespace" {
  value       = var.enable_model_deployer_seldon ? local.seldon.workloads_namespace : null
  description = "The namespace created for hosting your Seldon workloads"
}

output "seldon-base-url" {
  value = var.enable_model_deployer_seldon ? "http://${module.istio[0].ingress-hostname}:${module.istio[0].ingress-port}" : null
}

output "stack-yaml-path" {
  value = local_file.stack_file.filename
}

output "zenml-url" {
  value = var.enable_zenml ? module.zenml[0].zenml_server_url : null
}

output "zenml-username" {
  value = var.enable_zenml ? module.zenml[0].username : null
}
