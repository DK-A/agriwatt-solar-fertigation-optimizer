"""
AGRI-WATT Hardware Simulator Screen Recording Automation
Captures high-definition screen video of the 2D physical simulator
demonstrating MPPT solar throttling, active Zener snubber firing,
oscilloscope transients, and Edge-AI clog detection.
"""

import os
import sys
import time
import shutil
import cv2
from playwright.sync_api import sync_playwright

def record_simulation():
    base_dir = r"f:\HACKATHONS\vishwakarma\AGRI_WATT\simulation"
    html_path = os.path.join(base_dir, "agriwatt_2d_hardware_simulator.html")
    recordings_dir = os.path.join(base_dir, "recordings")
    temp_video_dir = os.path.join(recordings_dir, "temp_playwright")
    
    os.makedirs(recordings_dir, exist_ok=True)
    if os.path.exists(temp_video_dir):
        shutil.rmtree(temp_video_dir)
    os.makedirs(temp_video_dir, exist_ok=True)
    
    output_mp4 = os.path.join(recordings_dir, "agriwatt_hardware_simulation_demo.mp4")
    output_webm = os.path.join(recordings_dir, "agriwatt_hardware_simulation_demo.webm")

    print("[*] Launching Chromium with video capture (1280x720 60fps)...")
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-gpu",
                "--hide-scrollbars",
                "--window-size=1280,720"
            ]
        )
        
        context = browser.new_context(
            record_video_dir=temp_video_dir,
            record_video_size={"width": 1280, "height": 720},
            viewport={"width": 1280, "height": 720}
        )
        
        page = context.new_page()
        file_url = f"file:///{html_path.replace(os.sep, '/')}"
        print(f"[*] Navigating to: {file_url}")
        page.goto(file_url)
        page.wait_for_load_state("networkidle")
        
        # Give canvas time to initialize
        time.sleep(1.0)
        
        print("[1/5] Phase 1: Nominal Solar Operation & Closed-Loop Pressure Stabilization")
        time.sleep(3.5)
        
        print("[2/5] Phase 2: Active 36V Zener Snubber Micro-Dose Injections")
        # Ensure Active Zener is selected
        page.click("#btn-snubber-zener")
        time.sleep(0.5)
        for i in range(4):
            page.click("#btn-fire-pulse")
            time.sleep(0.8)
            
        print("[3/5] Phase 3: Benchmark Against Baseline Standard Diode Snubber (Slow Decay)")
        # Switch to diode
        page.click("#btn-snubber-diode")
        time.sleep(0.8)
        page.click("#btn-fire-pulse")
        time.sleep(1.5)
        page.click("#btn-fire-pulse")
        time.sleep(1.5)
        # Switch back to active zener
        page.click("#btn-snubber-zener")
        time.sleep(0.5)
        page.click("#btn-fire-pulse")
        time.sleep(1.0)
        
        print("[4/5] Phase 4: Cloud Shadow Transient & 10 kHz MPPT Motor Throttling")
        page.click("#btn-pass-cloud")
        time.sleep(3.5)
        # Recover sun
        page.click("#btn-clear-sun")
        time.sleep(3.0)
        
        print("[5/5] Phase 5: Edge-AI Anomaly Injection & Reverse Purge Sequence")
        page.click("#btn-sim-clog")
        time.sleep(2.5)
        page.click("#btn-purge")
        time.sleep(3.5)
        
        print("[*] Wrapping up demonstration video...")
        time.sleep(1.5)
        
        # Close page & context to flush the video file
        page.close()
        context.close()
        browser.close()
        
    print("[*] Browser closed. Locating recorded video file...")
    recorded_files = [f for f in os.listdir(temp_video_dir) if f.endswith(".webm")]
    if not recorded_files:
        raise RuntimeError("No recorded video found in Playwright output directory!")
        
    raw_video_path = os.path.join(temp_video_dir, recorded_files[0])
    shutil.copy2(raw_video_path, output_webm)
    print(f"[OK] Saved WebM video to: {output_webm} ({os.path.getsize(output_webm):,} bytes)")
    
    # Transcode to MP4 using OpenCV for universal cross-platform playback
    print("[*] Transcoding WebM to MP4 format with OpenCV...")
    cap = cv2.VideoCapture(raw_video_path)
    if not cap.isOpened():
        print("[!] OpenCV could not open WebM file directly. Keeping WebM as primary video.")
        return output_webm
        
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_mp4, fourcc, fps, (width, height))
    
    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        out.write(frame)
        frame_count += 1
        
    cap.release()
    out.release()
    print(f"[OK] Transcoded {frame_count} frames to MP4: {output_mp4} ({os.path.getsize(output_mp4):,} bytes)")
    
    # Clean up temp directory
    try:
        shutil.rmtree(temp_video_dir)
    except Exception:
        pass
        
    return output_mp4

if __name__ == "__main__":
    mp4_path = record_simulation()
    print(f"\n==========================================")
    print(f"SCREEN RECORDING COMPLETE!")
    print(f"Output: {mp4_path}")
    print(f"==========================================")
