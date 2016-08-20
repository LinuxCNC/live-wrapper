#!/bin/bash

set -e

rootdir=$1

# common needs rootdir to already be defined.
. /usr/share/vmdebootstrap/common/customise.lib

trap cleanup 0

mount_support
disable_daemons
# FIXME: pass the specified build mirror.
# MUST be available over http, file:// will not work inside the VM chroot
prepare_apt_source 'http://ftp.debian.org/debian/' 'stretch'

chroot ${rootdir} apt-get -y install initramfs-tools live-boot live-config ${LWR_TASK_PACKAGES} ${LWR_EXTRA_PACKAGES} task-laptop task-english libnss-myhostname

echo "blacklist bochs-drm" > $rootdir/etc/modprobe.d/qemu-blacklist.conf

replace_apt_source

