#!/usr/bin/env python3

import argparse, sys, os, json
from os.path import expanduser
home = expanduser("~")
CONFIG_FILE = home+"/.config/gcloud/mygcloud.json"
parser=argparse.ArgumentParser()

parser.add_argument("action", choices=["help", "delete", "create", "activate"], help="action wanted")
parser.add_argument("name", help="configuration name")
parser.add_argument("--zone", help="gcloud default zone")
parser.add_argument("--region", help="gcloud default region")
parser.add_argument("--project", help="gcloud project")
parser.add_argument("--account", help="gcloud account")
parser.add_argument("--k8s", help="k8s cluster name to be the default of this configuration")
args=parser.parse_args()



if sys.argv[2] == '' or sys.argv[2] == None:
    print("Configuration name is required")
    print("Usage example: mygcloud.py delete myconfig")
    sys.exit(1)

try:
    f = open(CONFIG_FILE)
except:
    f = open(CONFIG_FILE, 'w+')
    f.write('{}')
    f.close()
    f = open(CONFIG_FILE)   

data = json.load(f)

if sys.argv[1] == "delete":
    available_configs = os.popen("gcloud config configurations list --format='value(name, is_active)'")
    available = available_configs.read()
    available_list = available.split('\n')
    for config in available_list:
        (config_name, is_active) = config.split()
        if config_name == sys.argv[2]:
            if is_active == 'True':
                print("Cannot delete active configuration")
                sys.exit(1)
            p = os.popen("gcloud config configurations delete " + sys.argv[2] + " --quiet")
            p.read()
            remove_config = data.pop(sys.argv[2], None)
            with open(CONFIG_FILE, 'w') as fp:
                json.dump(data, fp)
            sys.exit(0)
    print("Configuration does not exist")
    sys.exit(1)

if sys.argv[1] == "activate":
    available_configs = os.popen("gcloud config configurations list --format='value(name, is_active)'")
    available = available_configs.read()
    available_list = available.split('\n')
    for config in available_list:
        (config_name, is_active) = config.split()
        if config_name == sys.argv[2]:
            if is_active == 'True':
                print("Configuration already active")
                sys.exit(0)
            p = os.popen("gcloud config configurations activate " + sys.argv[2])
            p.read()
            if sys.argv[2] in data and 'k8s' in  data[sys.argv[2]]:
                p = os.popen("kubectl config use-context " + data[sys.argv[2]]['k8s'])
                p.read()
            sys.exit(0)
    print("Configuration does not exist")
    sys.exit(1)

if sys.argv[1] == 'create':
    if sys.argv[2] == '' or sys.argv[2] == None:
        print("Configuration name is required")
        print("Usage example: mygcloud.py create myconfig --zone us-central1-a --project myproject --account email@email.com --k8s myk8s")
        sys.exit(1)

    available_configs = os.popen("gcloud config configurations list --format='value(name)'")
    available = available_configs.read()
    available_list = available.split('\n')
    for config in available_list:
        if config == sys.argv[2]:
            print("Configuration already exists")
            sys.exit(1)

    p = os.popen("gcloud config configurations create " + sys.argv[2] + " --quiet")
    p.read()
    if args.account != None and args.account != '':
        p = os.popen("gcloud config set account " + args.account + " --quiet")
        p.read()
    if args.project != None and args.project != '':
        p = os.popen("gcloud config set project " + args.project + " --quiet")
        p.read()
    if args.zone != None and args.zone != '':
        p = os.popen("gcloud config set compute/zone " + args.zone + " --quiet")
        p.read()
    if args.region != None and args.region != '':
        p = os.popen("gcloud config set compute/region " + args.region + " --quiet")
        p.read()
    if args.account != None and args.account != '' and args.project != None and args.project != '':
        available_clusters = os.popen("gcloud container clusters list --format='value(name, zone)'")
        available_clusters_read = available_clusters.read()
        available_clusters_list = available_clusters_read.split('\n')
        gke_cluster_names = []
        cluster_names = []
        for cluster_details in available_clusters_list:
            if cluster_details != '' and cluster_details != None:
                (cluster_name, cluster_zone) = cluster_details.split()
                cluster_names.append(cluster_name)
                p = os.popen("gcloud container clusters get-credentials " + cluster_name +" --zone " + cluster_zone + " --project " + args.project + " --quiet")
                p.read()
                gke_cluster_name = 'gke_' + args.project + '_' + cluster_zone + '_' + cluster_name
                gke_cluster_names.append(gke_cluster_name)
        if len(gke_cluster_names) > 0:
            update = False
            if args.k8s != None and args.k8s != '':
                if args.k8s in gke_cluster_names:
                    gke_cluster_name = args.k8s
                    update = True
                if args.k8s in cluster_names:
                    gke_cluster_name = 'gke_' + args.project + '_' + cluster_zone + '_' + args.k8s
                    update = True
                if update:
                    p = os.popen("kubectl config use-context " + gke_cluster_name)
                    p.read()
            data[sys.argv[2]] = {'k8s': gke_cluster_name}
            with open(CONFIG_FILE, 'w') as fp:
                json.dump(data, fp)