Wazuh unattended installer
==========================

[![Slack](https://img.shields.io/badge/slack-join-blue.svg)](https://wazuh.com/community/join-us-on-slack/)
[![Email](https://img.shields.io/badge/email-join-blue.svg)](https://groups.google.com/forum/#!forum/wazuh)
[![Documentation](https://img.shields.io/badge/docs-view-green.svg)](https://documentation.wazuh.com)
[![Documentation](https://img.shields.io/badge/web-view-green.svg)](https://wazuh.com)

## Goal

The Wazuh unattended installer is a tool that helps you to install and configure all Wazuh components, whatever be your architecture (All-in-One, distributed on no matter how many Wazuh or Elasticsearch nodes).

## Examples

We will show the use of this tool using 3 scenarios:

- [All components work in the same host, the All-in-one scenario.](#All-in-one)

               Host #1                      
          +--------------------------------+                                              
          |                                |
          |                                |
          |                                |
          |   +-----------------------+    |
          |   | Wazuh manager         |    |
          |   +-----------------------+    |
          |   | Filebeat              |    |
          |   +-----------------------+    |
          |                                |
          |                                |
          |   +-----------------------+    |
          |   | Elasticsearch         |    |
          |   +-----------------------+    |
          |                                |
          |                                |
          |   +-----------------------+    |
          |   | Kibana & Wazuh plugin |    |
          |   |                       |    |
          |   +-----------------------+    |
          |                                |
          |                                |
          +--------------------------------+

- [All distributed](#Distributed): every component will be installed on a different host. In this example, we will work on 6 hosts, a two nodes Wazuh cluster, a three Elasticsearch cluster and a Kibana node:
    - Host #1: Wazuh server - master node.
    - Host #2: Wazuh server - worker node.
    - Host #3: Elasticsearch node.
    - Host #4: Elasticsearch node.
    - Host #5: Elasticsearch node.
    - Host #6: Kibana node.

```
                                                                                   +------------------------------------------------------------------                                                                                      
                                      Host #1                                      |             Host #2                                             |                                                                                      
                                 +--------------------------------+                v        +--------------------------------+              Host #6  |                                                                                      
                                 |                                |                         |                                |         +--------------------------------+                                                                   
                                 | +----------------------------------------------------------------------------------------+|         |                                |                                                                   
                                 | |                              |   Wazuh cluster         |                               ||         |  +-----------------------+     |                                                                   
                                 | | +-----------------------+    |                         |   +-----------------------+   ||         |  | Kibana & Wazuh plugin |     |                                                                   
                                 | | | Wazuh manager master  |    |                         |   | Wazuh manager worker  |   ||         |  |                       |     |                                                                   
                                 | +----------------------------------------------------------------------------------------+|         |  +-----------------------+     |                                                                   
                                 |   | Filebeat              |    |                         |   | Filebeat              |    |         |                                |                                                                   
                                 |   +-----------------------+ ---------------+-----------------+-----------------------+    |         +--------------------------------+                                                                   
                                 |                                |           |             |                                |                     |                                                                                        
                                 |                                |           |             |                                |                     |                                                                                        
                                 +--------------------------------+           |             +--------------------------------+                     |                                                                                        
                                                                              |                                                                    |                                                                                        
                                                                              |                                                                    |                                                                                        
                                                                              |                                 +-----------------------------------                                                                                        
                                                                              |                                 |                                                                                                                           
                                                        +----------------------                                 |                                                                                                                           
                                                        |                                                       |                                                                                                                           
                                                        |                                                       |                                                                                                                           
                                                        |                                                       |                                                                                                                           
                                                        |                                                       |                                                                                                                           
          Host #3                                       |           Host #4                                     |             Host #5                                                                                                       
     +--------------------------------+                 |      +--------------------------------+               |        +--------------------------------+                                                                                 
     |+-------------------------------------------------v-------------------------------------------------------v---------------------------------------+ |                                                                                 
     || +-----------------------+     |   Elasticsearch        |   +-----------------------+    |                        |   +-----------------------+  | |                                                                                 
     || |  Elasticsearch        |     |   cluster              |   |  Elasticsearch        |    |                        |   |  Elasticsearch        |  | |                                                                                 
     || +-----------------------+     |                        |   +-----------------------+    |                        |   +-----------------------+  | |                                                                                 
     |+-------------------------------------------------------------------------------------------------------------------------------------------------+ |                                                                                 
     |                                |                        |                                |                        |                                |                                                                                 
     +--------------------------------+                        +--------------------------------+                        +--------------------------------+     
```

- [Mixed distributed](#Mixed): every component will be installed separately, but conforming to a Wazuh cluster and Elasticsearch cluster (it includes a Kibana installation on every node. It is not necessary to include Kibana in every node. The example shows how to do it with didactical proposes):
    - Host #1: Wazuh server - master node & Elasticsearch node & Kibana.
    - Host #2: Wazuh server - worker node & Elasticsearch node & Kibana.
    - Host #3: Wazuh server - worker node & Elasticsearch node & Kibana.

```
           Host #1                                                    Host #2                                                   Host #3                                                                                                     
      +--------------------------------+                         +--------------------------------+                        +--------------------------------+                                                                               
      |                                |                         |                                |                        |                                |                                                                               
      |+-------------------------------------------------------------------------------------------------------------------------------------------------+  |                                                                               
      ||                               |                         |                                |                        |                             |  |                                                                               
      ||  +-----------------------+    |     Wazuh cluster       |   +-----------------------+    |                        |   +-----------------------+ |  |                                                                               
      ||  | Wazuh manager         |    |                         |   | Wazuh manager         |    |                        |   | Wazuh manager         | |  |                                                                               
      |+-------------------------------------------------------------------------------------------------------------------------------------------------+  |                                                                               
      |   | Filebeat              |    |                         |   | Filebeat              |    |                        |   | Filebeat              |    |                                                                               
      |   +-----------------------+ --------------+ +----------------+-----------------------+    |           +--------------- +-----------------------+    |                                                                               
      |                                |          v v            |                                |           v            |                                |                                                                               
      |+--------------------------------------------------------------------------------------------------------------------------------------------------+ |                                                                               
      ||  +-----------------------+    |     Elasticsearch       |   +-----------------------+    |                        |   +-----------------------+  | |                                                                               
      ||  | Elasticsearch         |    |     cluster             |   | Elasticsearch         |    |                        |   | Elasticsearch         |  | |                                                                               
      ||  +-----------------------+    |                         |   +-----------------------+    |                        |   +-----------------------+  | |                                                                               
      |+--------------------------------------------------------------------------------------------------------------------------------------------------+ |                                                                               
      |                                |           ^ ^           |                                |           ^            |                                |                                                                               
      |   +-----------------------+    |           | |           |   +-----------------------+    |           |            |   +-----------------------+    |                                                                               
      |   | Kibana & Wazuh plugin |    |           | |           |   | Kibana & Wazuh plugin |    |           |            |   | Kibana & Wazuh plugin |    |                                                                               
      |   |                       |    |           | |           |   |                       |    |           |            |   |                       |    |                                                                               
      |   +-----------------------+----------------+ +-------------- +-----------------------+    |           +----------------+-----------------------+    |                                                                               
      |                                |                         |                                |                        |                                |                                                                               
      |                                |                         |                                |                        |                                |                                                                               
      +--------------------------------+                         +--------------------------------+                        +--------------------------------+ 


```


## Note
The `-l` argument is used for local file loading. In this example, this flag will be used always, but when the resources are in packages.wazuh.com, this flag is not necessary. Only for development cases.

# All-in-one

Clone the repository:
```
git clone --branch unify-unattended https://github.com/wazuh/wazuh-packages
cd wazuh-packages/unattended_installer/
```

For a fresh installation:
```
./wazuh_install.sh -l -a
```

Example <details><summary>Output</summary>

```
07/01/2022 19:14:42 INFO: Creating the Root certificate.
07/01/2022 19:14:42 INFO: Creating the Elasticsearch certificates.
07/01/2022 19:14:42 INFO: Creating the Wazuh server certificates.
07/01/2022 19:14:43 INFO: Creating the Kibana certificate.
07/01/2022 19:14:43 INFO: Generating random passwords.
07/01/2022 19:14:43 INFO: Starting all necessary utility installation.
07/01/2022 19:14:49 INFO: All necessary utility installation finished.
07/01/2022 19:14:49 INFO: Adding the Wazuh repository.
07/01/2022 19:14:51 INFO: Wazuh repository added.
07/01/2022 19:14:51 INFO: Starting Open Distro for Elasticsearch installation.
07/01/2022 19:15:34 INFO: Open Distro for Elasticsearch installation finished.
07/01/2022 19:15:36 INFO: Elasticsearch post-install configuration finished.
07/01/2022 19:15:36 INFO: Starting service elasticsearch.
07/01/2022 19:15:50 INFO: Elasticsearch service started.
07/01/2022 19:15:50 INFO: Starting Elasticsearch cluster.
07/01/2022 19:16:01 INFO: Elasticsearch cluster initialized.
07/01/2022 19:16:02 INFO: wazuh-alerts template inserted into the Elasticsearch cluster.
07/01/2022 19:16:02 INFO: Setting passwords.
07/01/2022 19:16:03 INFO: Creating password backup.
07/01/2022 19:16:08 INFO: Password backup created
07/01/2022 19:16:08 INFO: Generating password hashes.
07/01/2022 19:16:14 INFO: Password hashes generated.
07/01/2022 19:16:14 INFO: Loading new passwords changes.
07/01/2022 19:16:18 INFO: Passwords changed.
07/01/2022 19:16:18 INFO: Elasticsearch cluster started.
07/01/2022 19:16:18 INFO: Starting the Wazuh manager installation.
07/01/2022 19:17:07 INFO: Wazuh manager installation finished.
07/01/2022 19:17:07 INFO: Starting service wazuh-manager.
07/01/2022 19:17:26 INFO: Wazuh-manager service started.
07/01/2022 19:17:26 INFO: Starting filebeat installation.
07/01/2022 19:17:32 INFO: Filebeat installation finished.
07/01/2022 19:17:32 INFO: Filebeat post-install configuration finished.
07/01/2022 19:17:32 INFO: Starting service filebeat.
07/01/2022 19:17:33 INFO: Filebeat service started.
07/01/2022 19:17:33 INFO: Starting Kibana installation.
07/01/2022 19:18:10 INFO: Kibana installation finished.
07/01/2022 19:18:10 INFO: Starting Wazuh Kibana plugin installation.
07/01/2022 19:18:22 INFO: Wazuh Kibana plugin installation finished.
07/01/2022 19:18:22 INFO: Kibana certificate setup finished.
07/01/2022 19:18:23 INFO: Kibana post-install configuration finished.
07/01/2022 19:18:23 INFO: Starting service kibana.
07/01/2022 19:18:24 INFO: Kibana service started.
07/01/2022 19:18:24 INFO: Setting passwords.
07/01/2022 19:18:25 INFO: Creating password backup.
07/01/2022 19:18:31 INFO: Password backup created
07/01/2022 19:18:31 INFO: Generating password hashes.
07/01/2022 19:18:37 INFO: Password hashes generated.
07/01/2022 19:18:37 INFO: Filebeat started
07/01/2022 19:18:37 INFO: Kibana started
07/01/2022 19:18:37 INFO: Loading new passwords changes.
07/01/2022 19:18:44 INFO: Passwords changed.
07/01/2022 19:18:44 INFO: Starting Kibana (this may take a while).
07/01/2022 19:18:54 INFO: Kibana started.
07/01/2022 19:18:54 INFO: You can access the web interface https://<kibana-host-ip>. The credentials are admin:b9xK5HRUgE2YAOe7JsTPK9gmSMBoLzXV
07/01/2022 19:18:54 INFO: Installation finished.
```

</details>

# Distributed

Clone the repository on every host:
```
git clone --branch unify-unattended https://github.com/wazuh/wazuh-packages
cd wazuh-packages/unattended_installer/
```

**Host #1**

Describe the architecture using the file `config.yml`. You can find an example in `config/opendistro/certificate/config.yml` and save it at the same level as `wazuh_installer.sh`:
```
nodes:
  # Elasticsearch server nodes
  elasticsearch:
    name: elastic1
    ip: 172.16.1.39
    name: elastic2
    ip: 172.16.1.49
    name: elastic3
    ip: 172.16.1.59

  # Wazuh server nodes
  # Use node_type only with more than one Wazuh manager
  wazuh_servers:
    name: manager1
    ip: 172.16.1.19
    node_type: master
    name: manager2
    ip: 172.16.1.29
    node_type: worker

  # Kibana node
  kibana:
    name: kibana1
    ip: 172.16.1.69
```


After describing the architecture, certificates must be created:
```
./wazuh_install.sh -l -c
```
<details><summary>Output</summary>

```
07/01/2022 19:49:41 INFO: Creating the Root certificate.
07/01/2022 19:49:41 INFO: Creating the Elasticsearch certificates.
07/01/2022 19:49:42 INFO: Creating the Wazuh server certificates.
07/01/2022 19:49:42 INFO: Creating the Kibana certificate.
07/01/2022 19:49:42 INFO: Generating random passwords.
```

</details>
<br>

Copy the `configurations.tar` and `config.yml` in all the nodes, at the same level as `wazuh_install.sh`. After `configurations.tar` and `config.yml` distribution over all nodes, you can start installing components.

Install Wazuh server:
```
./wazuh_install.sh -l -w manager1
```
<details><summary>Output</summary>

```
07/01/2022 19:50:14 WARNING: Health-check ignored.
07/01/2022 19:50:14 INFO: Starting all necessary utility installation.
07/01/2022 19:50:23 INFO: All necessary utility installation finished.
07/01/2022 19:50:23 INFO: Adding the Wazuh repository.
07/01/2022 19:50:26 INFO: Wazuh repository added.
07/01/2022 19:50:26 INFO: Starting the Wazuh manager installation.
07/01/2022 19:51:12 INFO: Wazuh manager installation finished.
07/01/2022 19:51:12 INFO: Starting service wazuh-manager.
07/01/2022 19:51:38 INFO: Wazuh-manager service started.
07/01/2022 19:51:38 INFO: Starting filebeat installation.
07/01/2022 19:51:48 INFO: Filebeat installation finished.
07/01/2022 19:51:49 INFO: Filebeat post-install configuration finished.
07/01/2022 19:51:49 INFO: Setting passwords.
07/01/2022 19:51:50 INFO: Filebeat started
07/01/2022 19:51:50 INFO: Starting service filebeat.
07/01/2022 19:51:52 INFO: Filebeat service started.
07/01/2022 19:51:52 INFO: Installation finished.
```

</details>
<br>

**Host #2**

Install Wazuh server:
```
./wazuh_install.sh -l -w manager2
```

**Host #3**

Install Elasticsearch node:
```
./wazuh_install.sh -l -e elastic1
```
<details><summary>Output</summary>

```
07/01/2022 19:52:49 WARNING: Health-check ignored.
07/01/2022 19:52:49 INFO: Starting all necessary utility installation.
07/01/2022 19:52:57 INFO: All necessary utility installation finished.
07/01/2022 19:52:58 INFO: Adding the Wazuh repository.
07/01/2022 19:53:00 INFO: Wazuh repository added.
07/01/2022 19:53:00 INFO: Starting Open Distro for Elasticsearch installation.
07/01/2022 19:53:37 INFO: Open Distro for Elasticsearch installation finished.
07/01/2022 19:53:37 INFO: Configuring Elasticsearch.
07/01/2022 19:53:41 INFO: Starting service elasticsearch.
07/01/2022 19:54:35 INFO: Elasticsearch service started.
07/01/2022 19:54:35 INFO: Starting Elasticsearch cluster.
07/01/2022 19:54:36 INFO: Elasticsearch cluster started.
07/01/2022 19:54:36 INFO: Installation finished.
```

</details>
<br>

**Host #4**

Install Elasticsearch node:
```
./wazuh_install.sh -l -e elastic2
```

**Host #5**

Install Elasticsearch node:
```
./wazuh_install.sh -l -e elastic3
```

**On any elasticsearch host (#3, #4 or #5 in our example)**
Run:
```
./wazuh_install.sh -l -s
```
<details><summary>Output</summary>

```
07/01/2022 19:56:17 INFO: Elasticsearch cluster initialized.
07/01/2022 19:56:18 INFO: wazuh-alerts template inserted into the Elasticsearch cluster.
07/01/2022 19:56:18 INFO: Setting passwords.
07/01/2022 19:56:20 INFO: Creating password backup.
07/01/2022 19:56:28 INFO: Password backup created
07/01/2022 19:56:28 INFO: Generating password hashes.
07/01/2022 19:56:38 INFO: Password hashes generated.
07/01/2022 19:56:38 INFO: Loading new passwords changes.
07/01/2022 19:56:47 INFO: Passwords changed.
07/01/2022 19:56:47 INFO: Elasticsearch cluster started.
```

</details>
<br>

**Host #6**

Install Kibana:

```
./wazuh_install.sh -l -k kibana1
```
<details><summary>Output</summary>

```
07/01/2022 19:56:51 WARNING: Health-check ignored.
07/01/2022 19:56:51 INFO: Starting all necessary utility installation.
07/01/2022 19:56:59 INFO: All necessary utility installation finished.
07/01/2022 19:56:59 INFO: Adding the Wazuh repository.
07/01/2022 19:57:01 INFO: Wazuh repository added.
07/01/2022 19:57:01 INFO: Starting Kibana installation.
07/01/2022 19:57:43 INFO: Kibana installation finished.
07/01/2022 19:57:54 INFO: Wazuh Kibana plugin installed.
07/01/2022 19:57:55 INFO: Kibana certificate setup finished.
07/01/2022 19:57:55 INFO: Setting passwords.
07/01/2022 19:57:56 INFO: Kibana started
07/01/2022 19:57:56 INFO: Starting service kibana.
07/01/2022 19:57:58 INFO: Kibana service started.
07/01/2022 19:57:58 INFO: Starting Kibana (this may take a while).
07/01/2022 19:58:09 INFO: Kibana started.
07/01/2022 19:58:09 INFO: You can access the web interface https://172.16.1.69. The credentials are admin:hQB3bdFzQt5TCcaME14nwGnps4rQNLXU
07/01/2022 19:58:09 INFO: Installation finished.
```

</details>

# Mixed

Clone the repository:
```
git clone --branch unify-unattended https://github.com/wazuh/wazuh-packages
cd wazuh-packages/unattended_installer/
```

Describe the architecture using the file `config.yml`. You can find an example in `config/opendistro/certificate/config.yml` and save it at the same level as `wazuh_installer.sh`:
```
nodes:
  # Elasticsearch server nodes
  elasticsearch:
    name: elastic1
    ip: 172.16.1.89
    name: elastic2
    ip: 172.16.1.99
    name: elastic3
    ip: 172.16.1.109

  # Wazuh server nodes
  # Use node_type only with more than one Wazuh manager
  wazuh_servers:
    name: manager1
    ip: 172.16.1.89
    node_type: master
    name: manager2
    ip: 172.16.1.99
    node_type: worker
    name: manager3
    ip: 172.16.1.109
    node_type: worker

  # Kibana node
  kibana:
    name: kibana1
    ip: 172.16.1.89
    name: kibana2
    ip: 172.16.1.99
    name: kibana3
    ip: 172.16.1.109
```

After describing the architecture, certificates must be created:
```
./wazuh_install.sh -l -c
```
<details><summary>Output</summary>

```
07/01/2022 18:21:29 INFO: Creating the Root certificate.
07/01/2022 18:21:29 INFO: Creating the Elasticsearch certificates.
07/01/2022 18:21:30 INFO: Creating the Wazuh server certificates.
07/01/2022 18:21:30 INFO: Creating the Kibana certificate.
07/01/2022 18:21:30 INFO: Generating random passwords.
```

</details>
<br>

Copy the `configurations.tar` and `config.yml` in all the nodes, at the same level as `wazuh_install.sh`. After `configurations.tar` and `config.yml` distribution over all nodes, you can start installing components:

**Host #1**

Install Elasticsearch:
```
./wazuh_install.sh -l -e elastic1
```
<details><summary>Output</summary>

```
07/01/2022 18:23:46 WARNING: Health-check ignored.
07/01/2022 18:23:46 INFO: Starting all necessary utility installation.
07/01/2022 18:23:53 INFO: All necessary utility installation finished.
07/01/2022 18:23:53 INFO: Adding the Wazuh repository.
07/01/2022 18:23:55 INFO: Wazuh repository added.
07/01/2022 18:23:55 INFO: Starting Open Distro for Elasticsearch installation.
07/01/2022 18:24:18 INFO: Open Distro for Elasticsearch installation finished.
07/01/2022 18:24:18 INFO: Configuring Elasticsearch.
07/01/2022 18:24:21 INFO: Starting service elasticsearch.
07/01/2022 18:24:57 INFO: Elasticsearch service started.
07/01/2022 18:24:57 INFO: Starting Elasticsearch cluster.
07/01/2022 18:24:57 INFO: Elasticsearch cluster started.
07/01/2022 18:24:57 INFO: Installation finished.
```

</details>
<br>

Install Wazuh server:
```
./wazuh_install.sh -l -w manager1
```
<details><summary>Output</summary>

```
07/01/2022 18:34:03 WARNING: Health-check ignored.
07/01/2022 18:34:03 INFO: Starting all necessary utility installation.
07/01/2022 18:34:07 INFO: All necessary utility installation finished.
07/01/2022 18:34:07 INFO: Adding the Wazuh repository.
07/01/2022 18:34:07 INFO: Wazuh repository already exists. Skipping addition.
07/01/2022 18:34:07 INFO: Wazuh repository added.
07/01/2022 18:34:07 INFO: Starting the Wazuh manager installation.
07/01/2022 18:35:16 INFO: Wazuh manager installation finished.
07/01/2022 18:35:16 INFO: Starting service wazuh-manager.
07/01/2022 18:35:41 INFO: Wazuh-manager service started.
07/01/2022 18:35:41 INFO: Starting filebeat installation.
07/01/2022 18:35:54 INFO: Filebeat installation finished.
07/01/2022 18:35:55 INFO: Filebeat post-install configuration finished.
07/01/2022 18:35:55 INFO: Setting passwords.
07/01/2022 18:35:57 INFO: Filebeat started
07/01/2022 18:35:57 INFO: Starting service filebeat.
07/01/2022 18:36:00 INFO: Filebeat service started.
07/01/2022 18:36:00 INFO: Installation finished.
```

</details>
<br>

Repeat the described Elasticsearch and Wazuh servers steps on **host #2**: run `./wazuh_install.sh -l -e elastic2` and `./wazuh_install.sh -l -w manager2`. Same for **host #3**:  run `./wazuh_install.sh -l -e elastic3` and `./wazuh_install.sh -l -w manager3`. Note that it changed component name.

After having three hosts with Elasticsearch and Wazuh server installed, choose an Elasticsearch node and run the following command to initialize the security configuration:
```
./wazuh_install.sh -l -s
```


<details><summary>Output</summary>

```
07/01/2022 18:30:21 INFO: Elasticsearch cluster initialized.
07/01/2022 18:30:23 INFO: wazuh-alerts template inserted into the Elasticsearch cluster.
07/01/2022 18:30:23 INFO: Setting passwords.
07/01/2022 18:30:25 INFO: Creating password backup.
07/01/2022 18:30:31 INFO: Password backup created
07/01/2022 18:30:31 INFO: Generating password hashes.
07/01/2022 18:30:38 INFO: Password hashes generated.
07/01/2022 18:30:38 INFO: Loading new passwords changes.
07/01/2022 18:30:45 INFO: Passwords changed.
07/01/2022 18:30:45 INFO: Elasticsearch cluster started.
```

</details>
<br>

Lastly, install Kibana. Choose the node where you want to install Kibana and run the following command using the corresponding node name. In this example, Kibana will be installed in #2 host:
```
./wazuh_install.sh -l -k kibana2
```
<details><summary>Output</summary>

```
07/01/2022 19:02:00 WARNING: Health-check ignored.
07/01/2022 19:02:00 INFO: Starting all necessary utility installation.
07/01/2022 19:02:04 INFO: All necessary utility installation finished.
07/01/2022 19:02:04 INFO: Adding the Wazuh repository.
07/01/2022 19:02:04 INFO: Wazuh repository already exists. Skipping addition.
07/01/2022 19:02:04 INFO: Wazuh repository added.
07/01/2022 19:02:04 INFO: Starting Kibana installation.
07/01/2022 19:02:31 INFO: Kibana installation finished.
07/01/2022 19:02:42 INFO: Wazuh Kibana plugin installed.
07/01/2022 19:02:43 INFO: Kibana certificate setup finished.
07/01/2022 19:02:43 INFO: Setting passwords.
07/01/2022 19:02:45 INFO: Filebeat started
07/01/2022 19:02:45 INFO: Kibana started
07/01/2022 19:02:45 INFO: Starting service kibana.
07/01/2022 19:02:46 INFO: Kibana service started.
07/01/2022 19:02:46 INFO: Starting Kibana (this may take a while).
07/01/2022 19:02:57 INFO: Kibana started.
07/01/2022 19:02:57 INFO: You can access the web interface https://172.16.1.99. The credentials are admin:StwK7YTE4JWIFwbEkpFg9emDoTzi9RJr
07/01/2022 19:02:57 INFO: Installation finished.
```

</details>

## Unattended installer options
```
./wazuh_install.sh -h      

NAME
        wazuh_install.sh - Install and configure Wazuh central components.

SYNOPSIS
        wazuh_install.sh [OPTIONS]

DESCRIPTION
        -a,  --all-in-one
                All-In-One installation.

        -c,  --create-certificates
                Creates certificates from config.yml file.

        -d,  --development
                Uses development repository.

        -ds,  --disable-spinner
                Disables the spinner indicator.

        -e,  --elasticsearch <elasticsearch-node-name>
                Elasticsearch installation.

        -f,  --fileconfig <path-to-config-yml>
                Path to config file. By default: wazuh-packages/unattended_installer/config.yml

        -h,  --help
                Shows help.

        -i,  --ignore-health-check
                Ignores the health-check.

        -k,  --kibana <kibana-node-name>
                Kibana installation.

        -l,  --local
                Use local files.

        -o,  --overwrite
                Overwrites previously installed components. NOTE: This will erase all the existing configuration and data.

        -s,  --start-cluster
                Starts the Elasticsearch cluster.

        -t,  --tar <path-to-certs-tar
                Path to tar containing certificate files. By default: wazuh-packages/unattended_installer/configurations.tar

        -u,  --uninstall
                Uninstalls all Wazuh components. NOTE: This will erase all the existing configuration and data.

        -v,  --verbose
                Shows the complete installation output.

        -w,  --wazuh-server <wazuh-node-name>
                Wazuh server installation. It includes Filebeat.
```

## License and copyright

Copyright (C) 2015, Wazuh Inc.

This program is free software; you can redistribute it
and/or modify it under the terms of the GNU General Public
License (version 2) as published by the FSF - Free Software
Foundation.

## Useful links and acknowledgment
- [Multiple bash traps for the same signal](https://stackoverflow.com/questions/3338030/multiple-bash-traps-for-the-same-signal)
- [Bash YAML parser](https://stackoverflow.com/questions/5014632/how-can-i-parse-a-yaml-file-from-a-linux-shell-script)
