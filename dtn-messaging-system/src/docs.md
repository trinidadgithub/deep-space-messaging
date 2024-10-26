# Delay-Tolerant Networking (DTN) Messaging Simulation #

This project is a simple Python-based Delay-Tolerant Networking (DTN) messaging system prototype. It simulates the store-and-forward behavior of DTN, which is crucial for communication in environments with intermittent connectivity and long delays, such as space. DTN is commonly used in space communications (e.g., Mars missions), where reliable message transmission across nodes is essential despite network disruptions.
Overview

In this simulation:

- Nodes represent entities (such as satellites or planetary relays) capable of storing and forwarding messages, called bundles, to other nodes.
- Bundles are data units transmitted across the network from one node to another.
- Each Node has a list of connections (neighboring nodes) through which it can forward bundles.
- Intermittent connectivity is simulated by randomly choosing whether each message successfully forwards to the next node, mimicking real-world disruptions.

## Classes ##
1. Node

Represents a node in the network that can receive and forward bundles to other connected nodes.

Attributes:
```
    name: Name of the node (e.g., "Earth", "Mars Relay").
    storage: List to store received bundles.
    connections: List of other nodes connected to this node.
```
    Methods:
        receive_bundle(self, bundle): Receives a bundle and stores it if it hasn't been received already.
        forward_bundle(self): Attempts to forward stored bundles to each connected node, with simulated intermittent connectivity.

2. Bundle

Represents the message being sent between nodes.

    Attributes:
        data: The content of the message.

### Example Usage

This example demonstrates a simple network with three nodes (Earth, Mars Relay, and Mars Rover) and shows how a bundle is created and forwarded across the network.

### Initialize nodes
```
earth = Node("Earth")
mars_orbit = Node("Mars Relay")
rover = Node("Mars Rover")
```
###  Set connections
```
earth.connections.append(mars_orbit)
mars_orbit.connections.append(rover)
```

### Create a bundle and simulate transmission
```
bundle = Bundle("Message from Earth to Mars")
earth.receive_bundle(bundle)
earth.forward_bundle()
mars_orbit.forward_bundle()
```
### Simulation

- The Node.forward_bundle method uses random.choice([True, False]) to simulate the intermittent connectivity often encountered in space missions. 
- Messages (bundles) that do not successfully forward will remain in the node's storage, enabling reattempted transmission in future network cycles.


### Future Enhancements

This project can be extended with features like:

- Custody transfer: Ensuring that each bundle has a designated custodian node to maintain reliability.
- Retry mechanisms: Nodes could retry failed transmissions based on timeouts.
- Enhanced routing: Adding routing algorithms to dynamically select the optimal path for each bundle.

