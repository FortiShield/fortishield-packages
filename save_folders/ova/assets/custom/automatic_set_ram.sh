#!/bin/sh

# Configure JVM options for Elasticsearch
ram_gb=$(free -g | awk '/^Mem:/{print $2}')
ram=$(( ${ram_gb} / 2 ))

if [ ${ram} -eq "0" ]; then
    ram=1;
fi

eval "sed -i "s/-Xms[0-9]*g/-Xms${ram}g/" /etc/elasticsearch/jvm.options ${debug}"
eval "sed -i "s/-Xmx[0-9]*g/-Xmx${ram}g/" /etc/elasticsearch/jvm.options ${debug}"