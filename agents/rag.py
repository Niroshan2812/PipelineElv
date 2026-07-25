import os
import chromadb
from agents.memory import MemoryAgent
from models import ChatResponce

class RAGAgent(MemoryAgent):
    """
    Inherits from MemoryAgent but replaces the volatile Python dictionary 
    with a persistent ChromaDB Vector Database.
    """
    def __init__(self):
        super().__init__()
        
        # 1. We create a persistent database on the hard drive inside our sandbox
        db_path = os.path.join(os.getcwd(), "sandbox", "vector_memory")
        self.chroma_client = chromadb.PersistentClient(path=db_path)
        
        # 2. We create a "Collection" (like a table in SQL). 
        # Chroma automatically uses the all-MiniLM-L6-v2 Transformer model to embed text!
        self.collection = self.chroma_client.get_or_create_collection(name="long_term_memory")

    async def process_message(self, message: str, session_id: str) -> ChatResponce:
        # We start by preparing the message for the LLM
        current_context = [{"role": "user", "content": message}]

        # 3. Retrieve (The 'R' in RAG)
        # We search the vector database for 2 previous memories that are mathematically 
        # similar to the user's current message.
        results = self.collection.query(
            query_texts=[message],
            n_results=2 # Only get the top 2 most relevant memories
        )

        retrieved_memory = ""
        # Check if we actually found any previous documents
        if results['documents'] and results['documents'][0]:
            print(f"\n[RAG] Found related memories in Vector DB!")
            # Combine the retrieved texts into one string
            retrieved_memory = " ".join(results['documents'][0])
            
            # 4. Augment (The 'A' in RAG)
            # We inject these old memories into the LLM as a System Prompt
            system_prompt = f"SYSTEM: Use this past context to help answer the user if relevant. Past Context: {retrieved_memory}"
            current_context.insert(0, {"role": "system", "content": system_prompt})
        else:
            print(f"\n[RAG] No relevant memories found in Vector DB.")

        # 5. Generate (The 'G' in RAG)
        # We call the Groq LLM with our Augmented prompt
        groq_reply = await self.llm_serivce.generate_response(current_context)
        final_reply = groq_reply.content if hasattr(groq_reply, "content") else str(groq_reply)

        # 6. Save the new memory to the Vector DB for future use!
        # We generate a unique ID for this interaction
        import uuid
        interaction_id = str(uuid.uuid4())
        
        # We save BOTH the user's question and the AI's answer into the vector database
        memory_to_save = f"User asked: '{message}'. AI replied: '{final_reply}'."
        
        self.collection.add(
            documents=[memory_to_save],
            metadatas=[{"session": session_id}],
            ids=[interaction_id]
        )

        return ChatResponce(
            model_used="rag",
            reply=final_reply,
            metadata={
                "retrieved_context": retrieved_memory if retrieved_memory else "None"
            }
        )
