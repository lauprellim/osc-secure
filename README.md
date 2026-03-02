Secure OSC over UDP

A lightweight application-layer security envelope for transmitting Open Sound Control (OSC) performance data over UDP.

Overview

Open Sound Control (OSC) is widely used in live electronic music, interactive art, and networked performance systems. OSC messages are typically transmitted over UDP to maintain low latency.

However, UDP provides:
	•	No authentication
	•	No integrity protection
	•	No replay protection

On shared WiFi networks, any device that knows (or discovers) the destination IP address and port can inject OSC messages, potentially disrupting a performance.

This project demonstrates that vulnerability and implements a lightweight, application-layer security mechanism to mitigate it.

⸻

Project Goals

The system adds a secure transport envelope around OSC messages that provides:
	•	Message authenticity and integrity using HMAC-SHA256
	•	Anti-replay protection using monotonic sequence numbers
	•	Basic rate limiting and validation on the receiving host

The goal is to preserve low latency while significantly improving resilience against injection and replay attacks.

⸻

System Architecture

Baseline system:
	•	Raspberry Pi Pico W (“victim”) sends OSC over UDP
	•	Raspberry Pi Pico W (“attacker”) attempts message injection
	•	Laptop running Max/MSP receives OSC

Secure system:
	•	Pico W wraps OSC payloads in a secure packet format
	•	A verification gateway on the laptop:
	•	Validates HMAC authentication tags
	•	Enforces sequence number checks
	•	Forwards verified OSC to 127.0.0.1 for Max/MSP

Max/MSP receives only verified messages.

⸻

Secure Packet Format

Each UDP datagram contains:
	1.	A 12-byte header
	•	Version (1 byte)
	•	Reserved / flags (1 byte)
	•	Device ID (4 bytes)
	•	Sequence number (4 bytes)
	•	Payload length (2 bytes)
	2.	The original OSC payload (unmodified)
	3.	A 16-byte truncated HMAC-SHA256 authentication tag

The HMAC is computed over the header and payload using a pre-shared symmetric key provisioned out-of-band.
