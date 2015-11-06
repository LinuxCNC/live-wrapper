#!/bin/bash

set -e

rootdir=$1

# common needs rootdir to already be defined.
. /home/irl/debian/vmdebootstrap/common/customise.lib

trap cleanup 0

mount_support
disable_daemons
# prepare_apt_source

chroot ${rootdir} apt-get -y --force-yes install initramfs-tools live-boot live-config xserver-xorg task-xfce-desktop

echo "blacklist bochs-drm" > $rootdir/etc/modprobe.d/qemu-blacklist.conf

