#!/bin/bash

# Compile the C file into a binary named 'rohit'
gcc -o rohit rohit.c lpthread

# Give execution permissions to the binary
chmod +x rohit

echo "Build process completed. Binary 'rohit' is ready."
