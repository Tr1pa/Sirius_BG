cmake_minimum_required(VERSION 3.14)
project(HighPerfRouter CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Включаем максимальную оптимизацию для Release сборки
if(CMAKE_BUILD_TYPE MATCHES Release OR CMAKE_BUILD_TYPE MATCHES RelWithDebInfo)
    if(MSVC)
        add_compile_options(/O2 /Ob2 /Oi /Ot /arch:AVX2 /fp:fast)
    else()
        add_compile_options(-O3 -march=native -ffast-math)
    endif()
endif()

include(FetchContent)

# Автоматическая загрузка GLFW
FetchContent_Declare(glfw GIT_REPOSITORY https://github.com/glfw/glfw.git GIT_TAG 3.3.8)
set(GLFW_BUILD_DOCS OFF CACHE BOOL "" FORCE)
set(GLFW_BUILD_TESTS OFF CACHE BOOL "" FORCE)
set(GLFW_BUILD_EXAMPLES OFF CACHE BOOL "" FORCE)
FetchContent_MakeAvailable(glfw)

# Автоматическая загрузка Dear ImGui
FetchContent_Declare(imgui GIT_REPOSITORY https://github.com/ocornut/imgui.git GIT_TAG v1.89.9)
FetchContent_MakeAvailable(imgui)

# Настройка файлов ImGui
set(IMGUI_DIR ${imgui_SOURCE_DIR})
file(GLOB IMGUI_SOURCES
    ${IMGUI_DIR}/imgui.cpp ${IMGUI_DIR}/imgui_draw.cpp ${IMGUI_DIR}/imgui_tables.cpp
    ${IMGUI_DIR}/imgui_widgets.cpp
    ${IMGUI_DIR}/backends/imgui_impl_glfw.cpp
    ${IMGUI_DIR}/backends/imgui_impl_opengl3.cpp
)

add_executable(${PROJECT_NAME} 
    main.cpp 
    RouteOptimizer.cpp 
    Application.cpp 
    ${IMGUI_SOURCES}
)

target_include_directories(${PROJECT_NAME} PRIVATE 
    ${IMGUI_DIR} 
    ${IMGUI_DIR}/backends
)

# Подключение OpenGL и GLFW
if(APPLE)
    target_link_libraries(${PROJECT_NAME} PRIVATE glfw "-framework OpenGL" "-framework Cocoa" "-framework IOKit" "-framework CoreVideo")
elseif(WIN32)
    target_link_libraries(${PROJECT_NAME} PRIVATE glfw opengl32)
else()
    find_package(OpenGL REQUIRED)
    target_link_libraries(${PROJECT_NAME} PRIVATE glfw OpenGL::GL)
endif()