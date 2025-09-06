cmake_minimum_required(VERSION 3.16)
project(XRConverters LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

option(BUILD_EXAMPLES "Build example binaries" ON)
option(USE_VENDOR_ASSIMP "Prefer bundled Vendor/assimp instead of system Assimp" OFF)

find_package(ASSIMP QUIET)
find_package(PkgConfig QUIET)
pkg_check_modules(PUGIXML QUIET pugixml)
find_package(ZLIB QUIET)

# Prefer system Assimp includes/libs when available unless the user forces the
# bundled vendor tree via USE_VENDOR_ASSIMP.
find_path(SYSTEM_ASSIMP_INCLUDE NAMES assimp/Importer.hpp HINTS /usr/include /usr/local/include)
find_library(SYSTEM_ASSIMP_LIB NAMES assimp HINTS /usr/lib /usr/local/lib)

if(NOT USE_VENDOR_ASSIMP AND SYSTEM_ASSIMP_INCLUDE AND SYSTEM_ASSIMP_LIB)
	message(STATUS "Using system Assimp (include=${SYSTEM_ASSIMP_INCLUDE}, lib=${SYSTEM_ASSIMP_LIB})")
	set(ASSIMP_INCLUDE_DIRS ${SYSTEM_ASSIMP_INCLUDE})
	set(ASSIMP_LIB ${SYSTEM_ASSIMP_LIB})
elseif(ASSIMP_FOUND AND NOT USE_VENDOR_ASSIMP)
	message(STATUS "FindPackage reported Assimp found; using its settings")
	# ASSIMP_INCLUDE_DIRS / ASSIMP_LIBRARIES should be provided by the find module
else()
	message(STATUS "System Assimp not found or USE_VENDOR_ASSIMP=ON; falling back to bundled Vendor assimp headers")
	if(EXISTS ${CMAKE_CURRENT_SOURCE_DIR}/Vendor/assimp/include)
		set(ASSIMP_INCLUDE_DIRS ${CMAKE_CURRENT_SOURCE_DIR}/Vendor/assimp/include)
	elseif(EXISTS ${CMAKE_CURRENT_SOURCE_DIR}/../archive/XRConvertersSrc/Vendor/assimp/include)
		set(ASSIMP_INCLUDE_DIRS ${CMAKE_CURRENT_SOURCE_DIR}/../archive/XRConvertersSrc/Vendor/assimp/include)
	else()
		set(ASSIMP_INCLUDE_DIRS "")
	endif()
	find_library(ASSIMP_LIB assimp)
	if(ASSIMP_LIB)
		message(STATUS "Found assimp library at ${ASSIMP_LIB}")
	endif()
endif()

if(PUGIXML_FOUND)
	message(STATUS "Found system pugixml (pkg-config). Using system pugixml includes/libs")
	set(PUGIXML_LIBS ${PUGIXML_LIBRARIES})
else()
	message(STATUS "System pugixml not found via pkg-config; will fall back to bundled Vendor/pugi if present")
endif()

# Also try finding pugixml header directly in case pkg-config wasn't available
find_path(SYSTEM_PUGI_INCLUDE NAMES pugi/pugixml.hpp HINTS /usr/include /usr/local/include)
if(SYSTEM_PUGI_INCLUDE)
	message(STATUS "Found system pugixml include at ${SYSTEM_PUGI_INCLUDE}")
	if(NOT PUGIXML_FOUND)
		# Provide compatible variables used later
		set(PUGIXML_LIBS "")
	endif()
	set(PUGIXML_INCLUDE_DIRS ${SYSTEM_PUGI_INCLUDE})
	set(PUGIXML_FOUND 1)
endif()

if(NOT ZLIB_FOUND)
	find_package(ZLIB REQUIRED)
endif()

include_directories(
	${CMAKE_CURRENT_SOURCE_DIR}
	${CMAKE_CURRENT_SOURCE_DIR}/XRConverters
	${CMAKE_CURRENT_SOURCE_DIR}/include
)

# If system <half/half.hpp> isn't available, point to the archived vendor half
find_path(SYSTEM_HALF_INCLUDE NAMES half/half.hpp HINTS /usr/include /usr/local/include)
if(NOT SYSTEM_HALF_INCLUDE)
	# If the archived half header exists, don't add the whole vendor tree to
	# the include path (it may shadow system headers like pugixml). Instead
	# set a compile definition so the code can include the specific header via
	# a relative path from the source tree.
	if(EXISTS ${CMAKE_CURRENT_SOURCE_DIR}/../archive/XRConvertersSrc/Vendor/half/half.hpp)
		message(STATUS "Found archived half header; will use archived half.hpp")
		# Set a marker variable; we'll apply the compile definition to targets
		# after they are created.
		set(USE_ARCHIVE_HALF_MARKER 1)
		set(ARCHIVE_HALF_HEADER ${CMAKE_CURRENT_SOURCE_DIR}/../archive/XRConvertersSrc/Vendor/half/half.hpp)
	endif()
endif()

# If system pugixml not found, use archived vendor pugi include (only this include)
if(NOT PUGIXML_FOUND)
	if(EXISTS ${CMAKE_CURRENT_SOURCE_DIR}/../archive/XRConvertersSrc/Vendor/pugi)
		set(ARCHIVE_PUGI_INCLUDE ${CMAKE_CURRENT_SOURCE_DIR}/../archive/XRConvertersSrc/Vendor/pugi)
		message(STATUS "Using archived pugixml include: ${ARCHIVE_PUGI_INCLUDE}")
	endif()
endif()

file(GLOB_RECURSE XR_SRC
	XRConverters/*.cpp
	XRConverters/*/*.cpp
)

# Exclude Windows resources on non-Windows
if(WIN32)
	list(APPEND XR_SRC XRConverters/Resources.rc XRConvertersMain/Resources.rc)
endif()

add_library(xrconverters STATIC ${XR_SRC})
target_include_directories(xrconverters PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})

