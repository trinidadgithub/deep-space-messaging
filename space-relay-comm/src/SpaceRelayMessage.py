import threading
import time
import random


class SpaceRelayMessage:
    """
    Represents a message to be sent between relay nodes.

    Attributes:
        data (str): The message content.
        priority (int): Message priority, with higher values indicating more urgent data.
        transmitted (bool): Indicates if the message has been successfully forwarded.
        retries (int): The count of resend attempts due to connection failures.
        max_retries (int): Maximum allowed retries for each message.
    """

    def __init__(self, data, priority=1):
        self.data = data
        self.priority = priority
        self.transmitted = False
        self.retries = 0
        self.max_retries = 3


class RelayNode(threading.Thread):
    """
    Represents a space relay node operating as a thread, autonomously forwarding messages.

    Attributes:
        name (str): The name identifier for the node.
        storage (list): Stores messages received by the node.
        connections (list): List of other nodes connected to this node for message forwarding.
        running (bool): Controls the node’s active status; False stops the thread.
    """

    def __init__(self, name):
        super().__init__()
        self.name = name
        self.storage = []  # Store messages to be forwarded
        self.connections = []  # List of other nodes to connect to
        self.running = True  # Keeps the thread running

    def add_connection(self, node):
        """Adds a connected node to allow message forwarding."""
        self.connections.append(node)

    def receive_message(self, message):
        """
        Receives a message, adding it to storage if it's not a duplicate.

        Args:
            message (SpaceRelayMessage): The message to receive and store.
        """
        if message not in self.storage:
            self.storage.append(message)
            print(f"{self.name} received message: '{message.data}' with priority {message.priority}")

    def forward_message(self):
        """
        Attempts to forward messages in storage to connected nodes.
        - Messages are forwarded based on priority.
        - Simulates random link availability to reflect space conditions.
        """
        for message in sorted(self.storage, key=lambda x: x.priority, reverse=True):
            if message.transmitted:  # Skip already transmitted messages
                continue
            for node in self.connections:
                # Simulate dynamic link availability, representing connectivity disruptions
                if random.choice([True, False]):
                    print(f"{self.name} successfully forwarded message to {node.name}")
                    node.receive_message(message)
                    message.transmitted = True  # Mark as transmitted
                    break
                else:
                    print(f"{self.name} failed to forward message to {node.name} due to link disruption")
                    time.sleep(0.5)  # Delay for retry
                    message.retries += 1
                    # Stop retrying if max retries reached
                    if message.retries >= message.max_retries:
                        print(f"{self.name} gave up on message '{message.data}' after {message.retries} attempts")
                        break

    def run(self):
        """
        Main thread loop: attempts to forward messages at random intervals,
        simulating autonomous, ongoing operation.
        """
        while self.running:
            self.forward_message()
            time.sleep(random.uniform(1, 3))  # Random interval for realistic timing

    def stop(self):
        """Stops the node’s operations by ending the thread loop."""
        self.running = False


# Instantiate nodes
earth_station = RelayNode("Earth Station")
mars_relay = RelayNode("Mars Relay")
lunar_outpost = RelayNode("Lunar Outpost")

# Set up network connections
earth_station.add_connection(mars_relay)  # Earth connects to Mars
mars_relay.add_connection(lunar_outpost)  # Mars connects to Lunar Outpost

# Start each node as a separate thread
earth_station.start()
mars_relay.start()
lunar_outpost.start()

# Create a message and send from Earth Station
message = SpaceRelayMessage("Critical mission update from Earth", priority=2)
earth_station.receive_message(message)

# Run the simulation for a limited time
time.sleep(10)

# Stop all threads after the simulation period
earth_station.stop()
mars_relay.stop()
lunar_outpost.stop()

# Ensure threads complete execution
earth_station.join()
mars_relay.join()
lunar_outpost.join()
