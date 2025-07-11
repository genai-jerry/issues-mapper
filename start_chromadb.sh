#!/bin/bash

# ChromaDB Server Startup Script
# This script starts ChromaDB as a server for remote access

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
CHROMA_DIR="$PROJECT_DIR/chroma_db"
CHROMA_HOST=${CHROMA_HOST:-"localhost"}
CHROMA_PORT=${CHROMA_PORT:-8000}
CHROMA_PID_FILE="$PROJECT_DIR/chromadb.pid"
CHROMA_LOG_FILE="$PROJECT_DIR/chromadb.log"

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

# Function to check if ChromaDB is already running
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

# Function to check if port is available
check_port() {
    if command_exists netstat; then
        if netstat -tuln | grep -q ":$CHROMA_PORT "; then
            return 0  # Port in use
        fi
    elif command_exists ss; then
        if ss -tuln | grep -q ":$CHROMA_PORT "; then
            return 0  # Port in use
        fi
    fi
    return 1  # Port available
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to setup ChromaDB directory
setup_chromadb_dir() {
    print_status "Setting up ChromaDB directory..."
    
    if [ ! -d "$CHROMA_DIR" ]; then
        mkdir -p "$CHROMA_DIR"
        print_success "Created ChromaDB directory: $CHROMA_DIR"
    else
        print_status "ChromaDB directory already exists: $CHROMA_DIR"
    fi
}

# Function to start ChromaDB server
start_chromadb_server() {
    print_status "Starting ChromaDB server..."
    print_status "Host: $CHROMA_HOST"
    print_status "Port: $CHROMA_PORT"
    print_status "Data directory: $CHROMA_DIR"
    print_status "Log file: $CHROMA_LOG_FILE"
    echo
    
    # Create log directory if it doesn't exist
    mkdir -p "$(dirname "$CHROMA_LOG_FILE")"
    
    # Start ChromaDB server
    cd "$PROJECT_DIR"
    
    # Use chroma run command to start the server
    chroma run \
        --host "$CHROMA_HOST" \
        --port "$CHROMA_PORT" \
        --path "$CHROMA_DIR" \
        > "$CHROMA_LOG_FILE" 2>&1 &
    
    # Save PID
    echo $! > "$CHROMA_PID_FILE"
    
    # Wait a moment for server to start
    sleep 3
    
    # Check if server started successfully
    if check_chromadb_running; then
        print_success "ChromaDB server started successfully!"
        print_status "Server is running on: http://$CHROMA_HOST:$CHROMA_PORT"
        print_status "PID: $(cat "$CHROMA_PID_FILE")"
        print_status "Log file: $CHROMA_LOG_FILE"
        echo
        print_status "To stop the server, run: ./stop_chromadb.sh"
    else
        print_error "Failed to start ChromaDB server"
        print_status "Check the log file: $CHROMA_LOG_FILE"
        exit 1
    fi
}

# Function to start ChromaDB in persistent mode (local)
start_chromadb_persistent() {
    print_status "Starting ChromaDB in persistent mode (local)..."
    print_status "Data directory: $CHROMA_DIR"
    echo
    
    # This is just for setup - persistent mode doesn't need a server
    print_success "ChromaDB persistent mode is ready!"
    print_status "Data will be stored in: $CHROMA_DIR"
    print_status "Use the EmbeddingManager with vector_storage_type='chroma'"
}

# Function to cleanup on exit
cleanup() {
    print_status "Shutting down ChromaDB server..."
    if [ -f "$CHROMA_PID_FILE" ]; then
        PID=$(cat "$CHROMA_PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            kill "$PID"
            print_status "Sent termination signal to ChromaDB (PID: $PID)"
        fi
        rm -f "$CHROMA_PID_FILE"
    fi
    exit 0
}

# Main execution
main() {
    echo "=========================================="
    echo "  ChromaDB Server Startup"
    echo "=========================================="
    echo
    
    # Check if ChromaDB is already running
    if check_chromadb_running; then
        print_warning "ChromaDB is already running (PID: $(cat "$CHROMA_PID_FILE"))"
        read -p "Do you want to restart it? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            print_status "Stopping existing ChromaDB server..."
            ./stop_chromadb.sh
        else
            print_status "ChromaDB server is already running"
            exit 0
        fi
    fi
    
    # Check if port is available
    if check_port; then
        print_warning "Port $CHROMA_PORT is already in use"
        read -p "Do you want to continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    # Setup ChromaDB directory
    setup_chromadb_dir
    
    # Check if server mode is requested
    if [ "$1" = "server" ] || [ "$1" = "--server" ]; then
        start_chromadb_server
    else
        start_chromadb_persistent
    fi
    
    # Set up signal handlers
    trap cleanup SIGINT SIGTERM
    
    if [ "$1" = "server" ] || [ "$1" = "--server" ]; then
        print_status "ChromaDB server is running. Press Ctrl+C to stop."
        # Keep the script running
        while true; do
            sleep 10
            if ! check_chromadb_running; then
                print_error "ChromaDB server stopped unexpectedly"
                exit 1
            fi
        done
    fi
}

# Run main function
main "$@" 