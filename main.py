import subprocess
import time
import sys
import os

def run_system():
    processes = []
    
    print("=" * 50)
    print("🚀 Smart Factory Vision AI System - Integrated Launcher")
    print("=" * 50)
    
    try:
        # 1. API 서버 (Inference Server) 실행
        print("\n[1/3] Starting Inference API Server...")
        api_proc = subprocess.Popen(
            [sys.executable, "api/fastapi_server.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            env=os.environ.copy()
        )
        processes.append(api_proc)
        time.sleep(3) # 서버 기동 대기
        
        # 2. 대시보드 (Streamlit) 실행
        print("[2/3] Starting Quality Dashboard...")
        dashboard_proc = subprocess.Popen(
            ["streamlit", "run", "dashboard/streamlit_app.py", "--server.port", "8501"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            env=os.environ.copy()
        )
        processes.append(dashboard_proc)
        time.sleep(2)
        
        # 3. 카메라 시뮬레이터 (Simulator) 실행
        print("[3/3] Starting Camera Simulator...")
        sim_proc = subprocess.Popen(
            [sys.executable, "camera_simulator/camera_stream.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            env=os.environ.copy()
        )
        processes.append(sim_proc)
        
        print("\n" + "=" * 50)
        print("✅ All systems are running!")
        print("🔗 Dashboard URL: http://localhost:8501")
        print("🚨 Press Ctrl+C to stop all systems.")
        print("=" * 50 + "\n")

        # 프로세스 상태 모니터링 (실시간 로그 출력 생략 또는 간략화)
        while True:
            time.sleep(1)
            # 어느 하나라도 죽었는지 체크
            for p in processes:
                if p.poll() is not None:
                    print(f"\n⚠️ Process {p.args} has stopped execution.")
                    raise KeyboardInterrupt

    except KeyboardInterrupt:
        print("\n[!] Shutting down all systems...")
        for p in processes:
            p.terminate()
            try:
                p.wait(timeout=5)
                print(f"--- Process {p.args[0]} stopped.")
            except subprocess.TimeoutExpired:
                p.kill()
        print("\n✅ Goodbye.")

if __name__ == "__main__":
    run_system()
