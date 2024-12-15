# Project Description: Reverse Shell Backdoor
# This backdoor is a Python-based reverse shell that establishes a remote connection between a client and a server. It allows the operator to execute various commands on the target machine, transfer files, capture screenshots, and monitor keystrokes. The key features include:
# 
# Command Execution: Execute system commands remotely on the client machine.
# File Transfer:
# Download: Retrieve files from the client to the server.
# Upload: Send files from the server to the client.
# Keylogger: Start a keylogger to capture and retrieve keystrokes.
# Screenshots: Capture screenshots from the client machine.
# Persistence: The backdoor sets up persistence by adding itself to Windows startup via the registry.
# Connection Handling: Reconnect automatically if the connection is dropped.
# This backdoor consists of two components:
# 
# Client: The payload deployed on the target machine.
# Server: The command-and-control interface for interacting with the client.
