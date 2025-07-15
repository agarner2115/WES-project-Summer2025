#This module is used for accessing shared resources in the WES project.
import queue
import threading

# Shared data queue
data_queue = queue.Queue()
stop_event = threading.Event()
