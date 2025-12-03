import os
import time

def pipe_communication():
    """Demonstrate interprocess communication using pipes"""
    # Create pipe - returns (read_fd, write_fd)
    read_fd, write_fd = os.pipe()
    
    pid = os.fork()
    print(f"out: {pid}")
    if pid == 0:
        print(f"in if out: {pid}")
        # Child process - writer
        os.close(read_fd)  # Close unused read end
        
        messages = ["Hello", "World", "From", "Child"]
        for msg in messages:
            # Write to pipe
            os.write(write_fd, f"{msg}\n".encode())
            time.sleep(1)
        
        os.close(write_fd)
        os._exit(0)
    else:
        print(f"in else out: {pid}")
        # Parent process - reader
        os.close(write_fd)  # Close unused write end
        
        print("Parent reading from pipe:")
        # Read from pipe
        with os.fdopen(read_fd) as f:
            for line in f:
                print(f"Received: {line.strip()}")
        
        os.wait()  # Wait for child

pipe_communication()
