# live-wrapper - Wrapper for vmdebootstrap for creating live images
# (C) Iain R. Learmonth 2015 <irl@debian.org>
# See COPYING for terms of usage, modification and redistribution.
#
# lwr/vm.py - vmdebootstrap helpers

"""
The lwr.vm module provides helpers for calling vmdebootstrap as part of the
image creation process.

Directory listing of /live/
filesystem.packages
filesystem.packages-remove
filesystem.squashfs
initrd.img
vmlinuz

.. note::
    This module requires that the vmdebootstrap modules be available in the
    Python path.
"""

import os
from vmdebootstrap.base import runcmd

# pylint: disable=superfluous-parens,missing-docstring,too-few-public-methods

class VMDebootstrap(object):

    def __init__(self, distribution, architecture, mirror=None, cdroot='/tmp/'):
        self.cdroot = cdroot
        # FIXME: The customise script needs to be specified in the command line
        # arguments, falling back to /usr/share/vmdebootstrap/hooks/customise.sh
        # if no script is specified and hooks/customise.sh does not exist in
        # the current directory.
        self.args = ["vmdebootstrap",
                     "--sudo", "--lock-root-password",
                     "--no-systemd-networkd",
                     "--arch", architecture,
                     "--enable-dhcp", "--configure-apt", "--verbose",
                     "--log", "vmdebootstrap.log",
                     "--squash=%s" % os.path.join(self.cdroot, 'live'),
                     "--log-level", "debug"]
        self.args.extend(["--distribution", distribution])
        self.args.extend(["--mirror", mirror])
        # FIXME: apt-mirror is for what the booted image will use
        # this needs to be accessible over http://, not just file://
        # FIXME: this should be declared in the command line args for lwr
        self.args.extend(["--apt-mirror", 'http://ftp.debian.org/debian/'])

        # FIXME: Logging should happen here
        if os.path.exists(os.path.join(".", "hooks", "customise.sh")):
            self.args.extend(["--customize", "hooks/customise.sh"])
        elif os.path.exists("/usr/share/live-wrapper/customise.sh"):
            self.args.extend(["--customize", "/usr/share/live-wrapper/customise.sh"])
        else:
            raise cliapp.AppException("Could not locate customise.sh")

    def run(self):
        print(' '.join(self.args))
        runcmd(self.args)  # FIXME: may want to use a method which prints output in realtime
        print('vmdebootstrap complete')


def detect_kernels(cdroot):
    versions = []
    filenames = os.listdir(os.path.join(cdroot, "live"))
    for filename in filenames:
        if filename[0:8] == "vmlinuz-":
            versions.append(filename[8:])
    return versions
