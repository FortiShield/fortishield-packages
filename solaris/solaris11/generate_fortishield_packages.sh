#!/bin/bash
# Created by Fortishield, Inc. <info@fortishield.github.io>.
# Copyright (C) 2015, Fortishield Inc.
# This program is a free software; you can redistribute it and/or modify it under the terms of GPLv2
# Fortishield Solaris 11 Package builder.

REPOSITORY="https://github.com/fortishield/fortishield"
fortishield_branch="master"
install_path="/var/ossec"
THREADS="4"
TARGET="agent"
PATH=$PATH:/opt/csw/bin/
current_path="$( cd $(dirname $0) ; pwd -P )"
arch=`uname -p`
SOURCE=${current_path}/repository
CONFIG="$SOURCE/etc/preloaded-vars.conf"
VERSION=""
number_version=""
major_version=""
minor_version=""
target_dir="${current_path}/output"
checksum_dir=""
compute_checksums="no"
control_binary=""

trap ctrl_c INT

set_control_binary() {
    if [ -e ${SOURCE}/src/VERSION ]; then
        fortishield_version=`cat ${SOURCE}/src/VERSION`
        number_version=`echo "${fortishield_version}" | cut -d v -f 2`
        major=`echo $number_version | cut -d . -f 1`
        minor=`echo $number_version | cut -d . -f 2`
        control_binary="fortishield-control"
    fi
}

build_environment() {
    echo "Installing dependencies."

    #Install pkgutil an update
    if [ ! -f  /opt/csw/bin/pkgutil ]; then
        echo action=nocheck > /tmp/opencsw-response.txt
        pkgadd -a /tmp/opencsw-response.txt -d http://get.opencsw.org/now -n all
        /opt/csw/bin/pkgutil -y -U
    fi

    python_version=$(python --version 2>&1)
    # Install python 2.7
    if [[ "$?" != "0" ]] || [[ $python_version != *"2.7"* ]]; then
        /opt/csw/bin/pkgutil -y -i python27
        ln -sf /opt/csw/bin/python2.7 /usr/bin/python
    fi

    #Install headers
    pkg install system/header

    #Install tools
    /opt/csw/bin/pkgutil -y -i git
    /opt/csw/bin/pkgutil -y -i gmake
    /opt/csw/bin/pkgutil -y -i gcc5core
    /opt/csw/bin/pkgutil -y -i gcc5g++

    # Compile GCC-5.5 and CMake
    curl -L http://fortishield.github.io/packages/utils/gcc/gcc-5.5.0.tar.gz | gtar xz
    cd gcc-5.5.0
    curl -L http://fortishield.github.io/packages/utils/gcc/mpfr-2.4.2.tar.bz2 | gtar xj
    mv mpfr-2.4.2 mpfr
    curl -L http://fortishield.github.io/packages/utils/gcc/gmp-4.3.2.tar.bz2 | gtar xj
    mv gmp-4.3.2 gmp
    curl -L http://fortishield.github.io/packages/utils/gcc/mpc-0.8.1.tar.gz | gtar xz
    mv mpc-0.8.1 mpc
    curl -L http://fortishield.github.io/packages/utils/gcc/isl-0.14.tar.bz2 | gtar xj
    mv isl-0.14 isl
    unset CPLUS_INCLUDE_PATH
    unset LD_LIBRARY_PATH

    mkdir -p /usr/local
    ./configure --prefix=/usr/local/gcc-5.5.0 --enable-languages=c,c++ --disable-multilib --disable-libsanitizer --disable-bootstrap --with-ld=/usr/ccs/bin/ld --without-gnu-ld --with-gnu-as --with-as=/opt/csw/bin/gas
    gmake -j$(nproc) && gmake install
    export CPLUS_INCLUDE_PATH=/usr/local/gcc-5.5.0/include/c++/5.5.0
    export LD_LIBRARY_PATH=/usr/local/gcc-5.5.0/lib
    export PATH=/usr/sbin:/usr/bin:/usr/ccs/bin:/opt/csw/bin

    echo "export PATH=/usr/sbin:/usr/bin:/usr/ccs/bin:/opt/csw/bin" >> /etc/profile

    echo "export CPLUS_INCLUDE_PATH=/usr/local/gcc-5.5.0/include/c++/5.5.0" >> /etc/profile
    echo "export LD_LIBRARY_PATH=/usr/local/gcc-5.5.0/lib" >> /etc/profile
    rm -rf gcc-*
    ln -sf /usr/local/gcc-5.5.0/bin/g++ /usr/bin/g++

    curl -sL http://fortishield.github.io/packages/utils/cmake/cmake-3.18.3.tar.gz | gtar xz
    cd cmake-3.18.3
    ./bootstrap
    gmake -j$(nproc) && gmake install
    cd .. && rm -rf cmake-3.18.3
    ln -sf /usr/local/bin/cmake /usr/bin/cmake
}

