#!/bin/bash

# ChromaDB Server Status Script
# This script checks the status of ChromaDB server

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR"
CHROMA_PID_FILE="$PROJECT_DIR/chromadb.pid"
CHROMA_LOG_FILE="$PROJECT_DIR/chromadb.log"
CHROMA_HOST=${CHROMA_HOST:-"localhost"}
CHROMA_PORT=${CHROMA_PORT:-8000}

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if ChromaDB is running
check_chromadb_running() {
    if [ -f "$CHROMA_PID_FILE" ]; then
        PID=$(cat "$CHROMA_PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            return 0  # Running
        else
            # PID file exists but process is dead
            rm -f "$CHROMA_PID_FILE"
        fi
    fi
    return 1  # Not running
}

# Function to check if port is listening
check_port_listening() {
    if command_exists netstat; then
        if netstat -tuln | grep -q ":$CHROMA_PORT "; then
            return 0  # Port listening
        fi
    elif command_exists ss; then
        if ss -tuln | grep -q ":$CHROMA_PORT "; then
            return 0  # Port listening
        fi
    fi
    return 1  # Port not listening
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to test HTTP connection
test_http_connection() {
    if command_exists curl; then
        if curl -s --connect-timeout 5 "http://$CHROMA_HOST:$CHROMA_PORT/api/v1/heartbeat" > /dev/null 2>&1; then
            return 0  # HTTP connection successful
        fi
    elif command_exists wget; then
        if wget -q --timeout=5 --tries=1 "http://$CHROMA_HOST:$CHROMA_PORT/api/v1/heartbeat" -O /dev/null 2>&1; then
            return 0  # HTTP connection successful
        fi
    fi
    return 1  # HTTP connection failed
}

# Function to get process info
get_process_info() {
    local PID=$1
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "PID: $PID"
        echo "Command: $(ps -p "$PID" -o command=)"
        echo "Start Time: $(ps -p "$PID" -o lstart=)"
        echo "Memory Usage: $(ps -p "$PID" -o rss= | awk '{print $1/1024 " MB"}')"
        echo "CPU Usage: $(ps -p "$PID" -o %cpu=)%"
    fi
}

# Function to show log tail
show_log_tail() {
    if [ -f "$CHROMA_LOG_FILE" ]; then
        echo
        print_status "Recent log entries (last 10 lines):"
        echo "----------------------------------------"
        tail -n 10 "$CHROMA_LOG_FILE" 2>/dev/null || echo "No log entries found"
    fi
}

# Main execution
main() {
    echo "=========================================="
    echo "  ChromaDB Server Status"
    echo "=========================================="
    echo
    
    # Check if ChromaDB is running
    if check_chromadb_running; then
        PID=$(cat "$CHROMA_PID_FILE")
        print_success "ChromaDB server is RUNNING"
        echo
        print_status "Process Information:"
        get_process_info "$PID"
        echo
        
        # Check if port is listening
        if check_port_listening; then
            print_success "Port $CHROMA_PORT is listening"
        else
            print_warning "Port $CHROMA_PORT is not listening"
        fi
        
        # Test HTTP connection
        if test_http_connection; then
            print_success "HTTP connection successful"
            print_status "Server URL: http://$CHROMA_HOST:$CHROMA_PORT"
        else
            print_warning "HTTP connection failed"
        fi
        
        # Show log tail
        show_log_tail
        
    else
        print_error "ChromaDB server is NOT RUNNING"
        echo
        
        # Check if PID file exists but process is dead
        if [ -f "$CHROMA_PID_FILE" ]; then
            print_warning "PID file exists but process is dead"
            print_status "Cleaning up stale PID file..."
            rm -f "$CHROMA_PID_FILE"
        fi
        
        # Check if port is still in use
        if check_port_listening; then
            print_warning "Port $CHROMA_PORT is still in use by another process"
        fi
        
        # Show log tail if available
        show_log_tail
        
        echo
        print_status "To start ChromaDB server, run: ./start_chromadb.sh server"
    fi
    
    echo
    print_status "Configuration:"
    echo "  Host: $CHROMA_HOST"
    echo "  Port: $CHROMA_PORT"
    echo "  PID File: $CHROMA_PID_FILE"
    echo "  Log File: $CHROMA_LOG_FILE"
}

# Run main function
main "$@" 