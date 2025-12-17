# pipes_demo.py
import os
import sys
import subprocess
import multiprocessing
import platform
import time
import threading

def detect_os():
    """Detect the current operating system"""
    system = platform.system().lower()
    if 'linux' in system:
        return 'linux'
    elif 'darwin' in system:
        return 'darwin'  # macOS
    elif 'windows' in system or 'win32' in system or 'cygwin' in system:
        return 'windows'
    else:
        return 'unknown'

def get_os_specific_info():
    """Get OS-specific information about pipes"""
    current_os = detect_os()
    
    info = {
        'linux': {
            'pipe_syscall': 'pipe(int pipefd[2])',
            'header_file': '<unistd.h>',
            'max_pipe_size': '65,536 bytes (default, can be increased)',
            'location': '/proc/sys/fs/pipe-max-size',
            'type': 'Unidirectional, in-memory buffer',
            'key_command': 'cat /proc/sys/fs/pipe-max-size'
        },
        'darwin': {
            'pipe_syscall': 'pipe(int pipefd[2])',
            'header_file': '<unistd.h>',
            'max_pipe_size': '65,536 bytes (default)',
            'location': 'kern.ipc.maxpipekva (tunable)',
            'type': 'Unidirectional, in-memory buffer',
            'key_command': 'sysctl kern.ipc.maxpipekva'
        },
        'windows': {
            'pipe_syscall': 'CreatePipe()',
            'header_file': '<windows.h>',
            'max_pipe_size': '65,536 bytes (default)',
            'location': 'Registry: HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Services\\LanmanServer\\Parameters',
            'type': 'Unidirectional or bidirectional, can be named',
            'key_command': 'Not directly queryable via command line'
        }
    }
    
    return current_os, info.get(current_os, {})

def print_os_info():
    """Print information about the current OS and its pipe implementation"""
    os_name, info = get_os_specific_info()
    
    print("=" * 70)
    print(f"CURRENT OPERATING SYSTEM: {platform.system()} ({os_name.upper()})")
    print("=" * 70)
    
    if info:
        print(f"Pipe System Call: {info['pipe_syscall']}")
        print(f"Header File: {info['header_file']}")
        print(f"Default Max Pipe Size: {info['max_pipe_size']}")
        print(f"Configuration Location: {info['location']}")
        print(f"Pipe Type: {info['type']}")
        print(f"Command to check max size: {info['key_command']}")
    else:
        print("No specific information available for this OS")
    
    print("=" * 70)
    print()

def basic_pipe_demo():
    """Basic pipe demonstration using os.pipe() (works on all platforms)"""
    print("=== BASIC PIPE DEMONSTRATION (Cross-Platform) ===")
    
    # Create a pipe - returns (read_fd, write_fd) on Unix, handles on Windows
    read_fd, write_fd = os.pipe()
    
    print(f"Created pipe: read_fd={read_fd}, write_fd={write_fd}")
    
    # Write to the pipe
    message = "Hello from the write end of the pipe!"
    os.write(write_fd, message.encode('utf-8'))
    print(f"Written to pipe: '{message}'")
    
    # Read from the pipe
    # Note: In real code, you'd need to read in a loop to get all data
    data = os.read(read_fd, 1024)
    print(f"Read from pipe: '{data.decode('utf-8')}'")
    
    # Close file descriptors
    os.close(read_fd)
    os.close(write_fd)
    print("Closed pipe file descriptors")
    print()

def pipe_with_subprocess():
    """Demonstrate pipes with subprocess communication"""
    print("=== PIPE WITH SUBPROCESS ===")
    
    # Create a pipe
    read_fd, write_fd = os.pipe()
    
    # Fork a child process (Unix-like) or use multiprocessing (cross-platform)
    pid = os.fork()
    
    if pid == 0:
        # Child process
        os.close(read_fd)  # Close unused read end
        
        # Write data to pipe
        messages = ["Child: Hello!", "Child: How are you?", "Child: Goodbye!"]
        for msg in messages:
            os.write(write_fd, f"{msg}\n".encode('utf-8'))
            time.sleep(0.5)
        
        os.close(write_fd)
        os._exit(0)
    else:
        # Parent process
        os.close(write_fd)  # Close unused write end
        
        print("Parent reading from child:")
        # Read until EOF
        while True:
            try:
                # Read a chunk of data
                data = os.read(read_fd, 1024)
                if not data:
                    break
                print(f"Received: {data.decode('utf-8').strip()}")
            except OSError:
                break
        
        os.close(read_fd)
        os.wait()  # Wait for child to finish
    print()

