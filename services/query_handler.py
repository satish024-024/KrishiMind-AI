"""
Query Handler Module
Unified pipeline for processing user queries
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))
from config import TOP_K_RESULTS


class QueryHandler:
    """Unified query processing pipeline"""
    
    def __init__(self, faiss_searcher, watsonx_service=None):
        """
        Initialize query handler
        
        Args:
            faiss_searcher: FAISSSearcher instance
            watsonx_service: WatsonxService instance (optional, for online mode)
        """
        self.faiss_searcher = faiss_searcher
        self.watsonx_service = watsonx_service
    
    def process_query(self, query, top_k=TOP_K_RESULTS, online_mode=True, location_context=None, language='en'):
        """
        Process user query and return both offline and online answers
        
        Args:
            query: User query string
            top_k: Number of similar results to retrieve
            online_mode: Whether to generate LLM response
            location_context: Optional string with date/time/location/season info
            language: Target language for response (default: 'en')
            
        Returns:
            Dictionary with offline_answer and online_answer
        """
        # Search FAISS for similar Q&A pairs
        results = self.faiss_searcher.search(query, top_k=top_k)
        
        # Format offline answer
        offline_answer = self._format_offline_answer(results)
        
        # Generate online answer if enabled
        online_answer = None
        if online_mode and self.watsonx_service:
            try:
                # Extract Q&A pairs for context
                context_qa_pairs = [r['metadata'] for r in results]
                
                # Generate LLM response with location context
                online_answer = self.watsonx_service.answer_query(
                    query, context_qa_pairs, location_context=location_context, language=language
                )
            except Exception as e:
                online_answer = f"Error generating online response: {e}"
        
        return {
            'query': query,
            'offline_answer': offline_answer,
            'online_answer': online_answer,
            'retrieved_results': results
        }
    
    def _format_offline_answer(self, results):
        """
        Format offline answer from FAISS results
        
        Args:
            results: List of FAISS search results
            
        Returns:
            Formatted answer string
        """
        if not results:
            return "No relevant information found in the database for your query. Please try rephrasing or ask a different question."
        
        # Extract unique answers with confidence
        answers = []
        seen_answers = set()
        
        for result in results:
            answer = result['metadata']['answer']
            confidence = result.get('confidence', 0)
            
            # Avoid duplicates
            if answer not in seen_answers:
                # Confidence badge
                if confidence >= 0.7:
                    badge = "🟢 High Match"
                elif confidence >= 0.4:
                    badge = "🟡 Partial Match"
                else:
                    badge = "🟠 Low Match"
                answers.append((answer, badge, confidence))
                seen_answers.add(answer)
        
        # Format as numbered list with confidence
        formatted_answers = []
        for i, (answer, badge, conf) in enumerate(answers, 1):
            formatted_answers.append(f"{i}. {answer}")
        
        return "\n\n".join(formatted_answers)
    
    def get_query_metadata(self, results):
        """
        Extract metadata from search results
        
        Args:
            results: List of FAISS search results
            
        Returns:
            Dictionary with aggregated metadata
        """
        crops = set()
        states = set()
        query_types = set()
        
        if not results:
            return {
                'crops': [],
                'states': [],
                'query_types': []
            }
        
        for result in results:
            # Handle both direct and nested metadata
            metadata = result.get('metadata', {})
            inner_meta = metadata.get('metadata', {}) if isinstance(metadata.get('metadata'), dict) else {}
            
            # Check both locations for crop, state, etc.
            crop = inner_meta.get('crop') or metadata.get('crop')
            state = inner_meta.get('state') or metadata.get('state')
            qtype = inner_meta.get('query_type') or metadata.get('query_type')
            
            if crop: crops.add(crop)
            if state: states.add(state)
            if qtype: query_types.add(qtype)
        
        return {
            'crops': list(crops),
            'states': list(states),
            'query_types': list(query_types)
        }


if __name__ == "__main__":
    print("=" * 60)
    print("Kisan Call Centre - Query Handler Test")
    print("=" * 60)
    
    try:
        from faiss_store import FAISSSearcher
        from watsonx_service import WatsonxService
        
        # Load FAISS searcher
        print("[INFO] Loading FAISS searcher...")
        searcher = FAISSSearcher().load()
        print("[SUCCESS] FAISS searcher loaded")
        
        # Initialize query handler (offline mode only for testing)
        handler = QueryHandler(searcher)
        
        # Test query
        test_query = "How to control aphids in mustard?"
        print(f"\n[INFO] Test Query: {test_query}")
        
        # Process query (offline mode)
        print("\n[INFO] Processing query (offline mode)...")
        result = handler.process_query(test_query, online_mode=False)
        
        print("\n[INFO] Offline Answer:")
        print(result['offline_answer'])
        
        print(f"\n[INFO] Retrieved {len(result['retrieved_results'])} results")
        
        # Show metadata
        metadata = handler.get_query_metadata(result['retrieved_results'])
        print(f"\n[INFO] Metadata:")
        print(f"  Crops: {metadata.get('crops', [])}")
        print(f"  States: {metadata.get('states', [])}")
        print(f"  Query Types: {metadata.get('query_types', [])}")
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
