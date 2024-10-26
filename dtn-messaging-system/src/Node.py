# This code shows a basic structure, where nodes can receive and forward bundles.
# For a complete prototype, we would implement custody transfers, retransmission mechanisms,
# and proper storage management.

# TODO: Implement custody transfers
# TODO: Implement retransmission mechanisms
# TODO: Implement storage management

import time
import random


class Node:
    def __init__(self, name):
        self.name = name
        self.storage = []
        self.connections = []

    def receive_bundle(self, bundle):
        # Add bundle to storage if not already received
        if bundle not in self.storage:
            self.storage.append(bundle)
            print(f"{self.name} received bundle: {bundle.data}")

    def forward_bundle(self):
        if not self.connections:
            print(f"{self.name} has no connections to forward.")
            return
        for bundle in self.storage:
            for node in self.connections:
                # Simulate intermittent connectivity
                if random.choice([True, False]):
                    node.receive_bundle(bundle)


class Bundle:
    def __init__(self, data):
        self.data = data


# Example Usage
earth = Node("Earth")
mars_orbit = Node("Mars Relay")
rover = Node("Mars Rover")

# Set connections
earth.connections.append(mars_orbit)
mars_orbit.connections.append(rover)

# Create bundle and simulate transmission
bundle = Bundle("Message from Earth to Mars")
earth.receive_bundle(bundle)
earth.forward_bundle()
mars_orbit.forward_bundle()
