import glob
import os

from conans import CMake, ConanFile, tools


class PagmoConan(ConanFile):
    name = "pagmo"
    version = "2.10"
    description = (
        "A C++ / Python platform to perform parallel computations "
        "of optimisation tasks (global and local) via the"
        " asynchronous generalized island model."
    )
    # topics can get used for searches, GitHub topics, Bintray tags etc. Add here keywords about the library
    topics = ("parallelization", "optimization")
    url = "https://github.com/rhololkeolke/conan-pagmo"
    homepage = "https://esa.github.io/pagmo2/index.html"
    author = "Devin Schwab <dschwab@andrew.cmu.edu>"
    license = (
        "GPL3"
    )  # Indicates license type of the packaged library; please use SPDX Identifiers https://spdx.org/licenses/
    exports = ["LICENSE.md"]  # Packages the license for the
    exports_sources = ["CMakeLists.txt"]
    # conanfile.py
    generators = "cmake"

    # Options may need to change depending on the packaged library.
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_eigen3": [True, False],
        "with_ipopt": [True, False],
        "with_nlopt": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_eigen3": True,
        "with_ipopt": True,
        "with_nlopt": True,
    }

    # Custom attributes for Bincrafters recipe conventions
    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def requirements(self):
        if self.options.with_eigen3:
            self.requires("eigen/3.3.7@conan/stable")
        if self.options.with_nlopt:
            self.requires("nlopt/2.6.1@rhololkeolke/stable")

    def _system_package_architecture(self):
        if tools.os_info.with_apt:
            if self.settings.arch == "x86":
                return ":i386"
            elif self.settings.arch == "x86_64":
                return ":amd64"
            elif self.settings.arch == "armv6" or self.settings.arch == "armv7":
                return ":armel"
            elif self.settings.arch == "armv7hf":
                return ":armhf"
            elif self.settings.arch == "armv8":
                return ":arm64"

        if tools.os_info.with_yum:
            if self.settings.arch == "x86":
                return ".i686"
            elif self.settings.arch == "x86_64":
                return ".x86_64"
        return ""

    def system_requirements(self):
        packages = []
        if self.options.with_ipopt:
            packages.append("coinor-libipopt-dev")

        installer = tools.SystemPackageTool()
        arch_suffix = self._system_package_architecture()
        for package in packages:
            installer.install("{}{}".format(package, arch_suffix))

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def source(self):
        source_url = "https://github.com/esa/pagmo2"
        tools.get(
            "{0}/archive/v{1}.tar.gz".format(source_url, self.version),
            sha256="2fa95e2b464ddeadb9fc09bd314081293f02a1b6abc11c0b05064729a077227c",
        )
        extracted_dir = self.name + "2-" + self.version

        # Rename to "source_subfolder" is a convention to simplify later steps
        os.rename(extracted_dir, self._source_subfolder)
        os.symlink(
            os.path.join(os.getcwd(), self._source_subfolder, "cmake_modules"),
            "cmake_modules",
        )

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["PAGMO_BUILD_TESTS"] = False
        cmake.definitions["CMAKE_POSITION_INDEPENDENT_CODE"] = self.options.fPIC
        # Disable optional components
        cmake.definitions["PAGMO_WITH_EIGEN3"] = self.options.with_eigen3
        cmake.definitions["PAGMO_WITH_NLOPT"] = self.options.with_nlopt
        cmake.definitions["PAGMO_WITH_IPOPT"] = self.options.with_ipopt
        cmake.configure(build_folder=self._build_subfolder)
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.libs.append("pthread")
