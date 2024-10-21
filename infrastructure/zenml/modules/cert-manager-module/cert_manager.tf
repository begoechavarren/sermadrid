# create a namespace for cert-manager resources
resource "kubernetes_namespace" "cert-manager-ns" {
  metadata {
    name = var.namespace
  }
}
# create a cert-manager release
resource "helm_release" "cert-manager" {
  name       = "cert-manager"
  repository = "https://charts.jetstack.io"
  chart      = "cert-manager"
  version    = "v${var.chart_version}"

  namespace = kubernetes_namespace.cert-manager-ns.metadata[0].name

  set {
    name  = "installCRDs"
    value = "true"
  }

  depends_on = [
    kubernetes_namespace.cert-manager-ns
  ]
}

resource "null_resource" "wait_for_cert_manager" {
  provisioner "local-exec" {
    command = "sleep 15"
  }

  depends_on = [
    resource.helm_release.cert-manager
  ]
}

resource "null_resource" "wait_for_cert_manager_crd" {
  provisioner "local-exec" {
    command = <<EOT
      kubectl wait --for=condition=Established --timeout=300s crd/clusterissuers.cert-manager.io
    EOT
  }

  depends_on = [
    null_resource.wait_for_cert_manager
  ]
}

# create a cert-manager letsencrypt ClusterIssuer
# cannot use kubernetes_manifest resource since it practically 
# doesn't support CRDs. Going with kubectl instead.
resource "kubectl_manifest" "letsencrypt" {
  yaml_body         = <<YAML
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-staging
  namespace: cert-manager
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: stefan@zenml.io
    privateKeySecretRef:
      name: letsencrypt-staging
    solvers:
    - http01:
        ingress:
          class: nginx
YAML
  server_side_apply = true
  depends_on = [
    resource.null_resource.wait_for_cert_manager_crd
  ]
}
