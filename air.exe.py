"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                                                                               ║
║        🎬 APOCALIPSE GDI - 17 STAGES SEQUENCIAIS EM 170 SEGUNDOS 🎬          ║
║                                                                               ║
║  Junta TODOS os efeitos: Stage 1 → Stage 2 → ... → Stage 17                 ║
║  Cada stage: 10 segundos de puro caos visual                                 ║
║  Apenas GDI - Sem C++ - Python Puro                                          ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""

import ctypes
import time
import random
import math
import os
import tempfile
import wave
import winsound
import threading
import tkinter as tk
from tkinter import ttk
from ctypes import wintypes

# Funções Windows GDI
GetDC = ctypes.windll.user32.GetDC
ReleaseDC = ctypes.windll.user32.ReleaseDC
GetSystemMetrics = ctypes.windll.user32.GetSystemMetrics
BitBlt = ctypes.windll.gdi32.BitBlt
CreateCompatibleDC = ctypes.windll.gdi32.CreateCompatibleDC
CreateCompatibleBitmap = ctypes.windll.gdi32.CreateCompatibleBitmap
SelectObject = ctypes.windll.gdi32.SelectObject
DeleteObject = ctypes.windll.gdi32.DeleteObject
DeleteDC = ctypes.windll.gdi32.DeleteDC

# ROP Codes (Operações Raster)
SRCCOPY = 0x00CC0020      # Cópia direta
SRCINVERT = 0x00660046    # Inversão XOR
SRCAND = 0x008800C6       # AND (escurece)
SRCPAINT = 0x00EE0086     # OR (ilumina)

# GDI drawing helpers
CreateSolidBrush = ctypes.windll.gdi32.CreateSolidBrush
CreatePen = ctypes.windll.gdi32.CreatePen
SelectObject = ctypes.windll.gdi32.SelectObject
DeleteObject = ctypes.windll.gdi32.DeleteObject
Polygon = ctypes.windll.gdi32.Polygon
Rectangle = ctypes.windll.gdi32.Rectangle
Ellipse = ctypes.windll.gdi32.Ellipse
TextOutA = ctypes.windll.gdi32.TextOutA
SetTextColor = ctypes.windll.gdi32.SetTextColor
SetBkMode = ctypes.windll.gdi32.SetBkMode
GetStockObject = ctypes.windll.gdi32.GetStockObject

BLACK_BRUSH = 4
NULL_PEN = 8
TRANSPARENT = 1

STAGE_OPTIONS = [
    (1, "PIXEL STORM ⛈️"),
    (2, "WAVE CASCADE 🌊"),
    (3, "RADIAL BURST 💥"),
    (4, "COLOR SHIFT 🎨"),
    (5, "LIGHT PULSE ✨"),
    (6, "FRACTALS 🔮"),
    (7, "MIRROR TILES 🪟"),
    (8, "VORTEX IMPLOSION 🌀"),
    (9, "KALEIDOSCOPE 🔄"),
    (10, "PRISM SPLIT 🌈"),
    (11, "DISTORTION GRID 📐"),
    (12, "SCANLINE WARP 📺"),
    (13, "BLOCK CASCADE 🧱"),
    (14, "SPIRAL DECAY 🌪️"),
    (15, "CHROMATIC SHIFT 🎭"),
    (16, "TUNNEL ZOOM 🕳️"),
    (17, "CHAOS NOISE 🌀"),
    (18, "ROTATION BLUR ⚙️"),
    (20, "MOSAIC FLOW 🎨"),
    (29, "PARTICLE BURST 💫"),
    (30, "WAVE DISTORTION 〰️"),
    (31, "STRIPE WARP 📊"),
    (32, "PULSE RINGS 🎯"),
    (33, "MIRROR MAZE 🪞"),
    (34, "SINE WAVES 〰️"),
    (35, "STROBE SHIFT ⚡"),
    (36, "CIRCULAR WARP 🔵"),
    (37, "FIZZ BURST ✨"),
    (38, "SHATTER EFFECT 💎"),
    (39, "HYPNOTIC SPIRAL 🌀"),
    (40, "PLASMA VORTEX 🌊"),
]
PAYLOAD_ATIVO = 1
PAINEL_PAYLOAD = None
PAINEL_LOCK = threading.Lock()
STAGE_JUMP_TARGET = None
STOP_PAYLOAD = False
MOUSE_TRACKER_ATIVO = False





def abrir_painel_payload():
    """Abre um painel para selecionar qual stage pular ao pressionar Ctrl+8."""
    global PAINEL_PAYLOAD, PAYLOAD_ATIVO, STAGE_JUMP_TARGET

    with PAINEL_LOCK:
        if PAINEL_PAYLOAD is not None and PAINEL_PAYLOAD.winfo_exists():
            PAINEL_PAYLOAD.deiconify()
            PAINEL_PAYLOAD.focus_force()
            return

        root = tk.Tk()
        root.title("Stage Selector")
        root.geometry("430x220")
        root.configure(bg="#0f1223")
        root.attributes("-topmost", True)
        root.attributes("-toolwindow", True)
        root.resizable(False, False)

        frame = ttk.Frame(root, padding=16)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Escolha o stage para pular:", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(0, 8))

        selected = tk.IntVar(value=PAYLOAD_ATIVO)
        combo = ttk.Combobox(frame, textvariable=selected, state="readonly", width=30)
        combo["values"] = [f"{numero} - {nome}" for numero, nome in STAGE_OPTIONS]
        combo.pack(fill="x", pady=(0, 10))

        def aplicar_payload():
            global STAGE_JUMP_TARGET, PAYLOAD_ATIVO
            stage_num = selected.get()
            if isinstance(stage_num, int):
                PAYLOAD_ATIVO = stage_num
                STAGE_JUMP_TARGET = stage_num
                print(f"\n  🔀 Stage jump ativado para: {stage_num}\n")
            root.destroy()

        ttk.Button(frame, text="Aplicar", command=aplicar_payload).pack(anchor="e", pady=(12, 0))
        root.protocol("WM_DELETE_WINDOW", lambda: (root.destroy(), setattr(globals(), "PAINEL_PAYLOAD", None)))
        PAINEL_PAYLOAD = root
        root.mainloop()


def esconder_painel_payload():
    global PAINEL_PAYLOAD
    try:
        if PAINEL_PAYLOAD is not None and PAINEL_PAYLOAD.winfo_exists():
            PAINEL_PAYLOAD.destroy()
    except Exception:
        pass
    PAINEL_PAYLOAD = None


