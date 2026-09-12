#include <windows.h>
#include <chrono>
#include <thread>
#include <random>
#include <iostream>

int main() {
    // Get the screen device context
    HDC screenDC = GetDC(NULL);
    
    if (screenDC == NULL) {
        std::cerr << "Failed to get screen DC\n";
        return 1;
    }

    // Get screen dimensions
    int screenWidth = GetSystemMetrics(SM_CXSCREEN);
    int screenHeight = GetSystemMetrics(SM_CYSCREEN);

    // Create compatible device context and bitmap
    HDC memDC = CreateCompatibleDC(screenDC);
    HBITMAP memBitmap = CreateCompatibleBitmap(screenDC, screenWidth, screenHeight);
    HBITMAP oldBitmap = (HBITMAP)SelectObject(memDC, memBitmap);

    std::cout << "Screen shake starting for 10 seconds...\n";

    // Shake duration - 10 seconds
    auto startTime = std::chrono::high_resolution_clock::now();
    auto endTime = startTime + std::chrono::seconds(10);

    // Random number generator for shake effect
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_int_distribution<> dis(-15, 15);  // Shake intensity

    // Shake the screen
    while (std::chrono::high_resolution_clock::now() < endTime) {
        // Copy current screen to memory DC
        BitBlt(memDC, 0, 0, screenWidth, screenHeight, screenDC, 0, 0, SRCCOPY);

        // Generate random offsets for shake effect
        int offsetX = dis(gen);
        int offsetY = dis(gen);

        // Copy back with offset to create shake
        BitBlt(screenDC, offsetX, offsetY, screenWidth - abs(offsetX), screenHeight - abs(offsetY), 
               memDC, offsetX < 0 ? -offsetX : 0, offsetY < 0 ? -offsetY : 0, SRCCOPY);

        // Sleep for short time to create flickering shake effect
        std::this_thread::sleep_for(std::chrono::milliseconds(20));
    }

    // Restore original screen content
    BitBlt(screenDC, 0, 0, screenWidth, screenHeight, memDC, 0, 0, SRCCOPY);

    // Clean up resources
    SelectObject(memDC, oldBitmap);
    DeleteObject(memBitmap);
    DeleteDC(memDC);
    ReleaseDC(NULL, screenDC);

    std::cout << "Screen shake stopped!\n";

    return 0;
}
