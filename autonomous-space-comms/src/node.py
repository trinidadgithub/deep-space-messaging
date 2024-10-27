import threading
import time
import random
import socket
import json
import logging

# Configure centralized logging to capture all events in a shared log file
logging.basicConfig(
    filename="/app/logs/communication.log",  # Path to Docker-mounted volume for logs
    filemode="a",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

def log_event(node_name, event_type, message_data):
    """
    Logs events for the node's communication activities.

    Args:
        node_name (str): The name of the node logging the event.
        event_type (str): Type of the event (e.g., "SEND", "RECEIVE", "RETRY").
        message_data (str): Data content of the message involved in the event.
    """
    logging.info(f"{node_name} - {event_type} - {message_data}")

class SpaceRelayMessage:
    """
    Represents a message in the space relay system.

    Attributes:
        data (str): The content of the message.
        priority (int): Message priority, where higher values indicate higher importance.
        transmitted (bool): Indicates if the message has been successfully forwarded.
        retries (int): Count of retry attempts due to failed transmissions.
        max_retries (int): Maximum allowed retries before discarding the message.
    """
    def __init__(self, data, priority=1):
        self.data = data
        self.priority = priority
        self.transmitted = False
        self.retries = 0
        self.max_retries = 3

    def to_dict(self):
        """Converts the message attributes to a dictionary for easy JSON serialization."""
        return {
            "data": self.data,
            "priority": self.priority,
            "transmitted": self.transmitted,
            "retries": self.retries
        }

class RelayNode(threading.Thread):
    """
    Represents an autonomous relay node in a space communication network.

    Attributes:
        name (str): Node's identifier.
        port (int): Port on which the node listens for incoming messages.
        storage (list): Stores received messages for processing and forwarding.
        neighbors (list): List of neighboring nodes (hostname, port) tuples.
        running (bool): Controls the thread's active state; stops when False.
    """
    def __init__(self, name, port, neighbors):
        super().__init__()
        self.name = name
        self.port = port
        self.storage = []
        self.neighbors = neighbors
        self.running = True

    def receive_message(self, message):
        """
        Receives and logs a message if it's new; avoids duplicates.

        Args:
            message (dict): The message to be received and logged.
        """
        log_event(self.name, "RECEIVE", message['data'])
        if message not in self.storage:
            self.storage.append(message)
            print(f"{self.name} received message: '{message['data']}' with priority {message['priority']}")

    def send_message(self, message, neighbor):
        """
        Attempts to send a message to a neighboring node.

        Args:
            message (SpaceRelayMessage): The message to send.
            neighbor (tuple): Tuple containing (hostname, port) of the destination node.
        """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(neighbor)
                s.sendall(json.dumps(message.to_dict()).encode('utf-8'))
                log_event(self.name, "SEND", message.data)
                print(f"{self.name} sent message to {neighbor}")
        except ConnectionRefusedError:
            print(f"{self.name} could not connect to {neighbor}")

    def forward_messages(self):
        """
        Forwards stored messages to neighboring nodes.
        - Messages are prioritized by urgency.
        - Implements intermittent connectivity with randomized success.
        """
        for message in sorted(self.storage, key=lambda x: x['priority'], reverse=True):
            if message['transmitted']:
                continue
            for neighbor in self.neighbors:
                if random.choice([True, False]):  # Simulates intermittent connectivity
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
        """
        Main loop for node operation, forwarding messages periodically and listening for new messages.
        """
        threading.Thread(target=self.server).start()
        while self.running:
            self.forward_messages()
            time.sleep(random.uniform(1, 3))  # Random delay to simulate asynchronous operation

    def server(self):
        """
        Starts a server socket to receive incoming messages from other nodes.
        """
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
        """Stops the thread's main loop and ends the node's operations."""
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