def desenhar_x_vermelho_mouse():
    """Desenha um X vermelho gigante seguindo o mouse."""
    global MOUSE_TRACKER_ATIVO
    MOUSE_TRACKER_ATIVO = True
    user32 = ctypes.windll.user32
    
    try:
        screen_dc = GetDC(0)
        red_pen = CreatePen(0, 8, 0x0000FF)  # Vermelho em BGR
        old_pen = SelectObject(screen_dc, red_pen)
        
        while MOUSE_TRACKER_ATIVO:
            try:
                pos = wintypes.POINT()
                user32.GetCursorPos(ctypes.byref(pos))
                mx, my = pos.x, pos.y
                size = 80
                
                # Desenha X
                ctypes.windll.gdi32.MoveToEx(screen_dc, mx - size, my - size, None)
                ctypes.windll.gdi32.LineTo(screen_dc, mx + size, my + size)
                ctypes.windll.gdi32.MoveToEx(screen_dc, mx + size, my - size, None)
                ctypes.windll.gdi32.LineTo(screen_dc, mx - size, my + size)
                
                time.sleep(0.05)
            except Exception:
                time.sleep(0.05)
        
        SelectObject(screen_dc, old_pen)
        DeleteObject(red_pen)
        ReleaseDC(0, screen_dc)
    except Exception:
        pass


def finalizar_payload():
    """Finaliza o payload com X vermelho seguindo o mouse."""
    global STOP_PAYLOAD, MOUSE_TRACKER_ATIVO
    STOP_PAYLOAD = True
    print(f"\n{'='*85}")
    print("  🚨 FINALIZAÇÃO ACIONADA! X VERMELHO PERSEGUINDO O MOUSE...")
    print(f"{'='*85}\n")
    
    threading.Thread(target=desenhar_x_vermelho_mouse, daemon=True).start()


def monitorar_hotkeys():
    """Monitora Ctrl+8 (painel de stage) e Ctrl+0 (finalizar com X vermelho)."""
    try:
        user32 = ctypes.windll.user32
        MOD_CONTROL = 0x0002
        VK_8 = 0x38
        VK_0 = 0x30
        
        user32.RegisterHotKey(None, 1, MOD_CONTROL, VK_8)  # Ctrl+8
        user32.RegisterHotKey(None, 2, MOD_CONTROL, VK_0)  # Ctrl+0
        
        msg = wintypes.MSG()
        while True:
            if user32.GetMessageW(ctypes.byref(msg), None, 0, 0) != 0:
                if msg.message == 0x0312:
                    if msg.wParam == 1:
                        abrir_painel_payload()
                    elif msg.wParam == 2:
                        finalizar_payload()
                user32.TranslateMessage(ctypes.byref(msg))
                user32.DispatchMessageW(ctypes.byref(msg))
            time.sleep(0.01)
    except Exception:
        pass


