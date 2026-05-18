#pragma once
#include <vector>
#include <cstdint>
#include <tuple>

// Класс инкапсулирует данные и алгоритмы (ООП подход), 
// но внутри использует DOD (SoA) для скорости кэша.
class RouteOptimizer {
public:
    RouteOptimizer(float map_width, float map_height);
    
    void generatePoints(int count);
    
    // Возвращает время выполнения в секундах
    double solveNaive(int max_points = 10000); 
    double solveOptimized();
    
    // Геттеры для рендера
    const std::vector<float>& getX() const { return x_; }
    const std::vector<float>& getY() const { return y_; }
    const std::vector<int>& getRoute() const { return route_; }
    int getPointCount() const { return num_points_; }

private:
    float map_width_, map_height_;
    int num_points_ = 0;

    // --- DOD: Structure of Arrays (SoA) ---
    // Данные хранятся в отдельных векторах для идеального Cache Locality и SIMD
    std::vector<float> x_;
    std::vector<float> y_;
    std::vector<uint8_t> visited_; // uint8_t быстрее векторного bool
    std::vector<int> route_;

    // --- Вспомогательные методы ---
    void resetVisited();
    
    // Структуры для Spatial Hashing (Сетка)
    int grid_cols_, grid_rows_;
    float cell_size_;
    std::vector<int> grid_head_; // Индекс первой точки в ячейке
    std::vector<int> grid_next_; // Индекс следующей точки в той же ячейке (Связный список на массивах)

    void buildSpatialGrid();
    int findNearestInGrid(int current_idx);
};