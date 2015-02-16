import os
import subprocess
import logging

__version__ = '0.1'


FORMAT = '%(levelname)s %(lineno)d %(message)s'
logging.basicConfig(format=FORMAT)


class File(object):
    """Given mappings and a file, figure everything out."""

    def __init__(self, mappings, push, pull, path, verbose=False):
        self._be_quiet = not verbose
        self._from_root = None
        self.quietly('mappings %s' % mappings)
        assert mappings
        self.mappings = mappings
        self.quietly('not push or not pull')
        assert not push or not pull
        self.push = push
        self.pull = pull
        self.path = path
        assert self.is_from or self.is_to, 'Cannot resolve path: %s' % path

    def quietly(self, some_string):
        if not self._be_quiet:
            print some_string

    @property
    def from_root(self):
        """What is the path of the source's root."""
        if self._from_root is None:
            roots = set()
            if not self.pull:
                for root in self.mappings:
                    self.quietly('does %s start with %s ?' % (
                        self.full_path, root))
                    if self.full_path.startswith(root):
                        roots.add(root)
                        self.quietly('found %s' % root)
                    self.quietly('does %s start with %s ?' % (
                        self.path, root))
                    if self.path.startswith(root):
                        roots.add(root)
                        self.quietly('found %s' % root)
            if not self.push:
                for root, targets in self.mappings.items():
                    for target in targets:
                        self.quietly('does %s start with %s ?' % (
                            self.full_path, target))
                        if self.full_path.startswith(target):
                            roots.add(root)
                            self.quietly('found root %s for target %s' % (
                                root, target))
                        self.quietly(
                            'does %s start with %s ?' % (self.path, target))
                        if self.path.startswith(target):
                            roots.add(root)
                            self.quietly('found root %s for target %s' % (
                                root, target))
            assert roots, 'No root for %s in %s' % (self.path, self.mappings)
            self._from_root = max(roots, key=len)
        assert self._from_root
        return self._from_root

    @property
    def to_roots(self):
        """Where to send the file."""
        return self.mappings[self.from_root]

    @property
    def is_backed(self):
        """Has the file already been backed up."""
        return all(os.path.exists(to_path) for to_path in self.to_paths)

    @property
    def is_from(self):
        """Is the file in the source path."""
        self.quietly('is %s in %s ?' % (self.from_root, self.path))
        return not self.pull and self.from_root in self.path

    @property
    def is_to(self):
        """Is the file in a destination path."""
        self.quietly('is any %s in %s ?' % (self.to_roots, self.path))
        return not self.push and (
            any(root in self.path for root in self.to_roots)
            or any(root in self.full_path for root in self.to_roots))

    @property
    def is_remote(self):
        """Is the file likely to be a remote file?"""
        return self.path.count(':') == 1 and not os.path.exists(self.path)

    @property
    def exists(self):
        """Does the file exist."""
        return self.is_remote or os.path.exists(self.path)

    @property
    def full_path(self):
        """The fullest path we can generate"""
        if self.is_remote:
            return self.path
        else:
            return os.path.abspath(self.path)

    @property
    def from_path(self):
        """Where is the file in the source path."""
        is_dir = os.path.isdir(self.full_path)
        if self.is_from:
            self.quietly('file is from')
            path = self.full_path
        elif self.is_to:
            self.quietly('file is to')
            to_root = [x for x in self.to_roots
                       if self.path.startswith(x)
                       or self.full_path.startswith(x)][0]
            self.quietly('replacing %s with %s in %s' % (
                to_root, self.from_root, self.full_path))
            path = self.full_path.replace(to_root, self.from_root)
        if is_dir:
            if '/' != path[-1]:
                path = path + '/'
        return path

    @property
    def from_path_remote(self):
        return self.from_path.count(':') == 1

    @property
    def from_path_exists(self):
        """Does the path we are trying to copy from even exist?"""
        return self.from_path_remote or os.path.exists(self.from_path)

    @property
    def to_paths(self):
        """Where is the file in the destination path."""
        return [self.from_path.replace(self.from_root, to_root)
                for to_root in self.to_roots]

    @property
    def is_dir(self):
        """Is the file a directory."""
        return self.exists and os.path.exists(self.from_path)

    def mkdir(self):
        """Create all directories in the dests as needed."""
        for to_path in self.to_paths:
            if self.is_backed:
                print 'Not creating dir for %s' % to_path
            else:
                if self.is_dir:
                    dirname = to_path
                else:
                    dirname = os.path.dirname(to_path)
                print 'Making dir: %s' % dirname
                if os.path.exists(dirname):
                    print 'Exists: %s' % dirname
                else:
                    print 'Creating %s' % dirname
                    os.makedirs(dirname)

    def backup(self):
        """rsync the file correctly."""
        # self.mkdir()
        assert self.from_path_exists, '%s does not exist' % self.from_path
        self.quietly('from_path %s to_paths %s'
                     % (self.from_path, self.to_paths))
        for to_path in self.to_paths:
            assert self.from_path not in to_path, '%s should not be in %s' % (
                self.from_path, to_path)
            command = ['rsync', '-rtvl', '--progress', self.from_path, to_path]
            print ' '.join(command)
            subprocess.call(command)


def get_configs(config_path=None):
    """Load src to dests mappings from ~/.back.ini"""
    if config_path is None:
        config_path = os.path.expanduser('~/.back.ini')
    from ConfigParser import SafeConfigParser
    config = {}
    parser = SafeConfigParser()
    parser.read(config_path)
    for section_name in parser.sections():
        config[section_name] = {}
        for name, value in parser.items(section_name):
            if 'dest' == name:
                value = [x.strip() for x in value.split(',')]
            config[section_name][name] = value
    return config