def mostrar_aviso_inicial():
    """Mostra um aviso de segurança em estilo de placa de alerta antes do payload."""
    screen_dc = GetDC(0)
    w = GetSystemMetrics(0)
    h = GetSystemMetrics(1)

    mem_dc = CreateCompatibleDC(screen_dc)
    mem_bitmap = CreateCompatibleBitmap(screen_dc, w, h)
    old_bitmap = SelectObject(mem_dc, mem_bitmap)
    BitBlt(mem_dc, 0, 0, w, h, screen_dc, 0, 0, SRCCOPY)

    bg = CreateSolidBrush(0xE9E9E9)
    old_bg = SelectObject(screen_dc, bg)
    Rectangle(screen_dc, 0, 0, w, h)
    SelectObject(screen_dc, old_bg)
    DeleteObject(bg)

    yellow = CreateSolidBrush(0x00F4F400)
    silver = CreateSolidBrush(0x00C0C0C0)
    black = CreateSolidBrush(0x00000000)
    white = CreateSolidBrush(0x00FFFFFF)

    tri = (
        wintypes.POINT(w // 2, 70),
        wintypes.POINT(w // 2 - 350, h // 2 + 180),
        wintypes.POINT(w // 2 + 350, h // 2 + 180),
    )

    # Borda prateada da placa
    old_silver = SelectObject(screen_dc, silver)
    Polygon(screen_dc, (wintypes.POINT * 3)(*tri), 3)
    SelectObject(screen_dc, old_silver)

    # Triângulo amarelo interno
    inner_tri = (
        wintypes.POINT(w // 2, 120),
        wintypes.POINT(w // 2 - 260, h // 2 + 120),
        wintypes.POINT(w // 2 + 260, h // 2 + 120),
    )
    old_yellow = SelectObject(screen_dc, yellow)
    Polygon(screen_dc, (wintypes.POINT * 3)(*inner_tri), 3)
    SelectObject(screen_dc, old_yellow)

    # Exclamação preta
    old_black = SelectObject(screen_dc, black)
    Rectangle(screen_dc, w // 2 - 35, h // 2 - 80, w // 2 + 35, h // 2 + 120)
    Ellipse(screen_dc, w // 2 - 80, h // 2 + 110, w // 2 + 80, h // 2 + 180)
    SelectObject(screen_dc, old_black)

    # Texto do aviso
    SetBkMode(screen_dc, TRANSPARENT)
    SetTextColor(screen_dc, 0x00000000)
    text_lines = [
        "VOCE TEM CERTEZA?",
        "ESTE ARQUIVO TROLLAGEM CONTEM EPELEPSIA",
        "E O TROLL FOI CRIADO POR @testador de gdi rework",
    ]
    line_y = h // 2 + 200
    for line in text_lines:
        TextOutA(screen_dc, w // 2 - 300, line_y, line, len(line))
        line_y += 50

    DeleteObject(yellow)
    DeleteObject(silver)
    DeleteObject(black)
    DeleteObject(white)

    time.sleep(5)

    BitBlt(screen_dc, 0, 0, w, h, mem_dc, 0, 0, SRCCOPY)
    SelectObject(mem_dc, old_bitmap)
    DeleteObject(mem_bitmap)
    DeleteDC(mem_dc)
    ReleaseDC(0, screen_dc)


def gerar_bytebeat_aleatorio(seed, duracao=10, sample_rate=8000):
    """Gera um bytebeat aleatório em PCM monofônico 8-bit."""
    random.seed(seed)
    a = random.randint(1, 200)
    b = random.randint(1, 200)
    c = random.randint(1, 20)
    d = random.randint(1, 20)
    t = 0
    frames = int(sample_rate * duracao)
    samples = bytearray()

    for _ in range(frames):
        # fórmula bytebeat aleatória, sempre diferente por stage
        value = ((t * a) ^ (t * b) ^ (t >> c) ^ (t >> d)) & 0xFF
        envelope = 180 + int(40 * math.sin(t / 40.0))
        sample = (value + envelope) // 2
        sample = max(0, min(255, sample))
        samples.append(sample)
        t += 1

    return bytes(samples)


def tocar_bytebeat_stage(numero, duracao=10):
    """Cria um arquivo WAV temporário e toca a música aleatória do stage."""
    try:
        winsound.PlaySound(None, 0)
        seed = random.randint(1, 10**9)
        audio_data = gerar_bytebeat_aleatorio(seed, duracao=duracao, sample_rate=8000)

        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, f"bytebeat_stage_{numero}_{seed}.wav")

        with wave.open(temp_path, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(1)
            wav_file.setframerate(8000)
            wav_file.writeframes(audio_data)

        winsound.PlaySound(temp_path, winsound.SND_FILENAME | winsound.SND_ASYNC)
        return temp_path
    except Exception:
        return None


def parar_bytebeat_stage():
    try:
        winsound.PlaySound(None, 0)
    except Exception:
        pass


def executar_stage(numero, nome, duracao=10):
    """Executa um stage específico por 'duracao' segundos"""

    if STOP_PAYLOAD:
        return

    print(f"\n{'='*85}")
    print(f"  🎬 STAGE {numero:2d}: {nome:<50} | Duração: {duracao}s")
    print(f"{'='*85}")
    
    audio_path = tocar_bytebeat_stage(numero, duracao)

    screen_dc = GetDC(0)
    w = GetSystemMetrics(0)
    h = GetSystemMetrics(1)
    
    mem_dc = CreateCompatibleDC(screen_dc)
    mem_bitmap = CreateCompatibleBitmap(screen_dc, w, h)
    old_bitmap = SelectObject(mem_dc, mem_bitmap)
    
    start_time = time.time()
    counter = 0
    
    try:
        # STAGE 1: PIXEL STORM ⛈️
        if numero == 1:
            while time.time() - start_time < duracao and not STOP_PAYLOAD:
                try:
                    BitBlt(mem_dc, 0, 0, w, h, screen_dc, 0, 0, SRCCOPY)
                    
                    # Random pixel displacement storm
                    for _ in range(40):
                        src_x = random.randint(0, max(1, w - 50))
                        src_y = random.randint(0, max(1, h - 50))
                        dst_x = src_x + random.randint(-80, 80)
                        dst_y = src_y + random.randint(-80, 80)
                        
                        size = random.randint(10, 60)
                        if 0 <= dst_x < w and 0 <= dst_y < h:
                            BitBlt(screen_dc, dst_x, dst_y, size, size,
                                   mem_dc, src_x, src_y, SRCCOPY)
                    
                    # Add invert layers
                    for _ in range(3):
                        ix = random.randint(0, w)
                        iy = random.randint(0, h)
                        BitBlt(screen_dc, ix, iy, random.randint(50, 150), random.randint(50, 150),
                               screen_dc, ix, iy, SRCINVERT)
                    
                    counter += 1
                    time.sleep(0.04)
                except:
                    pass
        
        # STAGE 2: WAVE CASCADE 🌊
        elif numero == 2:
            while time.time() - start_time < duracao and not STOP_PAYLOAD:
                try:
                    elapsed = time.time() - start_time
                    BitBlt(mem_dc, 0, 0, w, h, screen_dc, 0, 0, SRCCOPY)
                    
                    # Cascading wave effect
                    for y in range(0, h, 8):
                        wave_offset = int(math.sin((y / 30.0) + elapsed * 6.0) * 60)
                        for x_segment in range(0, w, 40):
                            copy_w = min(40, w - x_segment)
                            if copy_w > 0:
                                BitBlt(screen_dc, x_segment + wave_offset, y, copy_w, 8,
                                       mem_dc, x_segment, y, SRCCOPY)
                    
                    counter += 1
                    time.sleep(0.03)
                except:
                    pass
        
        # STAGE 3: RADIAL BURST 💥
        elif numero == 3:
            while time.time() - start_time < duracao and not STOP_PAYLOAD:
                try:
                    elapsed = time.time() - start_time
                    BitBlt(mem_dc, 0, 0, w, h, screen_dc, 0, 0, SRCCOPY)
                    
                    cx = w // 2
                    cy = h // 2
                    burst_radius = int(50 + elapsed * 200)
                    
                    for angle in range(0, 360, 15):
                        rad = math.radians(angle)
                        x1 = int(cx + math.cos(rad) * burst_radius)
                        y1 = int(cy + math.sin(rad) * burst_radius)
                        
                        if 0 <= x1 < w and 0 <= y1 < h:
                            BitBlt(screen_dc, x1, y1, 30, 30,
                                   mem_dc, max(0, x1-15), max(0, y1-15), SRCCOPY)
                    
                    counter += 1
                    time.sleep(0.04)
                except:
                    pass
        
        # STAGE 4: COLOR SHIFT 🎨
        elif numero == 4:
            while time.time() - start_time < duracao and not STOP_PAYLOAD:
                try:
                    elapsed = time.time() - start_time
                    BitBlt(mem_dc, 0, 0, w, h, screen_dc, 0, 0, SRCCOPY)
                    
                    # Horizontal color shift stripes
                    for i in range(8):
                        shift = int(math.sin((i + elapsed * 5) * 0.8) * w // 3)
                        y_pos = (h // 8) * i
                        BitBlt(screen_dc, shift, y_pos, max(1, w - abs(shift)), h // 8,
                               mem_dc, 0, y_pos, SRCCOPY)
                    
                    counter += 1
                    time.sleep(0.03)
                except:
                    pass
        
        # STAGE 5: LIGHT PULSE ✨
        elif numero == 5:
            while time.time() - start_time < duracao and not STOP_PAYLOAD:
                try:
                    elapsed = time.time() - start_time
                    BitBlt(mem_dc, 0, 0, w, h, screen_dc, 0, 0, SRCCOPY)
                    
                    # Pulsing light from center
                    pulse = int(50 * math.sin(elapsed * 4.0))
                    for _ in range(8):
                        BitBlt(screen_dc, pulse, pulse, max(1, w - pulse*2), max(1, h - pulse*2),
                               mem_dc, 0, 0, SRCPAINT)
                    
                    counter += 1
                    time.sleep(0.05)
                except:
                    pass
        
        # STAGE 6: FRACTALS 🔮
        elif numero == 6:
            while time.time() - start_time < duracao and not STOP_PAYLOAD:
                try:
                    elapsed = time.time() - start_time
                    BitBlt(mem_dc, 0, 0, w, h, screen_dc, 0, 0, SRCCOPY)
                    
                    # Fractal-like recursive squares
                    size = int(100 + 50 * math.sin(elapsed * 3))
                    for _ in range(10):
                        x = random.randint(0, w - size)
                        y = random.randint(0, h - size)
                        BitBlt(screen_dc, x, y, size, size,
                               mem_dc, x, y, SRCINVERT)
                    
                    counter += 1
                    time.sleep(0.04)
                except:
                    pass
        
        # STAGE 7: MIRROR TILES 🪟
        elif numero == 7:
            while time.time() - start_time < duracao and not STOP_PAYLOAD:
                try:
                    elapsed = time.time() - start_time
                    BitBlt(mem_dc, 0, 0, w, h, screen_dc, 0, 0, SRCCOPY)
                    
                    tile_size = 40 + int(30 * math.sin(elapsed * 2.5))
                    for y in range(0, h, tile_size):
                        for x in range(0, w, tile_size):
                            mirror_x = w - x - tile_size
                            if 0 <= mirror_x < w:
                                BitBlt(screen_dc, x, y, tile_size, tile_size,
                                       mem_dc, mirror_x, y, SRCCOPY)
                    
                    time.sleep(0.04)
                except:
                    pass
        
        # STAGE 8: VORTEX IMPLOSION 🌀
        elif numero == 8:
            while time.time() - start_time < duracao and not STOP_PAYLOAD:
                try:
                    elapsed = time.time() - start_time
                    BitBlt(mem_dc, 0, 0, w, h, screen_dc, 0, 0, SRCCOPY)
                    
                    cx = w // 2
                    cy = h // 2
                    
                    for y in range(0, h, 6):
                        for x in range(0, w, 6):
                            dx = x - cx
                            dy = y - cy
                            angle = math.atan2(dy, dx) + elapsed * 3
                            r = math.hypot(dx, dy) * 0.8
                            src_x = int(cx + r * math.cos(angle))
                            src_y = int(cy + r * math.sin(angle))
                            if 0 <= src_x < w and 0 <= src_y < h:
                                BitBlt(screen_dc, x, y, 6, 6,
                                       mem_dc, src_x, src_y, SRCCOPY)
                    
                    time.sleep(0.04)
                except:
                    pass
        
        # STAGE 9: KALEIDOSCOPE 🔄
        elif numero == 9:
            while time.time() - start_time < duracao and not STOP_PAYLOAD:
                try:
                    elapsed = time.time() - start_time
                    BitBlt(mem_dc, 0, 0, w, h, screen_dc, 0, 0, SRCCOPY)
                    
                    cx = w // 2
                    cy = h // 2
                    
                    for i in range(6):
                        angle = (i * 60) + elapsed * 100
                        angle_rad = math.radians(angle)
                        for r in range(50, 300, 30):
                            x = int(cx + r * math.cos(angle_rad))
                            y = int(cy + r * math.sin(angle_rad))
                            if 0 <= x < w and 0 <= y < h:
                                BitBlt(screen_dc, x, y, 20, 20,
                                       mem_dc, x, y, SRCINVERT)
                    
                    time.sleep(0.04)
                except:
                    pass
        
        # STAGE 10: PRISM SPLIT 🌈
        elif numero == 10:
            while time.time() - start_time < duracao and not STOP_PAYLOAD:
                try:
                    elapsed = time.time() - start_time
                    BitBlt(mem_dc, 0, 0, w, h, screen_dc, 0, 0, SRCCOPY)
                    
                    # Vertical prism split
                    splits = 5
                    split_w = w // splits
                    for i in range(splits):
                        offset = int(math.sin((i + elapsed) * 1.5) * 40)
                        x0 = i * split_w
                        BitBlt(screen_dc, x0 + offset, 0, split_w, h,
                               mem_dc, x0, 0, SRCCOPY)
                    
                    time.sleep(0.03)
                except:
                    pass
        
        # STAGE 11: DISTORTION GRID 📐
        elif numero == 11:
            while time.time() - start_time < duracao and not STOP_PAYLOAD:
                try:
                    elapsed = time.time() - start_time
                    BitBlt(mem_dc, 0, 0, w, h, screen_dc, 0, 0, SRCCOPY)
                    
                    grid_size = 30
                    for y in range(0, h, grid_size):
                        for x in range(0, w, grid_size):
                            distort = int(math.sin((x + y) / 50.0 + elapsed * 4) * 15)
                            BitBlt(screen_dc, x + distort, y + distort, grid_size, grid_size,
                                   mem_dc, x, y, SRCCOPY)
                    
                    time.sleep(0.04)
                except:
                    pass
        
        # STAGE 12: SCANLINE WARP 📺
        elif numero == 12:
            while time.time() - start_time < duracao and not STOP_PAYLOAD:
                try:
                    elapsed = time.time() - start_time
                    BitBlt(mem_dc, 0, 0, w, h, screen_dc, 0, 0, SRCCOPY)
                    
                    # Scanline warp effect
                    for y in range(0, h, 3):
                        warp = int(math.sin(elapsed * 5 + y * 0.05) * 80)
                        BitBlt(screen_dc, warp, y, max(1, w - abs(warp)), 3,
                               mem_dc, 0, y, SRCCOPY)
                    
                    time.sleep(0.03)
                except:
                    pass
        
        # STAGE 13: BLOCK CASCADE 🧱
        elif numero == 13:
            while time.time() - start_time < duracao and not STOP_PAYLOAD:
                try:
                    elapsed = time.time() - start_time
                    BitBlt(mem_dc, 0, 0, w, h, screen_dc, 0, 0, SRCCOPY)
                    
                    block_size = int(20 + 30 * math.sin(elapsed * 3))
                    for y in range(0, h, block_size):
                        y_offset = int(math.sin(elapsed + y * 0.01) * 40)
                        for x in range(0, w, block_size):
                            BitBlt(screen_dc, x, y + y_offset, block_size, block_size,
                                   mem_dc, x, y, SRCCOPY)
                    
                    time.sleep(0.04)
                except:
                    pass
        
        # STAGE 14: SPIRAL DECAY 🌪️
        elif numero == 14:
            while time.time() - start_time < duracao and not STOP_PAYLOAD:
                try:
                    elapsed = time.time() - start_time
                    BitBlt(mem_dc, 0, 0, w, h, screen_dc, 0, 0, SRCCOPY)
                    
                    cx = w // 2
                    cy = h // 2
                    decay_factor = 1 - (elapsed / duracao)
                    
                    for i in range(0, 360, 20):
                        for r in range(50, 300, 20):
                            angle_rad = math.radians(i + elapsed * 60)
                            x = int(cx + r * math.cos(angle_rad) * decay_factor)
                            y = int(cy + r * math.sin(angle_rad) * decay_factor)
                            if 0 <= x < w and 0 <= y < h:
                                BitBlt(screen_dc, x, y, 15, 15,
                                       mem_dc, x, y, SRCCOPY)
                    
                    time.sleep(0.04)
                except:
                    pass
        
        # STAGE 15: CHROMATIC SHIFT 🎭
        elif numero == 15:
            while time.time() - start_time < duracao and not STOP_PAYLOAD:
                try:
                    elapsed = time.time() - start_time
                    BitBlt(mem_dc, 0, 0, w, h, screen_dc, 0, 0, SRCCOPY)
                    
                    # RGB channel separation effect
                    shift = int(math.sin(elapsed * 6) * 30)
                    BitBlt(screen_dc, shift, 0, max(1, w - shift), h,
                           mem_dc, 0, 0, SRCCOPY)
                    BitBlt(screen_dc, -shift, 0, max(1, w - shift), h,
                           mem_dc, 0, 0, SRCPAINT)
                    
                    time.sleep(0.03)
                except:
                    pass
        
        # STAGE 16: TUNNEL ZOOM 🕳️
        elif numero == 16:
            while time.time() - start_time < duracao and not STOP_PAYLOAD:
                try:
                    elapsed = time.time() - start_time
                    BitBlt(mem_dc, 0, 0, w, h, screen_dc, 0, 0, SRCCOPY)
                    
                    cx = w // 2
                    cy = h // 2
                    zoom_level = 0.5 + elapsed / duracao
                    
                    for y in range(0, h, 8):
                        for x in range(0, w, 8):
                            dx = (x - cx) / zoom_level
                            dy = (y - cy) / zoom_level
                            src_x = int(cx + dx)
                            src_y = int(cy + dy)
                            if 0 <= src_x < w and 0 <= src_y < h:
                                BitBlt(screen_dc, x, y, 8, 8,
                                       mem_dc, src_x, src_y, SRCCOPY)
                    
                    time.sleep(0.04)
                except:
                    pass
        
        # STAGE 17: CHAOS NOISE 🌀
        elif numero == 17:
            while time.time() - start_time < duracao and not STOP_PAYLOAD:
                try:
                    BitBlt(mem_dc, 0, 0, w, h, screen_dc, 0, 0, SRCCOPY)
                    
                    # Random noise blocks
                    for _ in range(20):
                        nx = random.randint(0, w)
                        ny = random.randint(0, h)
                        nw = random.randint(40, 200)
                        nh = random.randint(40, 200)
                        src_x = random.randint(0, max(1, w - nw))
                        src_y = random.randint(0, max(1, h - nh))
                        
                        BitBlt(screen_dc, nx, ny, min(nw, w - nx), min(nh, h - ny),
                               mem_dc, src_x, src_y, SRCCOPY)
                    
                    for _ in range(10):
                        BitBlt(screen_dc, random.randint(0, w), random.randint(0, h),
                               random.randint(50, 150), random.randint(50, 150),
                               screen_dc, 0, 0, SRCINVERT)
                    
                    time.sleep(0.04)
                except:
                    pass

        # STAGE 18: ROTATION BLUR ⚙️
        elif numero == 18:
            while time.time() - start_time < duracao and not STOP_PAYLOAD:
                try:
                    elapsed = time.time() - start_time
                    cx = w // 2
                    cy = h // 2
                    angle = (elapsed * 200) % 360
                    angle_rad = math.radians(angle)

                    BitBlt(mem_dc, 0, 0, w, h, screen_dc, 0, 0, SRCCOPY)

                    for y in range(0, h, 8):
                        for x in range(0, w, 8):
                            dx = x - cx
                            dy = y - cy
                            rotated_x = int(dx * math.cos(angle_rad) - dy * math.sin(angle_rad))
                            rotated_y = int(dx * math.sin(angle_rad) + dy * math.cos(angle_rad))
                            src_x = cx + rotated_x
                            src_y = cy + rotated_y

                            if 0 <= src_x < w and 0 <= src_y < h:
                                BitBlt(screen_dc, x, y, 8, 8,
                                       mem_dc, src_x, src_y, SRCCOPY)

                    time.sleep(0.04)
                except:
                    pass

        # STAGE 20: MOSAIC FLOW 🎨
        elif numero == 20:
            while time.time() - start_time < duracao and not STOP_PAYLOAD:
                try:
                    elapsed = time.time() - start_time
                    BitBlt(mem_dc, 0, 0, w, h, screen_dc, 0, 0, SRCCOPY)
                    
                    mosaic_size = int(8 + 20 * math.sin(elapsed * 2))
                    for y in range(0, h, mosaic_size):
                        for x in range(0, w, mosaic_size):
                            avg_x = x + (elapsed * 50) % w
                            BitBlt(screen_dc, x, y, mosaic_size, mosaic_size,
                                   mem_dc, int(avg_x) % w, y, SRCCOPY)
                    
                    time.sleep(0.04)
                except:
                    pass

        # STAGE 19: KALEIDOSCOPE 🎪
        elif numero == 19:
            while time.time() - start_time < duracao and not STOP_PAYLOAD:
                try:
                    elapsed = time.time() - start_time
                    BitBlt(mem_dc, 0, 0, w, h, screen_dc, 0, 0, SRCCOPY)
                    
                    cx = w // 2
                    cy = h // 2
                    angle = elapsed * 200
                    
                    for segment in range(6):
                        seg_angle = (segment * 60 + angle) * math.pi / 180
                        for r in range(50, 300, 30):
                            x = int(cx + r * math.cos(seg_angle))
                            y = int(cy + r * math.sin(seg_angle))
                            if 0 <= x < w and 0 <= y < h:
                                BitBlt(screen_dc, x, y, 20, 20, mem_dc, x, y, SRCCOPY)
                    
                    time.sleep(0.04)
                except:
                    pass

        # STAGE 21: FRACTAL ZOOM 🎆
        elif numero == 21:
            while time.time() - start_time < duracao and not STOP_PAYLOAD:
                try:
                    elapsed = time.time() - start_time
                    BitBlt(mem_dc, 0, 0, w, h, screen_dc, 0, 0, SRCCOPY)
                    
                    for _ in range(int(5 + elapsed * 5)):
                        for depth in range(3):
                            size = int(200 / (2 ** depth))
                            x = random.randint(0, w - size)
                            y = random.randint(0, h - size)
                            BitBlt(screen_dc, x, y, size, size,
                                   mem_dc, x, y, SRCCOPY)
                    
                    time.sleep(0.04)
                except:
                    pass

        # STAGE 22: GLITCH WAVE 📡
        elif numero == 22:
            while time.time() - start_time < duracao and not STOP_PAYLOAD:
                try:
                    elapsed = time.time() - start_time
                    BitBlt(mem_dc, 0, 0, w, h, screen_dc, 0, 0, SRCCOPY)
                    
                    for y in range(0, h, 8):
                        glitch_amount = int(math.sin((y / 50) + elapsed * 5) * 100)
                        if 0 <= y < h:
                            BitBlt(screen_dc, glitch_amount, y, max(1, w - abs(glitch_amount)), 8,
                                   mem_dc, 0, y, SRCCOPY)
                    
                    time.sleep(0.03)
                except:
                    pass

        # STAGE 23: RIPPLE CENTER 🌊
        elif numero == 23:
            while time.time() - start_time < duracao and not STOP_PAYLOAD:
                try:
                    elapsed = time.time() - start_time
                    cx, cy = w // 2, h // 2
                    BitBlt(mem_dc, 0, 0, w, h, screen_dc, 0, 0, SRCCOPY)
                    
                    for radius in range(30, 400, 30):
                        ripple = radius + int(20 * math.sin(elapsed * 5 - radius * 0.01))
                        for angle in range(0, 360, 40):
                            rad = math.radians(angle)
                            x = int(cx + ripple * math.cos(rad))
                            y = int(cy + ripple * math.sin(rad))
                            if 0 <= x < w and 0 <= y < h:
                                BitBlt(screen_dc, x, y, 15, 15, mem_dc, x, y, SRCCOPY)
                    
                    time.sleep(0.04)
                except:
                    pass

        # STAGE 24: INVERT BLOCKS 🔲
        elif numero == 24:
            while time.time() - start_time < duracao and not STOP_PAYLOAD:
                try:
                    elapsed = time.time() - start_time
                    block_size = int(20 + 40 * math.sin(elapsed * 3))
                    
                    for y in range(0, h, block_size):
                        for x in range(0, w, block_size):
                            if ((x // block_size) + (y // block_size)) % 2 == 0:
                                BitBlt(screen_dc, x, y, block_size, block_size,
                                       screen_dc, x, y, SRCINVERT)
                    
                    time.sleep(0.04)
                except:
                    pass

        # STAGE 25: COLOR BANDS 🏳️‍🌈
        elif numero == 25:
            while time.time() - start_time < duracao and not STOP_PAYLOAD:
                try:
                    elapsed = time.time() - start_time
                    BitBlt(mem_dc, 0, 0, w, h, screen_dc, 0, 0, SRCCOPY)
                    
                    band_count = int(5 + elapsed)
                    for i in range(band_count):
                        y_pos = int((i / band_count) * h + math.sin(elapsed * 2 + i) * 20)
                        if 0 <= y_pos < h:
                            BitBlt(screen_dc, 0, y_pos, w, h // band_count,
                                   mem_dc, 0, y_pos, SRCCOPY)
                    
                    time.sleep(0.03)
                except:
                    pass

        # STAGE 26: NOISE BURST 💥
        elif numero == 26:
            while time.time() - start_time < duracao and not STOP_PAYLOAD:
                try:
                    elapsed = time.time() - start_time
                    
                    # Heavy random copying for noise effect
                    for _ in range(100):
                        sx = random.randint(0, w - 1)
                        sy = random.randint(0, h - 1)
                        dx = random.randint(0, w - 1)
                        dy = random.randint(0, h - 1)
                        size = random.randint(10, 60)
                        BitBlt(screen_dc, dx, dy, size, size,
                               screen_dc, sx, sy, SRCCOPY)
                    
                    time.sleep(0.02)
                except:
                    pass

        # STAGE 27: LENS DISTORT 🔍
        elif numero == 27:
            while time.time() - start_time < duracao and not STOP_PAYLOAD:
                try:
                    elapsed = time.time() - start_time
                    cx, cy = w // 2, h // 2
                    BitBlt(mem_dc, 0, 0, w, h, screen_dc, 0, 0, SRCCOPY)
                    
                    for y in range(0, h, 10):
                        for x in range(0, w, 10):
                            dx = x - cx
                            dy = y - cy
                            dist = math.hypot(dx, dy)
                            distort = math.sin(elapsed * 3) * 0.8
                            new_dist = dist * (1 + distort)
                            
                            if dist > 0:
                                ratio = new_dist / dist
                                src_x = int(cx + dx * ratio)
                                src_y = int(cy + dy * ratio)
                                if 0 <= src_x < w and 0 <= src_y < h:
                                    BitBlt(screen_dc, x, y, 10, 10,
                                           mem_dc, src_x, src_y, SRCCOPY)
                    
                    time.sleep(0.04)
                except:
                    pass

        # STAGE 28: ACID TRIP 🍄
        elif numero == 28:
            while time.time() - start_time < duracao and not STOP_PAYLOAD:
                try:
                    elapsed = time.time() - start_time
                    BitBlt(mem_dc, 0, 0, w, h, screen_dc, 0, 0, SRCCOPY)
                    
                    # Psychedelic effect: mix of invert, rotate, and wild copying
                    for _ in range(20):
                        for _ in range(5):
                            x = random.randint(0, w - 1)
                            y = random.randint(0, h - 1)
                            size = random.randint(30, 150)
                            BitBlt(screen_dc, x, y, size, size,
                                   screen_dc, (x + int(elapsed * 30)) % w, y, SRCCOPY)
                    
                    if int(elapsed * 5) % 2:
                        BitBlt(screen_dc, 0, 0, w, h, screen_dc, 0, 0, SRCINVERT)
                    
                    time.sleep(0.04)
                except:
                    pass

        # STAGE 29: PARTICLE BURST 💫
        elif numero == 29:
            esconder_painel_payload()
            while time.time() - start_time < duracao and not STOP_PAYLOAD:
                try:
                    elapsed = time.time() - start_time
                    BitBlt(mem_dc, 0, 0, w, h, screen_dc, 0, 0, SRCCOPY)
                    
                    # Particle burst from center
                    cx = w // 2
                    cy = h // 2
                    burst_strength = int(200 * elapsed / duracao)
                    
                    for i in range(50):
                        angle = (i / 50.0) * math.tau
                        dx = int(math.cos(angle) * burst_strength)
                        dy = int(math.sin(angle) * burst_strength)
                        px = cx + dx
                        py = cy + dy
                        
                        if 0 <= px < w and 0 <= py < h:
                            BitBlt(screen_dc, px, py, 20, 20,
                                   mem_dc, px, py, SRCINVERT)
                    
                    time.sleep(0.04)
                except:
                    pass

        # STAGE 30: WAVE DISTORTION 〰️
        elif numero == 30:
            while time.time() - start_time < duracao and not STOP_PAYLOAD:
                try:
                    elapsed = time.time() - start_time
                    BitBlt(mem_dc, 0, 0, w, h, screen_dc, 0, 0, SRCCOPY)
                    
                    for y in range(0, h, 6):
                        wave_x = int(math.sin((y / 50.0) + elapsed * 4) * 60)
                        wave_y = int(math.cos((y / 40.0) + elapsed * 3.5) * 30)
                        
                        if 0 <= y + wave_y < h:
                            BitBlt(screen_dc, wave_x, y + wave_y, max(1, w - abs(wave_x)), 6,
                                   mem_dc, 0, y, SRCCOPY)
                    
                    time.sleep(0.03)
                except:
                    pass

        # STAGE 31: STRIPE WARP 📊
        elif numero == 31:
            while time.time() - start_time < duracao and not STOP_PAYLOAD:
                try:
                    elapsed = time.time() - start_time
                    BitBlt(mem_dc, 0, 0, w, h, screen_dc, 0, 0, SRCCOPY)
                    
                    for x in range(0, w, 10):
                        shear = int(math.cos((x / 20.0) + elapsed * 5) * 50)
                        BitBlt(screen_dc, x + shear, 0, 10, h,
                               mem_dc, x, 0, SRCCOPY)
                    
                    time.sleep(0.03)
                except:
                    pass

        # STAGE 32: PULSE RINGS 🎯
        elif numero == 32:
            while time.time() - start_time < duracao and not STOP_PAYLOAD:
                try:
                    elapsed = time.time() - start_time
                    BitBlt(mem_dc, 0, 0, w, h, screen_dc, 0, 0, SRCCOPY)
                    
                    cx = w // 2
                    cy = h // 2
                    pulse = int(30 + 50 * math.sin(elapsed * 5))
                    
                    for radius in range(20, 400, 40):
                        r = radius + pulse
                        for angle in range(0, 360, 30):
                            rad = math.radians(angle)
                            x = int(cx + r * math.cos(rad))
                            y = int(cy + r * math.sin(rad))
                            if 0 <= x < w and 0 <= y < h:
                                BitBlt(screen_dc, x, y, 25, 25,
                                       mem_dc, x, y, SRCCOPY)
                    
                    time.sleep(0.04)
                except:
                    pass

        # STAGE 33: MIRROR MAZE 🪞
        elif numero == 33:
            while time.time() - start_time < duracao and not STOP_PAYLOAD:
                try:
                    elapsed = time.time() - start_time
                    BitBlt(mem_dc, 0, 0, w, h, screen_dc, 0, 0, SRCCOPY)
                    
                    for x in range(0, w, 30):
                        for y in range(0, h, 30):
                            mirror_y = h - y if ((x + y) // 30) % 2 else y
                            BitBlt(screen_dc, x, y, 30, 30,
                                   mem_dc, x, mirror_y, SRCCOPY)
                    
                    time.sleep(0.04)
                except:
                    pass

        # STAGE 34: SINE WAVES 〰️
        elif numero == 34:
            while time.time() - start_time < duracao and not STOP_PAYLOAD:
                try:
                    elapsed = time.time() - start_time
                    BitBlt(mem_dc, 0, 0, w, h, screen_dc, 0, 0, SRCCOPY)
                    
                    for y in range(0, h, 4):
                        sine1 = int(math.sin((y / 30.0) + elapsed * 3) * 40)
                        sine2 = int(math.cos((y / 25.0) + elapsed * 2.5) * 35)
                        offset = sine1 + sine2
                        
                        BitBlt(screen_dc, offset, y, max(1, w - abs(offset)), 4,
                               mem_dc, 0, y, SRCCOPY)
                    
                    time.sleep(0.03)
                except:
                    pass

        # STAGE 35: STROBE SHIFT ⚡
        elif numero == 35:
            while time.time() - start_time < duracao and not STOP_PAYLOAD:
                try:
                    elapsed = time.time() - start_time
                    shift = int(60 * math.sin(elapsed * 8))
                    BitBlt(mem_dc, 0, 0, w, h, screen_dc, 0, 0, SRCCOPY)
                    BitBlt(screen_dc, shift, 0, max(1, w - abs(shift)), h, mem_dc, 0, 0, SRCCOPY)
                    if int(elapsed * 10) % 2:
                        BitBlt(screen_dc, 0, 0, w, h, screen_dc, 0, 0, SRCINVERT)
                    time.sleep(0.02)
                except:
                    pass

        # STAGE 36: CIRCULAR WARP 🔵
        elif numero == 36:
            while time.time() - start_time < duracao and not STOP_PAYLOAD:
                try:
                    elapsed = time.time() - start_time
                    cx, cy = w // 2, h // 2
                    BitBlt(mem_dc, 0, 0, w, h, screen_dc, 0, 0, SRCCOPY)
                    
                    for angle in range(0, 360, 10):
                        rad = math.radians(angle + elapsed * 120)
                        for radius in range(50, 300, 30):
                            x = int(cx + radius * math.cos(rad))
                            y = int(cy + radius * math.sin(rad))
                            if 0 <= x < w and 0 <= y < h:
                                BitBlt(screen_dc, x, y, 18, 18, mem_dc, x, y, SRCCOPY)
                    
                    time.sleep(0.04)
                except:
                    pass

        # STAGE 37: FIZZ BURST ✨
        elif numero == 37:
            while time.time() - start_time < duracao and not STOP_PAYLOAD:
                try:
                    elapsed = time.time() - start_time
                    BitBlt(mem_dc, 0, 0, w, h, screen_dc, 0, 0, SRCCOPY)
                    
                    for _ in range(40):
                        x = random.randint(0, w)
                        y = random.randint(0, h)
                        size = random.randint(5, 30)
                        offset = int(20 * math.sin(elapsed + x * 0.01) * math.cos(elapsed + y * 0.01))
                        
                        BitBlt(screen_dc, x + offset, y + offset, size, size,
                               mem_dc, x, y, SRCCOPY)
                    
                    time.sleep(0.04)
                except:
                    pass

        # STAGE 38: SHATTER EFFECT 💎
        elif numero == 38:
            while time.time() - start_time < duracao and not STOP_PAYLOAD:
                try:
                    elapsed = time.time() - start_time
                    BitBlt(mem_dc, 0, 0, w, h, screen_dc, 0, 0, SRCCOPY)
                    
                    shatter_factor = elapsed / duracao
                    for _ in range(30):
                        sx = random.randint(0, w)
                        sy = random.randint(0, h)
                        sw = random.randint(20, 100)
                        sh = random.randint(20, 100)
                        dx = int((random.random() - 0.5) * 300 * shatter_factor)
                        dy = int((random.random() - 0.5) * 300 * shatter_factor)
                        
                        if 0 <= sx + dx < w and 0 <= sy + dy < h:
                            BitBlt(screen_dc, sx + dx, sy + dy, sw, sh,
                                   mem_dc, sx, sy, SRCCOPY)
                    
                    time.sleep(0.04)
                except:
                    pass

        # STAGE 39: HYPNOTIC SPIRAL 🌀
        elif numero == 39:
            while time.time() - start_time < duracao and not STOP_PAYLOAD:
                try:
                    elapsed = time.time() - start_time
                    BitBlt(mem_dc, 0, 0, w, h, screen_dc, 0, 0, SRCCOPY)
                    
                    cx = w // 2
                    cy = h // 2
                    for i in range(0, 400, 20):
                        angle = (elapsed * 200 + i * 5) % 360
                        rad = math.radians(angle)
                        x = int(cx + i * math.cos(rad))
                        y = int(cy + i * math.sin(rad))
                        if 0 <= x < w and 0 <= y < h:
                            BitBlt(screen_dc, x, y, 25, 25, mem_dc, x, y, SRCCOPY)
                    
                    time.sleep(0.04)
                except:
                    pass

        # STAGE 40: PLASMA VORTEX 🌊
        elif numero == 40:
            while time.time() - start_time < duracao and not STOP_PAYLOAD:
                try:
                    elapsed = time.time() - start_time
                    cx = w // 2
                    cy = h // 2
                    BitBlt(mem_dc, 0, 0, w, h, screen_dc, 0, 0, SRCCOPY)

                    for y in range(0, h, 10):
                        for x in range(0, w, 10):
                            dx = x - cx
                            dy = y - cy
                            angle = math.atan2(dy, dx) - elapsed * 4
                            r = math.hypot(dx, dy) * 1.2
                            src_x = int(cx + r * math.cos(angle))
                            src_y = int(cy + r * math.sin(angle))
                            if 0 <= src_x < w and 0 <= src_y < h:
                                BitBlt(screen_dc, x, y, 10, 10,
                                       mem_dc, src_x, src_y, SRCCOPY)

                    time.sleep(0.04)
                except:
                    pass

    finally:
        parar_bytebeat_stage()
        if audio_path and os.path.exists(audio_path):
            try:
                os.remove(audio_path)
            except Exception:
                pass

        # Restaura a tela
        try:
            BitBlt(screen_dc, 0, 0, w, h, mem_dc, 0, 0, SRCCOPY)
        except:
            pass
        
        # Limpa recursos
        try:
            SelectObject(mem_dc, old_bitmap)
            DeleteObject(mem_bitmap)
            DeleteDC(mem_dc)
            ReleaseDC(0, screen_dc)
        except:
            pass
    
    print(f"  ✅ Stage {numero} COMPLETO!")


def main():
    """Executa todos os stages sequencialmente"""

    threading.Thread(target=monitorar_hotkeys, daemon=True).start()

    print("\n" + "=" * 85)
    print("  " + "🎬" * 20)
    print("  " + " " * 20 + "APOCALIPSE GDI - 17 STAGES")
    print("  " + " " * 15 + "170 SEGUNDOS DE PURO CAOS VISUAL")
    print("  " + "🎬" * 20)
    print("=" * 85)

    mostrar_aviso_inicial()
    print("\n  Iniciando em 5 segundos...\n")
    time.sleep(5)

    stages = STAGE_OPTIONS

    for numero, nome in stages:
        global STAGE_JUMP_TARGET
        if STOP_PAYLOAD:
            break
        if STAGE_JUMP_TARGET is not None and numero < STAGE_JUMP_TARGET:
            print(f"  ⏭️  Pulando stage {numero} para ir direto ao {STAGE_JUMP_TARGET}")
            continue
        if STAGE_JUMP_TARGET is not None and numero == STAGE_JUMP_TARGET:
            print(f"  🎯 Saltando diretamente para stage {STAGE_JUMP_TARGET}")
            STAGE_JUMP_TARGET = None
        executar_stage(numero, nome, duracao=10)
        time.sleep(0.5)

    print("\n" + "=" * 85)
    print("  " + "🎭" * 20)
    print("  " + " " * 15 + "✅ APOCALIPSE COMPLETO! ✅")
    print("  " + " " * 10 + "FIM DO CAOS! A TELA NUNCA MAIS SERÁ A MESMA!")
    print("  " + "🎭" * 20)
    print("=" * 85 + "\n")


if __name__ == "__main__":
    main()
