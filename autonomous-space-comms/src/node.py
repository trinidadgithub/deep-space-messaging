import threading
import time
import random
import socket
import json
import logging
import os
import uuid

# Configure centralized logging to capture all events in a shared log file
logging.basicConfig(
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
    def __init__(self, data, priority=1, sender=None, message_id=None):
        self.data = data
        self.priority = priority
        self.transmitted = False
        self.retries = 0
        self.max_retries = 3
        self.id = message_id if message_id else str(uuid.uuid4())
        self.sender = sender

    def to_dict(self):
        """Converts the message attributes to a dictionary for easy JSON serialization."""
        return {
            "id": self.id,
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
        self.storage = {}
        self.neighbors = neighbors
        self.running = True

    def receive_message(self, message):
        """
        Receives and logs a message if it's new; avoids duplicates.

        Args:
            message (dict): The message to be received and logged.
        """
        logging.info(f"Message received and added to storage with id : {message['id']}")
        log_event(self.name, "RECEIVE", message['data'])

        message.setdefault('sender', None)  # Ensure 'sender' key is present
        message.setdefault('id', str(uuid.uuid4()))  # Ensure 'id' key is present

        if message['sender'] != self.name and message['id'] not in self.storage:  # Use message ID as the dictionary key
            self.storage[message['id']] = message  # Store by ID
            log_event(self.name, "RECEIVE", f" message: '{message['data']}' with priority {message['priority']}")

    def send_message(self, message, neighbor):
        """
        Attempts to send a message to a neighboring node.

        Args:
            message (SpaceRelayMessage): The message to send.
            neighbor (tuple): Tuple containing (hostname, port) of the destination node.
        """
        logging.info(f"{self.name} is sending message to {neighbor}")

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(neighbor)
                s.sendall(json.dumps(message.to_dict()).encode('utf-8'))
                log_event(self.name, "SEND", f"sent message to {neighbor}")

                # Create the stop flag after the first message is sent
                if not os.path.exists("stop_flag"):
                    open("stop_flag", "w").close()
                    logging.info("Stop flag created, halting further messages.")
        except ConnectionRefusedError:
            log_event(self.name, "SEND", f"could not connect to {neighbor}")

    import os
    import time

    def forward_messages(self):
        """
        Forwards stored messages to neighboring nodes.
        - Messages are prioritized by urgency.
        - Implements intermittent connectivity with randomized success.
        """
        logging.info(f"{self.name} storage contents: {self.storage}")

        # Stop forwarding if the stop_flag exists
        if os.path.exists("stop_flag"):
            logging.info(f"{self.name} stopping message forwarding due to stop flag.")
            return  # Exit the function if the stop flag is set

        for message in list(self.storage.values()):
            sender = message.get('sender', self.name)
            message_id = message.get('id', str(uuid.uuid4()))
            new_message = SpaceRelayMessage(message['data'], message['priority'], sender=sender,
                                            message_id=message_id)
            if new_message.transmitted:
                continue

            for neighbor in self.neighbors:
                # Skip forwarding to the original sender
                if neighbor[0] != sender and random.choice([True, False]):
                    self.send_message(new_message, neighbor)
                    new_message.transmitted = True
                    log_event(self.name, "FORWARD", f"sent message to {neighbor}")
                    break
                else:
                    new_message.retries += 1
                    log_event(self.name, "RETRY", new_message.data)
                    if new_message.retries >= new_message.max_retries:
                        log_event(self.name, "RETRY",
                                  f"gave up on message '{new_message.data}' after {new_message.retries} attempts to {neighbor}")
                        break
            time.sleep(1)

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
    logging.info("Main program started")
    node_name = os.getenv("NODE_NAME", "Node1")
    node_port = int(os.getenv("NODE_PORT", 5000))
    neighbors = [
         (os.getenv("NEIGHBOR1_NAME", "Node2"), int(os.getenv("NEIGHBOR1_PORT", 5001))),
         (os.getenv("NEIGHBOR2_NAME", "Node3"), int(os.getenv("NEIGHBOR2_PORT", 5002)))
    ]


    node = RelayNode(node_name, node_port, neighbors)
    # Add a persistent test message
    node.storage["test_message_id"] = {"data": "Persistent test message", "priority": 1}
    node.start()

    # Run for 20 seconds then stop
    time.sleep(20)
    node.stop()
    node.join()
