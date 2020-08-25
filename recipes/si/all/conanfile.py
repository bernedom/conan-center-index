from conans import CMake, ConanFile, tools
from conans.errors import ConanInvalidConfiguration
from conans.tools import Version

import os


class SiConan(ConanFile):
    name = "si"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/bernedom/SI"
    description = "A header only c++ library that provides type safety and user defined literals \
         for handling pyhsical values defined in the International System of Units."
    topics = ("physical units", "SI-unit-conversion",
              "cplusplus-library", "cplusplus-17")
    exports_sources = "CMakeLists.txt"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True
    generators = "cmake"
    settings = {"compiler"}

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def configure(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, "17")
        elif not self._supports_cpp17():
            raise ConanInvalidConfiguration("SI requires C++17 support")

    def _supports_cpp17(self):
        supported_compilers = [
            ("gcc", "7"), ("clang", "5"), ("apple-clang", "10"), ("Visual Studio", "15.7")]
        compiler = self.settings.compiler
        version = Version(compiler.version)
        return any(compiler == sc[0] and version >= sc[1] for sc in supported_compilers)

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_folder = "SI-{}".format(self.version)
        os.rename(extracted_folder, self._source_subfolder)

    def _configure_cmake(self):
        if not self._cmake:
            self._cmake = CMake(self)
            # Add additional settings with cmake.definitions["SOME_DEFINITION"] = True
            self._cmake.definitions["SI_BUILD_TESTING"] = False
            self._cmake.definitions["SI_BUILD_DOC"] = False
            self._cmake.definitions["SI_INSTALL_LIBRARY"] = True
            self._cmake.configure(
                source_folder=self._source_subfolder, build_folder=self._build_subfolder)
        return self._cmake

    def configure(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, "17")
        elif not self._supports_cpp17():
            raise ConanInvalidConfiguration("SI requires C++17 support")

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        #  Remove folder containing cmake-specific files such as SIConfig.cmake and SIVersion.cmake
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "SI"
        self.cpp_info.names["cmake_find_package_multi"] = "SI"
