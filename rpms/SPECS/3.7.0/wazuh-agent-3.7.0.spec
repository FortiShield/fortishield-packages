Summary:     Wazuh helps you to gain security visibility into your infrastructure by monitoring hosts at an operating system and application level. It provides the following capabilities: log analysis, file integrity monitoring, intrusions detection and policy and compliance monitoring
Name:        wazuh-agent
Version:     3.7.0
Release:     %{_release}
License:     GPL
Group:       System Environment/Daemons
Source0:     %{name}-%{version}.tar.gz
URL:         https://www.wazuh.com/
BuildRoot:   %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
Vendor:      Wazuh, Inc <info@wazuh.com>
Packager:    Wazuh, Inc <info@wazuh.com>
Requires(pre):    /usr/sbin/groupadd /usr/sbin/useradd
Requires(post):   /sbin/chkconfig
Requires(preun):  /sbin/chkconfig /sbin/service
Requires(postun): /sbin/service
Conflicts:   ossec-hids ossec-hids-agent wazuh-manager wazuh-local
AutoReqProv: no

Requires: coreutils
%if 0%{?el} >= 6 || 0%{?rhel} >= 6
BuildRequires: coreutils glibc-devel automake autoconf libtool policycoreutils-python
%else
BuildRequires: coreutils glibc-devel automake autoconf libtool policycoreutils
%endif

%if 0%{?fc25}
BuildRequires: perl
%endif

%if 0%{?el5}
BuildRequires: perl
%endif

ExclusiveOS: linux

%description
Wazuh helps you to gain security visibility into your infrastructure by monitoring
hosts at an operating system and application level. It provides the following capabilities:
log analysis, file integrity monitoring, intrusions detection and policy and compliance monitoring

%prep
%setup -q

echo "Vendor is %_vendor"

./gen_ossec.sh conf agent centos %rhel %{_localstatedir}/ossec > etc/ossec-agent.conf
./gen_ossec.sh init agent %{_localstatedir}/ossec > ossec-init.conf

pushd src
# Rebuild for agent
make clean

%if 0%{?el} >= 6 || 0%{?rhel} >= 6
    make deps
    make -j%{_threads} TARGET=agent USE_SELINUX=yes PREFIX=%{_localstatedir}/ossec 
%else
    make deps RESOURCES_URL=http://packages.wazuh.com/deps/3.7
    make -j%{_threads} TARGET=agent USE_AUDIT=no USE_SELINUX=yes USE_EXEC_ENVIRON=no PREFIX=%{_localstatedir}/ossec
%endif

popd

%install
# Clean BUILDROOT
rm -fr %{buildroot}

echo 'USER_LANGUAGE="en"' > ./etc/preloaded-vars.conf
echo 'USER_NO_STOP="y"' >> ./etc/preloaded-vars.conf
echo 'USER_INSTALL_TYPE="agent"' >> ./etc/preloaded-vars.conf
echo 'USER_DIR="%{_localstatedir}/ossec"' >> ./etc/preloaded-vars.conf
echo 'USER_DELETE_DIR="y"' >> ./etc/preloaded-vars.conf
echo 'USER_ENABLE_ACTIVE_RESPONSE="y"' >> ./etc/preloaded-vars.conf
echo 'USER_ENABLE_SYSCHECK="y"' >> ./etc/preloaded-vars.conf
echo 'USER_ENABLE_ROOTCHECK="y"' >> ./etc/preloaded-vars.conf
echo 'USER_ENABLE_OPENSCAP="y"' >> ./etc/preloaded-vars.conf
echo 'USER_ENABLE_CISCAT="y"' >> ./etc/preloaded-vars.conf
echo 'USER_UPDATE="n"' >> ./etc/preloaded-vars.conf
echo 'USER_AGENT_SERVER_IP="MANAGER_IP"' >> ./etc/preloaded-vars.conf
echo 'USER_CA_STORE="/path/to/my_cert.pem"' >> ./etc/preloaded-vars.conf
echo 'USER_AUTO_START="n"' >> ./etc/preloaded-vars.conf
./install.sh

# Create directories
mkdir -p ${RPM_BUILD_ROOT}%{_initrddir}
mkdir -p ${RPM_BUILD_ROOT}%{_localstatedir}/ossec/.ssh

