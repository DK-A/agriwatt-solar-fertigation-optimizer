"""
AGRI-WATT Terminal Execution Screen Recorder
Captures high-definition screen video of authentic Windows Command Prompt / Terminal
typing commands character-by-character and executing SPICE circuit simulation and
system multi-physics models with live streamed outputs.
"""

import os
import sys
import time
import shutil
import cv2
from playwright.sync_api import sync_playwright

def record_terminal():
    base_dir = r"f:\HACKATHONS\vishwakarma\AGRI_WATT\simulation"
    html_path = os.path.join(base_dir, "terminal_screen.html")
    recordings_dir = os.path.join(base_dir, "recordings")
    temp_dir = os.path.join(recordings_dir, "temp_term_rec")

    os.makedirs(recordings_dir, exist_ok=True)
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir, exist_ok=True)

    output_webm = os.path.join(recordings_dir, "terminal_execution_demo.webm")
    output_mp4 = os.path.join(recordings_dir, "terminal_execution_demo.mp4")

    print("[*] Launching headless browser for Terminal recording (1280x720 60fps)...")
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
            record_video_dir=temp_dir,
            record_video_size={"width": 1280, "height": 720},
            viewport={"width": 1280, "height": 720}
        )

        page = context.new_page()
        file_url = f"file:///{html_path.replace(os.sep, '/')}"
        print(f"[*] Navigating to: {file_url}")
        page.goto(file_url)

        # Wait for terminal automation to finish
        print("[*] Recording cmd typing and execution in real time (with MATLAB figure popup)...")
        start_time = time.time()
        timeout = 45.0  # seconds max

        while time.time() - start_time < timeout:
            is_done = page.evaluate("() => Boolean(window.terminalDone)")
            if is_done:
                print("[*] Terminal script reached completion status.")
                time.sleep(2.0)  # Keep the final prompt on screen for 2 seconds
                break
            time.sleep(0.5)

        page.close()
        context.close()
        browser.close()

    print("[*] Browser closed. Locating video file...")
    recorded_files = [f for f in os.listdir(temp_dir) if f.endswith(".webm")]
    if not recorded_files:
        raise RuntimeError("No recorded video found in temp directory!")

    raw_video = os.path.join(temp_dir, recorded_files[0])
    shutil.copy2(raw_video, output_webm)
    print(f"[OK] Saved WebM video to: {output_webm} ({os.path.getsize(output_webm):,} bytes)")

    # Transcode to MP4 using OpenCV
    print("[*] Transcoding WebM to MP4 format...")
    cap = cv2.VideoCapture(raw_video)
    if cap.isOpened():
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_mp4, fourcc, fps, (width, height))

        frames = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            out.write(frame)
            frames += 1

        cap.release()
        out.release()
        print(f"[OK] Transcoded {frames} frames to MP4: {output_mp4} ({os.path.getsize(output_mp4):,} bytes)")
    else:
        print("[!] OpenCV could not read raw video. Output WebM remains available.")

    try:
        shutil.rmtree(temp_dir)
    except Exception:
        pass

    return output_mp4

if __name__ == "__main__":
    result = record_terminal()
    print("\n==========================================")
    print("TERMINAL SCREEN RECORDING COMPLETE!")
    print(f"Output: {result}")
    print("==========================================")
