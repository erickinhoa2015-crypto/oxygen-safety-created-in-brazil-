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
    (1, "TREMOR EXTREMO 🔥"),
    (2, "TREMOR ALTERNADO ⚡"),
    (3, "TREMOR ESPIRAL 🌀"),
    (4, "GLITCH VISUAL 👾"),
    (5, "ESCURECIMENTO CAÓTICO 🌑"),
    (6, "FLASHBANG TOTAL 💥"),
    (7, "TELA MULTIPLICADA 🔄"),
    (8, "SPIRAL EXTREMO 🌪️"),
    (9, "DISTORÇÃO DE ZOOM 🔍"),
    (10, "EFEITO ESPELHO 🪞"),
    (11, "ONDAS HORIZONTAIS 〰️"),
    (12, "LINHAS VARRIDAS 📟"),
    (13, "PIXELAÇÃO PROGRESSIVA 🔲"),
    (14, "DESINTEGRAÇÃO LATERAL ☠️"),
    (15, "CORTINA DE FOGO 🔥"),
    (16, "EFEITO TUNNEL 🌀"),
    (17, "RISCO DE LOUCURA 🎭"),
    (18, "TELA RODANDO 🔄"),
    (20, "DISTORÇÃO DE CORES 🌈"),
    (29, "DVD 3D BOUNCE + MORFO"),
    (30, "CHROMA WARP 🌈"),
    (31, "RAINBOW SHEAR 🧪"),
    (32, "RGB PULSE 💥"),
    (33, "PRISM MIRROR 🌫️"),
    (34, "SPECTRUM CURVE 🌀"),
    (35, "DUAL SHIFT STROBE 🚨"),
    (36, "RAINBOW VORTEX 🪐"),
    (37, "FIZZ CHROMA ✨"),
    (38, "PRISM SLICES 🔷"),
    (39, "FINAL SPECTRUM 😵"),
    (40, "FAST SPIN ROTATE ⚙️"),
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
        # STAGE 1: TREMOR EXTREMO 🔥
        if numero == 1:
            while time.time() - start_time < duracao and not STOP_PAYLOAD:
                try:
                    BitBlt(mem_dc, 0, 0, w, h, screen_dc, 0, 0, SRCCOPY)
                    offset_x = random.randint(-50, 50)
                    offset_y = random.randint(-50, 50)
                    BitBlt(screen_dc, offset_x, offset_y, w, h, mem_dc, 0, 0, SRCCOPY)
                    time.sleep(0.01)
                except:
                    pass
        
        # STAGE 2: TREMOR ALTERNADO ⚡
        elif numero == 2:
            while time.time() - start_time < duracao and not STOP_PAYLOAD:
                try:
                    BitBlt(mem_dc, 0, 0, w, h, screen_dc, 0, 0, SRCCOPY)
                    if counter % 2 == 0:
                        offset_x = random.randint(-35, 35)
                        offset_y = random.randint(-5, 5)
                    else:
                        offset_x = random.randint(-5, 5)
                        offset_y = random.randint(-35, 35)
                    BitBlt(screen_dc, offset_x, offset_y, w, h, mem_dc, 0, 0, SRCCOPY)
                    counter += 1
                    time.sleep(0.03)
                except:
                    pass
        
        # STAGE 3: TREMOR ESPIRAL 🌀
        elif numero == 3:
            while time.time() - start_time < duracao and not STOP_PAYLOAD:
                try:
                    BitBlt(mem_dc, 0, 0, w, h, screen_dc, 0, 0, SRCCOPY)
                    angle = (counter * 15) % 360
                    radius = 30
                    offset_x = int(math.cos(math.radians(angle)) * radius)
                    offset_y = int(math.sin(math.radians(angle)) * radius)
                    
                    if offset_x >= 0 and offset_y >= 0:
                        BitBlt(screen_dc, offset_x, offset_y, w-offset_x, h-offset_y, 
                               mem_dc, 0, 0, SRCCOPY)
                    
                    counter += 1
                    time.sleep(0.03)
                except:
                    pass
        
        # STAGE 4: GLITCH VISUAL 👾
        elif numero == 4:
            while time.time() - start_time < duracao and not STOP_PAYLOAD:
                try:
                    BitBlt(mem_dc, 0, 0, w, h, screen_dc, 0, 0, SRCCOPY)
                    for _ in range(random.randint(5, 15)):
                        gx = random.randint(0, max(1, w-100))
                        gy = random.randint(0, max(1, h-100))
                        gw = random.randint(50, 300)
                        gh = random.randint(50, 300)
                        BitBlt(screen_dc, gx, gy, min(gw, w-gx), min(gh, h-gy),
                               screen_dc, gx, gy, SRCINVERT)
                    time.sleep(0.05)
                except:
                    pass
        
        # STAGE 5: ESCURECIMENTO CAÓTICO 🌑
        elif numero == 5:
            while time.time() - start_time < duracao and not STOP_PAYLOAD:
                try:
                    BitBlt(mem_dc, 0, 0, w, h, screen_dc, 0, 0, SRCCOPY)
                    for _ in range(random.randint(1, 3)):
                        BitBlt(screen_dc, 0, 0, w, h, screen_dc, 0, 0, SRCAND)
                    time.sleep(0.05)
                except:
                    pass
        
        # STAGE 6: FLASHBANG TOTAL 💥
        elif numero == 6:
            while time.time() - start_time < duracao and not STOP_PAYLOAD:
                try:
                    BitBlt(mem_dc, 0, 0, w, h, screen_dc, 0, 0, SRCCOPY)
                    if counter % 5 == 0:
                        for _ in range(2):
                            BitBlt(screen_dc, 0, 0, w, h, screen_dc, 0, 0, SRCPAINT)
                    
                    offset_x = random.randint(-60, 60)
                    offset_y = random.randint(-60, 60)
                    BitBlt(screen_dc, offset_x, offset_y, w, h, mem_dc, 0, 0, SRCCOPY)
                    
                    counter += 1
                    time.sleep(0.02)
                except:
                    pass
        
        # STAGE 7: TELA MULTIPLICADA 🔄
        elif numero == 7:
            while time.time() - start_time < duracao and not STOP_PAYLOAD:
                try:
                    elapsed = time.time() - start_time
                    BitBlt(mem_dc, 0, 0, w, h, screen_dc, 0, 0, SRCCOPY)
                    
                    tile_size = max(50, int(300 - (elapsed * 30)))
                    tile_size = min(tile_size, min(w, h))
                    tile_size = max(10, tile_size)
                    
                    x = 0
                    while x < w:
                        y = 0
                        while y < h:
                            try:
                                max_sx = max(1, w - tile_size)
                                max_sy = max(1, h - tile_size)
                                src_x = random.randint(0, max_sx)
                                src_y = random.randint(0, max_sy)
                                offset_x = random.randint(-5, 5)
                                offset_y = random.randint(-5, 5)
                                
                                copy_w = min(tile_size, w - x)
                                copy_h = min(tile_size, h - y)
                                
                                if copy_w > 0 and copy_h > 0:
                                    BitBlt(screen_dc, x + offset_x, y + offset_y, copy_w, copy_h,
                                           mem_dc, src_x, src_y, SRCCOPY)
                            except:
                                pass
                            y += tile_size
                        x += tile_size
                    
                    time.sleep(0.04)
                except:
                    pass
        
        # STAGE 8: SPIRAL EXTREMO 🌪️
        elif numero == 8:
            while time.time() - start_time < duracao and not STOP_PAYLOAD:
                try:
                    elapsed = time.time() - start_time
                    BitBlt(mem_dc, 0, 0, w, h, screen_dc, 0, 0, SRCCOPY)
                    
                    angle = (counter * 30) % 360
                    radius = int(100 + 50 * math.sin(counter * 0.1))
                    offset_x = int(math.cos(math.radians(angle)) * radius) + random.randint(-10, 10)
                    offset_y = int(math.sin(math.radians(angle)) * radius) + random.randint(-10, 10)
                    
                    if offset_x >= 0 and offset_y >= 0:
                        BitBlt(screen_dc, offset_x, offset_y, w-offset_x, h-offset_y,
                               mem_dc, 0, 0, SRCCOPY)
                    
                    counter += 1
                    time.sleep(0.03)
                except:
                    pass
        
        # STAGE 9: DISTORÇÃO DE ZOOM 🔍
        elif numero == 9:
            while time.time() - start_time < duracao and not STOP_PAYLOAD:
                try:
                    BitBlt(mem_dc, 0, 0, w, h, screen_dc, 0, 0, SRCCOPY)
                    
                    for _ in range(random.randint(2, 5)):
                        zoom_x = random.randint(0, max(1, w - 200))
                        zoom_y = random.randint(0, max(1, h - 200))
                        zoom_w = random.randint(100, 300)
                        zoom_h = random.randint(100, 300)
                        
                        source_offset = random.randint(-50, 50)
                        src_x = max(0, min(zoom_x + source_offset, w - zoom_w))
                        src_y = max(0, min(zoom_y + source_offset, h - zoom_h))
                        
                        BitBlt(screen_dc, zoom_x, zoom_y, zoom_w, zoom_h,
                               mem_dc, src_x, src_y, SRCCOPY)
                    
                    time.sleep(0.05)
                except:
                    pass
        
        # STAGE 10: EFEITO ESPELHO 🪞
        elif numero == 10:
            while time.time() - start_time < duracao and not STOP_PAYLOAD:
                try:
                    BitBlt(mem_dc, 0, 0, w, h, screen_dc, 0, 0, SRCCOPY)
                    
                    center_x = w // 2
                    center_y = h // 2
                    mirror_offset_x = random.randint(-20, 20)
                    mirror_offset_y = random.randint(-20, 20)
                    
                    for offset in range(0, w // 2, random.randint(10, 30)):
                        BitBlt(screen_dc, center_x + offset + mirror_offset_x, 0, 100, h,
                               mem_dc, center_x - offset, 0, SRCCOPY)
                    
                    for offset in range(0, h // 2, random.randint(10, 30)):
                        BitBlt(screen_dc, 0, center_y + offset + mirror_offset_y, w, 100,
                               mem_dc, 0, center_y - offset, SRCCOPY)
                    
                    time.sleep(0.03)
                except:
                    pass
        
        # STAGE 11: ONDAS HORIZONTAIS 〰️
        elif numero == 11:
            while time.time() - start_time < duracao and not STOP_PAYLOAD:
                try:
                    elapsed = time.time() - start_time
                    BitBlt(mem_dc, 0, 0, w, h, screen_dc, 0, 0, SRCCOPY)
                    
                    for y in range(0, h, 5):
                        wave_offset = int(20 * math.sin((y / 50) + elapsed * 3))
                        
                        if 0 <= y + wave_offset < h:
                            src_x = abs(wave_offset) if wave_offset < 0 else 0
                            copy_w = w - abs(wave_offset)
                            
                            if copy_w > 0:
                                BitBlt(screen_dc, wave_offset, y, copy_w, 5,
                                       mem_dc, src_x, y, SRCCOPY)
                    
                    time.sleep(0.04)
                except:
                    pass
        
        # STAGE 12: LINHAS VARRIDAS 📟
        elif numero == 12:
            while time.time() - start_time < duracao and not STOP_PAYLOAD:
                try:
                    elapsed = time.time() - start_time
                    line_position = int((elapsed) * 500) % h
                    
                    for offset in range(-100, h + 100, 20):
                        y = (line_position + offset) % h
                        if 0 <= y < h:
                            BitBlt(screen_dc, 0, y, w, min(3, h - y),
                                   screen_dc, 0, y, SRCINVERT)
                    
                    time.sleep(0.04)
                except:
                    pass
        
        # STAGE 13: PIXELAÇÃO PROGRESSIVA 🔲
        elif numero == 13:
            while time.time() - start_time < duracao and not STOP_PAYLOAD:
                try:
                    elapsed = time.time() - start_time
                    BitBlt(mem_dc, 0, 0, w, h, screen_dc, 0, 0, SRCCOPY)
                    
                    pixel_size = int(2 + (elapsed * 10))
                    
                    x = 0
                    while x < w:
                        y = 0
                        while y < h:
                            src_x = (x // pixel_size) * pixel_size
                            src_y = (y // pixel_size) * pixel_size
                            copy_w = min(pixel_size, w - x)
                            copy_h = min(pixel_size, h - y)
                            
                            if copy_w > 0 and copy_h > 0:
                                BitBlt(screen_dc, x, y, copy_w, copy_h,
                                       mem_dc, src_x, src_y, SRCCOPY)
                            
                            y += pixel_size
                        x += pixel_size
                    
                    time.sleep(0.04)
                except:
                    pass
        
        # STAGE 14: DESINTEGRAÇÃO LATERAL ☠️
        elif numero == 14:
            while time.time() - start_time < duracao and not STOP_PAYLOAD:
                try:
                    elapsed = time.time() - start_time
                    BitBlt(mem_dc, 0, 0, w, h, screen_dc, 0, 0, SRCCOPY)
                    
                    remaining_width = int(w * (1 - (elapsed / duracao)))
                    if remaining_width > 0:
                        BitBlt(screen_dc, w - remaining_width, 0, remaining_width, h,
                               mem_dc, w - remaining_width, 0, SRCCOPY)
                    
                    for _ in range(20):
                        glitch_x = random.randint(max(0, w - remaining_width - 100), max(1, w - remaining_width))
                        glitch_y = random.randint(0, max(1, h - 1))
                        glitch_w = random.randint(10, 50)
                        glitch_h = random.randint(10, 50)
                        BitBlt(screen_dc, glitch_x, glitch_y, glitch_w, glitch_h,
                               screen_dc, 0, 0, 0x00220326)
                    
                    time.sleep(0.04)
                except:
                    pass
        
        # STAGE 15: CORTINA DE FOGO 🔥
        elif numero == 15:
            while time.time() - start_time < duracao and not STOP_PAYLOAD:
                try:
                    elapsed = time.time() - start_time
                    BitBlt(mem_dc, 0, 0, w, h, screen_dc, 0, 0, SRCCOPY)
                    
                    curtain_position = int(h * (1 - (elapsed / duracao)))
                    if curtain_position > 0 and curtain_position < h:
                        BitBlt(screen_dc, 0, curtain_position, w, h - curtain_position,
                               mem_dc, 0, curtain_position, SRCCOPY)
                    
                    for _ in range(50):
                        fire_x = random.randint(0, max(1, w - 1))
                        fire_y = curtain_position + random.randint(-50, 50)
                        fire_w = random.randint(20, 100)
                        fire_h = random.randint(5, 30)
                        
                        if 0 <= fire_y < h:
                            BitBlt(screen_dc, fire_x, fire_y, min(fire_w, w - fire_x), fire_h,
                                   screen_dc, 0, 0, SRCINVERT)
                    
                    time.sleep(0.04)
                except:
                    pass
        
        # STAGE 16: EFEITO TUNNEL 🌀
        elif numero == 16:
            while time.time() - start_time < duracao and not STOP_PAYLOAD:
                try:
                    elapsed = time.time() - start_time
                    BitBlt(mem_dc, 0, 0, w, h, screen_dc, 0, 0, SRCCOPY)
                    
                    center_x = w // 2
                    center_y = h // 2
                    
                    for radius in range(50, int(400 + elapsed * 100), 30):
                        for angle in range(0, 360, 30):
                            rad = math.radians(angle)
                            x1 = int(center_x + radius * math.cos(rad))
                            y1 = int(center_y + radius * math.sin(rad))
                            
                            if 0 <= x1 < w and 0 <= y1 < h:
                                src_x = (x1 + int(elapsed * 50)) % w
                                src_y = (y1 + int(elapsed * 50)) % h
                                BitBlt(screen_dc, x1, y1, 20, 20,
                                       mem_dc, src_x, src_y, SRCCOPY)
                    
                    time.sleep(0.04)
                except:
                    pass
        
        # STAGE 17: RISCO DE LOUCURA 🎭
        elif numero == 17:
            while time.time() - start_time < duracao and not STOP_PAYLOAD:
                try:
                    BitBlt(mem_dc, 0, 0, w, h, screen_dc, 0, 0, SRCCOPY)
                    
                    # Linhas aleatórias que "arranhão" a tela
                    for _ in range(random.randint(10, 30)):
                        x1 = random.randint(0, w)
                        y1 = random.randint(0, h)
                        x2 = (x1 + random.randint(-200, 200)) % w
                        y2 = (y1 + random.randint(-200, 200)) % h
                        
                        line_width = random.randint(1, 10)
                        line_height = random.randint(1, 10)
                        
                        for step in range(0, 200, 10):
                            progress = step / 200.0
                            x = int(x1 + (x2 - x1) * progress)
                            y = int(y1 + (y2 - y1) * progress)
                            
                            if 0 <= x < w and 0 <= y < h:
                                BitBlt(screen_dc, x, y, line_width, line_height,
                                       screen_dc, x, y, SRCINVERT)
                    
                    # Glitches aleatórios
                    for _ in range(random.randint(5, 15)):
                        glitch_x = random.randint(0, max(1, w - 1))
                        glitch_y = random.randint(0, max(1, h - 1))
                        glitch_w = random.randint(50, 150)
                        glitch_h = random.randint(10, 50)
                        offset_x = random.randint(-30, 30)
                        offset_y = random.randint(-30, 30)
                        
                        BitBlt(screen_dc, glitch_x + offset_x, glitch_y, 
                               min(glitch_w, w - glitch_x - offset_x), glitch_h,
                               mem_dc, glitch_x, glitch_y, SRCCOPY)
                    
                    time.sleep(0.04)
                except:
                    pass

        # STAGE 18: TELA RODANDO 🔄
        elif numero == 18:
            while time.time() - start_time < duracao and not STOP_PAYLOAD:
                try:
                    elapsed = time.time() - start_time
                    center_x = w // 2
                    center_y = h // 2
                    angle = (elapsed * 80) % 360
                    angle_rad = math.radians(angle)

                    BitBlt(mem_dc, 0, 0, w, h, screen_dc, 0, 0, SRCCOPY)

                    for y in range(0, h, 4):
                        for x in range(0, w, 4):
                            dx = x - center_x
                            dy = y - center_y
                            rotated_x = int(dx * math.cos(angle_rad) - dy * math.sin(angle_rad))
                            rotated_y = int(dx * math.sin(angle_rad) + dy * math.cos(angle_rad))
                            src_x = center_x + rotated_x
                            src_y = center_y + rotated_y

                            if 0 <= src_x < w and 0 <= src_y < h:
                                BitBlt(screen_dc, x, y, 4, 4,
                                       mem_dc, src_x, src_y, SRCCOPY)

                    time.sleep(0.025)
                except:
                    pass

        # STAGE 20: DISTORÇÃO DE CORES / COLORIDO 🌈
        elif numero == 20:
            while time.time() - start_time < duracao and not STOP_PAYLOAD:
                try:
                    elapsed = time.time() - start_time
                    BitBlt(mem_dc, 0, 0, w, h, screen_dc, 0, 0, SRCCOPY)
                    wave_shift = int(28 * math.sin(elapsed * 4.0))
                    for y in range(0, h, 5):
                        offset = int(math.sin((y / 18.0) + elapsed * 3.2) * 32)
                        src_y = max(0, min(h - 5, y + offset))
                        BitBlt(screen_dc, offset, y, max(1, w - abs(offset)), 5,
                               mem_dc, 0, src_y, SRCCOPY)

                    color_offset = int(35 * math.sin(elapsed * 2.0))
                    BitBlt(screen_dc, color_offset, 0, max(1, w - abs(color_offset)), h,
                           mem_dc, 0, 0, SRCCOPY)
                    BitBlt(screen_dc, -color_offset, 0, max(1, w - abs(color_offset)), h,
                           mem_dc, 0, 0, SRCPAINT)

                    for _ in range(8):
                        x = random.randint(0, w)
                        y = random.randint(0, h)
                        sx = random.randint(35, 110)
                        sy = random.randint(20, 80)
                        BitBlt(screen_dc, x, y, min(sx, w - x), min(sy, h - y),
                               screen_dc, x, y, SRCINVERT)

                    time.sleep(0.025)
                except:
                    pass

        # STAGE 29: DVD BOUNCING 3D + MORFOGEO + RASTROS
        elif numero == 29:
            esconder_painel_payload()
            cx, cy = w // 2, h // 2
            x = random.randint(100, w - 100)
            y = random.randint(100, h - 100)
            vx = random.choice([-8, 8])
            vy = random.choice([-7, 7])
            trail = []
            shape_phase = 0.0
            while time.time() - start_time < duracao and not STOP_PAYLOAD:
                try:
                    elapsed = time.time() - start_time
                    shape_phase += 0.06

                    # deixa rastros suaves movendo a tela em 1 pixel para gerar efeito de linger
                    BitBlt(screen_dc, 1, 1, w - 1, h - 1, screen_dc, 0, 0, SRCCOPY)

                    x += vx
                    y += vy
                    if x <= 30 or x >= w - 30:
                        vx *= -1
                        x = max(30, min(w - 30, x))
                    if y <= 30 or y >= h - 30:
                        vy *= -1
                        y = max(30, min(h - 30, y))

                    trail.append((x, y))
                    if len(trail) > 120:
                        trail.pop(0)

                    # mini bolinhas 3D que formam a esfera
                    orbit_mode = int((elapsed * 2.2) % 4)
                    for idx in range(110):
                        angle = idx * (2 * math.pi / 110)
                        z_factor = math.sin(shape_phase * 1.8 + idx * 0.25)
                        radius = 55 + int(18 * z_factor)
                        sx = int(math.cos(angle) * radius)
                        sy = int(math.sin(angle) * radius)
                        sz = int(math.sin(angle * 2.3 + shape_phase) * 32)

                        if orbit_mode == 0:
                            px = x + sx
                            py = y + sy + sz * 0.3
                        elif orbit_mode == 1:
                            px = x + sx + int(math.sin(shape_phase + idx) * 12)
                            py = y + sy + int(math.cos(shape_phase + idx) * 12)
                        elif orbit_mode == 2:
                            px = x + int(math.sin(angle + shape_phase) * radius)
                            py = y + int(math.cos(angle * 1.3 + shape_phase) * radius)
                        else:
                            px = x + int(math.sin(angle * 1.7 + shape_phase) * 18)
                            py = y + int(math.cos(angle * 1.7 + shape_phase) * 18)

                        if 0 <= px < w and 0 <= py < h:
                            for dx in range(-2, 3):
                                for dy in range(-2, 3):
                                    xx = px + dx
                                    yy = py + dy
                                    if 0 <= xx < w and 0 <= yy < h:
                                        BitBlt(screen_dc, xx, yy, 2, 2, screen_dc, xx, yy, SRCINVERT)

                    # rastros do corpo em movimento
                    for i, (tx, ty) in enumerate(trail[:-1]):
                        if i % 2 == 0:
                            for dx in range(-3, 4):
                                for dy in range(-3, 4):
                                    xx = tx + dx
                                    yy = ty + dy
                                    if 0 <= xx < w and 0 <= yy < h:
                                        BitBlt(screen_dc, xx, yy, 1, 1, screen_dc, xx, yy, SRCINVERT)

                    # ocasionalmente a bola vira outra forma geométrica
                    if int(elapsed * 3.5) % 7 == 0:
                        for ix in range(-3, 4):
                            for iy in range(-3, 4):
                                xx = x + ix * 11
                                yy = y + iy * 11
                                if 0 <= xx < w and 0 <= yy < h:
                                    BitBlt(screen_dc, xx, yy, 3, 3, screen_dc, xx, yy, SRCINVERT)

                    time.sleep(0.025)
                except:
                    pass

        # STAGE 30: CHROMA WARP 🌈
        elif numero == 30:
            while time.time() - start_time < duracao and not STOP_PAYLOAD:
                try:
                    elapsed = time.time() - start_time
                    BitBlt(mem_dc, 0, 0, w, h, screen_dc, 0, 0, SRCCOPY)
                    drift = int(30 * math.sin(elapsed * 5.0))
                    for y in range(0, h, 6):
                        offset = int(math.sin((y / 16.0) + elapsed * 4.2) * 44)
                        BitBlt(screen_dc, offset + drift, y, max(1, w - abs(offset + drift)), 6,
                               mem_dc, 0, y, SRCCOPY)
                        BitBlt(screen_dc, -(offset + drift), y, max(1, w - abs(offset + drift)), 6,
                               mem_dc, 0, y, SRCPAINT)
                    for _ in range(12):
                        x = random.randint(0, w)
                        y = random.randint(0, h)
                        BitBlt(screen_dc, x, y, random.randint(20, 90), random.randint(12, 70),
                               screen_dc, x, y, SRCINVERT)
                    time.sleep(0.02)
                except:
                    pass

        # STAGE 31: RAINBOW SHEAR 🧪
        elif numero == 31:
            while time.time() - start_time < duracao and not STOP_PAYLOAD:
                try:
                    elapsed = time.time() - start_time
                    BitBlt(mem_dc, 0, 0, w, h, screen_dc, 0, 0, SRCCOPY)
                    for y in range(0, h, 4):
                        shear = int(math.sin((y / 12.0) + elapsed * 3.5) * 56)
                        BitBlt(screen_dc, shear, y, max(1, w - abs(shear)), 4,
                               mem_dc, 0, y, SRCCOPY)
                    time.sleep(0.025)
                except:
                    pass

        # STAGE 32: RGB PULSE 💥
        elif numero == 32:
            while time.time() - start_time < duracao and not STOP_PAYLOAD:
                try:
                    elapsed = time.time() - start_time
                    pulse = int(48 * math.sin(elapsed * 6.0))
                    BitBlt(mem_dc, 0, 0, w, h, screen_dc, 0, 0, SRCCOPY)
                    BitBlt(screen_dc, pulse, 0, max(1, w - abs(pulse)), h, mem_dc, 0, 0, SRCCOPY)
                    BitBlt(screen_dc, -pulse, 0, max(1, w - abs(pulse)), h, mem_dc, 0, 0, SRCPAINT)
                    time.sleep(0.03)
                except:
                    pass

        # STAGE 33: PRISM MIRROR 🌫️
        elif numero == 33:
            while time.time() - start_time < duracao and not STOP_PAYLOAD:
                try:
                    elapsed = time.time() - start_time
                    BitBlt(mem_dc, 0, 0, w, h, screen_dc, 0, 0, SRCCOPY)
                    for x in range(0, w, 20):
                        offset = int(math.sin((x / 20.0) + elapsed * 2.8) * 35)
                        BitBlt(screen_dc, x + offset, 0, 20, h,
                               mem_dc, x, 0, SRCCOPY)
                    time.sleep(0.03)
                except:
                    pass

        # STAGE 34: SPECTRUM CURVE 🌀
        elif numero == 34:
            while time.time() - start_time < duracao and not STOP_PAYLOAD:
                try:
                    elapsed = time.time() - start_time
                    BitBlt(mem_dc, 0, 0, w, h, screen_dc, 0, 0, SRCCOPY)
                    for x in range(0, w, 10):
                        shift = int(math.sin((x / 30.0) + elapsed * 3.0) * 60)
                        BitBlt(screen_dc, x, shift, 10, h, mem_dc, x, 0, SRCCOPY)
                    for _ in range(15):
                        xx = random.randint(0, w)
                        yy = random.randint(0, h)
                        BitBlt(screen_dc, xx, yy, random.randint(12, 40), random.randint(8, 35),
                               screen_dc, xx, yy, SRCINVERT)
                    time.sleep(0.025)
                except:
                    pass

        # STAGE 35: DUAL SHIFT STROBE 🚨
        elif numero == 35:
            while time.time() - start_time < duracao and not STOP_PAYLOAD:
                try:
                    elapsed = time.time() - start_time
                    shift = int(55 * math.sin(elapsed * 7.0))
                    BitBlt(mem_dc, 0, 0, w, h, screen_dc, 0, 0, SRCCOPY)
                    BitBlt(screen_dc, shift, 0, w, h, mem_dc, 0, 0, SRCCOPY)
                    BitBlt(screen_dc, -shift, 0, w, h, mem_dc, 0, 0, SRCPAINT)
                    time.sleep(0.018)
                except:
                    pass

        # STAGE 36: RAINBOW VORTEX 🪐
        elif numero == 36:
            while time.time() - start_time < duracao and not STOP_PAYLOAD:
                try:
                    elapsed = time.time() - start_time
                    cx, cy = w // 2, h // 2
                    BitBlt(mem_dc, 0, 0, w, h, screen_dc, 0, 0, SRCCOPY)
                    for radius in range(30, max(w, h), 20):
                        theta = elapsed * 2.8 + radius * 0.06
                        x = int(cx + math.cos(theta) * radius)
                        y = int(cy + math.sin(theta) * radius)
                        if 0 <= x < w and 0 <= y < h:
                            BitBlt(screen_dc, x, y, 14, 14, mem_dc, x, y, SRCINVERT)
                    time.sleep(0.02)
                except:
                    pass

        # STAGE 37: FIZZ CHROMA ✨
        elif numero == 37:
            while time.time() - start_time < duracao and not STOP_PAYLOAD:
                try:
                    elapsed = time.time() - start_time
                    BitBlt(mem_dc, 0, 0, w, h, screen_dc, 0, 0, SRCCOPY)
                    for _ in range(30):
                        sx = random.randint(0, w)
                        sy = random.randint(0, h)
                        sw = random.randint(10, 80)
                        sh = random.randint(10, 80)
                        dx = int(math.sin(elapsed + sx * 0.02) * 18)
                        dy = int(math.cos(elapsed + sy * 0.02) * 18)
                        BitBlt(screen_dc, sx + dx, sy + dy, sw, sh,
                               mem_dc, sx, sy, SRCCOPY)
                    time.sleep(0.025)
                except:
                    pass

        # STAGE 38: PRISM SLICES 🔷
        elif numero == 38:
            while time.time() - start_time < duracao and not STOP_PAYLOAD:
                try:
                    elapsed = time.time() - start_time
                    BitBlt(mem_dc, 0, 0, w, h, screen_dc, 0, 0, SRCCOPY)
                    slices = 14
                    slice_w = w // slices
                    for i in range(slices):
                        offset = int(math.sin((i * 0.9) + elapsed * 4.0) * 70)
                        x0 = i * slice_w
                        x1 = min(w, x0 + slice_w)
                        BitBlt(screen_dc, x0 + offset, 0, x1 - x0, h,
                               mem_dc, x0, 0, SRCCOPY)
                    time.sleep(0.025)
                except:
                    pass

        # STAGE 39: FINAL SPECTRUM 😵
        elif numero == 39:
            while time.time() - start_time < duracao and not STOP_PAYLOAD:
                try:
                    elapsed = time.time() - start_time
                    BitBlt(mem_dc, 0, 0, w, h, screen_dc, 0, 0, SRCCOPY)
                    for x in range(0, w, 8):
                        offset = int(math.sin((x / 18.0) + elapsed * 5.0) * 70)
                        BitBlt(screen_dc, x + offset, 0, 8, h,
                               mem_dc, x, 0, SRCCOPY)
                    for _ in range(20):
                        xx = random.randint(0, w)
                        yy = random.randint(0, h)
                        BitBlt(screen_dc, xx, yy, random.randint(28, 120), random.randint(14, 70),
                               screen_dc, xx, yy, SRCINVERT)
                    time.sleep(0.02)
                except:
                    pass

        # STAGE 40: RODA RAPIDO SEM LINHA FIXA ⚙️
        elif numero == 40:
            while time.time() - start_time < duracao and not STOP_PAYLOAD:
                try:
                    elapsed = time.time() - start_time
                    cx = w // 2
                    cy = h // 2
                    angle = (elapsed * 300) % 360
                    angle_rad = math.radians(angle)

                    # cache da tela base em um frame limpo para não deixar a linha de carga
                    BitBlt(mem_dc, 0, 0, w, h, screen_dc, 0, 0, SRCCOPY)

                    step = 10
                    for y in range(0, h, step):
                        for x in range(0, w, step):
                            dx = x - cx
                            dy = y - cy
                            r = math.hypot(dx, dy)
                            theta = math.atan2(dy, dx) + angle_rad
                            src_x = int(cx + r * math.cos(theta))
                            src_y = int(cy + r * math.sin(theta))
                            if 0 <= src_x < w and 0 <= src_y < h:
                                BitBlt(screen_dc, x, y, step, step,
                                       mem_dc, src_x, src_y, SRCCOPY)

                    # shimmer de cores para manter a sensação de rotação intensa
                    for _ in range(18):
                        px = random.randint(0, w)
                        py = random.randint(0, h)
                        sw = random.randint(20, 90)
                        sh = random.randint(10, 60)
                        BitBlt(screen_dc, px, py, sw, sh,
                               screen_dc, px, py, SRCINVERT)

                    time.sleep(0.035)
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
