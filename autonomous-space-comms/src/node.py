import threading
import time
import random
import socket
import json
import logging

# Configure logger
logging.basicConfig(
    filename="/app/logs/communication.log",  # Ensure this path matches the volume mount in Docker
    filemode="a",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

def log_event(node_name, event_type, message_data):
    logging.info(f"{node_name} - {event_type} - {message_data}")

class SpaceRelayMessage:
    def __init__(self, data, priority=1):
        self.data = data
        self.priority = priority
        self.transmitted = False
        self.retries = 0
        self.max_retries = 3

    def to_dict(self):
        return {
            "data": self.data,
            "priority": self.priority,
            "transmitted": self.transmitted,
            "retries": self.retries
        }

class RelayNode(threading.Thread):
    def __init__(self, name, port, neighbors):
        super().__init__()
        self.name = name
        self.port = port
        self.storage = []
        self.neighbors = neighbors  # List of (hostname, port) tuples
        self.running = True

    def receive_message(self, message):
        # Log message reception
        log_event(self.name, "RECEIVE", message['data'])

        # Store the message if it's not a duplicate
        if message not in self.storage:
            self.storage.append(message)
            print(f"{self.name} received message: '{message['data']}' with priority {message['priority']}")

    def send_message(self, message, neighbor):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(neighbor)
                s.sendall(json.dumps(message.to_dict()).encode('utf-8'))
                log_event(self.name, "SEND", message.data)
                print(f"{self.name} sent message to {neighbor}")
        except ConnectionRefusedError:
            print(f"{self.name} could not connect to {neighbor}")

    def forward_messages(self):
        for message in sorted(self.storage, key=lambda x: x['priority'], reverse=True):
            if message['transmitted']:
                continue
            for neighbor in self.neighbors:
                if random.choice([True, False]):  # Simulate intermittent connection
                    self.send_message(SpaceRelayMessage(**message), neighbor)
                    message['transmitted'] = True
                    break
                else:
                    message['retries'] += 1
                    log_event(self.name, "RETRY", message['data'])
                    if message['retries'] >= message['max_retries']:
                        print(f"{self.name} gave up on message '{message['data']}' after {message['retries']} attempts")
                        break

    def run(self):
        threading.Thread(target=self.server).start()
        while self.running:
            self.forward_messages()
            time.sleep(random.uniform(1, 3))

    def server(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
            server.bind(("0.0.0.0", self.port))
            server.listen()
            while self.running:
                conn, _ = server.accept()
                with conn:
                    data = conn.recv(1024)
                    if data:
                        message = json.loads(data.decode('utf-8'))
                        self.receive_message(message)

    def stop(self):
        self.running = False

# Instantiate and start the node
if __name__ == "__main__":
    node_name = "Node1"  # Should be set dynamically in each Docker container
    node_port = 5000  # Unique for each node/container
    neighbors = [("Node2", 5001), ("Node3", 5002)]  # Neighboring nodes with their ports

    node = RelayNode(node_name, node_port, neighbors)
    node.start()
    time.sleep(20)
    node.stop()
    node.join()
