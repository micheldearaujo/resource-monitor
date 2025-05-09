import psutil
import GPUtil
import time
from tqdm import tqdm

def get_gpu_info():
    try:
        gpus = GPUtil.getGPUs()
        if gpus:
            gpu = gpus[0]
            return gpu.load * 100, gpu.memoryUsed, gpu.memoryTotal, gpu.temperature
        return None
    except:
        return None

def format_bytes(bytes):
    for unit in ['', 'K', 'M', 'G', 'T', 'P']:
        if bytes < 1024:
            return f"{bytes:.2f}{unit}B"
        bytes /= 1024

def monitor_resources():
    try:
        with tqdm(total=100, bar_format='{l_bar}{bar}', ncols=50) as cpu_bar, \
             tqdm(total=100, bar_format='{l_bar}{bar}', ncols=50) as ram_bar, \
             tqdm(total=100, bar_format='{l_bar}{bar}', ncols=50) as gpu_bar, \
             tqdm(total=100, bar_format='{l_bar}{bar}', ncols=50) as disk_bar, \
             tqdm(total=100, bar_format='{l_bar}{bar}', ncols=50) as net_bar:

            net_io_last = psutil.net_io_counters()
            time_last = time.time()

            while True:
                # CPU Usage
                cpu_percent = psutil.cpu_percent()
                cpu_bar.set_description(f"CPU {cpu_percent:5.1f}%")
                cpu_bar.n = cpu_percent
                cpu_bar.refresh()

                # RAM Usage
                ram = psutil.virtual_memory()
                ram_percent = ram.percent
                ram_bar.set_description(f"RAM {ram_percent:5.1f}% ({format_bytes(ram.used)})")
                ram_bar.n = ram_percent
                ram_bar.refresh()

                # GPU Usage
                gpu_info = get_gpu_info()
                if gpu_info:
                    gpu_percent, gpu_used, gpu_total, gpu_temp = gpu_info
                    gpu_bar.set_description(f"GPU {gpu_percent:5.1f}% ({gpu_temp:.1f}°C)")
                    gpu_bar.n = gpu_percent
                    gpu_bar.refresh()
                else:
                    gpu_bar.set_description("GPU N/A")
                    gpu_bar.n = 0
                    gpu_bar.refresh()

                # Disk Usage
                disk = psutil.disk_usage('/')
                disk_percent = disk.percent
                disk_bar.set_description(f"Disk {disk_percent:5.1f}% ({format_bytes(disk.used)})")
                disk_bar.n = disk_percent
                disk_bar.refresh()

                # Network I/O
                net_io = psutil.net_io_counters()
                time_now = time.time()
                time_delta = time_now - time_last
                net_sent = (net_io.bytes_sent - net_io_last.bytes_sent) / time_delta
                net_recv = (net_io.bytes_recv - net_io_last.bytes_recv) / time_delta
                net_total = net_sent + net_recv
                net_percent = min(net_total / 1e6, 100)  # Assume 1 GB/s as 100%
                net_bar.set_description(f"Network ↑{format_bytes(net_sent)}/s ↓{format_bytes(net_recv)}/s")
                net_bar.n = net_percent
                net_bar.refresh()
                net_io_last = net_io
                time_last = time_now

                time.sleep(1)  # Update every second

    except KeyboardInterrupt:
        print("\nMonitoring stopped.")

if __name__ == "__main__":
    print("Monitoring computer resources. Press Ctrl+C to stop.")
    monitor_resources()