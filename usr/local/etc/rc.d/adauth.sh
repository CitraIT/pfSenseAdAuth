#!/bin/sh
# This file was automatically generated
# by the pfSense service handler.

rc_start() {
        #ADAUTH_ENABLED=$(/usr/local/sbin/read_xml_tag.sh string installedpackages/adauth/config/enable_adauth)
        #if [ "$ADAUTH_ENABLED}" != "on" ]; then
        #       exit 0
        #elif [ -z "`/bin/ps auxw | /usr/bin/grep "adauth.py " | /usr/bin/awk '{print $2}'`" ]; then
                /usr/local/sbin/adauth.py
        #fi

}

rc_stop() {
        /usr/local/sbin/adauth.py -k kill
        # Just to be sure...
        sleep 3
        /usr/bin/killall -9 adauth.py 2>/dev/null
        /usr/bin/killall adauth.py 2>/dev/null

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

