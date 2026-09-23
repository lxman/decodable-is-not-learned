"""Thermal/clock screen for a rented GPU: 120 s of fp16 matmul, SM clock + temperature + throttle
reasons sampled every 10 s. Pass = clock stays near max and no thermal slowdown. Runs on the image's
own torch (before the venv exists)."""
import subprocess, time, torch
def smi():
    q = "temperature.gpu,clocks.sm,clocks.max.sm,power.draw,utilization.gpu,clocks_throttle_reasons.sw_thermal_slowdown,clocks_throttle_reasons.hw_thermal_slowdown,clocks_throttle_reasons.sw_power_cap"
    return subprocess.run(["nvidia-smi", f"--query-gpu={q}", "--format=csv,noheader"], capture_output=True, text=True).stdout.strip()
print("idle:", smi(), flush=True)
a = torch.randn(8192, 8192, device="cuda", dtype=torch.float16); b = torch.randn(8192, 8192, device="cuda", dtype=torch.float16)
t0 = time.time(); n = 0; last = t0
while time.time() - t0 < 120:
    c = a @ b; n += 1
    if time.time() - last >= 10:
        torch.cuda.synchronize(); el = time.time() - t0
        print(f"t={el:5.1f}s  {n*2*8192**3/el/1e12:6.1f} TFLOP/s  |", smi(), flush=True); last = time.time()
torch.cuda.synchronize()
print("done:", smi(), flush=True)
