"""
AGRI-WATT Video Concatenation and Dynamic Subtitle Engine
Merges terminal_execution_demo.mp4 and agriwatt_hardware_simulation_demo.mp4
with high-resolution lower-third subtitle banners explaining each simulation step,
circuit transient, MATLAB visual, and physical fluidic event.
"""

import os
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

def create_subtitle_banner(width, height, badge_text, desc_text, badge_color=(0, 230, 118)):
    """Creates a transparent RGBA banner with Segoe UI text."""
    banner = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(banner)
    
    # Coordinates for lower-third box
    bx1, by1 = 24, height - 84
    bx2, by2 = width - 24, height - 14
    
    # Draw dark translucent backdrop
    draw.rounded_rectangle([bx1, by1, bx2, by2], radius=8, fill=(11, 17, 32, 225), outline=(51, 65, 85, 255), width=1)
    
    # Top accent line (Schneider Green or custom badge color)
    draw.line([bx1 + 8, by1 + 1, bx2 - 8, by1 + 1], fill=(*badge_color, 255), width=3)
    
    # Fonts
    font_bold = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 15)
    font_regular = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 16)
    
    # Draw Badge / Phase
    draw.text((bx1 + 16, by1 + 10), badge_text.upper(), font=font_bold, fill=(*badge_color, 255))
    
    # Draw Detailed Description
    draw.text((bx1 + 16, by1 + 36), desc_text, font=font_regular, fill=(241, 245, 249, 255))
    
    return banner

