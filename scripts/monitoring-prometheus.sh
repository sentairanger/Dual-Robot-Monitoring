#!/bin/bash
# create monitoring namespace
kubectl create ns monitoring
# add prometheus chart
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
# add stable chart
helm repo add stable https://charts.helm.sh/stable
# update helm repos
helm repo update
# install prometheus and grafana
helm install prometheus prometheus-community/kube-prometheus-stack --namespace monitoring
