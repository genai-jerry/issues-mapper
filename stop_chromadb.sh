#!/bin/bash

# ChromaDB Server Stop Script
# This script stops the ChromaDB server

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

# Function to stop ChromaDB gracefully
stop_chromadb_graceful() {
    local PID=$1
    print_status "Stopping ChromaDB gracefully (PID: $PID)..."
    
    # Send SIGTERM signal
    kill -TERM "$PID"
    
    # Wait for graceful shutdown (up to 30 seconds)
    local count=0
    while [ $count -lt 30 ]; do
        if ! ps -p "$PID" > /dev/null 2>&1; then
            print_success "ChromaDB stopped gracefully"
            return 0
        fi
        sleep 1
        count=$((count + 1))
    done
    
    return 1  # Graceful shutdown failed
}

# Function to force stop ChromaDB
stop_chromadb_force() {
    local PID=$1
    print_warning "Force stopping ChromaDB (PID: $PID)..."
    
    # Send SIGKILL signal
    kill -KILL "$PID"
    
    # Wait a moment
    sleep 2
    
    if ! ps -p "$PID" > /dev/null 2>&1; then
        print_success "ChromaDB force stopped"
        return 0
    else
        print_error "Failed to force stop ChromaDB"
        return 1
    fi
}

# Function to cleanup
cleanup() {
    if [ -f "$CHROMA_PID_FILE" ]; then
        rm -f "$CHROMA_PID_FILE"
    fi
}

# Main execution
main() {
    echo "=========================================="
    echo "  ChromaDB Server Stop"
    echo "=========================================="
    echo
    
    # Check if ChromaDB is running
    if ! check_chromadb_running; then
        print_warning "ChromaDB is not running"
        cleanup
        exit 0
    fi
    
    # Get PID
    PID=$(cat "$CHROMA_PID_FILE")
    print_status "Found ChromaDB process (PID: $PID)"
    
    # Try graceful shutdown first
    if stop_chromadb_graceful "$PID"; then
        cleanup
        print_success "ChromaDB server stopped successfully"
        exit 0
    fi
    
    # If graceful shutdown failed, try force stop
    print_warning "Graceful shutdown failed, trying force stop..."
    if stop_chromadb_force "$PID"; then
        cleanup
        print_success "ChromaDB server force stopped"
        exit 0
    else
        print_error "Failed to stop ChromaDB server"
        print_status "You may need to manually kill the process: kill -9 $PID"
        exit 1
    fi
}

# Run main function
main "$@" 