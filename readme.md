# My Gcloud

I work on many projects at the same time, each project has its own gcloud project, and many are on different gcloud account of mine. I always hated having to change from 1 project to another...

> gcloud config set account X
> gcloud config set project Y

etc... enters gcloud configuration, so you create a configuration and you set the project and account for it and that's it, the only problem remaining was that to create a configuration you still had to run multiple commands to set project zone and account, additionally you still had the issue of gke. You can't link a gke to a configuration, and if by mistake you run a simple command 

> kubectl get po

on the wrong gke cluster, then the configuration is lost, for this specific cluster, and you have to run the get credentials command again, and that's why I decided to create this simple wrapper.

My gcloud is a simple python script, a small wrapper around gcloud config configuration. it fixes these pain points:

+ Set all options at once, region, zone, account, project
+ If project and account are set, it will bring all k8s cluster configurations
+ If k8s value is set, it will link that k8s cluster to this configuration, so when your activate the configuration, it will change k8s context
+ If k8s value is not set, it will default to the last k8s cluster in the list.

Use it directly as executable 

> chmod +x mygcloud.py 

Add it to your PATH to use it as a normal command.

## Usages
### Create configuration

This will automatically fetch all your gke clusters credentials, and link the k8s cluster you provided to this configuration.

> ./mygcloud.py create config_name --account=email@email.com --zone=us-central1-a --region=us-central1 --project=project-name --k8s=some_kubernetes_cluster

### Activate configuation

This will activate the configuration, and change your kubectl context to the one you provided when you created the configuration, or default to the last k8s cluster in your clusters

> ./mygcloud.py activate config_name 


### Delete configuration

This will delete gcloud configuration

> ./mygcloud.py delete config_name