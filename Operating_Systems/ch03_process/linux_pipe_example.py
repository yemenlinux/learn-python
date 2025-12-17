#!/usr/bin/env python3
# linux_pipe_example.py
import os

# Create a pipe
read_fd, write_fd = os.pipe()

# Fork a child process
pid = os.fork()

if pid == 0:
    # Child process - writer
    os.close(read_fd)
    messages = ["Hello", "from", "Linux", "pipe"]
    for msg in messages:
        os.write(write_fd, f"{msg}\n".encode())
    os.close(write_fd)
    os._exit(0)
else:
    # Parent process - reader
    os.close(write_fd)
    print("Parent reading from pipe:")
    while True:
        data = os.read(read_fd, 1024)
        if not data:
            break
        print(data.decode().strip())
    os.close(read_fd)
    os.wait()
