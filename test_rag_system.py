#!/usr/bin/env python3
"""
Test script for RAG system functionality
"""

import os
from dotenv import load_dotenv
load_dotenv()

from coach_core.rag_system import rag_system
from coach_core.mentor_brain import get_mentor_context, search_mentor_knowledge, get_mentor_statistics

def test_rag_system():
    """Test the RAG system functionality"""
    print("🧪 Testing RAG System")
    print("=" * 50)
    
    # Test mentor statistics
    print("📊 Mentor Knowledge Base Statistics:")
    stats = get_mentor_statistics()
    if 'error' not in stats:
        print(f"  • Total chunks: {stats.get('total_chunks', 0)}")
        print(f"  • Unique mentors: {stats.get('unique_mentors', 0)}")
        print(f"  • Mentors: {', '.join(stats.get('mentors', []))}")
    else:
        print(f"  ❌ Error: {stats['error']}")
    
    # Test search functionality
    test_queries = [
        "How should I train for handstands?",
        "What's the best way to improve mobility?",
        "I have shoulder pain, what should I do?",
        "How do I build movement control?",
        "What's the philosophy behind movement training?"
    ]
    
    print("\n🔍 Testing Knowledge Search:")
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Query: {query}")
        
        # Test search
        results = search_mentor_knowledge(query, top_k=2)
        if results:
            print(f"   Found {len(results)} relevant chunks:")
            for j, result in enumerate(results, 1):
                print(f"   {j}. From {result['mentor']}: {result['text'][:100]}...")
        else:
            print("   No relevant results found")
    
    # Test mentor context retrieval
    print("\n📚 Testing Mentor Context Retrieval:")
    test_contexts = [
        ("yoga and control", ["dylan_werner"]),
        ("movement complexity", ["ido_portal"]),
        ("joint safety", ["squatu", "kneesovertoesguy"]),
        ("natural movement", ["patrick_beach", "ido_portal"])
    ]
    
    for i, (query, mentors) in enumerate(test_contexts, 1):
        print(f"\n{i}. Query: '{query}' (Mentors: {mentors})")
        context = get_mentor_context(query, mentors)
        print(f"   Context length: {len(context)} characters")
        print(f"   Preview: {context[:200]}...")
    
    # Test weekly planning context
    print("\n📅 Testing Weekly Planning Context:")
    planning_context = get_mentor_context("weekly training planning")
    print(f"   Planning context length: {len(planning_context)} characters")
    print(f"   Preview: {planning_context[:300]}...")
    
    print("\n" + "=" * 50)
    print("✅ RAG system test completed")

if __name__ == "__main__":
    test_rag_system() 