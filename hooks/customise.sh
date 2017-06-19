#!/bin/bash

set -e

rootdir=$1

# common needs rootdir to already be defined.
. /usr/share/vmdebootstrap/common/customise.lib

trap cleanup 0

mount_support
disable_daemons

mv ${rootdir}/etc/resolv.conf ${rootdir}/etc/resolv.conf.bak
cat /etc/resolv.conf > ${rootdir}/etc/resolv.conf

prepare_apt_source "${LWR_MIRROR}" "${LWR_DISTRIBUTION}"

${LWR_EXTRA_PACKAGES} task-laptop task-english libnss-myhostname
for PKG in ${FIRMWARE_PKGS}; do
    echo "$PKG        $PKG/license/accepted       boolean true" | \
       chroot ${rootdir} debconf-set-selections
done

chroot ${rootdir} apt-get -q -y install initramfs-tools live-boot live-config ${LWR_TASK_PACKAGES} ${LWR_EXTRA_PACKAGES} ${LWR_FIRMWARE_PACKAGES} task-laptop task-english libnss-myhostname >> vmdebootstrap.log 2>&1

# Temporary fix for #843983
chroot ${rootdir} chmod 755 /

echo "blacklist bochs-drm" > $rootdir/etc/modprobe.d/qemu-blacklist.conf

replace_apt_source

mv ${rootdir}/etc/resolv.conf ${rootdir}/etc/resolv.conf.bak

