output "ingress-controller-name" {
  value = helm_release.nginx-controller.name
}
output "ingress-controller-namespace" {
  value = kubernetes_namespace.nginx-ns.metadata[0].name
}
output "ingress-hostname" {
  value = data.kubernetes_service.nginx-ingress-controller.status.0.load_balancer.0.ingress.0.hostname
}
output "ingress-ip-address" {
  value = data.kubernetes_service.nginx-ingress-controller.status.0.load_balancer.0.ingress.0.ip

}
resource "null_resource" "wait_for_ingress" {
  depends_on = [helm_release.nginx-controller]

  provisioner "local-exec" {
    command = <<-EOT
      #!/bin/bash

      log() {
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
      }

      max_retries=90
      retry_interval=20
      count=0

      log "Starting wait for Nginx Ingress to be fully ready"

      while [ $count -lt $max_retries ]; do
        ingress_status=$(kubectl get pods -n ${kubernetes_namespace.nginx-ns.metadata[0].name} -l app.kubernetes.io/component=controller -o jsonpath='{.items[0].status.phase}')
        log "Ingress controller pod status: $ingress_status"
        
        if [ "$ingress_status" = "Running" ]; then
          log "Nginx Ingress controller is running"
          
          # Check if LoadBalancer has an IP/hostname assigned
          lb_status=$(kubectl get svc ${helm_release.nginx-controller.name}-ingress-nginx-controller -n ${kubernetes_namespace.nginx-ns.metadata[0].name} -o jsonpath='{.status.loadBalancer.ingress[0].ip}{.status.loadBalancer.ingress[0].hostname}')
          if [ ! -z "$lb_status" ]; then
            log "LoadBalancer IP/hostname is assigned: $lb_status"
            exit 0
          else
            log "LoadBalancer IP/hostname not yet assigned"
          fi
        fi

        log "Waiting for Nginx Ingress to be fully ready... (Attempt $((count+1))/$max_retries)"
        sleep $retry_interval
        count=$((count+1))
      done

      log "Timeout waiting for Nginx Ingress to be ready"
      exit 1
    EOT
  }
}

data "external" "getIP" {
  depends_on = [null_resource.wait_for_ingress]
  program    = ["sh", "${path.module}/dig.sh"]

  query = {
    hostname = data.kubernetes_service.nginx-ingress-controller.status.0.load_balancer.0.ingress.0.hostname
  }
}

output "ingress-ip-address-aws" {
  value      = data.external.getIP.result.ip
  depends_on = [null_resource.wait_for_ingress]
}