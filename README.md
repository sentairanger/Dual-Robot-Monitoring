# Dual-Robot-CNCF

## Introduction

This project is based on what I've learned from the Cloud Native Application Architecture Nanodegree Program. I took what I learned from my Dual Robot Flask Project and decided to make it into a Dual Robot Monitoring project. I will explain each layer of the project and show you how you can run it on your own. I've provided the necessary scripts to help you along the way.

## Breakdown of Project

### Code

The main code of concern is `app.py`. This not only controls the robots but also collects the data which is displayed in the `/metrics` endpoint. Here are the python libraries that are the main focus:

* `flask`: This is important to set up the app and this is how the app connects to a web browser. 
* `prometheus_flask_exporter`: In order for metrics to be collected by Prometheus and Grafana, this needs to be invoked. That way when Prometheus scrapes the data, it shows up in Grafana.
* `jaeger_client`: To create a span, there needs to be a Jaeger Client set up in order for Jaeger UI to find the traces of each span. 
* `gpiozero`: This is needed to control any electronics like robots and motors.
* `pigpio`: This is needed to remotely connect to any Raspberry Pi.

The app design is below to get an idea of what it looks like. You can alter as you wish and test the app with `python3 app.py` or `python app.py`. This step is important before you move on to the next step. Because if it doesn't work then the next steps won't work at all.

#### App Design

![Flask](https://github.com/sentairanger/Dual-Robot-CNCF/blob/main/images/app-design.png)


### Docker

After a successful test of the code the application is then packaged into a Docker container. The `Dockerfile` explains each step to run the container. Here is a rundown:

* FROM: This sets up what the image will be based on. In this case it's `python:3.8-slim`. I chose slim as I wanted to reduce image size and only use the required libraries. This is good practice and avoids security issues.
* LABEL: This is an optional step as it names the maintainer of the image.
* COPY: Here the files from the current directory are copied to a directory called `/app`.
* WORKDIR: Here, the working directory is set as `/app`.
* RUN: Here, a command can be run on the image. In this case we are installing the necessary libraries from `requirements.txt`.
* CMD: Here the code is run using the command listed. Remember to separate with commas and quotations.

Run the image using `docker build -t dualrobot-cncf .` . Then test it with `docker run -d -p 5000:5000 dualrobot-cncf`. This runs the image in the background detached at port 5000. Run `docker ps` and the container should be listed. Access the app with `0.0.0.0:5000` and you should see the app. Test it out before closing it. You can tag it with `docker tag dualrobot-cncf <your-username>/dualrobot-cncf:<tag>`. Make sure you have an account with Docker Hub first. Then use `docker login` to login and then run `docker push <your-username>/dualrobot-cncf:<tag>`. 

### Kubernetes

After packaging with Docker, the next layer is using Kubernetes to deploy the application. Here the manifest file `dualrobot-cncf.yaml` is split into three sections:

* The deployment section: This is necessary to hold the Docker image and in this case add annotations. As you see in order to enable Jaeger sidecar injection needs to be set to true and in order for Prometheus to scrape data it needs to be set to true, with the `/metrics` path and the port which is 5000.
* The service section: Here it sets up the service so that it can be used to port-forward the application. The port is set to 5000 and also the type is set to LoadBalancer.
* The service monitor section: In order for Prometheus to monitor the data it needs this section to monitor the `/metrics` endpoint at an interval of 15ms.

I created a diagram of the project which is shown below. In order to run the application, it's best to port-forward the service with `kubectl port-forward svc/dualrobot-cncf 5000`. If using the Vagrant box, make sure you use 5000:5000 to expose the application publicly.

#### Diagram

![Diagram](https://github.com/sentairanger/Dual-Robot-CNCF/blob/main/images/dualrobotdiagram.drawio.png)

### Github Actions

Continuous Integration is the action of merging code changes into a repository. In this case, I created two actions that will merge any changes to the Docker Repository. 

* `docker-build.yml` builds a new image any time there is a change in the repo.
* `docker-sha-tag.yml` creates new sha-tags for each build. This is good for security.

### ArgoCD

There are many ways to deploy a cluster and ArgoCD is one that I used in this case. There are other options but this is one that I learned about from the course. To provide assistance, I created a `argocd-install.sh` script to install ArgoCD as well as `argocd-service-nodeport.yaml` to expose the application publicly. I also provided a `dualrobot-argocd.yaml` file that deploys the cluster. The image below shows a sample ArgoCD deployment of the application. To run the application use `kubectl apply -f dualrobot-cncf.yaml`. It should show up and all you need to do is to sync it and it will sync the cluster.

#### ArgoCD Deployment

![ArgoCD](https://github.com/sentairanger/Dual-Robot-CNCF/blob/main/images/argocd-dualrobot.png)

### Jaeger

Here Jaeger is used to find traces any time Linus or Torvald's eyes are blinked. A sample span is given below to show how a span is traced. In order for this to work properly, in the `app.py` code a `JAEGER_HOST` is defined and `getenv` is used to define this variable. In the yaml file provided you see in the env section there is a variable named `JAEGER_HOST` with the value given. This value can be changed if you used a different Jaeger agent name. I have also provided a `observability-jaeger.sh` and `helm-install.sh` in order to install the Jaeger helm charts. In my case once I had enough spans collected, I ran `kubectl port-forward svc/my-jaeger-tracing-default-query 16686`. If using Vagrant make sure you change it to 16686:16686. From there make sure to go to `localhost:16686` or replace localhost with the IP address of the Vagrant box. And there you choose the service and then click on Find traces. Then the traces should be detected. 

#### Jaeger Span

![span](https://github.com/sentairanger/Dual-Robot-CNCF/blob/main/images/jaeger-span.png)

### Prometheus/Grafana

Prometheus is used to scrape and collect data from the `/metrics` endpoint and then that data is sent to Grafana which displays the data using panels. Each panel measures different benchmarks as listed in the panel titles. You can get more information by visiting [this](https://github.com/rycus86/prometheus_flask_exporter) link. I have provided a `monitoring-prometheus.sh` script that will install Prometheus and Grafana. Once they're installed test out Prometheus with `kubectl port-forward -n monitoring svc/prometheus-kube-prometheus-prometheus 9090`. Make sure you're using 9090:9090 if using Vagrant. Go to `localhost:9090` or the IP-Address of the Vagrant box if not using localhost and then go to status, click on targets and the application should appear.  Next, assuming you ran and tested the application port-forward grafana with `kubectl port-forward -n monitoring svc/prometheus-grafana 3000`. Again, go to `localhost:3000` or the IP-Address of the Vagrant box and then log in to Grafana with admin and the password prom-operator. You should change this as this is not very secure. Once you are in, go to Data Sources and make sure Prometheus is added. In order to display Jaeger spans, add the Jaeger Data Source and choose the correct Kubernetes FQDN. In my case it would be `my-jaeger-tracing-default-query.default.svc.local:16686`. Once it connects you can go to the plus symbol and select new Dashboard. I have provided a json file which you can use to import and alter as you wish. The Dashboard I created is shown below.

#### Dashboard

![Dashboard](https://github.com/sentairanger/Dual-Robot-CNCF/blob/main/images/dashboard.png)


## Using Vagrant to Run Project

If using Mac or Windows, you can use the Vagrantfile I have provided which will have Docker and k3s already installed. You should be able to run everything on there and you can always install other dependencies if needed. 

