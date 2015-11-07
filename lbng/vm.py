"""
live-build-ng - Live-Build NG
(C) Iain R. Learmonth 2015 <irl@debian.org>
See COPYING for terms of usage, modification and redistribution.

lbng/vm.py - vmdebootstrap helpers
"""

from vmdebootstrap.base import runcmd

class VMDebootstrap:

    def __init__(distribution, mirror=None):
        self.args = ["vmdebootstrap",
            "--sudo", "--lock-root-password",
            "--enable-dhcp", "--configure-apt", "--log", "vmdebootstrap.log"
            "--squash=cdroot/live/", "--log-level", "debug",
            "--customize", "hooks/customise.sh"]

        self.args.extend(["--distribution", self.settings['distribution']])

        if mirror is not None:
            self.args.extend(["--mirror", self.settings['mirror'])

    def run(self):
        runcmd(args)

def detect_kernels():
    versions = []
    filenames = os.listdir(directory)
    for filename in filenames:
        if filename[0:8] == "vmlinuz-":
            versions.append(filename[8:])
    return versions
