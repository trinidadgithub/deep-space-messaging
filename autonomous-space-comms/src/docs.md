# Implementation of autonomous space communication prototype

In this directory is a prototype for our autonomous space communication system using Python with threading and Docker. Each node will act as a separate Docker container, sending and receiving messages randomly across a network. Here’s the plan:

**Python Node Prototype:** Each node will be a Python script representing a node with autonomous behavior.

**Threaded Communication:** Nodes will run as separate threads in each Docker container.

**Docker Network:** Nodes will be able to communicate with each other via Docker’s networking capabilities.

**Message Simulation:** Each node will send random messages to other nodes, implementing a store-and-forward model with retries.

**Centralized Communication Logs:** Implement a centralized logger to store log events.  These events will be used to train machine learning algorithms to learn the best routes for communication.

### Node Chatter

We want to see the nodes chattering and log these events centrally.

**Step 1:** Implement Logging in Each Node

We’ll add a simple logger in node.py to send each message’s details to a centralized log server or print to a single log file if running locally.

```python
import logging

# Configure logger
logging.basicConfig(
    filename="communication.log",  # Or use '/app/logs/communication.log' if logging to a shared volume in Docker
    filemode="a",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

def log_event(node_name, event_type, message_data):
    logging.info(f"{node_name} - {event_type} - {message_data}")

```

Update each action within `RelayNode` to log events:

```python
# In receive_message method
log_event(self.name, "RECEIVE", message['data'])

# In forward_messages method, after successfully forwarding
log_event(self.name, "FORWARD", message['data'])
```

**Step 2:** Aggregate Logs from Docker Containers

- Option 1: View Logs Directly in Docker Compose.  Use docker compose logs -f to view real-time logs for all containers in one terminal session.
- Option 2: Docker Volumes for Centralized Logging

If you want all nodes to write to a shared file, create a volume in Docker Compose:

```dockerfile
volumes:
  log_volume:

services:
  node1:
    # ...
    volumes:
      - log_volume:/app/logs

  node2:
    # ...
    volumes:
      - log_volume:/app/logs

  node3:
    # ...
    volumes:
      - log_volume:/app/logs

networks:
  skynet:
    driver: bridge

volumes:
  log_volume:

```

This configuration allows each node to write to /app/logs/communication.log, creating a single file with consolidated logs.

- log_volume: Defined as a Docker-managed volume, Docker will handle its lifecycle. All logs written to /app/logs inside each container will be stored in this shared volume.
- To view the logs stored in log_volume, you can use:
```bash
docker volume inspect log_volume
docker run --rm -v log_volume:/data alpine ls /data
```

**Step 3:** Future Machine Learning Integration

With this setup, each message interaction is logged with details on routes, message success, and retries. This data can later be processed to train a model for route optimization based on observed performance, helping predict the best paths and times for future transmissions.

## Enhancements and Future Suggestions

1. Advanced Routing Algorithm:  
   - Replace random message forwarding with a smart routing algorithm that selects the best neighbor based on latency, availability, and proximity.
   - Implement machine learning-based predictions for optimal routes based on historical data.

2. Enhanced Retry and Timeout Mechanisms:
   - Add exponential backoff for retry intervals to manage bandwidth and reduce congestion.
   - Include a message expiry mechanism where old messages are discarded if they exceed a maximum wait time.

3. Power and Resource Management Simulation:
    - Implement power constraints for each node, adjusting message forwarding based on available energy levels.
    - Introduce resource checks to prioritize messages when storage or bandwidth is limited.

4. Self-Monitoring and Health Reporting:
    - Allow nodes to monitor their own health (e.g., connection status, error rates) and report issues.
    - Enable neighboring nodes to adjust their routing if a node reports connectivity or processing issues.

5. Centralized Monitoring and Visualization:
    - Add support for sending logs to a centralized monitoring system, enabling real-time visualization of node activities, message flows, and network health.
    - Integrate with tools like Grafana or Prometheus for advanced data analysis.

These future improvements will help simulate an even more realistic, autonomous space communication network, especially beneficial for scalability and predictive analysis. 