def windows_named_pipe_demo():
    """Demonstrate Windows named pipes"""
    print("=== WINDOWS NAMED PIPES DEMONSTRATION ===")
    
    if detect_os() != 'windows':
        print("Skipping Windows named pipe demo (not on Windows)")
        return
    
    try:
        import win32pipe
        import win32file
        import win32api
        import pywintypes
        
        # Create a named pipe
        pipe_name = r'\\.\pipe\MyTestPipe'
        
        print(f"Creating named pipe: {pipe_name}")
        
        # Create the pipe
        pipe_handle = win32pipe.CreateNamedPipe(
            pipe_name,
            win32pipe.PIPE_ACCESS_DUPLEX,
            win32pipe.PIPE_TYPE_MESSAGE | win32pipe.PIPE_READMODE_MESSAGE | win32pipe.PIPE_WAIT,
            1,  # Max instances
            65536,  # Out buffer size
            65536,  # In buffer size
            0,  # Default timeout
            None  # Default security attributes
        )
        
        print("Named pipe created. Waiting for client connection...")
        
        # In a real application, you'd have a separate client process
        # For demo, we'll simulate with threading
        def client_thread():
            time.sleep(1)
            try:
                # Client connects to the named pipe
                client_handle = win32file.CreateFile(
                    pipe_name,
                    win32file.GENERIC_READ | win32file.GENERIC_WRITE,
                    0,
                    None,
                    win32file.OPEN_EXISTING,
                    0,
                    None
                )
                
                # Send message
                message = "Hello from client!"
                win32file.WriteFile(client_handle, message.encode('utf-8'))
                print(f"Client sent: {message}")
                
                # Read response
                result, data = win32file.ReadFile(client_handle, 4096)
                print(f"Client received: {data.decode('utf-8')}")
                
                win32file.CloseHandle(client_handle)
            except Exception as e:
                print(f"Client error: {e}")
        
        # Start client thread
        client = threading.Thread(target=client_thread)
        client.start()
        
        # Server waits for connection
        win32pipe.ConnectNamedPipe(pipe_handle, None)
        print("Client connected to named pipe")
        
        # Read from client
        result, data = win32file.ReadFile(pipe_handle, 4096)
        message = data.decode('utf-8')
        print(f"Server received: {message}")
        
        # Send response
        response = f"Server response to: {message}"
        win32file.WriteFile(pipe_handle, response.encode('utf-8'))
        print(f"Server sent: {response}")
        
        # Cleanup
        win32pipe.DisconnectNamedPipe(pipe_handle)
        win32file.CloseHandle(pipe_handle)
        client.join()
        
    except ImportError:
        print("pywin32 module not installed. Install with: pip install pywin32")
    except Exception as e:
        print(f"Windows named pipe error: {e}")
    print()

def darwin_mach_port_demo():
    """Demonstrate macOS Mach ports (advanced interprocess communication)"""
    print("=== DARWIN MACH PORTS DEMONSTRATION ===")
    
    if detect_os() != 'darwin':
        print("Skipping Mach port demo (not on macOS/Darwin)")
        return
    
    try:
        # Mach ports are a macOS-specific IPC mechanism
        # This is a simplified demonstration
        print("Mach ports are a macOS-specific IPC mechanism.")
        print("They are more complex than pipes but offer more features.")
        
        # We'll use a simpler demonstration with ordinary pipes
        print("\nUsing ordinary pipes on macOS (same as Linux):")
        
        read_fd, write_fd = os.pipe()
        
        # Write some data
        os.write(write_fd, b"Data through pipe on macOS\n")
        
        # Read it back
        data = os.read(read_fd, 1024)
        print(f"Read from macOS pipe: {data.decode('utf-8').strip()}")
        
        os.close(read_fd)
        os.close(write_fd)
        
    except Exception as e:
        print(f"Darwin/Mach port error: {e}")
    print()

