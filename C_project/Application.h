#pragma once
#include <GLFW/glfw3.h>
#include <memory>
#include "RouteOptimizer.h"

class Application {
public:
    Application();
    ~Application();
    
    void run();

private:
    GLFWwindow* window_;
    std::unique_ptr<RouteOptimizer> optimizer_;

    // Статистика
    double time_naive_ = 0.0;
    double time_opt_ = 0.0;
    bool show_route_ = false;

    // OpenGL данные для быстрого рендера 1 млн линий
    std::vector<float> gl_vertex_buffer_;

    void initImGui();
    void renderUI();
    void updateRenderBuffer();
    void renderRoute();
};