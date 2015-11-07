"""
live-build-ng - Live-Build NG
(C) Iain R. Learmonth 2015 <irl@debian.org>
See COPYING for terms of usage, modification and redistribution.

lbng/vm.py - vmdebootstrap helpers
"""

from vmdebootstrap.base import runcmd

def detect_kernels():
    versions = []
    filenames = os.listdir(directory)
    for filename in filenames:
        if filename[0:8] == "vmlinuz-":
            versions.append(filename[8:])
    return versions

def vmdebootstrap(args):
    """
    Call vmdebootstrap.
    """
    runcmd(args)

