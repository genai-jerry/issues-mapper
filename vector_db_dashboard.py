#!/usr/bin/env python3
"""
Vector Database Dashboard

A web-based dashboard to visualize and explore data in your vector database.
Supports ChromaDB, Pinecone, and in-memory storage backends.
"""

import os
import sys
import json
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import List, Dict, Any, Optional
from datetime import datetime
import numpy as np

# Add the mvp directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'mvp'))

from llm.llm_config import LLMConfig
from embeddings.embedding_manager import EmbeddingManager
from vector_storage.vector_models import VectorDocument

class VectorDBDashboard:
    """Dashboard for visualizing vector database data."""
    
    def __init__(self):
        self.embedding_manager = None
        self.setup_page()
        self.initialize_connection()
    
    def setup_page(self):
        """Setup Streamlit page configuration."""
        st.set_page_config(
            page_title="Vector Database Dashboard",
            page_icon="🗄️",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        st.title("🗄️ Vector Database Dashboard")
        st.markdown("---")
    
    def initialize_connection(self):
        """Initialize connection to vector database."""
        with st.sidebar:
            st.header("🔗 Database Connection")
            
            # Storage type selection
            storage_type = st.selectbox(
                "Storage Type",
                ["chroma", "pinecone", "inmemory"],
                help="Select your vector database backend"
            )
            
            # Configuration based on storage type
            if storage_type == "chroma":
                persist_directory = st.text_input(
                    "ChromaDB Directory",
                    value="chroma_db",
                    help="Directory where ChromaDB data is stored"
                )
                config = {"persist_directory": persist_directory}
                
            elif storage_type == "pinecone":
                api_key = st.text_input(
                    "Pinecone API Key",
                    type="password",
                    help="Your Pinecone API key"
                )
                environment = st.text_input(
                    "Pinecone Environment",
                    value="us-west1-gcp",
                    help="Your Pinecone environment"
                )
                config = {
                    "api_key": api_key,
                    "environment": environment
                }
                
            else:  # inmemory
                config = {}
            
            # LLM Configuration
            st.subheader("🤖 LLM Configuration")
            llm_provider = st.selectbox(
                "Embedding Provider",
                ["openai", "openrouter", "huggingface"],
                help="Select embedding provider"
            )
            
            api_key = st.text_input(
                f"{llm_provider.upper()} API Key",
                type="password",
                help=f"Your {llm_provider.upper()} API key"
            )
            
            model = st.text_input(
                "Embedding Model",
                value="text-embedding-ada-002",
                help="Embedding model to use"
            )
            
            # Connect button
            if st.button("🔌 Connect to Database", type="primary"):
                try:
                    self.connect_to_database(
                        storage_type, config, llm_provider, api_key, model
                    )
                    st.success("✅ Connected successfully!")
                except Exception as e:
                    st.error(f"❌ Connection failed: {str(e)}")
    
    def connect_to_database(self, storage_type: str, config: Dict[str, Any], 
                           provider: str, api_key: str, model: str):
        """Connect to the vector database."""
        # Setup LLM configuration
        llm_config = LLMConfig()
        llm_config.embedding_provider = provider
        llm_config.embedding_model = model
        llm_config.embedding_api_key = api_key
        llm_config.enable_cache = True
        
        # Initialize embedding manager
        self.embedding_manager = EmbeddingManager(
            config_instance=llm_config,
            vector_storage_type=storage_type,
            vector_storage_config=config
        )
        
        # Store connection info in session state
        st.session_state.connected = True
        st.session_state.storage_type = storage_type
        st.session_state.collections = self.embedding_manager.list_collections()
    
    def main_dashboard(self):
        """Main dashboard interface."""
        if not hasattr(st.session_state, 'connected') or not st.session_state.connected:
            st.info("👈 Please connect to your vector database using the sidebar.")
            return
        
        # Create tabs for different views
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 Overview", "🔍 Collections", "📝 Documents", "🔎 Search", "📈 Analytics"
        ])
        
        with tab1:
            self.show_overview()
        
        with tab2:
            self.show_collections()
        
        with tab3:
            self.show_documents()
        
        with tab4:
            self.show_search()
        
        with tab5:
            self.show_analytics()
    
    def show_overview(self):
        """Show database overview."""
        st.header("📊 Database Overview")
        
        # Get collections
        collections = self.embedding_manager.list_collections()
        
        # Create metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Collections", len(collections))
        
        total_docs = 0
        total_embeddings = 0
        
        for collection in collections:
            try:
                stats = self.embedding_manager.get_collection_stats(collection)
                total_docs += stats.get('document_count', 0)
                total_embeddings += stats.get('embedding_count', 0)
            except:
                pass
        
        with col2:
            st.metric("Total Documents", total_docs)
        
        with col3:
            st.metric("Total Embeddings", total_embeddings)
        
        with col4:
            st.metric("Storage Type", st.session_state.storage_type.upper())
        
        # Collections summary
        st.subheader("📁 Collections Summary")
        
        if collections:
            collection_data = []
            for collection in collections:
                try:
                    stats = self.embedding_manager.get_collection_stats(collection)
                    collection_data.append({
                        "Collection": collection,
                        "Documents": stats.get('document_count', 0),
                        "Embeddings": stats.get('embedding_count', 0),
                        "Dimension": stats.get('dimension', 'N/A'),
                        "Size (MB)": round(stats.get('size_mb', 0), 2)
                    })
                except Exception as e:
                    collection_data.append({
                        "Collection": collection,
                        "Documents": "Error",
                        "Embeddings": "Error",
                        "Dimension": "Error",
                        "Size (MB)": "Error"
                    })
            
            df = pd.DataFrame(collection_data)
            st.dataframe(df, use_container_width=True)
            
            # Create bar chart
            if len(collection_data) > 0:
                fig = px.bar(
                    df, 
                    x="Collection", 
                    y="Documents",
                    title="Documents per Collection",
                    color="Documents"
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No collections found in the database.")
    
    def show_collections(self):
        """Show collections management."""
        st.header("🔍 Collections Management")
        
        collections = self.embedding_manager.list_collections()
        
        # Create new collection
        with st.expander("➕ Create New Collection", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                new_collection_name = st.text_input("Collection Name")
            with col2:
                dimension = st.number_input("Dimension", min_value=1, value=1536)
            
            if st.button("Create Collection"):
                if new_collection_name:
                    try:
                        success = self.embedding_manager.create_collection(
                            new_collection_name, dimension
                        )
                        if success:
                            st.success(f"✅ Collection '{new_collection_name}' created!")
                            st.rerun()
                        else:
                            st.error("❌ Failed to create collection")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
                else:
                    st.warning("Please enter a collection name")
        
        # List existing collections
        st.subheader("📁 Existing Collections")
        
        if collections:
            for collection in collections:
                with st.expander(f"📁 {collection}", expanded=False):
                    try:
                        stats = self.embedding_manager.get_collection_stats(collection)
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Documents", stats.get('document_count', 0))
                        with col2:
                            st.metric("Dimension", stats.get('dimension', 'N/A'))
                        with col3:
                            st.metric("Size", f"{stats.get('size_mb', 0):.2f} MB")
                        
                        # Actions
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            if st.button(f"🗑️ Clear {collection}", key=f"clear_{collection}"):
                                try:
                                    self.embedding_manager.clear_collection(collection)
                                    st.success(f"✅ Collection '{collection}' cleared!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"❌ Error: {str(e)}")
                        
                        with col2:
                            if st.button(f"❌ Delete {collection}", key=f"delete_{collection}"):
                                try:
                                    self.embedding_manager.delete_collection(collection)
                                    st.success(f"✅ Collection '{collection}' deleted!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"❌ Error: {str(e)}")
                        
                        with col3:
                            if st.button(f"📊 View Documents {collection}", key=f"view_{collection}"):
                                st.session_state.selected_collection = collection
                                st.rerun()
                        
                    except Exception as e:
                        st.error(f"Error loading collection stats: {str(e)}")
        else:
            st.info("No collections found.")
    
    def show_documents(self):
        """Show documents in collections."""
        st.header("📝 Documents")
        
        collections = self.embedding_manager.list_collections()
        
        if not collections:
            st.info("No collections available.")
            return
        
        # Select collection
        selected_collection = st.selectbox(
            "Select Collection",
            collections,
            index=0
        )
        
        if selected_collection:
            try:
                # Get documents from collection
                # Note: This is a simplified approach - you might need to implement
                # a method to get all documents from a collection
                
                st.subheader(f"📄 Documents in '{selected_collection}'")
                
                # Search functionality to find documents
                search_query = st.text_input(
                    "Search documents",
                    placeholder="Enter search query..."
                )
                
                if search_query:
                    results = self.embedding_manager.search_similar(
                        collection=selected_collection,
                        query=search_query,
                        limit=20
                    )
                    
                    st.write(f"Found {len(results)} similar documents:")
                    
                    for i, (doc_id, similarity) in enumerate(results):
                        doc = self.embedding_manager.get_document(selected_collection, doc_id)
                        if doc:
                            with st.expander(f"📄 Document {i+1} (Similarity: {similarity:.4f})"):
                                st.write("**Content:**")
                                st.text_area(
                                    "Content",
                                    value=doc.content,
                                    height=100,
                                    key=f"content_{i}",
                                    disabled=True
                                )
                                
                                st.write("**Metadata:**")
                                st.json(doc.metadata)
                                
                                # Actions
                                col1, col2 = st.columns(2)
                                with col1:
                                    if st.button(f"✏️ Edit {i+1}", key=f"edit_{i}"):
                                        st.session_state.editing_doc = doc_id
                                        st.session_state.editing_collection = selected_collection
                                
                                with col2:
                                    if st.button(f"🗑️ Delete {i+1}", key=f"delete_{i}"):
                                        try:
                                            self.embedding_manager.delete_document(selected_collection, doc_id)
                                            st.success("✅ Document deleted!")
                                            st.rerun()
                                        except Exception as e:
                                            st.error(f"❌ Error: {str(e)}")
                
                else:
                    st.info("Enter a search query to view documents.")
                
            except Exception as e:
                st.error(f"Error loading documents: {str(e)}")
    
    def show_search(self):
        """Show search interface."""
        st.header("🔎 Semantic Search")
        
        collections = self.embedding_manager.list_collections()
        
        if not collections:
            st.info("No collections available for search.")
            return
        
        # Search interface
        col1, col2 = st.columns([3, 1])
        
        with col1:
            search_query = st.text_area(
                "Search Query",
                placeholder="Enter your search query here...",
                height=100
            )
        
        with col2:
            selected_collection = st.selectbox("Collection", collections)
            limit = st.number_input("Results Limit", min_value=1, max_value=100, value=10)
            
            # Metadata filter
            st.write("**Metadata Filter (Optional)**")
            filter_key = st.text_input("Filter Key")
            filter_value = st.text_input("Filter Value")
        
        if st.button("🔍 Search", type="primary") and search_query:
            try:
                # Prepare filter
                filter_metadata = None
                if filter_key and filter_value:
                    filter_metadata = {filter_key: filter_value}
                
                # Perform search
                results = self.embedding_manager.search_similar(
                    collection=selected_collection,
                    query=search_query,
                    limit=limit,
                    filter_metadata=filter_metadata
                )
                
                st.subheader(f"🔍 Search Results ({len(results)} found)")
                
                if results:
                    # Create results dataframe
                    results_data = []
                    for i, (doc_id, similarity) in enumerate(results):
                        doc = self.embedding_manager.get_document(selected_collection, doc_id)
                        if doc:
                            results_data.append({
                                "Rank": i + 1,
                                "Similarity": round(similarity, 4),
                                "Content": doc.content[:100] + "..." if len(doc.content) > 100 else doc.content,
                                "Document ID": doc_id,
                                "Metadata": str(doc.metadata)[:50] + "..." if len(str(doc.metadata)) > 50 else str(doc.metadata)
                            })
                    
                    df = pd.DataFrame(results_data)
                    st.dataframe(df, use_container_width=True)
                    
                    # Similarity distribution chart
                    similarities = [sim for _, sim in results]
                    fig = px.histogram(
                        x=similarities,
                        title="Similarity Score Distribution",
                        labels={"x": "Similarity Score", "y": "Count"}
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Detailed results
                    st.subheader("📄 Detailed Results")
                    for i, (doc_id, similarity) in enumerate(results):
                        doc = self.embedding_manager.get_document(selected_collection, doc_id)
                        if doc:
                            with st.expander(f"#{i+1} - Similarity: {similarity:.4f}"):
                                st.write("**Content:**")
                                st.text_area(
                                    "Content",
                                    value=doc.content,
                                    height=150,
                                    key=f"search_content_{i}",
                                    disabled=True
                                )
                                
                                st.write("**Metadata:**")
                                st.json(doc.metadata)
                                
                                st.write("**Document ID:**")
                                st.code(doc_id)
                
                else:
                    st.info("No results found.")
                    
            except Exception as e:
                st.error(f"Search error: {str(e)}")
    
    def show_analytics(self):
        """Show analytics and insights."""
        st.header("📈 Analytics & Insights")
        
        collections = self.embedding_manager.list_collections()
        
        if not collections:
            st.info("No collections available for analytics.")
            return
        
        # Collection analytics
        st.subheader("📊 Collection Analytics")
        
        collection_data = []
        for collection in collections:
            try:
                stats = self.embedding_manager.get_collection_stats(collection)
                collection_data.append({
                    "Collection": collection,
                    "Documents": stats.get('document_count', 0),
                    "Size_MB": stats.get('size_mb', 0),
                    "Dimension": stats.get('dimension', 0)
                })
            except:
                pass
        
        if collection_data:
            df = pd.DataFrame(collection_data)
            
            # Charts
            col1, col2 = st.columns(2)
            
            with col1:
                fig1 = px.pie(
                    df, 
                    values="Documents", 
                    names="Collection",
                    title="Document Distribution"
                )
                st.plotly_chart(fig1, use_container_width=True)
            
            with col2:
                fig2 = px.bar(
                    df,
                    x="Collection",
                    y="Size_MB",
                    title="Collection Size (MB)"
                )
                st.plotly_chart(fig2, use_container_width=True)
            
            # Summary statistics
            st.subheader("📋 Summary Statistics")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Collections", len(collection_data))
            
            with col2:
                total_docs = df["Documents"].sum()
                st.metric("Total Documents", total_docs)
            
            with col3:
                total_size = df["Size_MB"].sum()
                st.metric("Total Size", f"{total_size:.2f} MB")
        
        # Embedding dimension analysis
        st.subheader("🔢 Embedding Dimension Analysis")
        
        dimension_counts = {}
        for collection in collections:
            try:
                stats = self.embedding_manager.get_collection_stats(collection)
                dimension = stats.get('dimension', 0)
                if dimension > 0:
                    dimension_counts[dimension] = dimension_counts.get(dimension, 0) + 1
            except:
                pass
        
        if dimension_counts:
            fig = px.bar(
                x=list(dimension_counts.keys()),
                y=list(dimension_counts.values()),
                title="Embedding Dimensions Distribution",
                labels={"x": "Dimension", "y": "Collections"}
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No dimension data available.")

def main():
    """Main application entry point."""
    dashboard = VectorDBDashboard()
    dashboard.main_dashboard()

if __name__ == "__main__":
    main() 