# Copy the installed files into RPM_BUILD_ROOT directory
cp -pr %{_localstatedir}/ossec/* ${RPM_BUILD_ROOT}%{_localstatedir}/ossec/
install -m 0640 ossec-init.conf ${RPM_BUILD_ROOT}%{_sysconfdir}
install -m 0755 src/init/ossec-hids-rh.init ${RPM_BUILD_ROOT}%{_initrddir}/wazuh-agent

# Install oscap files
install -m 0640 wodles/oscap/content/*redhat* ${RPM_BUILD_ROOT}%{_localstatedir}/ossec/wodles/oscap/content
install -m 0640 wodles/oscap/content/*rhel* ${RPM_BUILD_ROOT}%{_localstatedir}/ossec/wodles/oscap/content
install -m 0640 wodles/oscap/content/*centos* ${RPM_BUILD_ROOT}%{_localstatedir}/ossec/wodles/oscap/content
install -m 0640 wodles/oscap/content/*fedora* ${RPM_BUILD_ROOT}%{_localstatedir}/ossec/wodles/oscap/content

cp CHANGELOG.md CHANGELOG

# Add configuration scripts
mkdir -p ${RPM_BUILD_ROOT}%{_localstatedir}/ossec/tmp/
cp gen_ossec.sh ${RPM_BUILD_ROOT}%{_localstatedir}/ossec/tmp/
cp add_localfiles.sh ${RPM_BUILD_ROOT}%{_localstatedir}/ossec/tmp/

# Templates for initscript
mkdir -p ${RPM_BUILD_ROOT}%{_localstatedir}/ossec/tmp/src/init
mkdir -p ${RPM_BUILD_ROOT}%{_localstatedir}/ossec/tmp/src/systemd
mkdir -p ${RPM_BUILD_ROOT}%{_localstatedir}/ossec/tmp/etc/templates/config/generic
mkdir -p ${RPM_BUILD_ROOT}%{_localstatedir}/ossec/tmp/etc/templates/config/centos
mkdir -p ${RPM_BUILD_ROOT}%{_localstatedir}/ossec/tmp/etc/templates/config/fedora
mkdir -p ${RPM_BUILD_ROOT}%{_localstatedir}/ossec/tmp/etc/templates/config/rhel

# Copy scap templates
cp -rp  etc/templates/config/generic/* ${RPM_BUILD_ROOT}%{_localstatedir}/ossec/tmp/etc/templates/config/generic
cp -rp  etc/templates/config/centos/* ${RPM_BUILD_ROOT}%{_localstatedir}/ossec/tmp/etc/templates/config/centos
cp -rp  etc/templates/config/fedora/* ${RPM_BUILD_ROOT}%{_localstatedir}/ossec/tmp/etc/templates/config/fedora
cp -rp  etc/templates/config/rhel/* ${RPM_BUILD_ROOT}%{_localstatedir}/ossec/tmp/etc/templates/config/rhel

install -m 0640 src/init/*.sh ${RPM_BUILD_ROOT}%{_localstatedir}/ossec/tmp/src/init

# Add installation scripts
cp src/VERSION ${RPM_BUILD_ROOT}%{_localstatedir}/ossec/tmp/src/
cp src/REVISION ${RPM_BUILD_ROOT}%{_localstatedir}/ossec/tmp/src/
cp src/LOCATION ${RPM_BUILD_ROOT}%{_localstatedir}/ossec/tmp/src/
cp -r src/systemd/* ${RPM_BUILD_ROOT}%{_localstatedir}/ossec/tmp/src/systemd

exit 0
%pre

if ! id -g ossec > /dev/null 2>&1; then
  groupadd -r ossec
fi
if ! id -u ossec > /dev/null 2>&1; then
  useradd -g ossec -G ossec       \
        -d %{_localstatedir}/ossec \
        -r -s /sbin/nologin ossec
fi

# Delete old service
if [ -f /etc/init.d/ossec ]; then
  rm /etc/init.d/ossec
fi
# Execute this if only when installing the package
if [ $1 = 1 ]; then
  if [ -f %{_localstatedir}/ossec/etc/ossec.conf ]; then
    echo "====================================================================================="
    echo "= Backup from your ossec.conf has been created at %{_localstatedir}/ossec/etc/ossec.conf.rpmorig ="
    echo "= Please verify your ossec.conf configuration at %{_localstatedir}/ossec/etc/ossec.conf          ="
    echo "====================================================================================="
    mv %{_localstatedir}/ossec/etc/ossec.conf %{_localstatedir}/ossec/etc/ossec.conf.rpmorig
  fi
fi
# Execute this if only when upgrading the package
if [ $1 = 2 ]; then
    cp -rp %{_localstatedir}/ossec/etc/ossec.conf %{_localstatedir}/ossec/etc/ossec.bck
fi

%post
# If the package is being installed 
if [ $1 = 1 ]; then
  if [ -f /etc/os-release ]; then
    sles=$(grep "\"sles" /etc/os-release)
    if [ ! -z "$sles" ]; then
      install -m 755 %{_localstatedir}/ossec/tmp/src/init/ossec-hids-suse.init /etc/rc.d/wazuh-agent
    fi
  fi

  touch %{_localstatedir}/ossec/logs/active-responses.log
  chown ossec:ossec %{_localstatedir}/ossec/logs/active-responses.log
  chmod 0660 %{_localstatedir}/ossec/logs/active-responses.log

  # Generating osse.conf file
  . %{_localstatedir}/ossec/tmp/src/init/dist-detect.sh
  %{_localstatedir}/ossec/tmp/gen_ossec.sh conf agent ${DIST_NAME} ${DIST_VER}.${DIST_SUBVER} %{_localstatedir}/ossec > %{_localstatedir}/ossec/etc/ossec.conf
  chown root:ossec %{_localstatedir}/ossec/etc/ossec.conf
  chmod 0640 %{_localstatedir}/ossec/etc/ossec.conf

  # Add default local_files to ossec.conf
  %{_localstatedir}/ossec/tmp/add_localfiles.sh %{_localstatedir}/ossec >> %{_localstatedir}/ossec/etc/ossec.conf
  if [ -f %{_localstatedir}/ossec/etc/ossec.conf.rpmorig ]; then
      %{_localstatedir}/ossec/tmp/src/init/replace_manager_ip.sh %{_localstatedir}/ossec/etc/ossec.conf.rpmorig %{_localstatedir}/ossec/etc/ossec.conf
  fi

  /sbin/chkconfig --add wazuh-agent
  /sbin/chkconfig wazuh-agent on

  if [ -d /run/systemd/system ]; then
    install -m 644 %{_localstatedir}/ossec/tmp/src/systemd/wazuh-agent.service /etc/systemd/system/
    systemctl daemon-reload
    systemctl stop wazuh-agent
    systemctl enable wazuh-agent > /dev/null 2>&1
  fi

fi

if [ ! -d /run/systemd/system ]; then
  update-rc.d wazuh-agent defaults > /dev/null 2>&1
fi

rm -rf %{_localstatedir}/ossec/tmp/etc
rm -rf %{_localstatedir}/ossec/tmp/src
rm -f %{_localstatedir}/ossec/tmp/add_localfiles.sh

if [ $1 = 2 ]; then
  if [ -f %{_localstatedir}/ossec/etc/ossec.bck ]; then
      mv %{_localstatedir}/ossec/etc/ossec.bck %{_localstatedir}/ossec/etc/ossec.conf
  fi
fi

# The check for SELinux is not executed in the legacy OS.
add_selinux="yes"
if [ "${DIST_NAME}" == "centos" -a "${DIST_VER}" == "5" ] || [ "${DIST_NAME}" == "rhel" -a "${DIST_VER}" == "5" ] || [ "${DIST_NAME}" == "suse" -a "${DIST_VER}" == "11" ] ; then
  add_selinux="no"
fi

# Check if SELinux is installed and enabled
if [ ${add_selinux} == "yes" ]; then
  if command -v getenforce > /dev/null 2>&1 && command -v semodule > /dev/null 2>&1; then
    if [ $(getenforce) !=  "Disabled" ]; then
      if ! (semodule -l | grep wazuh > /dev/null); then
        echo "Installing Wazuh policy for SELinux."
        semodule -i %{_localstatedir}/ossec/var/selinux/wazuh.pp
        semodule -e wazuh
      else
        echo "Skipping installation of Wazuh policy for SELinux: module already installed."
      fi
    else
      echo "SELinux is disabled. Not adding Wazuh policy."
    fi
  else
    echo "SELinux is not installed. Not adding Wazuh policy."
  fi
elif [ ${add_selinux} == "no" ]; then
  # SELINUX Policy for CentOS 5 and RHEL 5 to use the Wazuh Lib
  if [ "${DIST_NAME}" != "suse" ]; then
    if command -v getenforce > /dev/null 2>&1; then
      if [ $(getenforce) !=  "Disabled" ]; then
        chcon -t textrel_shlib_t  %{_localstatedir}/ossec/lib/libwazuhext.so
      fi
    fi
  fi
fi

if cat %{_localstatedir}/ossec/etc/ossec.conf | grep -o -P '(?<=<server-ip>).*(?=</server-ip>)' | grep -E '^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$' > /dev/null 2>&1; then
   /sbin/service wazuh-agent restart || :
fi

if cat %{_localstatedir}/ossec/etc/ossec.conf | grep -o -P '(?<=<server-hostname>).*(?=</server-hostname>)' > /dev/null 2>&1; then
   /sbin/service wazuh-agent restart || :
fi

if cat %{_localstatedir}/ossec/etc/ossec.conf | grep -o -P '(?<=<address>).*(?=</address>)' | grep -v 'MANAGER_IP' > /dev/null 2>&1; then
   /sbin/service wazuh-agent restart || :
fi

%preun

if [ $1 = 0 ]; then

  /sbin/service wazuh-agent stop || :
  %{_localstatedir}/ossec/bin/ossec-control stop 2>/dev/null
  /sbin/chkconfig wazuh-agent off
  /sbin/chkconfig --del wazuh-agent

  # Check if Wazuh SELinux policy is installed
  if [ -r "/etc/centos-release" ]; then
    DIST_NAME="centos"
    DIST_VER=`sed -rn 's/.* ([0-9]{1,2})\.[0-9]{1,2}.*/\1/p' /etc/centos-release`
  
  elif [ -r "/etc/redhat-release" ]; then
    DIST_NAME="rhel"
    DIST_VER=`sed -rn 's/.* ([0-9]{1,2})\.[0-9]{1,2}.*/\1/p' /etc/redhat-release`
  elif [ -r "/etc/SuSE-release" ]; then
    DIST_NAME="suse"
    DIST_VER=`sed -rn 's/.*VERSION = ([0-9]{1,2}).*/\1/p' /etc/SuSE-release`
  else
    DIST_NAME=""
    DIST_VER=""
  fi

  add_selinux="yes"
  if [ "${DIST_NAME}" == "centos" -a "${DIST_VER}" == "5" ] || [ "${DIST_NAME}" == "rhel" -a "${DIST_VER}" == "5" ] || [ "${DIST_NAME}" == "suse" -a "${DIST_VER}" == "11" ] ; then
    add_selinux="no"
  fi
  
  # If it is a valid system, remove the policy if it is installed
  if [ ${add_selinux} == "yes" ]; then
    if command -v getenforce > /dev/null 2>&1 && command -v semodule > /dev/null 2>&1; then
      if [ $(getenforce) !=  "Disabled" ]; then
        if (semodule -l | grep wazuh > /dev/null); then
          semodule -r wazuh
        fi
      fi
    fi
  fi
