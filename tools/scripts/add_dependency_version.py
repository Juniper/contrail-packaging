import ConfigParser, os, StringIO, argparse, shutil, tempfile, argparse
from itertools import ifilterfalse, tee


class ChangeDepends(object):
    def __init__(self, version, filename, outfile=None):
        self._file = filename
        self._outfile = outfile or self.gen_outfile(filename)
        self._version = version
        self.cfg_fp = None
        self.control = None

    def gen_outfile(self, fn):
        if fn.endswith('.in'):
            return fn[:-3]
        return fn + '.save'

    def make_cfg_fp(self):
        if self.cfg_fp is None:
            self.cfg_fp = StringIO.StringIO()
            self.cfg_fp.write('[dummysection]\n')
            self.cfg_fp.write(open(self._file).read())
        self.cfg_fp.seek(0, os.SEEK_SET)

    def read_config(self):
        if self.control is None:
            self.control = ConfigParser.ConfigParser()
            self.make_cfg_fp()
            self.control.readfp(self.cfg_fp)

    def cset_cond(self, pkg):
        return '|' not in pkg and 'contrail' in pkg and pkg != 'contrail-vrouter'

    def cset_or_cond(self, pkg):
        return '|' in pkg and 'contrail' in pkg and pkg != 'contrail-vrouter'

    def partition(self, pred, ittr):
        t1, t2 = tee(ittr)
        return filter(bool, ifilterfalse(pred, t1)), filter(pred, t2)

    def add_version_to_or_depends(self, depends):
        return [dep.strip() + ' (>= %s)' % self._version for dep in depends.split('|')]

    def depends(self):
        try:
            self.control.get('dummysection', 'Depends')
        except raise NoOptionError:
            return False
        return True

    def change_config(self):
        dep_list = map(lambda x: x.strip(), self.control.get('dummysection', 'Depends').split(','))
        dummy_set, ch_or_set = self.partition(self.cset_or_cond, dep_list)
        im_set, ch_set = self.partition(self.cset_cond, dep_list)
        new_set = map(lambda x: x + ' (>= %s)' % self._version, ch_set)
        new_or_set = map(lambda x: ' | '.join(self.add_version_to_or_depends(x)), ch_or_set)
        self.control.set('dummysection', 'Depends', ',\n    '.join(new_set
                     + list(new_or_set) + list(im_set)))

    def format_key(self, key):
        t = key.split('-')
        s = '-'.join(map(str.capitalize, t))
        if s == 'Package':
            return '\n' + s
        return s

    def write_output(self):
        with open(self._outfile, "w") as f:
            for k in self.control.options('dummysection'):
                f.write('%s: %s\n' % (self.format_key(k),
                            self.control.get('dummysection', k)))

    def run(self):
        self.read_config()
        if self.depends():
            self.change_config()
        self.write_output()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", help="File to be modified", default='debian/control')
    parser.add_argument("--outfile", help="save output as", default=None)
    parser.add_argument("--version", help="version tag", required=True)
    args = parser.parse_args()
    cd = ChangeDepends(args.version, args.file, args.outfile)
    cd.run()

if __name__ == '__main__':
    main()
