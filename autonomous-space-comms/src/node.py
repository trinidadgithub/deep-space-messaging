import threading
import time
import random
import socket
import json
import logging
import os

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
        logging.info("Function init of SpaceRelayMessage started")
        self.data = data
        self.priority = priority
        self.transmitted = False
        self.retries = 0
        self.max_retries = 3

    def to_dict(self):
        """Converts the message attributes to a dictionary for easy JSON serialization."""
        logging.info("Function to_dict started")
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
        logging.info("Function init of RelayNode class started")
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
        logging.info("Function receive_message started")
        logging.info(f"Message received and added to storage: {message}")
        log_event(self.name, "RECEIVE", message['data'])
        if message not in self.storage:
            self.storage.append(message)
            log_event(self.name, "RECEIVE", " received message: '{message['data']}' with priority {message['priority']}")

    def send_message(self, message, neighbor):
        """
        Attempts to send a message to a neighboring node.

        Args:
            message (SpaceRelayMessage): The message to send.
            neighbor (tuple): Tuple containing (hostname, port) of the destination node.
        """
        logging.info("Function send_message started")
        logging.info(f"{self.name} is sending message to {neighbor}")

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(neighbor)
                s.sendall(json.dumps(message.to_dict()).encode('utf-8'))
                log_event(self.name, "SEND", f"sent message to {neighbor}")
        except ConnectionRefusedError:
            log_event(self.name, "SEND", f"could not connect to {neighbor}")

    def forward_messages(self):
        """
        Forwards stored messages to neighboring nodes.
        - Messages are prioritized by urgency.
        - Implements intermittent connectivity with randomized success.
        """
        logging.info("Function forward_messages started")
        logging.info(f"{self.name} storage contents: {self.storage}")

        for message in self.storage:
         # Convert dictionary-based message to SpaceRelayMessage object
         new_message = SpaceRelayMessage(message['data'], message['priority'])
        
         if new_message.transmitted:
             continue
        
         for neighbor in self.neighbors:
             if random.choice([True, False]):  # Simulate intermittent connectivity
                 self.send_message(new_message, neighbor)
                 new_message.transmitted = True
                 break
             else:
                 new_message.retries += 1
                 
                 log_event(self.name, "RETRY", new_message.data)
                 
                 if new_message.retries >= new_message.max_retries:
                     log_event(self.name, "FORWARD", f" gave up on message '{new_message.data}' after {new_message.retries} attempts")
                     break

    def run(self):
        """
        Main loop for node operation, forwarding messages periodically and listening for new messages.
        """
        logging.info("Function run started")
        threading.Thread(target=self.server).start()
        while self.running:
            self.forward_messages()
            time.sleep(random.uniform(1, 3))  # Random delay to simulate asynchronous operation

    def server(self):
        """
        Starts a server socket to receive incoming messages from other nodes.
        """
        logging.info("Function server started")
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
        logging.info("Function stop started")
        self.running = False

# Instantiate and start the node
if __name__ == "__main__":
    logging.info("Main program started")
    node_name = os.getenv("NODE_NAME", "Node1")
    node_port = int(os.getenv("NODE_PORT", 5000))
    neighbors = [
         (os.getenv("NEIGHBOR1_NAME", "Node2"), int(os.getenv("NEIGHBOR1_PORT", 5001))),
         (os.getenv("NEIGHBOR2_NAME", "Node3"), int(os.getenv("NEIGHBOR2_PORT", 5002)))
    ]


    node = RelayNode(node_name, node_port, neighbors)
    # Add a persistent test message
    node.storage.append({"data": "Persistent test message", "priority": 1})
    node.start()
