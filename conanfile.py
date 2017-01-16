from conans import ConanFile, CMake, tools
import os


class FibioConan(ConanFile):
    name = "mbedtls"
    version = "2.4.0"
    license = "Apache License 2.0"
    url = "https://tls.mbed.org/"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = "shared=False"
    generators = "cmake"
    description = "mbed TLS"

    def configure(self):
        self.requires("zlib/1.2.11@windoze/stable")
        self.options["zlib/1.2.11"].shared = self.options.shared                    

    def source(self):
        zip_name = "mbedtls-%s-apache.tgz" % self.version
        url = "https://tls.mbed.org/download/%s" % zip_name
        self.output.info("Downloading %s..." % url)
        tools.download(url, zip_name)
        tools.unzip(zip_name, ".")
        os.unlink(zip_name)
        tools.replace_in_file("mbedtls-%s/CMakeLists.txt" % self.version, 'project("mbed TLS" C)', '''PROJECT("mbed TLS" C)
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()''')

    def build(self):
        cmake = CMake(self.settings)
        if self.options.shared:
            opt="-DUSE_SHARED_MBEDTLS_LIBRARY=ON -DUSE_STATIC_MBEDTLS_LIBRARY=OFF"
        else:
            opt="-DUSE_SHARED_MBEDTLS_LIBRARY=OFF -DUSE_STATIC_MBEDTLS_LIBRARY=ON"
        opt += " -DENABLE_ZLIB_SUPPORT=ON -DENABLE_TESTING=OFF"

        self.run('cmake mbedtls-%s %s %s' % (self.version, cmake.command_line, opt))
        self.run("cmake --build . %s" % cmake.build_config)

    def package(self):
        self.copy("*.h", dst="include/mbedtls", src="mbedtls-%s/include/mbedtls" % self.version)
        self.copy("*.lib", dst="lib", src="lib", keep_path=False)
        self.copy("*.dll", dst="bin", src="lib", keep_path=False)
        self.copy("*.dylib", dst="lib", src="library", keep_path=False)
        self.copy("*.so", dst="lib", src="library", keep_path=False)
        self.copy("*.a", dst="lib", src="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["mbedcrypto", "mbedtls", "mbedx509"]
