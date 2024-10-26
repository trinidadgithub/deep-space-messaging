## Astro Messaging Simulation

To make each node a separate running thread and simulate real-time message passing between nodes, we’ll use Python’s threading library. Each AstroNode will run as an independent thread, which continuously attempts to receive and forward messages based on intermittent connectivity. This approach will bring a more dynamic, asynchronous feel to the system, much like real space communication networks.

Explanation of Features

    Threading Each Node:
        By inheriting from threading.Thread, each AstroNode instance becomes a separate thread, allowing asynchronous operation.
        The run method of each thread continuously attempts to forward messages at random intervals, simulating real-time message handling.

    Intermittent Connectivity and Retry Mechanism:
        Each node attempts to forward messages based on random connectivity, using random.choice([True, False]) to decide if a connection is available, representing cosmic interference or obstacles in signal paths.
        If a connection fails, the node retries up to three times with short delays.

    Graceful Stop Mechanism:
        A stop method sets a running flag to False, allowing each node to exit its run loop when the simulation ends.
        After a defined period (10 seconds in this example), we stop and join all threads, ensuring a clean shutdown.

    Random Forwarding Intervals:
        Nodes attempt to forward messages at random intervals between 1 and 3 seconds (time.sleep(random.uniform(1, 3))), simulating delays in real-time communication.

How This Simulates Real Space Communication

    Concurrent Operation: Each node operates independently, mimicking how real-world space nodes (satellites, relay stations) act autonomously, only transmitting data when conditions permit.
    Dynamic Connectivity: Randomized connection availability reflects the unpredictable nature of space communications, where obstacles, radiation, and interference can disrupt signals.
    Retry Mechanisms: The retry logic with short delays simulates handling errors due to cosmic interference, which is common in deep-space environments.

This system provides a realistic representation of a DTN-inspired communication network for space, with asynchronous message handling, intermittent connectivity, and autonomous retry logic. This framework can be expanded further to include message prioritization across multiple threads, power-saving modes, or even queue management algorithms.

### Running the simulation

In your python virtual environment, launch the simulation like this `python AstroMessage.py`

Explanation of Each Attribute and Method

    Attributes:
        data: Stores the core content of the message, simulating the data transmitted between space nodes.
        priority: This helps nodes decide which messages to process first, with higher-priority messages handled before routine data.
        transmitted: Indicates if the message has reached its final destination.
        integrity_check: A calculated checksum used to verify that the message remains unchanged during transmission.
        retry_count: Tracks how many times the message has been resent due to failed integrity checks.

    Methods:
        calculate_checksum(): Calculates a basic checksum based on ASCII values to detect corruption.
        validate_integrity(): Compares checksums to ensure the message has not been altered, providing a basic data integrity check.