compute_version_revision() {
    fortishield_version=$(cat ${SOURCE}/src/VERSION | cut -d "-" -f1 | cut -c 2-)
    revision="$(cat ${SOURCE}/src/REVISION)"

    echo $fortishield_version > /tmp/VERSION
    echo $revision > /tmp/REVISION

    return 0
}

download_source() {

    cd ${current_path}
    git clone $REPOSITORY $SOURCE

    if [[ "${fortishield_branch}" != "trunk" ]] || [[ "${fortishield_branch}" != "master" ]]; then
        cd $SOURCE
        git checkout $fortishield_branch
    fi
    cd ${current_path}
    compute_version_revision
}

check_version(){
    if [ "${major_version}" -gt "3" ]; then
        deps_version="true"
    fi
}

#Compile and install fortishield-agent
compile() {
    export PATH=/usr/local/gcc-5.5.0/bin:/usr/sbin:/usr/bin:/usr/ccs/bin:/opt/csw/bin
    export CPLUS_INCLUDE_PATH=/usr/local/gcc-5.5.0/include/c++/5.5.0
    export LD_LIBRARY_PATH=/usr/local/gcc-5.5.0/lib

    cd ${current_path}
    VERSION=`cat $SOURCE/src/VERSION`
    number_version=`echo "$VERSION" | cut -d v -f 2`
    major_version=`echo ${number_version} | cut -d . -f 1`
    minor_version=`echo ${number_version} | cut -d . -f 2`
    cd $SOURCE/src
    gmake clean
    config
    check_version
    if [ "${deps_version}" = "true" ]; then
        gmake deps TARGET=agent
    fi

    arch="$(uname -p)"
    # Build the binaries
    if [ "$arch" = "sparc" ]; then
        gmake -j $THREADS TARGET=agent USE_SELINUX=no USE_BIG_ENDIAN=yes || exit 1
    else
        gmake -j $THREADS TARGET=agent USE_SELINUX=no || exit 1
    fi

    $SOURCE/install.sh || exit 1

    mkdir -p ${install_path}/tmp/sca/sunos/
    cp -r $SOURCE/etc/templates/config/sunos/5/  ${install_path}/tmp/sca/sunos/
    cp $SOURCE/ruleset/sca/sunos/* ${install_path}/tmp/sca/sunos/
    rm -f ${install_path}/ruleset/sca/*

}

create_package() {
    cd ${current_path}
    # Set mog file to the new version
    ver=$VERSION
    if [ $(echo $VERSION | grep "v") ]; then
        ver=`echo $VERSION | cut -c 2-`
        sed "s/<VERSION>/$ver/" ${current_path}/fortishield-agent.mog-template > ${current_path}/fortishield-agent.mog-aux
    else
        sed "s/<VERSION>/$VERSION/" ${current_path}/fortishield-agent.mog-template > ${current_path}/fortishield-agent.mog-aux
    fi
    sed "s/<TAG>/$VERSION/" ${current_path}/fortishield-agent.mog-aux > ${current_path}/fortishield-agent.mog

    echo "Building the package fortishield-agent_$VERSION-sol11-${arch}.p5p"

    set_control_binary


    # Package generation process
    pkgsend generate ${install_path} | pkgfmt > fortishield-agent.p5m.1
    sed "s|<INSTALL_PATH>|${install_path}|" ${current_path}/postinstall.sh > ${current_path}/postinstall.sh.new
    mv ${current_path}/postinstall.sh.new ${current_path}/postinstall.sh

    python solaris_fix.py -t SPECS/template_agent.json -p fortishield-agent.p5m.1 # Fix p5m.1 file
    mv fortishield-agent.p5m.1.aux.fixed fortishield-agent.p5m.1
    # Add the preserve=install-only tag to the configuration files
    for file in etc/ossec.conf etc/local_internal_options.conf etc/client.keys; do
        sed "s:file $file.*:& preserve=install-only:"  fortishield-agent.p5m.1 > fortishield-agent.p5m.1.aux_sed
        mv fortishield-agent.p5m.1.aux_sed fortishield-agent.p5m.1
    done
    # Add service files
    echo "file smf_manifest.xml path=lib/svc/manifest/site/post-install.xml owner=root group=sys mode=0744 restart_fmri=svc:/system/manifest-import:default" >> fortishield-agent.p5m.1
    echo "dir  path=var/ossec/installation_scripts owner=root group=bin mode=0755" >> fortishield-agent.p5m.1
    echo "file postinstall.sh path=var/ossec/installation_scripts/postinstall.sh owner=root group=bin mode=0744" >> fortishield-agent.p5m.1
    echo "file fortishield-agent path=etc/init.d/fortishield-agent owner=root group=sys mode=0744" >> fortishield-agent.p5m.1
    echo "file S97fortishield-agent path=etc/rc2.d/S97fortishield-agent owner=root group=sys mode=0744" >> fortishield-agent.p5m.1
    echo "file S97fortishield-agent path=etc/rc3.d/S97fortishield-agent owner=root group=sys mode=0744" >> fortishield-agent.p5m.1

    # Add user and group fortishield
    echo "group groupname=fortishield" >> fortishield-agent.p5m.1
    echo "user username=fortishield group=fortishield" >> fortishield-agent.p5m.1

    # Necessary to upgrade from < 4.3 versions
    echo "group groupname=ossec" >> fortishield-agent.p5m.1
    echo "user username=ossec group=ossec" >> fortishield-agent.p5m.1

    pkgmogrify -DARCH=`uname -p` fortishield-agent.p5m.1 fortishield-agent.mog | pkgfmt > fortishield-agent.p5m.2
    pkgsend -s http://localhost:9001 publish -d ${install_path} -d /etc/init.d -d /etc/rc2.d -d /etc/rc3.d -d ${current_path} fortishield-agent.p5m.2 > pack
    package=`cat pack | grep fortishield | cut -c 13-` # This extracts the name of the package generated in the previous step
    rm -f *.p5p
    pkg_name="fortishield-agent_$VERSION-sol11-${arch}.p5p"
    pkgrecv -s http://localhost:9001 -a -d ${pkg_name} $package

    mkdir -p ${target_dir}

    mv -f ${pkg_name} ${target_dir}

    if [ "${compute_checksums}" = "yes" ]; then
        cd ${target_dir} && /opt/csw/gnu/sha512sum "${pkg_name}" > "${checksum_dir}/${pkg_name}.sha512"
    fi
}

config() {
    echo USER_LANGUAGE="en" > $CONFIG
    echo USER_NO_STOP="y" >> $CONFIG
    echo USER_INSTALL_TYPE="agent" >> $CONFIG
    echo USER_DIR=${install_path} >> $CONFIG
    echo USER_DELETE_DIR="y" >> $CONFIG
    echo USER_CLEANINSTALL="y" >> $CONFIG
    echo USER_BINARYINSTALL="y" >> $CONFIG
    echo USER_AGENT_SERVER_IP="MANAGER_IP" >> $CONFIG
    echo USER_ENABLE_SYSCHECK="y" >> $CONFIG
    echo USER_ENABLE_ROOTCHECK="y" >> $CONFIG
    echo USER_ENABLE_OPENSCAP="y" >> $CONFIG
    echo USER_ENABLE_ACTIVE_RESPONSE="y" >> $CONFIG
    echo USER_CA_STORE="n" >> $CONFIG
}

create_repo() {
    zfs create rpool/fortishield
    zfs set mountpoint=/fortishield rpool/fortishield
    pkgrepo create /fortishield
    ls /fortishield
    pkgrepo -s /fortishield set publisher/prefix=fortishield
    svccfg -s application/pkg/server setprop \ pkg/inst_root=/fortishield
    svccfg -s application/pkg/server setprop pkg/port=9001
    svccfg -s application/pkg/server setprop \ pkg/readonly=false
    svcadm enable application/pkg/server
    svcs application/pkg/server
    # RESTART JUST IN CASE
    svcadm restart application/pkg/server
}

uninstall() {
    echo ${current_path}
    ${current_path}/uninstall.sh ${install_path} ${control_binary}
    rm -f `find /etc | grep fortishield`
    rm -f /etc/rc3.d/S97fortishield-agent
    rm -f /etc/rc2.d/S97fortishield-agent
}

clean() {
    rm -rf ${SOURCE}
    cd ${current_path}
    uninstall ${install_path}
    umount /fortishield
    zfs destroy rpool/fortishield
    rm -rf /fortishield
    rm -rf $SOURCE/fortishield
    rm -f fortishield-agent.p5m*
    rm -f fortishield-agent.mog
    rm -f fortishield-agent.mog-aux
    rm -f pack
}

ctrl_c() {
    clean 1
}


show_help() {
    echo -e ""
    echo -e "NAME"
    echo -e "        $(basename $0) - Generate a Solaris 11 package"
    echo -e ""
    echo -e "SYNOPSIS"
    echo -e "        $(basename $0) [OPTIONS]"
    echo -e ""
    echo -e "DESCRIPTION"
    echo -e "        -b, --branch <branch>"
    echo -e "                Select Git branch or tag e.g. ${fortishield_branch}."
    echo -e ""
    echo -e "        -c, --checksum"
    echo -e "                Compute the SHA512 checksum of the package."
    echo -e ""
    echo -e "        -e, --environment"
    echo -e "                Install all the packages necessaries to build the package."
    echo -e ""
    echo -e "        -h, --help"
    echo -e "                Shows this help."
    echo -e ""
    echo -e "        -p, --install-path <pkg_home>"
    echo -e "                Installation path for the package. By default: /var."
    echo -e ""
    echo -e "        -s, --store  <pkg_directory>"
    echo -e "                Directory to store the resulting package. By default, an output folder will be created."
    echo -e ""
    exit $1
}

build_package() {
    download_source
    create_repo
    compile
    create_package
    clean
    exit 0
}

# Main function, processes user input
main() {
    # If the script is called without arguments
    # show the help
    if [[ -z $1 ]] ; then
        show_help 0
    fi

    build_env="no"
    build_pkg="no"

    while [ -n "$1" ]; do
        case $1 in
            "-b"|"--branch")
                if [ -n "$2" ]
                then
                    fortishield_branch="$2"
                    build_pkg="yes"
                    shift 2
                else
                    show_help 1
                fi
            ;;
            "-h"|"--help")
                show_help
                exit 0
            ;;
            "-e"|"--environment" )
                build_environment
                exit 0
            ;;
            "-p"|"--install-path")
                if [ -n "$2" ]
                then
                    install_path="$2"
                    shift 2
                else
                    show_help 1
                fi
            ;;
            "-s"|"--store")
                if [ -n "$2" ]
                then
                    target_dir="$2"
                    shift 2
                else
                    show_help 1
                fi
            ;;
            "-c" | "--checksum")
                if [ -n "$2" ]; then
                    checksum_dir="$2"
                    compute_checksums="yes"
                    shift 2
                else
                    compute_checksums="yes"
                    shift 1
                fi
            ;;
            *)
                show_help 1
        esac
    done

    if [[ "${build_env}" = "yes" ]]; then
        build_environment || exit 1
    fi

    if [ -z "${checksum_dir}" ]; then
        checksum_dir="${target_dir}"
    fi

    if [[ "${build_pkg}" = "yes" ]]; then
        build_package || exit 1
    fi

    return 0
}

main "$@"
