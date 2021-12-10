#!/bin/bash
# create observability namespace
kubectl create ns observability
# add CRD if not present
https://raw.githubusercontent.com/jaegertracing/jaeger-operator/master/deploy/crds/jaegertracing.io_jaegers_crd.yaml
# add jaeger repo
helm repo add jaegertracing https://jaegertracing.github.io/helm-charts  
# update helm repos
helm repo update 
# install jaeger
helm install jaeger jaegertracing/jaeger-operator --namespace observability --set rbac.clusterRole=true 
# add cluster wide permissions
kubectl create -f https://raw.githubusercontent.com/jaegertracing/jaeger-operator/master/deploy/cluster_role.yaml
# add role based permissions
kubectl create -f https://raw.githubusercontent.com/jaegertracing/jaeger-operator/master/deploy/cluster_role_binding.yaml
# add ingress
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.0.3/deploy/static/provider/cloud/deploy.yaml
# if not created add a simplest jaeger instance
cat <<EOF | kubectl apply -f -
apiVersion: jaegertracing.io/v1
kind: Jaeger
metadata:
  name: simplest
EOF
