# System Architecture

## Overview

This project implements a simplified Redis-like server using a modular design.

## Flow

Client → TCP Socket → Parser → Command Executor → Store → Response

## Components

### Parser

Handles both:

- plain text commands
- RESP array format

### Command Executor

Maps commands to store operations and handles validation.

### Store

Thread-safe key-value store with:

- TTL support
- lazy expiration
- atomic operations

### Persistence

Snapshot-based persistence:

- saves data and expiry metadata
- loads on server startup

### Networking

- multi-client handling using threads
- per-client transaction state