def create_transition_card(width, height, title, subtitle):
    """Creates a full-frame transition title card between videos."""
    card = Image.new('RGB', (width, height), (11, 17, 32))
    draw = ImageDraw.Draw(card)
    
    font_title = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 32)
    font_sub = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 18)
    font_meta = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 14)
    
    # Subtle accent grid
    draw.line([60, height // 2 - 50, width - 60, height // 2 - 50], fill=(0, 158, 77), width=3)
    
    # Text rendering
    draw.text((width // 2, height // 2 - 15), title, font=font_title, fill=(255, 255, 255), anchor="mm")
    draw.text((width // 2, height // 2 + 35), subtitle, font=font_sub, fill=(56, 189, 248), anchor="mm")
    draw.text((width // 2, height - 50), "SCHNEIDER ELECTRIC YUVA YODHA | CHALLENGE 01: SUSTAINABLE AGRICULTURE", font=font_meta, fill=(148, 163, 184), anchor="mm")
    
    return np.array(card)[:, :, ::-1] # Return BGR

def overlay_banner(frame_bgr, banner_rgba):
    """Blends RGBA PIL banner over a BGR OpenCV frame."""
    frame_pil = Image.fromarray(cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)).convert('RGBA')
    composite = Image.alpha_composite(frame_pil, banner_rgba)
    return cv2.cvtColor(np.array(composite.convert('RGB')), cv2.COLOR_RGB2BGR)

def merge_videos():
    base_dir = r"f:\HACKATHONS\vishwakarma\AGRI_WATT\simulation\recordings"
    video1_path = os.path.join(base_dir, "terminal_execution_demo.mp4")
    video2_path = os.path.join(base_dir, "agriwatt_hardware_simulation_demo.mp4")
    out_path = os.path.join(base_dir, "agriwatt_complete_simulation_showcase.mp4")
    
    print("[*] Opening video streams...")
    cap1 = cv2.VideoCapture(video1_path)
    cap2 = cv2.VideoCapture(video2_path)
    
    if not cap1.isOpened() or not cap2.isOpened():
        raise RuntimeError("Failed to open source videos!")
        
    width = int(cap1.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap1.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap1.get(cv2.CAP_PROP_FPS) or 25.0
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(out_path, fourcc, fps, (width, height))
    
    # -------------------------------------------------------------
    # TIMELINE 1: Terminal Execution & SPICE & MATLAB (757 frames)
    # -------------------------------------------------------------
    timeline1 = [
        (0, 80, "PART 1: TERMINAL INITIALIZATION", "Navigating to AGRI-WATT directory in Windows Command Prompt environment", (0, 230, 118)),
        (80, 180, "SPICE CIRCUIT ANALYSIS", "Executing continuous-time nodal differential solver for solenoid drive (dt = 0.5 us)", (56, 189, 248)),
        (180, 275, "SNUBBER BENCHMARK PROOF", "Active 36V Zener: 0.29 ms vs Standard Diode: 4.61 ms (16.0x faster cutoff)", (0, 230, 118)),
        (275, 375, "SYSTEM MULTI-PHYSICS RUN", "Simulating 10 kHz MPPT power tracking & closed-loop discrete PI pressure regulation", (255, 179, 0)),
        (375, 475, "RESOURCE CONSERVATION AUDIT", "Quantified proof: 65.0% pumping energy cut & 75.0% freshwater saved per hectare", (0, 230, 118)),
        (475, 630, "MATLAB R2024b GRAPHICS ENGINE", "Figure 1 popup: Multi-domain plots (Solar MPPT, 38-42 PSI Pressure, Solenoid, Seasonal savings)", (235, 104, 65)),
        (630, 757, "ARTIFACT CONFIRMATION", "All 300 DPI publication plots and SPICE traces verified and written to disk", (0, 230, 118))
    ]
    
    print("[*] Processing Video 1: Terminal, SPICE & MATLAB...")
    frame_idx = 0
    current_banner = None
    last_phase = -1
    
    while True:
        ret, frame = cap1.read()
        if not ret:
            break
            
        # Determine subtitle
        for p_idx, (start_f, end_f, badge, desc, col) in enumerate(timeline1):
            if start_f <= frame_idx < end_f:
                if p_idx != last_phase:
                    current_banner = create_subtitle_banner(width, height, badge, desc, col)
                    last_phase = p_idx
                break
                
        if current_banner:
            frame = overlay_banner(frame, current_banner)
            
        out.write(frame)
        frame_idx += 1
        
    cap1.release()
    print(f"[OK] Video 1 finished: {frame_idx} frames written.")
    
    # -------------------------------------------------------------
    # TRANSITION CARD (35 frames = ~1.4 seconds)
    # -------------------------------------------------------------
    print("[*] Generating transition inter-title card...")
    trans_frame = create_transition_card(
        width, height, 
        "PART 2: 2D HARDWARE WORKBENCH SIMULATOR", 
        "Real-Time Physical Emulation: Solar MPPT, Solenoid Plunger & Fluidics"
    )
    for _ in range(35):
        out.write(trans_frame)
        
    # -------------------------------------------------------------
    # TIMELINE 2: 2D Hardware Workbench Simulation (732 frames)
    # -------------------------------------------------------------
    timeline2 = [
        (0, 90, "STEADY-STATE FLUIDICS", "Solar direct drive at 950 W/m2; closed-loop PI maintains 40.1 PSI across manifold", (0, 230, 118)),
        (90, 200, "ACTIVE ZENER MICRO-INJECTION", "Sub-1.2 ms plunger snap-shut (0.38 ms cutoff) ensures crisp atomization with zero dribble", (0, 230, 118)),
        (200, 330, "STANDARD DIODE FAILURE MODE", "Sluggish 35 ms demagnetization causes plunger lag and visible post-spray chemical leakage", (239, 68, 68)),
        (330, 415, "ACTIVE ZENER RESTORED", "Switched back to 36V Zener clamp: instant cutoff and zero droplet dribble verified", (0, 230, 118)),
        (415, 530, "DYNAMIC CLOUD SHADOW TRANSIENT", "60% solar insolation drop: 10 kHz MPPT down-throttles pump motor with zero stalls", (255, 179, 0)),
        (530, 620, "EDGE-AI ANOMALY DETECTION", "Simulated particulate clog: abnormal pressure decay detected by on-chip ESP-NN classifier", (239, 68, 68)),
        (620, 732, "SELF-HEALING REVERSE PURGE", "5-second reverse back-flush cycle executed; 0.3 mm micro-orifice cleared and normalized", (0, 230, 118))
    ]
    
    print("[*] Processing Video 2: 2D Hardware Workbench...")
    frame_idx = 0
    current_banner = None
    last_phase = -1
    
    while True:
        ret, frame = cap2.read()
        if not ret:
            break
            
        for p_idx, (start_f, end_f, badge, desc, col) in enumerate(timeline2):
            if start_f <= frame_idx < end_f:
                if p_idx != last_phase:
                    current_banner = create_subtitle_banner(width, height, badge, desc, col)
                    last_phase = p_idx
                break
                
        if current_banner:
            frame = overlay_banner(frame, current_banner)
            
        out.write(frame)
        frame_idx += 1
        
    cap2.release()
    out.release()
    
    file_size = os.path.getsize(out_path)
    print(f"\n=======================================================")
    print(f"[OK] COMPLETE SHOWCASE VIDEO GENERATED SUCCESSFULLY!")
    print(f"Output File: {out_path}")
    print(f"Total Size:  {file_size:,} bytes ({file_size / (1024*1024):.2f} MB)")
    print(f"=======================================================")
    return out_path

if __name__ == '__main__':
    merge_videos()