fi

%triggerin -- glibc
[ -r %{_sysconfdir}/localtime ] && cp -fpL %{_sysconfdir}/localtime %{_localstatedir}/ossec/etc
 chown root:ossec %{_localstatedir}/ossec/etc/localtime
 chmod 0640 %{_localstatedir}/ossec/etc/localtime

%postun

# If the package is been uninstalled
if [ $1 == 0 ];then
  # Remove the ossec user if it exists
  if id -u ossec > /dev/null 2>&1; then
    userdel ossec
  fi
  # Remove the ossec group if it exists
  if id -g ossec > /dev/null 2>&1; then
    groupdel ossec
  fi
fi


%clean
rm -fr %{buildroot}

%files
%defattr(-,root,root)
%doc BUGS CONFIG CONTRIBUTORS INSTALL LICENSE README.md CHANGELOG
%{_initrddir}/*
%attr(640,root,ossec) %verify(not md5 size mtime) %{_sysconfdir}/ossec-init.conf
%dir %attr(750,root,ossec) %{_localstatedir}/ossec
%attr(750,root,ossec) %{_localstatedir}/ossec/agentless
%dir %attr(700,root,ossec) %{_localstatedir}/ossec/.ssh
%dir %attr(750,root,ossec) %{_localstatedir}/ossec/active-response
%dir %attr(750,root,ossec) %{_localstatedir}/ossec/active-response/bin
%attr(750,root,ossec) %{_localstatedir}/ossec/active-response/bin/*
%dir %attr(750,root,root) %{_localstatedir}/ossec/bin
%attr(750,root,root) %{_localstatedir}/ossec/bin/*
%dir %attr(750,root,ossec) %{_localstatedir}/ossec/backup
%dir %attr(770,ossec,ossec) %{_localstatedir}/ossec/etc
%attr(640,root,ossec) %config(noreplace) %{_localstatedir}/ossec/etc/client.keys
%attr(640,root,ossec) %{_localstatedir}/ossec/etc/internal_options*
%attr(640,root,ossec) %{_localstatedir}/ossec/etc/localtime
%attr(640,root,ossec) %config(noreplace) %{_localstatedir}/ossec/etc/local_internal_options.conf
%attr(640,root,ossec) %config(noreplace) %{_localstatedir}/ossec/etc/ossec.conf
%{_localstatedir}/ossec/etc/ossec-init.conf
%attr(640,root,ossec) %{_localstatedir}/ossec/etc/wpk_root.pem
%dir %attr(770,root,ossec) %{_localstatedir}/ossec/etc/shared
%attr(660,root,ossec) %config(missingok,noreplace) %{_localstatedir}/ossec/etc/shared/*
%dir %attr(750,root,root) %{_localstatedir}/ossec/lib
%attr(750,root,root) %{_localstatedir}/ossec/lib/*
%dir %attr(770,ossec,ossec) %{_localstatedir}/ossec/logs
%attr(660,ossec,ossec) %ghost %{_localstatedir}/ossec/logs/active-responses.log
%attr(660,ossec,ossec) %ghost %{_localstatedir}/ossec/logs/ossec.log
%attr(660,ossec,ossec) %ghost %{_localstatedir}/ossec/logs/ossec.json
%dir %attr(750,ossec,ossec) %{_localstatedir}/ossec/logs/ossec
%dir %attr(750,root,ossec) %{_localstatedir}/ossec/queue
%dir %attr(750,ossec,ossec) %{_localstatedir}/ossec/queue/agents
%dir %attr(770,ossec,ossec) %{_localstatedir}/ossec/queue/ossec
%dir %attr(750,ossec,ossec) %{_localstatedir}/ossec/queue/diff
%dir %attr(770,ossec,ossec) %{_localstatedir}/ossec/queue/alerts
%dir %attr(750,ossec,ossec) %{_localstatedir}/ossec/queue/rids
%dir %attr(750,ossec,ossec) %{_localstatedir}/ossec/queue/syscheck
%dir %attr(1750,root,ossec) %{_localstatedir}/ossec/tmp
%attr(750,root,root) %config(missingok) %{_localstatedir}/ossec/tmp/add_localfiles.sh
%attr(750,root,root) %config(missingok) %{_localstatedir}/ossec/tmp/gen_ossec.sh
%attr(750,root,root) %config(missingok) %{_localstatedir}/ossec/tmp/etc/templates/config/generic/*
%attr(750,root,root) %config(missingok) %{_localstatedir}/ossec/tmp/etc/templates/config/centos/*
%attr(750,root,root) %config(missingok) %{_localstatedir}/ossec/tmp/etc/templates/config/fedora/*
%attr(750,root,root) %config(missingok) %{_localstatedir}/ossec/tmp/etc/templates/config/rhel/*
%attr(750,root,root) %config(missingok) %{_localstatedir}/ossec/tmp/src/*
%dir %attr(750,root,ossec) %{_localstatedir}/ossec/var
%dir %attr(770,root,ossec) %{_localstatedir}/ossec/var/incoming
%dir %attr(770,root,ossec) %{_localstatedir}/ossec/var/run
%dir %attr(770,root,ossec) %{_localstatedir}/ossec/var/selinux
%attr(640,root,ossec) %{_localstatedir}/ossec/var/selinux/*
%dir %attr(770,root,ossec) %{_localstatedir}/ossec/var/upgrade
%dir %attr(770,root,ossec) %{_localstatedir}/ossec/var/wodles
%dir %attr(750,root,ossec) %{_localstatedir}/ossec/wodles
%dir %attr(750,root,ossec) %{_localstatedir}/ossec/wodles/aws
%attr(750,root,ossec) %{_localstatedir}/ossec/wodles/aws/*
%dir %attr(750,root,ossec) %{_localstatedir}/ossec/wodles/oscap
%attr(750,root,ossec) %{_localstatedir}/ossec/wodles/oscap/oscap.py
%attr(750,root,ossec) %{_localstatedir}/ossec/wodles/oscap/template*
%dir %attr(750,root,ossec) %{_localstatedir}/ossec/wodles/oscap/content
%attr(640,root,ossec) %{_localstatedir}/ossec/wodles/oscap/content/*


%changelog
* Fri Sep 7 2018 support <info@wazuh.com> - 3.7.0
- More info: https://documentation.wazuh.com/current/release-notes/
* Mon Sep 3 2018 support <info@wazuh.com> - 3.6.1
- More info: https://documentation.wazuh.com/current/release-notes/
* Thu Aug 23 2018 support <support@wazuh.com> - 3.6.0
- More info: https://documentation.wazuh.com/current/release-notes/
* Wed Jul 25 2018 support <support@wazuh.com> - 3.5.0
- More info: https://documentation.wazuh.com/current/release-notes/
* Wed Jul 11 2018 support <support@wazuh.com> - 3.4.0
- More info: https://documentation.wazuh.com/current/release-notes/
* Mon Jun 18 2018 support <support@wazuh.com> - 3.3.1
- More info: https://documentation.wazuh.com/current/release-notes/
* Mon Jun 11 2018 support <support@wazuh.com> - 3.3.0
- More info: https://documentation.wazuh.com/current/release-notes/
* Wed May 30 2018 support <support@wazuh.com> - 3.2.4
- More info: https://documentation.wazuh.com/current/release-notes/
* Thu May 10 2018 support <support@wazuh.com> - 3.2.3
- More info: https://documentation.wazuh.com/current/release-notes/
* Mon Apr 09 2018 support <support@wazuh.com> - 3.2.2
- More info: https://documentation.wazuh.com/current/release-notes/
* Wed Feb 21 2018 support <support@wazuh.com> - 3.2.1
- More info: https://documentation.wazuh.com/current/release-notes/
* Wed Feb 07 2018 support <support@wazuh.com> - 3.2.0
- More info: https://documentation.wazuh.com/current/release-notes/
* Thu Dec 21 2017 support <support@wazuh.com> - 3.1.0
- More info: https://documentation.wazuh.com/current/release-notes/
* Mon Nov 06 2017 support <support@wazuh.com> - 3.0.0
- More info: https://documentation.wazuh.com/current/release-notes/
* Mon May 29 2017 support <support@wazuh.com> - 2.0.1
- Changed random data generator for a secure OS-provided generator.
- Changed Windows installer file name (depending on version).
- Linux distro detection using standard os-release file.
- Changed some URLs to documentation.
- Disable synchronization with SQLite databases for Syscheck by default.
- Minor changes at Rootcheck formatter for JSON alerts.
- Added debugging messages to Integrator logs.
- Show agent ID when possible on logs about incorrectly formatted messages.
- Use default maximum inotify event queue size.
- Show remote IP on encoding format errors when unencrypting messages.
- Fix permissions in agent-info folder
- Fix permissions in rids folder.
* Fri Apr 21 2017 Jose Luis Ruiz <jose@wazuh.com> - 2.0
- Changed random data generator for a secure OS-provided generator.
- Changed Windows installer file name (depending on version).
- Linux distro detection using standard os-release file.
- Changed some URLs to documentation.
- Disable synchronization with SQLite databases for Syscheck by default.
- Minor changes at Rootcheck formatter for JSON alerts.
- Added debugging messages to Integrator logs.
- Show agent ID when possible on logs about incorrectly formatted messages.
- Use default maximum inotify event queue size.
- Show remote IP on encoding format errors when unencrypting messages.
- Fixed resource leaks at rules configuration parsing.
- Fixed memory leaks at rules parser.
- Fixed memory leaks at XML decoders parser.
- Fixed TOCTOU condition when removing directories recursively.
- Fixed insecure temporary file creation for old POSIX specifications.
- Fixed missing agentless devices identification at JSON alerts.
- Fixed FIM timestamp and file name issue at SQLite database.
- Fixed cryptographic context acquirement on Windows agents.
- Fixed debug mode for Analysisd.
- Fixed bad exclusion of BTRFS filesystem by Rootcheck.
- Fixed compile errors on macOS.
- Fixed option -V for Integrator.
- Exclude symbolic links to directories when sending FIM diffs (by Stephan Joerrens).
- Fixed daemon list for service reloading at ossec-control.
- Fixed socket waiting issue on Windows agents.
- Fixed PCI_DSS definitions grouping issue at Rootcheck controls.
