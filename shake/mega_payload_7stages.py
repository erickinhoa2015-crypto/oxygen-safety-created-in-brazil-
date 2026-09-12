import ctypes
import time
import random
import math

# Windows API functions
GetDC = ctypes.windll.user32.GetDC
ReleaseDC = ctypes.windll.user32.ReleaseDC
GetSystemMetrics = ctypes.windll.user32.GetSystemMetrics
BitBlt = ctypes.windll.gdi32.BitBlt
CreateCompatibleDC = ctypes.windll.gdi32.CreateCompatibleDC
CreateCompatibleBitmap = ctypes.windll.gdi32.CreateCompatibleBitmap
SelectObject = ctypes.windll.gdi32.SelectObject
DeleteObject = ctypes.windll.gdi32.DeleteObject
DeleteDC = ctypes.windll.gdi32.DeleteDC

# ROP codes
SRCCOPY = 0x00CC0020
SRCAND = 0x008800C6
SRCINVERT = 0x00660046
SRCPAINT = 0x00EE0086

def shake_stage(stage_num, name, duration, effect_func):
    print(f"\n{'='*60}")
    print(f"🎬 STAGE {stage_num}: {name}")
    print(f"{'='*60}\n")
    
    screen_dc = GetDC(0)
    w = GetSystemMetrics(0)
    h = GetSystemMetrics(1)
    
    mem_dc = CreateCompatibleDC(screen_dc)
    mem_bitmap = CreateCompatibleBitmap(screen_dc, w, h)
    old_bitmap = SelectObject(mem_dc, mem_bitmap)
    
    start_time = time.time()
    counter = 0
    
    while time.time() - start_time < duration:
        BitBlt(mem_dc, 0, 0, w, h, screen_dc, 0, 0, SRCCOPY)
        effect_func(screen_dc, mem_dc, w, h, counter, time.time() - start_time)
        counter += 1
        time.sleep(0.03)
    
    BitBlt(screen_dc, 0, 0, w, h, mem_dc, 0, 0, SRCCOPY)
    SelectObject(mem_dc, old_bitmap)
    DeleteObject(mem_bitmap)
    DeleteDC(mem_dc)
    ReleaseDC(0, screen_dc)
    
    print(f"✅ STAGE {stage_num} CONCLUÍDO!\n")

# STAGE 1: Tremor Extremo
def stage1(screen_dc, mem_dc, w, h, counter, elapsed):
    offset_x = random.randint(-50, 50)
    offset_y = random.randint(-50, 50)
    BitBlt(screen_dc, offset_x, offset_y, w - abs(offset_x), h - abs(offset_y),
           mem_dc, abs(offset_x) if offset_x < 0 else 0, abs(offset_y) if offset_y < 0 else 0, SRCCOPY)

# STAGE 2: Tremor Alternado
def stage2(screen_dc, mem_dc, w, h, counter, elapsed):
    if counter % 2 == 0:
        offset_x = random.randint(-35, 35)
        offset_y = random.randint(-5, 5)
    else:
        offset_x = random.randint(-5, 5)
        offset_y = random.randint(-35, 35)
    BitBlt(screen_dc, offset_x, offset_y, w - abs(offset_x), h - abs(offset_y),
           mem_dc, abs(offset_x) if offset_x < 0 else 0, abs(offset_y) if offset_y < 0 else 0, SRCCOPY)

# STAGE 3: Tremor Espiral
def stage3(screen_dc, mem_dc, w, h, counter, elapsed):
    angle = (counter * 15) % 360
    radius = 30
    offset_x = int(math.cos(math.radians(angle)) * radius)
    offset_y = int(math.sin(math.radians(angle)) * radius)
    BitBlt(screen_dc, offset_x, offset_y, w - abs(offset_x), h - abs(offset_y),
           mem_dc, abs(offset_x) if offset_x < 0 else 0, abs(offset_y) if offset_y < 0 else 0, SRCCOPY)

