#!/bin/sh
# This file was automatically generated
# by the pfSense service handler.

rc_start() {
        #ADAUTH_ENABLED=$(/usr/local/sbin/read_xml_tag.sh string installedpackages/adauth/config/enable_adauth)
        #if [ "$ADAUTH_ENABLED}" != "on" ]; then
        #       exit 0
        #elif [ -z "`/bin/ps auxw | /usr/bin/grep "adauth.py " | /usr/bin/awk '{print $2}'`" ]; then
        echo "starting adauth daemon..."
        /usr/local/sbin/adauth.py
        echo "done"
        #fi

}

rc_stop() {
        target_pid=$(cat /var/run/adauth.pid)
        if [ "${target_pid}" == "" ]
        then
                echo "no pid found for adauth"
        else
                kill $target_pid
        fi
        # Just to be sure...
        sleep 3
        #ps auxwww | grep -iE adauth | grep -v grep |  awk '{print $2}' | xargs -I@ kill @

}

case $1 in
        start)
                rc_start
                ;;
        stop)
                rc_stop
                ;;
        restart)
                rc_stop
                rc_start
                ;;
esac
