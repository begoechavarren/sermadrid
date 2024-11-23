resource "null_resource" "zenml_stack" {
  count = var.enable_zenml ? 1 : 0

  triggers = {
    timestamp = timestamp()
  }

  provisioner "local-exec" {
    interpreter = ["/bin/bash", "-c"]
    command     = <<-EOT
      set -e # Exit on any error
      
      # Configure kubectl
      aws eks update-kubeconfig --region ${var.region} --name ${aws_eks_cluster.cluster[0].name}
      
      echo "Looking for ZenML deployment..."
      ZENML_NS=$(kubectl get pods -A | grep -i zen | head -n 1 | awk '{print $1}')
      # TODO: I know it is called zen-server
      ZENML_DEPLOY=$(kubectl get deployments -n $ZENML_NS -o custom-columns=:metadata.name | grep -i zen | head -n 1)
      
      echo "Found ZenML deployment: $ZENML_DEPLOY in namespace: $ZENML_NS"

      echo "Checking if service account exists..."
      SA_EXISTS=$(kubectl -n $ZENML_NS exec deploy/$ZENML_DEPLOY -- zenml service-account list | grep -q "^.*${local.zenml.service_account_name}.*" && echo "yes" || echo "no")
      
      if [ "$SA_EXISTS" = "yes" ]; then
        echo "Service account ${local.zenml.service_account_name} exists, deleting it..."
        kubectl -n $ZENML_NS exec deploy/$ZENML_DEPLOY -- zenml service-account delete ${local.zenml.service_account_name}
        echo "Service account deleted successfully"
      fi

      echo "Creating new ZenML service account and retrieving API key..."
      RAW_OUTPUT=$(kubectl -n $ZENML_NS exec deploy/$ZENML_DEPLOY -- zenml service-account create ${local.zenml.service_account_name} | tr -d '\n' | sed 's/\x1b\[[0-9;]*m//g')
      echo "Raw Output from ZenML service account creation:"
      echo "$RAW_OUTPUT"
      ZENML_API_KEY=$(echo "$RAW_OUTPUT" | grep -o "'ZENKEY_[^']*'" | tr -d "'")

      # Verify we got a key that starts with ZENKEY_
      if [[ ! "$ZENML_API_KEY" =~ ^ZENKEY_ ]]; then
        echo "Error: Failed to retrieve valid ZenML API key"
        echo "Raw output was:"
        echo "$RAW_OUTPUT"
        exit 1
      fi
      
      echo "Successfully retrieved ZenML API key"
      echo "ZenML API Key: $ZENML_API_KEY"
      # echo "$ZENML_API_KEY" > zenml_api_key.txt

      # Check if artifact store exists
      ARTIFACT_EXISTS=$(kubectl -n $ZENML_NS exec deploy/$ZENML_DEPLOY -- zenml artifact-store list | grep -q "^.*s3_artifact_store.*" && echo "yes" || echo "no")
      if [ "$ARTIFACT_EXISTS" = "no" ]; then
        echo "Registering S3 artifact store..."
        kubectl -n $ZENML_NS exec deploy/$ZENML_DEPLOY -- zenml artifact-store register s3_artifact_store \
          --flavor s3 \
          --path="s3://${var.bucket_name}"
      else
        echo "S3 artifact store already exists, skipping registration..."
      fi

      # Check if container registry exists
      REGISTRY_EXISTS=$(kubectl -n $ZENML_NS exec deploy/$ZENML_DEPLOY -- zenml container-registry list | grep -q "^.*ecr_registry.*" && echo "yes" || echo "no")
      if [ "$REGISTRY_EXISTS" = "no" ]; then
        echo "Registering ECR container registry..."
        ECR_URL="${data.aws_caller_identity.current.account_id}.dkr.ecr.${var.region}.amazonaws.com"
        kubectl -n $ZENML_NS exec deploy/$ZENML_DEPLOY -- zenml container-registry register ecr_registry \
          --flavor aws \
          --uri="$ECR_URL"
      else
        echo "ECR container registry already exists, skipping registration..."
      fi

      # Check if orchestrator exists
      ORCHESTRATOR_EXISTS=$(kubectl -n $ZENML_NS exec deploy/$ZENML_DEPLOY -- zenml orchestrator list | grep -q "^.*k8s_orchestrator.*" && echo "yes" || echo "no")
      if [ "$ORCHESTRATOR_EXISTS" = "no" ]; then
        echo "Registering Kubernetes orchestrator..."
        kubectl -n $ZENML_NS exec deploy/$ZENML_DEPLOY -- zenml orchestrator register k8s_orchestrator \
          --flavor kubernetes \
          --kubernetes_namespace=${local.eks.workloads_namespace}
      else
        echo "Kubernetes orchestrator already exists, skipping registration..."
      fi

      # Check if experiment tracker exists
      TRACKER_EXISTS=$(kubectl -n $ZENML_NS exec deploy/$ZENML_DEPLOY -- zenml experiment-tracker list | grep -q "^.*mlflow_tracker.*" && echo "yes" || echo "no")
      if [ "$TRACKER_EXISTS" = "no" ]; then
        echo "Registering MLflow experiment tracker..."
        MLFLOW_URL="https://${local.mlflow.ingress_host_prefix}.${module.nginx-ingress[0].ingress-ip-address-aws}.nip.io"
        kubectl -n $ZENML_NS exec deploy/$ZENML_DEPLOY -- zenml experiment-tracker register mlflow_tracker \
          --flavor mlflow \
          --tracking_uri="$MLFLOW_URL" \
          --tracking_username=${var.mlflow-username} \
          --tracking_password=${var.mlflow-password}
      else
        echo "MLflow experiment tracker already exists, skipping registration..."
      fi

      # Improved stack existence check
      echo "Checking if stack exists..."
      STACK_EXISTS=$(kubectl -n $ZENML_NS exec deploy/$ZENML_DEPLOY -- zenml stack list | grep -q "[[:space:]]${local.zenml.stacks.sermadrid}[[:space:]]" && echo "yes" || echo "no")
      if [ "$STACK_EXISTS" = "no" ]; then
        echo "Registering new stack..."
        kubectl -n $ZENML_NS exec deploy/$ZENML_DEPLOY -- zenml stack register ${local.zenml.stacks.sermadrid} \
          -a s3_artifact_store \
          -c ecr_registry \
          -o k8s_orchestrator \
          -e mlflow_tracker \
          || echo "Failed to register stack, it might already exist"
      else
        echo "Stack '${local.zenml.stacks.sermadrid}' already exists, skipping registration..."
      fi

      # Verify final configuration
      echo "Final configuration:"
      echo "Current Stacks:"
      kubectl -n $ZENML_NS exec deploy/$ZENML_DEPLOY -- zenml stack list
      
      echo "Current Components:"
      echo "Artifact Stores:"
      kubectl -n $ZENML_NS exec deploy/$ZENML_DEPLOY -- zenml artifact-store list
      echo "Container Registries:"
      kubectl -n $ZENML_NS exec deploy/$ZENML_DEPLOY -- zenml container-registry list
      echo "Orchestrators:"
      kubectl -n $ZENML_NS exec deploy/$ZENML_DEPLOY -- zenml orchestrator list
      echo "Experiment Trackers:"
      kubectl -n $ZENML_NS exec deploy/$ZENML_DEPLOY -- zenml experiment-tracker list
    EOT
  }

  depends_on = [
    aws_eks_cluster.cluster,
    module.zenml,
    aws_s3_bucket.zenml-artifact-store,
    aws_ecr_repository.zenml-ecr-repository,
    module.mlflow,
    kubernetes_namespace.k8s-workloads
  ]
}