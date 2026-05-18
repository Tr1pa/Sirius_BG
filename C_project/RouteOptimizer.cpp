#include "RouteOptimizer.h"
#include <random>
#include <chrono>
#include <limits>
#include <cmath>
#include <algorithm>

RouteOptimizer::RouteOptimizer(float map_width, float map_height) 
    : map_width_(map_width), map_height_(map_height), cell_size_(2.0f) // Размер ячейки подобран эмпирически
{
    grid_cols_ = static_cast<int>(map_width_ / cell_size_) + 1;
    grid_rows_ = static_cast<int>(map_height_ / cell_size_) + 1;
}

void RouteOptimizer::generatePoints(int count) {
    num_points_ = count;
    x_.resize(count);
    y_.resize(count);
    visited_.resize(count, 0);
    route_.clear();
    route_.reserve(count);

    std::mt19937 rng(42); // Фиксированный сид для воспроизводимости
    std::uniform_real_distribution<float> dist_x(0.0f, map_width_);
    std::uniform_real_distribution<float> dist_y(0.0f, map_height_);

    for (int i = 0; i < count; ++i) {
        x_[i] = dist_x(rng);
        y_[i] = dist_y(rng);
    }
}

void RouteOptimizer::resetVisited() {
    std::fill(visited_.begin(), visited_.end(), 0);
    route_.clear();
}

double RouteOptimizer::solveNaive(int max_points) {
    // ЗАЩИТА: Наивный метод на 1М точек повесит систему на часы. 
    // Ограничиваем количество для теста.
    int limit = std::min(num_points_, max_points);
    resetVisited();
    
    auto start = std::chrono::high_resolution_clock::now();

    int current = 0;
    visited_[current] = 1;
    route_.push_back(current);

    for (int step = 1; step < limit; ++step) {
        float min_dist_sq = std::numeric_limits<float>::max();
        int best_idx = -1;
        float cx = x_[current];
        float cy = y_[current];

        // Ужасный цикл O(N^2)
        for (int i = 0; i < limit; ++i) {
            if (!visited_[i]) {
                float dx = x_[i] - cx;
                float dy = y_[i] - cy;
                float dist_sq = dx * dx + dy * dy; // Без sqrt!
                if (dist_sq < min_dist_sq) {
                    min_dist_sq = dist_sq;
                    best_idx = i;
                }
            }
        }
        
        current = best_idx;
        visited_[current] = 1;
        route_.push_back(current);
    }

    auto end = std::chrono::high_resolution_clock::now();
    return std::chrono::duration<double>(end - start).count();
}

void RouteOptimizer::buildSpatialGrid() {
    grid_head_.assign(grid_cols_ * grid_rows_, -1);
    grid_next_.assign(num_points_, -1);

    // Построение сетки за один проход O(N)
    for (int i = 0; i < num_points_; ++i) {
        if (visited_[i]) continue;

        int cx = static_cast<int>(x_[i] / cell_size_);
        int cy = static_cast<int>(y_[i] / cell_size_);
        int cell_idx = cy * grid_cols_ + cx;

        grid_next_[i] = grid_head_[cell_idx];
        grid_head_[cell_idx] = i;
    }
}

int RouteOptimizer::findNearestInGrid(int current_idx) {
    float cx = x_[current_idx];
    float cy = y_[current_idx];
    
    int cell_x = static_cast<int>(cx / cell_size_);
    int cell_y = static_cast<int>(cy / cell_size_);

    float min_dist_sq = std::numeric_limits<float>::max();
    int best_idx = -1;

    // Расширяющийся радиус поиска (в ячейках)
    for (int radius = 1; radius < 50; ++radius) {
        int min_x = std::max(0, cell_x - radius);
        int max_x = std::min(grid_cols_ - 1, cell_x + radius);
        int min_y = std::max(0, cell_y - radius);
        int max_y = std::min(grid_rows_ - 1, cell_y + radius);

        for (int y = min_y; y <= max_y; ++y) {
            for (int x = min_x; x <= max_x; ++x) {
                int cell_idx = y * grid_cols_ + x;
                int p_idx = grid_head_[cell_idx];

                // Проход по связному списку ячейки
                while (p_idx != -1) {
                    if (!visited_[p_idx]) {
                        float dx = x_[p_idx] - cx;
                        float dy = y_[p_idx] - cy;
                        float dist_sq = dx * dx + dy * dy;
                        
                        if (dist_sq < min_dist_sq) {
                            min_dist_sq = dist_sq;
                            best_idx = p_idx;
                        }
                    }
                    p_idx = grid_next_[p_idx]; // Следующий в ячейке
                }
            }
        }
        // Если нашли точку в этом радиусе, дальше не ищем
        if (best_idx != -1) return best_idx; 
    }
    
    // Fallback: если точки слишком разбросаны (крайне редкий случай)
    for (int i = 0; i < num_points_; ++i) {
        if (!visited_[i]) return i;
    }
    return -1;
}

double RouteOptimizer::solveOptimized() {
    resetVisited();
    
    auto start = std::chrono::high_resolution_clock::now();

    int current = 0;
    visited_[current] = 1;
    route_.push_back(current);

    // Периодическое обновление сетки (т.к. точки "удаляются")
    const int grid_rebuild_freq = 50000; 

    for (int step = 1; step < num_points_; ++step) {
        if (step % grid_rebuild_freq == 1) {
            buildSpatialGrid();
        }

        int next = findNearestInGrid(current);
        if (next == -1) break;

        visited_[next] = 1;
        route_.push_back(next);
        current = next;
    }

    auto end = std::chrono::high_resolution_clock::now();
    return std::chrono::duration<double>(end - start).count();
}