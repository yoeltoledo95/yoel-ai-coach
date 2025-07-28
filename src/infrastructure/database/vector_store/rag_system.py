"""
RAG (Retrieval Augmented Generation) System for Mentor Knowledge
Handles chunking, embedding, and retrieving mentor knowledge from vector database
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional
import chromadb
from sentence_transformers import SentenceTransformer
import numpy as np
from langchain.schema import Document
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

logger = logging.getLogger(__name__)

# Convert mentor knowledge to LangChain Documents with metadata
def mentor_knowledge_to_documents(mentor_dict):
    docs = []
    for mentor, data in mentor_dict.items():
        # Key principles
        for principle in data.get("key_principles", []):
            docs.append(Document(
                page_content=principle,
                metadata={"mentor": mentor, "type": "principle"}
            ))
        # Typical session flow
        for flow in data.get("typical_session_flow", []):
            docs.append(Document(
                page_content=flow,
                metadata={"mentor": mentor, "type": "session_flow"}
            ))
        # Exercise library
        for ex in data.get("exercise_library", []):
            docs.append(Document(
                page_content=f"{ex['name']}: {ex['description']} Benefits: {', '.join(ex['benefits'])} Progressions: {', '.join(ex['progressions_regressions']['progressions'])} Regressions: {', '.join(ex['progressions_regressions']['regressions'])} Key cues: {', '.join(ex['key_cues'])} Purpose: {ex['purpose_in_system']}",
                metadata={"mentor": mentor, "type": "exercise", "name": ex['name']}
            ))
    return docs

# Initialize LangChain RAG system
def initialize_langchain_rag():
    from coach_core.mentor_brain import MENTOR_KNOWLEDGE  # Import here to avoid circular import
    docs = mentor_knowledge_to_documents(MENTOR_KNOWLEDGE)
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectorstore = Chroma.from_documents(docs, embeddings, persist_directory="./chroma_db")
    return vectorstore

# Provide a retriever interface
def get_mentor_retriever():
    vectorstore = initialize_langchain_rag()
    return vectorstore.as_retriever(search_kwargs={"k": 5})

# Example query interface
def search_mentor_knowledge(query):
    retriever = get_mentor_retriever()
    relevant_docs = retriever.get_relevant_documents(query)
    return [doc.page_content for doc in relevant_docs]

class MentorRAGSystem:
    """RAG system for retrieving mentor knowledge from vector database"""
    
    def __init__(self):
        self.chroma_client = None
        self.embedding_model = None
        self.collection = None
        self.initialize_system()
    
    def initialize_system(self):
        """Initialize the RAG system with ChromaDB and embedding model"""
        try:
            # Initialize ChromaDB
            self.chroma_client = chromadb.PersistentClient(path="./chroma_db")
            
            # Initialize embedding model
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Get or create collection
            self.collection = self.chroma_client.get_or_create_collection(
                name="mentor_knowledge",
                metadata={"hnsw:space": "cosine"}
            )
            
            logger.info("✅ RAG system initialized successfully")
            
            # Check if knowledge base needs to be indexed
            if self.collection.count() == 0:
                logger.info("📚 Indexing mentor knowledge base...")
                self.index_knowledge_base()
            
        except Exception as e:
            logger.error(f"❌ Error initializing RAG system: {e}")
            raise
    
    def chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """Split text into overlapping chunks"""
        chunks = []
        words = text.split()
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk = ' '.join(words[i:i + chunk_size])
            if chunk.strip():
                chunks.append(chunk.strip())
        
        return chunks
    
    def add_document(self, content: str, metadata: Dict[str, Any]) -> bool:
        """Add a document to the vector store"""
        try:
            # Generate a unique ID
            import uuid
            doc_id = str(uuid.uuid4())
            
            # Add to collection
            self.collection.add(
                documents=[content],
                metadatas=[metadata],
                ids=[doc_id]
            )
            
            return True
        except Exception as e:
            logger.error(f"Error adding document: {e}")
            return False
    
    def process_mentor_data(self, mentor_id: str, mentor_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process mentor data from MENTOR_KNOWLEDGE dictionary"""
        documents = []
        
        # Process core philosophy
        if 'core_philosophy' in mentor_data:
            chunks = self.chunk_text(mentor_data['core_philosophy'])
            for i, chunk in enumerate(chunks):
                documents.append({
                    'id': f"{mentor_id}_philosophy_{i}",
                    'text': chunk,
                    'mentor': mentor_data.get('name', mentor_id),
                    'source': 'mentor_brain.py',
                    'type': 'philosophy',
                    'chunk_index': i
                })
        
        # Process key principles
        for i, principle in enumerate(mentor_data.get('key_principles', [])):
            documents.append({
                'id': f"{mentor_id}_principle_{i}",
                'text': principle,
                'mentor': mentor_data.get('name', mentor_id),
                'source': 'mentor_brain.py',
                'type': 'principle',
                'chunk_index': i
            })
        
        # Process training methods
        for i, method in enumerate(mentor_data.get('training_methods', [])):
            documents.append({
                'id': f"{mentor_id}_method_{i}",
                'text': method,
                'mentor': mentor_data.get('name', mentor_id),
                'source': 'mentor_brain.py',
                'type': 'training_method',
                'chunk_index': i
            })
        
        # Process exercise library
        for i, exercise in enumerate(mentor_data.get('exercise_library', [])):
            exercise_text = f"{exercise['name']}: {exercise['description']}"
            if 'benefits' in exercise:
                exercise_text += f" Benefits: {', '.join(exercise['benefits'])}"
            if 'key_cues' in exercise:
                exercise_text += f" Cues: {', '.join(exercise['key_cues'])}"
            
            documents.append({
                'id': f"{mentor_id}_exercise_{i}",
                'text': exercise_text,
                'mentor': mentor_data.get('name', mentor_id),
                'source': 'mentor_brain.py',
                'type': 'exercise',
                'exercise_name': exercise['name'],
                'chunk_index': i
            })
        
        return documents
    
    def index_knowledge_base(self):
        """Index mentor knowledge base for vector search"""
        try:
            # Import mentor knowledge directly
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'data', 'mentors'))
            
            try:
                from mentor_brain import MENTOR_KNOWLEDGE
            except ImportError:
                # Fallback to static mentor knowledge
                MENTOR_KNOWLEDGE = {
                    "dylan_werner": {
                        "name": "Dylan Werner",
                        "focus": "Yoga and Movement Control",
                        "core_philosophy": "Control your body, control your mind. Focus on precise movement control and isometric strength.",
                        "key_principles": ["Movement Control", "Isometric Strength", "Mind-Body Integration"],
                        "training_methods": ["Isometric Training", "Movement Flow", "Strength Through Control"],
                        "motivational_style": "Calm, focused, emphasizes precision and control"
                    },
                    "ido_portal": {
                        "name": "Ido Portal",
                        "focus": "Movement complexity, natural patterns, holistic physical development",
                        "core_philosophy": "Movement Culture: An integrated approach beyond traditional fitness, encompassing health, aesthetics, performance, and art.",
                        "key_principles": ["Movement Culture", "The 'Mover' Concept", "Generalist vs. Specialist", "Holistic Approach"],
                        "training_methods": ["Movement Flow", "Skill Work", "Integration & Strength"],
                        "motivational_style": "Philosophical, challenging, emphasizes curiosity and intrinsic motivation"
                    },
                    "tom_merrick": {
                        "name": "Tom Merrick",
                        "focus": "Calisthenics and Flexibility",
                        "core_philosophy": "Build strength and flexibility through bodyweight training and systematic progression.",
                        "key_principles": ["Progressive Overload", "Proper Form", "Consistency"],
                        "training_methods": ["Calisthenics", "Flexibility Training", "Skill Work"],
                        "motivational_style": "Educational, systematic, emphasizes proper form and progression"
                    }
                }
            
            # Index each mentor's knowledge
            for mentor_id, mentor_data in MENTOR_KNOWLEDGE.items():
                # Create documents for different aspects of mentor knowledge
                documents = []
                
                # Core philosophy
                documents.append({
                    "content": f"{mentor_data['name']}: {mentor_data['core_philosophy']}",
                    "metadata": {
                        "mentor": mentor_id,
                        "type": "philosophy",
                        "name": mentor_data['name']
                    }
                })
                
                # Key principles
                for principle in mentor_data.get('key_principles', []):
                    documents.append({
                        "content": f"{mentor_data['name']} - {principle}",
                        "metadata": {
                            "mentor": mentor_id,
                            "type": "principle",
                            "name": mentor_data['name']
                        }
                    })
                
                # Training methods
                for method in mentor_data.get('training_methods', []):
                    documents.append({
                        "content": f"{mentor_data['name']} training method: {method}",
                        "metadata": {
                            "mentor": mentor_id,
                            "type": "method",
                            "name": mentor_data['name']
                        }
                    })
                
                # Add documents to vector store
                for doc in documents:
                    self.add_document(doc["content"], doc["metadata"])
            
            logger.info(f"✅ Indexed knowledge for {len(MENTOR_KNOWLEDGE)} mentors")
            
        except Exception as e:
            logger.error(f"❌ Error indexing knowledge base: {e}")
            raise
    
    def search_mentor_knowledge(self, query: str, mentor_names: Optional[List[str]] = None, 
                               top_k: int = 5) -> List[Dict[str, Any]]:
        """Search mentor knowledge for relevant information"""
        try:
            # Prepare query
            query_embedding = self.embedding_model.encode([query])
            
            # Build where clause for specific mentors if provided
            where_clause = None
            if mentor_names:
                where_clause = {"mentor": {"$in": mentor_names}}
            
            # Search the collection
            results = self.collection.query(
                query_embeddings=query_embedding.tolist(),
                n_results=top_k,
                where=where_clause
            )
            
            # Format results
            formatted_results = []
            for i in range(len(results['documents'][0])):
                formatted_results.append({
                    'text': results['documents'][0][i],
                    'mentor': results['metadatas'][0][i]['mentor'],
                    'source': results['metadatas'][0][i]['source'],
                    'type': results['metadatas'][0][i]['type'],
                    'distance': results['distances'][0][i] if 'distances' in results else None
                })
            
            logger.info(f"🔍 Found {len(formatted_results)} relevant chunks for query: '{query}'")
            return formatted_results
            
        except Exception as e:
            logger.error(f"❌ Error searching mentor knowledge: {e}")
            return []
    
    def get_mentor_context(self, query: str, mentor_names: Optional[List[str]] = None) -> str:
        """Get formatted mentor context for AI prompts"""
        try:
            results = self.search_mentor_knowledge(query, mentor_names, top_k=3)
            
            if not results:
                return "No relevant mentor knowledge found."
            
            # Format context
            context_parts = []
            for result in results:
                mentor = result['mentor']
                text = result['text']
                context_parts.append(f"From {mentor}:\n{text}\n")
            
            return "\n".join(context_parts)
            
        except Exception as e:
            logger.error(f"❌ Error getting mentor context: {e}")
            return "Error retrieving mentor knowledge."
    
    def get_all_mentors_context(self, query: str) -> str:
        """Get context from all mentors for a query"""
        return self.get_mentor_context(query)
    
    def get_specific_mentor_context(self, query: str, mentor_name: str) -> str:
        """Get context from a specific mentor"""
        return self.get_mentor_context(query, [mentor_name])
    
    def get_weekly_planning_context(self) -> str:
        """Get comprehensive context for weekly planning"""
        try:
            # Search for planning-related knowledge
            planning_queries = [
                "training progression",
                "weekly planning",
                "training methods",
                "movement principles",
                "strength development",
                "recovery planning"
            ]
            
            all_contexts = []
            for query in planning_queries:
                results = self.search_mentor_knowledge(query, top_k=2)
                for result in results:
                    all_contexts.append(f"From {result['mentor']}:\n{result['text']}")
            
            return "\n\n".join(all_contexts)
            
        except Exception as e:
            logger.error(f"❌ Error getting weekly planning context: {e}")
            return "Error retrieving planning knowledge."
    
    def get_mentor_statistics(self) -> Dict[str, Any]:
        """Get statistics about the knowledge base"""
        try:
            total_count = self.collection.count()
            
            # Get unique mentors
            results = self.collection.get()
            mentors = set(metadata['mentor'] for metadata in results['metadatas'])
            
            return {
                'total_chunks': total_count,
                'unique_mentors': len(mentors),
                'mentors': list(mentors)
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting mentor statistics: {e}")
            return {'error': str(e)}

# Initialize global RAG system
rag_system = MentorRAGSystem() 