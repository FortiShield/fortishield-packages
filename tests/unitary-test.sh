trap clean SIGINT

function startDocker() {

    if [ -n "$(ps -e | egrep ^\ *1\ .*systemd$)" ]; then
        eval "systemctl daemon-reload"
        eval "systemctl enable docker.service"
        eval "systemctl start docker.service"
        if [ "$?" != 0 ]; then
            echo "Docker could not be started"
            exit 1
        else 
            echo "Docker started correctly"
        fi
    elif [ -n "$(ps -e | egrep ^\ *1\ .*init$)" ]; then
        eval "chkconfig docker on"
        eval "service docker start"
        eval "/etc/init.d/docker start"
        if [ "$?" != 0 ]; then
            echo "Docker could not be started"
            exit 1
        else 
            echo "Docker started correctly"
        fi
    elif [ -x /etc/rc.d/init.d/docker ] ; then
        eval "/etc/rc.d/init.d/docker start"
        if [ "$?" != 0 ]; then
            echo "Docker could not be started"
            exit 1
        else 
            echo "Docker started correctly"
        fi
    else
        echo "Docker could not be started. No system manager found"
        exit 1
    fi

}

function createDocker() {

    if [ ! -f ./Dockerfile ]; then
        echo "Error: No Dockerfile found to create the environment"
    fi

    image_name="testing-img"
    if [ -z "$(docker images | grep $image_name)" ]; then
        eval "docker build -t $image_name . >/dev/null"
    fi
    container_name="testing-container"
    eval "docker run -d -t --name $container_name $image_name /bin/bash >/dev/null"
    container_id="$( docker ps -a | grep $container_name | awk '{ print $1 }' )"
    eval "docker cp bach.sh $container_id:/tests/bach.sh >/dev/null"
}

function testCommon() {
    eval "docker cp unattended/test-common.sh $container_id:/tests/unattended/test-common.sh"
    eval "mkdir -p temp/"
    eval "cp ../unattended_installer/install_functions/opendistro/common.sh temp/"
    eval "docker cp temp/common.sh $container_id:/tests/unattended/common.sh"
    eval "docker exec $container_name bash -lc \"cd /tests/unattended && bash test-common.sh\" "
    echo -e "All unitary tests for the functions in common.sh finished.\n"
}

function testChecks() {
    eval "docker cp unattended/test-checks.sh $container_id:/tests/unattended/test-checks.sh"
    eval "mkdir -p temp/"
    eval "cp ../unattended_installer/install_functions/opendistro/checks.sh temp/"
    eval "docker cp temp/checks.sh $container_id:/tests/unattended/checks.sh"
    eval "docker exec $container_name bash -lc \"cd /tests/unattended && bash test-checks.sh\" "
    echo -e "All unitary tests for the functions in checks.sh finished.\n"
}

function testWazuh() {
    eval "docker cp unattended/test-wazuh.sh $container_id:/tests/unattended/test-wazuh.sh"
    eval "mkdir -p temp/"
    eval "cp ../unattended_installer/install_functions/opendistro/wazuh.sh temp/"
    eval "docker cp temp/wazuh.sh $container_id:/tests/unattended/wazuh.sh"
    eval "docker exec $container_name bash -lc \"cd /tests/unattended && bash test-wazuh.sh\" "
    echo -e "All unitary tests for the functions in wazuh.sh finished.\n"
}

function clean() {
    eval "docker stop $container_name"
    eval "docker rm $container_name"
    eval "rm -rf temp/"
}

main() {

    if [ -z "${1}" ]; then
        all_tests=1
    fi

    while [ -n "${1}" ]
    do
        case "${1}" in
            "common")
                common=1
                shift 1
                ;;
            "checks")
                checks=1
                shift 1
                ;;
            "wazuh")
                wazuh=1
                shift 1
                ;;
            *)
                echo "Unknow option: ${1}"
                getHelp
        esac
    done

    if [ "$EUID" -ne 0 ]; then
        echo "Error: This script must be run as root."
        exit 1
    fi

    if [ -z "$(command -v docker)" ]; then
        echo "Error: Docker must be installed in the system to run the tests"
        exit 1
    fi

    startDocker
    createDocker
    if [ -n "$all_tests" ] || [ -n "$common" ]; then
        testCommon
    fi
    if [ -n "$all_tests" ] || [ -n "$checks" ]; then
        testChecks
    fi
    if [ -n "$all_tests" ] || [ -n "$wazuh" ]; then
        testWazuh
    fi
    clean
}

main $@