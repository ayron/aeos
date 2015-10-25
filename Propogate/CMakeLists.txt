cmake_minimum_required(VERSION 2.8)

project( Space )
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11 -Wall -Wno-long-long -pedantic")

#find_package( Eigen3 REQUIRED )

add_executable( space Main.cpp )
#target_link_libraries( space ${OpenCV_LIBS} )



