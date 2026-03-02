Secure OSC over UDP

A lightweight application-layer security envelope for transmitting Open Sound Control (OSC) performance data over UDP.

Overview

Open Sound Control (OSC) is widely used in live electronic music, interactive art, and networked performance systems. OSC messages are typically transmitted over UDP to maintain low latency. However, UDP does not provide authentication, integrity protection or replay protection. On shared WiFi networks, any device that knows (or discovers) the destination IP address and port can inject OSC messages, potentially disrupting a performance.

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
	•	Laptop or other computer running Max/MSP or Pd receives OSC

Secure system:
	•	Pico W wraps OSC payloads in a secure packet format
	•	A verification gateway on the laptop validates HMAC authentication tags, enforces sequence number checks and forwards verified OSC to 127.0.0.1 for Max/MSP.

Max/MSP or Pd receives only verified messages.

⸻

Secure Packet Format

Each UDP datagram contains:
	1.	A 12-byte header
	2.	Version (1 byte)
	3.	Reserved / flags (1 byte)
	4.	Device ID (4 bytes)
	5.	Sequence number (4 bytes)
	6.	Payload length (2 bytes)
	7.	The original OSC payload (unmodified)
	8.	A 16-byte truncated HMAC-SHA256 authentication tag

The HMAC is computed over the header and payload using a pre-shared symmetric key provisioned out-of-band.
