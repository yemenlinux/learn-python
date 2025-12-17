#!/bin/bash
# test_linux_pipes.sh

echo "Testing Linux pipes..."

# Clean up any existing pipes first
cleanup() {
    echo "Cleaning up..."
    rm -f mypipe
#     rm -f mydarwinpipe
}
trap cleanup EXIT

# Test 1: Simple pipe in shell
echo "Test 1: Shell pipe"
echo "hello world" | tr '[:lower:]' '[:upper:]'

# Test 2: Named pipe (FIFO)
echo -e "\nTest 2: Named pipe (FIFO)"
if [ -p mypipe ]; then
    echo "Removing existing pipe: mypipe"
    rm mypipe
fi
mkfifo mypipe &
echo "data through fifo" > mypipe &
cat mypipe

echo "remove pipe"
rm mypipe
trap cleanup EXIT

# Test 3: Check pipe limits
echo -e "\nTest 3: Pipe limits"
cat /proc/sys/fs/pipe-max-size
ulimit -a | grep pipe 
