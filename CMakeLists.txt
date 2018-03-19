# required to specify the c++ standard
cmake_minimum_required(VERSION 3.0)

# define project information
project(GooseSLURM)

# option: install all
option(ALL "Install all binaries" OFF)

# initialize list with binaries
set(PROJECT_BINARIES "bin/Gscript")

# find "squeue"
find_program(SQUEUE squeue)
# add relevant binaries
if("${SQUEUE}" MATCHES "SQUEUE-NOTFOUND" AND NOT ALL)
  message(STATUS "squeue not found: excluding Gstat")
else ()
  set(PROJECT_BINARIES ${PROJECT_BINARIES} "bin/Gstat")
endif()

# find "sinfo"
find_program(SINFO sinfo)
# add relevant binaries
if("${SINFO}" MATCHES "SINFO-NOTFOUND" AND NOT ALL)
  message(STATUS "sinfo not found: excluding Ginfo")
else ()
  set(PROJECT_BINARIES ${PROJECT_BINARIES} "bin/Ginfo")
endif()

# find "sbatch"
find_program(SBATCH sbatch)
# add relevant binaries
if("${SBATCH}" MATCHES "SBATCH-NOTFOUND" AND NOT ALL)
  message(STATUS "sbatch not found: excluding Gsub, Gdel, Gcopy")
else ()
  set(PROJECT_BINARIES ${PROJECT_BINARIES} "bin/Gsub")
  set(PROJECT_BINARIES ${PROJECT_BINARIES} "bin/Gdel")
  set(PROJECT_BINARIES ${PROJECT_BINARIES} "bin/Gopy")
endif()

# install binaries
INSTALL(PROGRAMS ${CMAKE_CURRENT_SOURCE_DIR}/${PROJECT_BINARIES} DESTINATION bin)

# print information to screen
message(STATUS "")
message(STATUS "+-------------------------------------------------------------------------------")
message(STATUS "|")
if(NOT ALL)
message(STATUS "| Install, based on availability of squeue, sinfo, sbatch:")
else()
message(STATUS "| Install:")
endif()
message(STATUS "|")
message(STATUS "|   ${PROJECT_BINARIES}")
message(STATUS "|")
message(STATUS "| Use 'make install' to install in:")
message(STATUS "|")
message(STATUS "|   ${CMAKE_INSTALL_PREFIX}")
if(NOT ALL)
message(STATUS "|")
message(STATUS "| To include all commands, add the following cmake-option:")
message(STATUS "|")
message(STATUS "|   cmake ... -DALL=ON")
endif()
message(STATUS "|")
message(STATUS "| To specify a custom directory, add the following cmake-option:")
message(STATUS "|")
message(STATUS "|   cmake ... -DCMAKE_INSTALL_PREFIX=yourprefix")
message(STATUS "|")
message(STATUS "| For custom paths, add the following line to your '~/.bashrc'")
message(STATUS "|")
message(STATUS "|   export PATH=${CMAKE_INSTALL_PREFIX}/bin:$PATH")
message(STATUS "|")
message(STATUS "+-------------------------------------------------------------------------------")
message(STATUS "")