# If we detected the archived half header earlier, add the compile definition
if(DEFINED USE_ARCHIVE_HALF_MARKER)
	target_compile_definitions(xrconverters PRIVATE USE_ARCHIVE_HALF)
endif()

# If system pugixml was found by pkg-config, add its include dirs and define a
# compile macro so source code picks the system header instead of the archived
# pugi include.
if(PUGIXML_FOUND)
	if(DEFINED PUGIXML_INCLUDE_DIRS)
		target_include_directories(xrconverters PRIVATE ${PUGIXML_INCLUDE_DIRS})
	endif()
	if(DEFINED PUGIXML_LIBS)
		# Link later via PUGIXML_LIBS variable
	endif()
	target_compile_definitions(xrconverters PRIVATE USE_SYSTEM_PUGIXML)
endif()

# If ZLIB was found, add its include dirs and link library and define a macro
if(ZLIB_FOUND)
	if(DEFINED ZLIB_INCLUDE_DIRS)
		target_include_directories(xrconverters PRIVATE ${ZLIB_INCLUDE_DIRS})
	else()
		# Some find_package variants provide ZLIB_INCLUDE_DIR instead
		if(DEFINED ZLIB_INCLUDE_DIR)
			target_include_directories(xrconverters PRIVATE ${ZLIB_INCLUDE_DIR})
		endif()
	endif()
	target_link_libraries(xrconverters PRIVATE ${ZLIB_LIBRARIES})
	target_compile_definitions(xrconverters PRIVATE USE_SYSTEM_ZLIB)
endif()

# Assimp include/libs (prefer system; fall back to vendor include or found lib)
if(ASSIMP_INCLUDE_DIRS)
	if(ASSIMP_INCLUDE_DIRS)
		target_include_directories(xrconverters PRIVATE ${ASSIMP_INCLUDE_DIRS})
	endif()

	# If vendor half or pugi are present under the archive, add them so includes resolve.
	if(DEFINED ARCHIVE_HALF_INCLUDE)
		target_include_directories(xrconverters PRIVATE ${ARCHIVE_HALF_INCLUDE})
	endif()
	if(DEFINED ARCHIVE_PUGI_INCLUDE)
		target_include_directories(xrconverters PRIVATE ${ARCHIVE_PUGI_INCLUDE})
	endif()
endif()

if(ASSIMP_LIBRARIES)
	target_link_libraries(xrconverters PRIVATE ${ASSIMP_LIBRARIES})
elseif(ASSIMP_LIB)
	target_link_libraries(xrconverters PRIVATE ${ASSIMP_LIB})
endif()
if(PUGIXML_LIBS)
	target_link_libraries(xrconverters PRIVATE ${PUGIXML_LIBS})
endif()
if(ZLIB_LIBRARIES)
	target_link_libraries(xrconverters PRIVATE ${ZLIB_LIBRARIES})
endif()

add_executable(xrconverters_main XRConvertersMain/main.cpp XRConvertersMain/StdInc.cpp)
target_link_libraries(xrconverters_main PRIVATE xrconverters)

if(DEFINED USE_ARCHIVE_HALF_MARKER)
	target_compile_definitions(xrconverters_main PRIVATE USE_ARCHIVE_HALF)
endif()

if(NOT WIN32)
	# ensure compat header directory is available
	target_include_directories(xrconverters PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/include)
	target_include_directories(xrconverters_main PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/include)
endif()

install(TARGETS xrconverters xrconverters_main DESTINATION bin)