# STAGE 4: Glitch Visual
def stage4(screen_dc, mem_dc, w, h, counter, elapsed):
    glitch_x = random.randint(0, w - 100)
    glitch_y = random.randint(0, h - 100)
    glitch_w = random.randint(50, 300)
    glitch_h = random.randint(50, 300)
    BitBlt(screen_dc, glitch_x, glitch_y, glitch_w, glitch_h, screen_dc, glitch_x, glitch_y, SRCINVERT)
    
    shake_x = random.randint(-5, 5)
    shake_y = random.randint(-5, 5)
    BitBlt(screen_dc, shake_x, shake_y, w - abs(shake_x), h - abs(shake_y),
           mem_dc, abs(shake_x) if shake_x < 0 else 0, abs(shake_y) if shake_y < 0 else 0, SRCCOPY)

# STAGE 5: Escurecimento
def stage5(screen_dc, mem_dc, w, h, counter, elapsed):
    shake_x = random.randint(-30, 30)
    shake_y = random.randint(-30, 30)
    
    for i in range(random.randint(1, 3)):
        BitBlt(screen_dc, 0, 0, w, h, screen_dc, 0, 0, SRCAND)
    
    BitBlt(screen_dc, shake_x, shake_y, w - abs(shake_x), h - abs(shake_y),
           mem_dc, abs(shake_x) if shake_x < 0 else 0, abs(shake_y) if shake_y < 0 else 0, SRCCOPY)

# STAGE 6: Flashbang
def stage6(screen_dc, mem_dc, w, h, counter, elapsed):
    shake_x = random.randint(-60, 60)
    shake_y = random.randint(-60, 60)
    
    if counter % 5 == 0:
        for i in range(2):
            BitBlt(screen_dc, 0, 0, w, h, screen_dc, 0, 0, SRCPAINT)
    
    BitBlt(screen_dc, shake_x, shake_y, w - abs(shake_x), h - abs(shake_y),
           mem_dc, abs(shake_x) if shake_x < 0 else 0, abs(shake_y) if shake_y < 0 else 0, SRCCOPY)

# STAGE 7: Tela Multiplicada
def stage7(screen_dc, mem_dc, w, h, counter, elapsed):
    try:
        # Tamanho do tile diminui com o tempo (efeito de aproximação)
        tile_size = max(50, int(300 - (elapsed * 30)))
        tile_size = min(tile_size, w, h)
        
        if tile_size < 10:
            tile_size = 10
        
        # Desenha múltiplas cópias da tela em grades
        x = 0
        while x < w:
            y = 0
            while y < h:
                max_src_x = max(1, w - tile_size)
                max_src_y = max(1, h - tile_size)
                
                src_x = random.randint(0, max_src_x)
                src_y = random.randint(0, max_src_y)
                
                offset_x = random.randint(-5, 5)
                offset_y = random.randint(-5, 5)
                
                copy_w = min(tile_size, w - x)
                copy_h = min(tile_size, h - y)
                
                if copy_w > 0 and copy_h > 0:
                    BitBlt(screen_dc, x + offset_x, y + offset_y, copy_w, copy_h,
                           mem_dc, src_x, src_y, SRCCOPY)
                
                y += tile_size
            x += tile_size
    except:
        pass

# Main execution
print("╔═══════════════════════════════════════════════════════════════╗")
print("║   🎬 PAYLOAD ULTRA 7-STAGE GDI SCREEN DESTROYER 🎬          ║")
print("║              70 SEGUNDOS DE PURO CAOS E TREMOR               ║")
print("║              Cada Stage = 10 segundos                         ║")
print("╚═══════════════════════════════════════════════════════════════╝")

time.sleep(3)

shake_stage(1, "TREMOR EXTREMO 🔥", 10, stage1)
shake_stage(2, "TREMOR ALTERNADO ⚡", 10, stage2)
shake_stage(3, "TREMOR ESPIRAL 🌀", 10, stage3)
shake_stage(4, "GLITCH VISUAL 👾", 10, stage4)
shake_stage(5, "ESCURECIMENTO CAÓTICO 🌑", 10, stage5)
shake_stage(6, "FLASHBANG TOTAL 💥", 10, stage6)
shake_stage(7, "TELA MULTIPLICADA 🔄", 10, stage7)

print("\n╔═══════════════════════════════════════════════════════════════╗")
print("║           ✅ PAYLOAD COMPLETO! 7 STAGES EXECUTADOS! ✅       ║")
print("║                     PREPARE-SE PARA O CAOS!                   ║")
print("╚═══════════════════════════════════════════════════════════════╝\n")
