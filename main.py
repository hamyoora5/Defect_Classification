import subprocess
import time
import sys
import os

def run_system():
    processes = []
    
    print("=" * 50)
    print("🚀 Smart Factory Vision AI System - Integrated Launcher")
    print("=" * 50)
    
    # 가상환경 내에서 실행하기 위해 python 인스턴스 경로 확보
    python_exe = sys.executable
    
    try:
        # 1. API 서버 (Inference Server) 실행
        print("\n[1/3] Starting Inference API Server...")
        api_proc = subprocess.Popen(
            [python_exe, "api/fastapi_server.py"],
            env=os.environ.copy()
        )
        processes.append(api_proc)
        time.sleep(3) # 서버 기동 대기
        
        # 2. 대시보드 (Streamlit) 실행 - python -m streamlit 방식으로 안정성 확보
        print("[2/3] Starting Quality Dashboard...")
        dashboard_proc = subprocess.Popen(
            [python_exe, "-m", "streamlit", "run", "dashboard/streamlit_app.py", "--server.port", "8501"],
            env=os.environ.copy()
        )
        processes.append(dashboard_proc)
        time.sleep(3)
        
        # 3. 카메라 시뮬레이터 (Simulator) 실행
        print("[3/3] Starting Camera Simulator...")
        sim_proc = subprocess.Popen(
            [python_exe, "camera_simulator/camera_stream.py"],
            env=os.environ.copy()
        )
        processes.append(sim_proc)
        
        print("\n" + "=" * 50)
        print("✅ All systems initialized and running!")
        print("🔗 Dashboard URL: http://localhost:8501")
        print("🚨 Press Ctrl+C in this terminal to stop everything.")
        print("=" * 50 + "\n")

        # 프로세스 상태 모니터링
        while True:
            time.sleep(2)
            for p in processes:
                if p.poll() is not None:
                    # 프로세스가 비정상 종료된 경우
                    cmd_str = " ".join(p.args) if isinstance(p.args, list) else p.args
                    print(f"\n⚠️ Critical Process Stopped: {cmd_str}")
                    print("Check if the port (8000 or 8501) is already in use.")
                    raise KeyboardInterrupt

    except KeyboardInterrupt:
        print("\n[!] Shutting down all systems...")
        # 역순으로 종료 (시뮬레이터 -> 대시보드 -> API)
        for p in reversed(processes):
            p.terminate()
            try:
                p.wait(timeout=3)
            except subprocess.TimeoutExpired:
                p.kill()
        print("\n✅ System closed safely.")

if __name__ == "__main__":
    run_system()
