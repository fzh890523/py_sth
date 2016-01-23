# encoding: utf-8
import importlib
from optparse import OptionParser
import os
import tempfile
import subprocess
import sys

__author__ = 'yonka'


class Requirement(object):

    @staticmethod
    def parse(t, s):
        if t == "git":
            return GitRequirement.parse(s)
        else:
            raise ValueError("not support requirement type (%s)" % t)

    def do_collect(self, exp_dir, temp_dir=None):
        raise NotImplementedError()


class GitRequirement(Requirement):
    """
    git requirement content: k1=v1; k2=v2
    refer to __init__ params for keys
    """

    @classmethod
    def parse(cls, s):
        items = {k: v for k, v in (item.strip().split("=", 1) for item in s.split(";"))}
        name = items.pop("name", None)
        url = items.pop("url", None)
        return cls(name, url, **items)

    def __init__(self, name, url, branch=None, commit=None, tag=None, path=None, dir_name=None):
        """
        :param name git clone ${url} ${name}
        :param url git repo url
        :param branch None means default branch of remote
        :param commit None means newest commit, if not None prior to tag
        :param tag
        :param path if valid, will do `cp -r os.path.join(name, path) os.path.join(exp_dir, \
        dir_name or os.path.basename(path))`; or will do `cp -r name os.path.join(exp_dir, dir_name or name)`
        :param dir_name to replace name or bansename(path)
        """
        self.name = name
        self.url = url
        self.branch = branch
        self.commit = commit
        self.tag = tag
        self.path = path
        self.dir_name = dir_name
        if not name or not url:
            raise ValueError("url (%s) or name (%s) is invalid" % (url, name))

    def do_collect(self, exp_dir, temp_dir=None):
        if temp_dir is None:
            temp_dir = tempfile.mkdtemp()

        cmd = "cd %s && git clone %s %s" % (temp_dir, self.url, self.name)
        ret = subprocess.call([cmd])
        if ret != 0:
            sys.stderr.write("met error when do clone for %s" % self)
            return
        repo_path = os.path.join(temp_dir, self.name)

        if self.branch is not None:
            cmd = "cd %s && git checkout %s" % (repo_path, self.branch)
            ret = subprocess.call([cmd])
            if ret != 0:
                sys.stderr.write("met error when do change branch for %s" % self)
                return

        if self.commit is not None:
            cmd = "cd %s && git checkout %s" % (repo_path, self.commit)
            ret = subprocess.call([cmd])
            if ret != 0:
                sys.stderr.write("met error when do change commit for %s" % self)
                return
        elif self.tag is not None:
            cmd = "cd %s && git fetch --tags && checkout %s" % (repo_path, self.tag)
            ret = subprocess.call([cmd])
            if ret != 0:
                sys.stderr.write("met error when do change tag for %s" % self)
                return

        if self.path is None:
            dst_path = os.path.join(exp_dir, self.dir_name or self.name)
            cmd = "cd %s && rm -rf .git* && cd .. && cp -r %s %s" % (
                repo_path, repo_path, dst_path)
        else:
            dst_path = os.path.join(exp_dir, self.dir_name or os.path.basename(self.path))
            cmd = "cp -r %s %s" % (
                os.path.join(repo_path, self.path),
                dst_path)
        ret = subprocess.call([cmd])
        if ret != 0:
            sys.stderr.write("met error when do cp cmd (%s) for %s" % (cmd, self))
            return

        return dst_path


def parse_requirement_from_module_doc(mod_doc):
    """
    :param mod_doc: the module doc
    :return: list of requirement class instance
    mod_doc example:
    requirements_start
    type type_require_content
    requirements_end
    """
    res = []
    doc_lines = mod_doc.split("\n")
    for i, l in enumerate(doc_lines):
        if l.strip() == "requirements_start":
            break
    else:
        return res
    for l in doc_lines[1+1:]:
        l = l.strip()
        lis = l.split(None, 1)
        if len(lis) != 2:
            sys.stderr.write("requirement line is invalid: %s" % l)
        res.append(Requirement.parse(*lis))
    return res


def main():
    global d, m, e
    if not m:
        m = os.path.basename(d)
        d = os.path.dirname(d)
    if d:
        os.chdir(d)
    mod = importlib.import_module(m)
    mod_doc = mod.__doc__
    mod_requirements = parse_requirement_from_module_doc(mod_doc)
    if not mod_requirements:
        print "module %s has no requirement, module doc is %s, exit!" % (m, mod_doc)
        return
    print "having parsed requirements from module doc as below:\n%s" % mod_requirements
    exp_dir = e
    if not exp_dir:
        exp_dir = "./"
    exp_dir = os.path.join(exp_dir, "_%s_requirements" % m)
    if not os.path.exists(exp_dir):
        print "export dir %s not exist, try to create it" % exp_dir
        os.makedirs(exp_dir)
        
    temp_dir = tempfile.mkdtemp()
    for mod_requirement in mod_requirements:
        mod_requirement.do_collect(exp_dir, temp_dir)
    pass


if __name__ == "__main__":
    help_info = """
    usage:
    python refresh_captcha.py --bid ${bid: int, default 0} --size ${size: string, default 100x50} \
    --groupid ${groupid: int, mandatory or string all} --routine ${routine: int, should be larger than 0} \
    --sleepms ${sleepms: int,default 100} --conf ${conf, string, default ./}
    \n
    """
    parser = OptionParser(help_info)

    parser.add_option(
        "-d",
        "--dir",
        dest="d",
        help="the dir of the m, default means cur dir",
        default="",
        action="store"
    )
    parser.add_option(
        "-m",
        "--module",
        dest="m",
        help="module name",
        action="store"
    )
    parser.add_option(
        "-e",
        "--export_dir",
        dest="e",
        help="the dir to export to, default means the same dir of the module",
        action="store",
        default=""
    )
    options, args = parser.parse_args()
    d, m, e = options.d, options.m, options.e
    main()
