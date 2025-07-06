import threading

from server.map_class import auto_update_map

background_thread = None
background_thread_lock = threading.Lock()


def run_map_update_thread(cloud_url: str) -> None:
    global background_thread
    global background_thread_lock
    with background_thread_lock:
        if not background_thread:
            # Start the background thread
            background_thread = threading.Thread(target=auto_update_map, args=(cloud_url,))
            background_thread.daemon = True  # Daemonize so it runs in background and exits with main program
            background_thread.start()
            print(f"Started thread: {background_thread.is_alive()}")