def linux_advanced_pipe_demo():
    """Demonstrate advanced Linux pipe features"""
    print("=== LINUX ADVANCED PIPE FEATURES ===")
    
    if detect_os() != 'linux':
        print("Skipping Linux advanced features demo (not on Linux)")
        return
    
    try:
        print("1. Checking current pipe buffer size limit:")
        result = subprocess.run(['cat', '/proc/sys/fs/pipe-max-size'], 
                              capture_output=True, text=True)
        print(f"   Maximum pipe size: {result.stdout.strip()} bytes")
        
        print("\n2. Creating pipe with O_NONBLOCK flag:")
        # On Linux, we can create pipes with different flags
        # For simplicity, we'll use os.pipe() which is the standard
        
        print("\n3. Using pipe() with fork() for IPC:")
        read_fd, write_fd = os.pipe()
        
        pid = os.fork()
        if pid == 0:
            # Child
            os.close(read_fd)
            for i in range(3):
                os.write(write_fd, f"Message {i} from child\n".encode())
                time.sleep(0.3)
            os.close(write_fd)
            os._exit(0)
        else:
            # Parent
            os.close(write_fd)
            print("   Parent reading from child:")
            while True:
                try:
                    data = os.read(read_fd, 1024)
                    if data:
                        print(f"   Received: {data.decode().strip()}")
                    else:
                        break
                except BlockingIOError:
                    break
            os.close(read_fd)
            os.wait()
        
        print("\n4. Using pipe() with popen (shell pipelines):")
        # Example of how shells implement pipelines
        p1 = subprocess.Popen(['echo', 'hello world'], stdout=subprocess.PIPE)
        p2 = subprocess.Popen(['tr', '[:lower:]', '[:upper:]'], 
                             stdin=p1.stdout, stdout=subprocess.PIPE)
        p1.stdout.close()
        output = p2.communicate()[0]
        print(f"   Pipeline result: {output.decode().strip()}")
        
    except Exception as e:
        print(f"Linux pipe demo error: {e}")
    print()

def cross_platform_pipe_example():
    """Cross-platform pipe example using multiprocessing"""
    print("=== CROSS-PLATFORM PIPE USING MULTIPROCESSING ===")
    
    def producer(conn):
        """Producer process/thread"""
        messages = ["Hello", "World", "From", "Cross-platform", "Pipe"]
        for msg in messages:
            conn.send(msg)
            time.sleep(0.2)
        conn.send("END")
        conn.close()
    
    def consumer(conn):
        """Consumer process/thread"""
        while True:
            try:
                msg = conn.recv()
                if msg == "END":
                    break
                print(f"Consumer received: {msg}")
            except EOFError:
                break
        conn.close()
    
    # Create a pipe using multiprocessing.Pipe
    parent_conn, child_conn = multiprocessing.Pipe()
    
    # Create processes
    producer_proc = multiprocessing.Process(target=producer, args=(child_conn,))
    consumer_proc = multiprocessing.Process(target=consumer, args=(parent_conn,))
    
    # Start processes
    consumer_proc.start()
    producer_proc.start()
    
    # Wait for completion
    producer_proc.join()
    consumer_proc.join()
    
    print("Cross-platform pipe example completed!")
    print()

def pipe_performance_test():
    """Test pipe performance on current OS"""
    print("=== PIPE PERFORMANCE TEST ===")
    
    os_name = detect_os()
    
    # Create pipe
    read_fd, write_fd = os.pipe()
    
    # Test data
    test_sizes = [1024, 4096, 16384, 65536]  # bytes
    results = {}
    
    for size in test_sizes:
        # Generate test data
        test_data = b'X' * size
        
        # Time write operation
        start = time.time()
        os.write(write_fd, test_data)
        write_time = time.time() - start
        
        # Time read operation
        start = time.time()
        data = os.read(read_fd, size)
        read_time = time.time() - start
        
        results[size] = {
            'write_time': write_time,
            'read_time': read_time,
            'throughput_write': size / write_time / (1024*1024) if write_time > 0 else 0,
            'throughput_read': size / read_time / (1024*1024) if read_time > 0 else 0
        }
    
    # Close file descriptors
    os.close(read_fd)
    os.close(write_fd)
    
    # Print results
    print(f"OS: {os_name.upper()}")
    print(f"{'Size (bytes)':<12} {'Write Time (s)':<15} {'Read Time (s)':<15} {'Write MB/s':<12} {'Read MB/s':<12}")
    print("-" * 70)
    
    for size, res in results.items():
        print(f"{size:<12} {res['write_time']:<15.6f} {res['read_time']:<15.6f} "
              f"{res['throughput_write']:<12.2f} {res['throughput_read']:<12.2f}")
    
    print()

def os_specific_commands():
    """Show OS-specific commands related to pipes"""
    print("=== OS-SPECIFIC PIPE COMMANDS ===")
    
    os_name = detect_os()
    
    commands = {
        'linux': [
            "cat /proc/sys/fs/pipe-max-size",
            "ulimit -a | grep pipe",
            "ls -la /proc/<pid>/fd/ | grep pipe",
            "strace -e pipe,read,write <command>",
            "lsof | grep FIFO",
        ],
        'darwin': [
            "sysctl kern.ipc.maxpipekva",
            "sysctl kern.ipc.pipekva",
            "lsof | grep PIPE",
            "dtrace -n 'syscall::pipe*:entry'",
        ],
        'windows': [
            "netstat -a | findstr PIPE",
            "Get-ChildItem \\\\.\\pipe\\",
            "powershell: [System.IO.Directory]::GetFiles('\\\\.\\pipe\\')",
            "Handle.exe -a | findstr Pipe",
        ]
    }
    
    if os_name in commands:
        print(f"Useful {os_name.upper()} commands for pipe debugging:")
        for cmd in commands[os_name]:
            print(f"  {cmd}")
    else:
        print("No OS-specific commands available")
    print()

