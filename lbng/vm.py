"""
lbng - Live Build Next Generation
(C) Iain R. Learmonth 2015 <irl@debian.org>
See COPYING for terms of usage, modification and redistribution.

lbng/vm.py - vmdebootstrap helpers
"""

from vmdebootstrap.base import runcmd

def vmdebootstrap(args):
    """
    Call vmdebootstrap.
    """
    runcmd(args)

