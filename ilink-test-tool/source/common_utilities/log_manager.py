from queue import Queue, Empty


class LogManager:
    def __init__(self):
        self.log_queue = Queue()

    def add_log(self, message):
        self.log_queue.put(message)

    def get_log(self):
        try:
            return self.log_queue.get_nowait()
        except Empty:
            return None


log_manager = LogManager()