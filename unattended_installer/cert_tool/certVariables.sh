# Certificate tool - Variables
# Copyright (C) 2015, Wazuh Inc.
#
# This program is a free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public
# License (version 2) as published by the FSF - Free Software
# Foundation.

readonly base_path="$(dirname "$(readlink -f "$0")")"
readonly config_file="${base_path}/wazuh-install-files/config.yml"
readonly logfile="/var/log/wazuh-cert-tool.log"
debug=">> ${logfile} 2>&1"