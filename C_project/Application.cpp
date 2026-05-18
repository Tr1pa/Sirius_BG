#include "Application.h"
#include "imgui.h"
#include "backends/imgui_impl_glfw.h"
#include "backends/imgui_impl_opengl3.h"
#include <iostream>

Application::Application() {
    if (!glfwInit()) exit(1);
    
    glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3);
    glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 0);
    window_ = glfwCreateWindow(1280, 720, "High Performance Route Optimizer 1M", NULL, NULL);
    glfwMakeContextCurrent(window_);
    glfwSwapInterval(1); // VSync

    initImGui();

    // Создаем оптимизатор. Поле 1000x1000 абстрактных единиц.
    optimizer_ = std::make_unique<RouteOptimizer>(1000.0f, 1000.0f);
}

Application::~Application() {
    ImGui_ImplOpenGL3_Shutdown();
    ImGui_ImplGlfw_Shutdown();
    ImGui::DestroyContext();
    glfwDestroyWindow(window_);
    glfwTerminate();
}

void Application::initImGui() {
    IMGUI_CHECKVERSION();
    ImGui::CreateContext();
    ImGui::StyleColorsDark();
    ImGui_ImplGlfw_InitForOpenGL(window_, true);
    ImGui_ImplOpenGL3_Init("#version 130");
}

void Application::updateRenderBuffer() {
    const auto& route = optimizer_->getRoute();
    const auto& X = optimizer_->getX();
    const auto& Y = optimizer_->getY();
    
    gl_vertex_buffer_.clear();
    gl_vertex_buffer_.reserve(route.size() * 2);

    // Нормализуем координаты [0, 1000] в OpenGL экраные координаты [-1, 1]
    for (int idx : route) {
        float screen_x = (X[idx] / 1000.0f) * 2.0f - 1.0f;
        float screen_y = (Y[idx] / 1000.0f) * 2.0f - 1.0f;
        gl_vertex_buffer_.push_back(screen_x);
        gl_vertex_buffer_.push_back(screen_y);
    }
}

void Application::renderRoute() {
    if (!show_route_ || gl_vertex_buffer_.empty()) return;

    // Быстрый рендер 1 миллиона линий на чистом OpenGL (до ImGui)
    glEnableClientState(GL_VERTEX_ARRAY);
    glVertexPointer(2, GL_FLOAT, 0, gl_vertex_buffer_.data());
    glColor3f(0.0f, 1.0f, 0.5f); // Зеленоватый цвет маршрута
    glDrawArrays(GL_LINE_STRIP, 0, gl_vertex_buffer_.size() / 2);
    glDisableClientState(GL_VERTEX_ARRAY);
}

void Application::renderUI() {
    ImGui_ImplOpenGL3_NewFrame();
    ImGui_ImplGlfw_NewFrame();
    ImGui::NewFrame();

    ImGui::Begin("Control Panel");
    ImGui::Text("Points: %d", optimizer_->getPointCount());
    
    if (ImGui::Button("Generate 1,000,000 Points")) {
        optimizer_->generatePoints(1000000);
        show_route_ = false;
        time_naive_ = time_opt_ = 0;
    }

    ImGui::Separator();

    ImGui::Text("NAIVE O(N^2) Approach:");
    ImGui::TextColored(ImGui::ColorConvertU32ToFloat4(IM_COL32(255,100,100,255)), 
                       "Warning: Tested on 10,000 points only! \n1M would take ~6 hours.");
    if (ImGui::Button("Run Naive (10k points)")) {
        time_naive_ = optimizer_->solveNaive(10000);
        updateRenderBuffer();
    }
    ImGui::Text("Naive Time: %.4f sec", time_naive_);

    ImGui::Separator();

    ImGui::Text("OPTIMIZED O(N) DOD + Grid Approach:");
    ImGui::TextColored(ImGui::ColorConvertU32ToFloat4(IM_COL32(100,255,100,255)), 
                       "Runs perfectly on full 1,000,000 points.");
    if (ImGui::Button("Run Optimized (1M points)")) {
        time_opt_ = optimizer_->solveOptimized();
        updateRenderBuffer();
    }
    ImGui::Text("Optimized Time: %.4f sec", time_opt_);

    ImGui::Separator();
    ImGui::Checkbox("Render Route", &show_route_);
    ImGui::Text("FPS: %.1f", ImGui::GetIO().Framerate);

    ImGui::End();

    ImGui::Render();
    ImGui_ImplOpenGL3_RenderDrawData(ImGui::GetDrawData());
}

void Application::run() {
    while (!glfwWindowShouldClose(window_)) {
        glfwPollEvents();

        int display_w, display_h;
        glfwGetFramebufferSize(window_, &display_w, &display_h);
        glViewport(0, 0, display_w, display_h);
        
        // Очистка экрана (темный фон)
        glClearColor(0.1f, 0.1f, 0.12f, 1.0f);
        glClear(GL_COLOR_BUFFER_BIT);

        renderRoute(); // Сначала рисуем массивные линии
        renderUI();    // Поверх рисуем интерфейс

        glfwSwapBuffers(window_);
    }
}