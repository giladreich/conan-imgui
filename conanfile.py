#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import shutil
from conans import ConanFile, CMake, tools

class IMGUIConan(ConanFile):
    name = "imgui"
    version = "1.67"
    description = "Bloat-free Immediate Mode Graphical User interface for C++ with minimal dependencies"
    topics = ("conan", "imgui", "c++")
    url = "https://github.com/giladreich/conan-imgui"
    homepage = "https://github.com/ocornut/imgui"
    author = "Gilad Reich <giladreichgr@gmail.com>"
    license = "MIT"
    exports = ["LICENSE.md"]
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = dict({
        "shared": [True, False],
        "fPIC": [True, False],

        "with_impl": [True, False],
        "dx9": [True, False],
        "dx10": [True, False],
        "dx11": [True, False],
        "dx12": [True, False]
    })
    default_options = dict({
        "shared": False,
        "fPIC": True,

        "with_impl": False,
        "dx9": False,
        "dx10": False,
        "dx11": False,
        "dx12": False
    })

    # Custom attributes
    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"



    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC


    def source(self):
        # Get the cmake module for building imgui:
        module_name = "ImGui-CMake-Installer"
        tools.get("https://github.com/giladreich/{0}/archive/v{1}.tar.gz".format(module_name, self.version))
        os.rename("{0}-{1}".format(module_name, self.version), self._source_subfolder)
        os.rmdir(self._source_subfolder + "/imgui")

        # Unfortunately github doesn't support including submodule sources when archiving a release, therefore we do this step:
        # Get ImGui sources and move them under the cmake module directory:
        tools.get("{0}/archive/v{1}.tar.gz".format(self.homepage, self.version))
        imgui_dir = "{0}-{1}".format(self.name, self.version)
        os.rename(imgui_dir, self.name)
        shutil.move(self.name, self._source_subfolder)


    def _configure_cmake(self):
        cmake = CMake(self)
        if self.options.shared:
            cmake.definitions["IMGUI_STATIC_LIBRARY"] = "OFF"
        if self.options.with_impl and tools.os_info.is_windows:
            cmake.definitions["IMGUI_WITH_IMPL"] = "ON"
            if self.options.dx9:
                cmake.definitions["IMGUI_IMPL_DX9"] = "ON"
            elif self.options.dx10:
                cmake.definitions["IMGUI_IMPL_DX10"] = "ON"
            elif self.options.dx11:
                cmake.definitions["IMGUI_IMPL_DX11"] = "ON"
            elif self.options.dx12:
                cmake.definitions["IMGUI_IMPL_DX12"] = "ON"
            else:
                self.output.warn("[WARNING] 'with_impl' option is set to True but no graphic api selected(dx9, dx10 etc..). See 'CMakeOptions.cmake'.")
        else:
            cmake.definitions["IMGUI_WITH_IMPL"] = "OFF"

        cmake.configure(build_dir=self._build_subfolder)
        return cmake


    def build(self):
        cmake = self._configure_cmake()
        cmake.build()


    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        dist_dir = "{0}/dist/{1}".format(self._build_subfolder, self.settings.build_type)
        self.copy("*", src=dist_dir + "/bin",        dst="bin")
        self.copy("*", src=dist_dir + "/lib",        dst="lib")
        self.copy("*", src=dist_dir + "/include",    dst="include")
        self.copy("*", src=dist_dir + "/misc/fonts", dst="misc/fonts")
        self.copy("LICENSE*", dst="licenses", src=self._source_subfolder)

        if self.settings.build_type == "RelWithDebInfo" and self.settings.compiler == "Visual Studio":
            pdb_dir = "{0}/source_subfolder/imgui.dir/RelWithDebInfo/".format(self._build_subfolder)
            self.copy("imgui.pdb", src=pdb_dir, dst="lib")


    def package_info(self):
        if self.settings.os == "Windows":
            self.env_info.path.append(os.path.join(self.package_folder, "bin"))
        self.cpp_info.libs = tools.collect_libs(self)