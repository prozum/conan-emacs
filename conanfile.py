import os

from conans import AutoToolsBuildEnvironment, ConanFile, Meson, tools


class EmacsConan(ConanFile):
    name = "emacs"
    version = tools.get_env("GIT_TAG", "26.3")
    description = "The chosen editor"
    license = "GPL3"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "web": [True, False],
        "nativecomp": [True, False],
    }
    default_options = ("web=True", "nativecomp=False")

    def build_requirements(self):
        if self.options.web:
            self.build_requires("meson/[>=0.51.2]@%s/stable" % self.user)
        else:
            self.build_requires("generators/1.0.0@%s/stable" % self.user)
            self.build_requires("make/[>=3.4.0]@%s/stable" % self.user)
            self.build_requires("autoconf/[>=2.69]@%s/stable" % self.user)
            self.build_requires("automake/[>=1.16.1]@%s/stable" % self.user)
            self.build_requires("texinfo/[>=6.6]@%s/stable" % self.user)

    def requirements(self):
        if self.options.web:
            self.requires("generators/1.0.0@%s/stable" % self.user)
        elif self.options.nativecomp:
            self.requires("gcc/9.3.0-jit@%s/stable" % self.user)
        else:
            self.requires("cc/1.0.0@%s/stable" % self.user)

        if not self.options.web:
            self.requires("ncurses/6.1@%s/stable" % self.user)
            self.requires("gtk3/3.24.11@%s/stable" % self.user)
            self.requires("libxpm/3.5.13@%s/stable" % self.user)
            self.requires("giflib/5.2.1@%s/stable" % self.user)
            self.requires("libtiff/4.1.0@%s/stable" % self.user)
            self.requires("gnutls/3.6.12@%s/stable" % self.user)

    def source(self):
        if self.options.web:
            branch = "feature/web-frontend"
        elif self.options.nativecomp:
            branch = "feature/native-comp"
        else:
            branch = "emacs-" + self.version
        git = tools.Git("emacs")
        git.clone("git@github.com:noverby/emacs.git", branch, shallow=True)

    def build(self):
        args = []
        if self.options.web:
            args.append("--with-web")
            args.append("--without-x")
            args.append("--without-xpm")
            args.append("--without-gif")
            args.append("--without-tiff")
            args.append("--without-sound")
            args.append("--without-dbus")
            args.append("--without-selinux")
            args.append("--without-xml2")
            args.append("--without-gnutls")
            args.append("--without-libgmp")
        elif self.options.nativecomp:
            args.append("--with-nativecomp")
        else:
            args.append("--with-x-toolkit=gtk3")

        if self.options.web:
            meson = Meson(self)
            meson.configure(source_folder="emacs")
        else:
            with tools.chdir("emacs"):
                self.run("sh autogen.sh")
                autotools = AutoToolsBuildEnvironment(self)
                autotools.configure(args=args)
                autotools.make()
