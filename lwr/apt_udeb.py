# live-wrapper - Wrapper for vmdebootstrap for creating live images
# (C) 2016 Neil Williams <codehelp@debian.org>
# See COPYING for terms of usage, modification and redistribution.
#
# lwr/apt.py - .apt folder helpers

# depends debian-archive-keyring vmdebootstrap python-apt

import os
import sys
import shutil
import tempfile
import apt
import apt_pkg
from vmdebootstrap.base import copy_files

# handle a list of package names (udebs)
# handle a list of excluded package names
# handle a supplementary apt source for local udebs
# unique sort the combined package names


class AptUdebDownloader(object):

    def __init__(self, destdir):
        self.architecture = 'armhf'
        self.mirror = None
        self.suite = None
        self.components = [
            'main/debian-installer', 'contrib/debian-installer',
            'non-free/debian-installer']
        self.dirlist = []
        self.cache = None
        self.destdir = destdir

    def prepare_apt(self):
        if not self.suite or not self.mirror:
            raise RuntimeError("Misconfiguration: no suite or mirror set")
        state_dir = tempfile.mkdtemp()
        os.mkdir(os.path.join(state_dir, 'lists'))
        self.dirlist.append(state_dir)
        cache_dir = tempfile.mkdtemp()
        os.makedirs(os.path.join(cache_dir, 'archives', 'partial'))
        self.dirlist.append(cache_dir)
        etc_dir = tempfile.mkdtemp()
        os.mkdir(os.path.join(etc_dir, 'apt.conf.d'))
        os.mkdir(os.path.join(etc_dir, 'preferences.d'))
        os.mkdir(os.path.join(etc_dir, 'trusted.gpg.d'))
        copy_files(
            '/etc/apt/trusted.gpg.d',
            os.path.join(etc_dir, 'trusted.gpg.d')
        )
        with open(os.path.join(etc_dir, 'sources.list'), 'w') as sources:
            sources.write('deb %s %s %s\n' % (
                self.mirror, self.suite, ' '.join(self.components)))
        self.dirlist.append(etc_dir)
        updates = {
            'APT::Architecture': self.architecture,
            'APT::Architectures': self.architecture,
            'Dir::State': state_dir,
            'Dir::Cache': cache_dir,
            'Dir::Etc': etc_dir,
        }
        for key, value in updates.items():
            apt_pkg.config[key] = value
        self.cache = apt.cache.Cache()
        try:
            self.cache.update()
            self.cache.open()
        except apt.cache.FetchFailedException as exc:
            raise RuntimeError('Unable to update cache: %s' % exc)
        if not os.path.exists(self.destdir):
            raise RuntimeError('Destination directory %s does not exist' % self.destdir)

    def download_udebs(self, exclude_list):
        if not self.cache:
            raise RuntimeError('No cache available.')
        for pkg_name in self.cache.keys():
            if pkg_name in exclude_list:
                continue
            pkg = self.cache[pkg_name]
            if not hasattr(pkg, 'versions'):
                continue
            if len(pkg.versions) > 1:
                pkg.version_list.sort(apt_pkg.version_compare)
                version = pkg.version_list[0]
                print("Multiple versions returned for %s - using newest: %s" % (pkg_name, pkg.version_list[0]))
            else:
                version = pkg.versions[0]
            if not version.uri:
                continue
            try:
                version.fetch_binary(destdir=self.destdir)
            except TypeError as exc:
                continue
            except apt.package.FetchError as exc:
                raise RuntimeError('Unable to fetch %s: %s' % (pkg_name, exc))

    def clean_up_apt(self):
        for clean in self.dirlist:
            shutil.rmtree(clean)


def main():
    apt_udeb = AptUdebDownloader('/tmp/test/')
    apt_udeb.mirror = "file:///home/neil/mirror/debian"
    apt_udeb.architecture = 'amd64'
    apt_udeb.suite = 'stable'
    apt_udeb.prepare_apt()
    apt_udeb.download_udebs([])
    apt_udeb.clean_up_apt()


if __name__ == '__main__':
    sys.exit(main())
