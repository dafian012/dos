from mcstatus.server import MinecraftServer
import threading
import concurrent.futures
import time
import logging
import random

# Setup logging untuk mencatat hasil ke dalam file log
logging.basicConfig(filename='server_status.log', level=logging.INFO, format='%(asctime)s - %(message)s')

# Fungsi untuk mendapatkan status server Minecraft dan mencatat latency
def send_request(request_id, server_address, server_port):
    server = MinecraftServer.lookup(f"{server_address}:{server_port}")
    try:
        # Mencatat waktu mulai untuk mengukur latency
        start_time = time.time()
        status = server.status()
        latency = (time.time() - start_time) * 1000  # Latency dalam milidetik
        
        # Menampilkan status server di konsol
        print(f"Request {request_id} berhasil: Server is online, {status.players.online} players online. Max players: {status.players.max}. Latency: {latency:.2f} ms")
        
        # Menampilkan status login pemain (misalnya nama pemain yang online)
        if status.players.online > 0 and status.players.sample:
            print(f"Request {request_id}: Pemain online:")
            for player in status.players.sample:
                print(f" - {player.name}")
        
        # Logging status ke file
        logging.info(f"Request {request_id} berhasil: Server is online, {status.players.online} players online. Max players: {status.players.max}. Latency: {latency:.2f} ms")
        if status.players.online > 0 and status.players.sample:
            for player in status.players.sample:
                logging.info(f"Pemain online: {player.name}")
        
    except Exception as e:
        # Jika gagal menghubungi server
        print(f"Request {request_id}: Error: Request gagal menghubungi server. Error: {e}")
        logging.error(f"Request {request_id}: Error: Request gagal menghubungi server. Error: {e}")

# Fungsi untuk melakukan uji beban menggunakan ThreadPoolExecutor
def stress_test(server_address, server_port, num_requests):
    # Tentukan jumlah thread secara dinamis berdasarkan jumlah permintaan
    max_threads = min(500, num_requests)  # Tingkatkan hingga 500 thread per permintaan

    print(f"Menjalankan {num_requests} permintaan dengan {max_threads} thread bersamaan...")
    
    # Menggunakan ThreadPoolExecutor untuk mengelola thread secara efisien
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:  # Maksimal 500 thread
        futures = [executor.submit(send_request, i, server_address, server_port) for i in range(1, num_requests + 1)]
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()  # Menunggu hasil dari setiap thread
            except Exception as e:
                print(f"Error in thread: {e}")
                logging.error(f"Error in thread: {e}")

# Fungsi untuk meminta input dari pengguna
def get_user_input():
    print("Masukkan alamat server Minecraft (misal: minecraft.my.id atau 192.168.1.10): ")
    server_address = input().strip()

    print("Masukkan port server Minecraft (default 25565): ")
    try:
        server_port = int(input().strip())
    except ValueError:
        server_port = 25565  # Jika input invalid, gunakan port default 25565

    return server_address, server_port

# Ambil input dari pengguna
server_address, server_port = get_user_input()

# Tentukan jumlah permintaan yang ingin dikirim
num_requests = int(input("Masukkan jumlah permintaan yang ingin dikirim (misalnya 1000): ").strip())

# Memulai waktu untuk mengukur durasi uji coba
start_time = time.time()

# Mulai pengujian beban
stress_test(server_address, server_port, num_requests)

# Waktu selesai pengujian
end_time = time.time()

# Mengukur total waktu pengujian
total_time = end_time - start_time
print(f"Total waktu untuk mengirim {num_requests} permintaan: {total_time:.2f} detik")
logging.info(f"Total waktu untuk mengirim {num_requests} permintaan: {total_time:.2f} detik")
