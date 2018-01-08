# required to specify the c++ standard
cmake_minimum_required(VERSION 3.0)

# define project information
project(GooseCluster)

# list with binaries
set(PROJECT_BINARIES
  bin/Gcopy
  bin/Gdel
  bin/Gscript
  bin/Gstat
  bin/Ginfo
  bin/Ginfo_summary
  bin/Gsub
)

# install binaries
INSTALL(PROGRAMS ${CMAKE_CURRENT_SOURCE_DIR}/${PROJECT_BINARIES} DESTINATION bin)

# print information to screen
message(STATUS "")
message(STATUS "+-------------------------------------------------------------------------------")
message(STATUS "|")
message(STATUS "| Use 'make install' to install in '${CMAKE_INSTALL_PREFIX}'")
message(STATUS "| To specify a custom directory call")
message(STATUS "|   cmake .. -DCMAKE_INSTALL_PREFIX=yourprefix")
message(STATUS "| For custom paths, add the following line to your '~/.bashrc'")
message(STATUS "|   export PATH=${CMAKE_INSTALL_PREFIX}/bin:$PATH")
message(STATUS "|")
message(STATUS "+-------------------------------------------------------------------------------")
message(STATUS "")