def create_pipe_examples():
    """Create example files for each OS"""
    print("=== CREATING OS-SPECIFIC EXAMPLE FILES ===")
    
    os_name = detect_os()
    
    # Linux example
    linux_example = '''#!/usr/bin/env python3
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
        os.write(write_fd, f"{msg}\\n".encode())
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
'''

    # Windows example
    windows_example = '''# windows_pipe_example.py
import os
import multiprocessing
import time

def writer(conn):
    messages = ["Hello", "from", "Windows", "pipe"]
    for msg in messages:
        conn.send(msg)
        time.sleep(0.1)
    conn.close()

def reader(conn):
    while True:
        try:
            msg = conn.recv()
            print(f"Received: {msg}")
        except EOFError:
            break
    conn.close()

if __name__ == "__main__":
    # Create a pipe
    parent_conn, child_conn = multiprocessing.Pipe()
    
    # Create processes
    writer_proc = multiprocessing.Process(target=writer, args=(child_conn,))
    reader_proc = multiprocessing.Process(target=reader, args=(parent_conn,))
    
    # Start processes
    reader_proc.start()
    writer_proc.start()
    
    writer_proc.join()
    reader_proc.join()
'''

    # Darwin/macOS example
    darwin_example = '''#!/usr/bin/env python3
# darwin_pipe_example.py
import os

# Create a pipe (works same as Linux on macOS)
read_fd, write_fd = os.pipe()

# Write some data
os.write(write_fd, b"Hello from macOS/Darwin pipe\\n")

# Read it back
data = os.read(read_fd, 1024)
print(f"Read: {data.decode().strip()}")

# Close file descriptors
os.close(read_fd)
os.close(write_fd)

# Demonstrate with subprocess (common use case)
import subprocess

# Create a pipeline like in shell: echo "hello" | tr '[:lower:]' '[:upper:]'
p1 = subprocess.Popen(['echo', 'hello darwin'], stdout=subprocess.PIPE)
p2 = subprocess.Popen(['tr', '[:lower:]', '[:upper:]'], 
                     stdin=p1.stdout, stdout=subprocess.PIPE)
p1.stdout.close()
output = p2.communicate()[0]
print(f"Pipeline result: {output.decode().strip()}")
'''

    # Write appropriate example file
    filename = f"{os_name}_pipe_example.py"
    if os_name == 'linux':
        content = linux_example
    elif os_name == 'windows':
        content = windows_example
    elif os_name == 'darwin':
        content = darwin_example
    else:
        content = "# Generic pipe example\nimport os\nprint('Pipe demo')\n"
        filename = "generic_pipe_example.py"
    
    with open(filename, 'w') as f:
        f.write(content)
    
    print(f"Created example file: {filename}")
    print(f"Run it with: python {filename}")
    print()

def main():
    """Main function to run all demonstrations"""
    print("=" * 70)
    print("PIPE DEMONSTRATION ACROSS OPERATING SYSTEMS")
    print("=" * 70)
    print()
    
    # Print OS information
    print_os_info()
    
    # Run demonstrations
    basic_pipe_demo()
    
    # OS-specific demos
    windows_named_pipe_demo()
    darwin_mach_port_demo()
    linux_advanced_pipe_demo()
    
    # Cross-platform examples
    try:
        # This only works on Unix-like systems
        pipe_with_subprocess()
    except AttributeError:
        print("fork() not available on this OS (likely Windows)")
        print()
    
    cross_platform_pipe_example()
    pipe_performance_test()
    os_specific_commands()
    create_pipe_examples()
    
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print("""
Key Differences Between OS Pipe Implementations:

1. LINUX:
   - Uses pipe() system call from <unistd.h>
   - Maximum size configurable via /proc/sys/fs/pipe-max-size
   - Supports advanced features like pipe2() with flags
   - Fully bidirectional with socketpair()

2. DARWIN (macOS):
   - Similar to Linux (POSIX compliant)
   - Also supports Mach ports for advanced IPC
   - Maximum size tunable via sysctl
   - Uses same pipe() system call

3. WINDOWS:
   - Uses CreatePipe() API
   - Supports named pipes (\\\\.\\pipe\\name)
   - Can be bidirectional
   - Different error codes and behaviors
   - No fork(), so multiprocessing needed for similar patterns

Common Features:
- All support anonymous pipes for parent-child communication
- All provide stream-oriented communication
- All handle buffer management automatically
- All support blocking and non-blocking modes (with appropriate flags)
    """)

if __name__ == "__main__":
    main() 
