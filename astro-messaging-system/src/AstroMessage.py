import threading
import time
import random

"""
Represents a message transmitted between nodes in the Astro Messaging System.

Attributes:
    data (str): The content of the message being sent.
    priority (int): The priority level of the message, with higher values indicating
                    more critical information. Defaults to 1.
    transmitted (bool): Flag indicating whether the message has been successfully
                        transmitted to its destination.
    integrity_check (int): A checksum value calculated from the message content to
                           verify data integrity during transmission.
    retry_count (int): The number of times the message has been re-sent due to detected
                       data corruption, simulating retry attempts in space environments
                       affected by cosmic radiation.

Methods:
    calculate_checksum(): Calculates a checksum for data integrity validation by summing
                          the ASCII values of characters in the message, modulated to a
                          smaller integer range. This helps detect data corruption.
    validate_integrity(checksum): Compares the message's original checksum with the provided
                                  checksum to determine if data corruption has occurred.
"""

class AstroMessage:
    def __init__(self, data, priority=1):
        self.data = data
        self.priority = priority
        self.transmitted = False
        self.integrity_check = self.calculate_checksum()
        self.retry_count = 0  # Track number of retries due to corruption

    def calculate_checksum(self):
        # Simple checksum for data integrity validation
        return sum(ord(char) for char in self.data) % 256

    def validate_integrity(self, checksum):
        return self.integrity_check == checksum

class AstroNode(threading.Thread):
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.storage = []
        self.connections = []
        self.running = True

    def run(self):
        while self.running:
            # Periodically attempt to forward messages in storage
            self.forward_message()
            time.sleep(random.uniform(1, 3))  # Random delay to simulate real-time operation

    def receive_message(self, message):
        # Simulate integrity check in a high-radiation environment
        if message.validate_integrity(message.integrity_check):
            self.storage.append(message)
            print(f"{self.name} received message: {message.data}")
        else:
            print(f"{self.name} detected message corruption. Requesting resend.")
            message.retry_count += 1
            if message.retry_count < 3:
                # Retry receiving the message after a short delay
                time.sleep(1)
                self.receive_message(message)

    def forward_message(self):
        if not self.connections:
            print(f"{self.name} has no connections to forward.")
            return
        for message in sorted(self.storage, key=lambda x: x.priority, reverse=True):
            if not message.transmitted:
                for node in self.connections:
                    # Simulate intermittent connectivity due to cosmic interference
                    if random.choice([True, False]):
                        node.receive_message(message)
                        message.transmitted = True
                        print(f"{self.name} forwarded message to {node.name}")
                        break
                    else:
                        print(f"{self.name} failed to forward message to {node.name} due to cosmic interference.")
                        time.sleep(0.5)
                        message.retry_count += 1
                        if message.retry_count < 3:
                            self.forward_message()  # Retry sending within allowed retries

    def stop(self):
        self.running = False

# Create nodes and connections
earth = AstroNode("Earth")
mars_orbit = AstroNode("Mars Relay")
mars_rover = AstroNode("Mars Rover")

earth.connections.append(mars_orbit)
mars_orbit.connections.append(mars_rover)

# Start the nodes as threads
earth.start()
mars_orbit.start()
mars_rover.start()

# Send a high-priority message from Earth
message = AstroMessage("Critical mission data from Earth to Mars", priority=2)
earth.receive_message(message)

# Run the simulation for a limited time
time.sleep(10)

# Stop all threads after the simulation period
earth.stop()
mars_orbit.stop()
mars_rover.stop()

# Ensure threads complete
earth.join()
mars_orbit.join()
mars_rover.join()
