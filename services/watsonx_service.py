"""
Watsonx Service Module (Powered by Google Gemini)
Handles LLM integration for AI-enhanced responses
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))
from config import (
    GEMINI_API_KEY,
    GEMINI_MODEL_NAME,
    LLM_MAX_TOKENS,
    LLM_TEMPERATURE,
    LLM_TOP_P
)


class WatsonxService:
    """AI LLM Service (Powered by Google Gemini)"""
    
    def __init__(self):
        """Initialize service"""
        self.api_key = GEMINI_API_KEY
        self.model_name = GEMINI_MODEL_NAME
        self.client = None
        
    def initialize(self):
        """Initialize Gemini client"""
        if not self.api_key:
            raise ValueError(
                "Gemini API key not configured. "
                "Please set GEMINI_API_KEY in .env file"
            )
        
        try:
            from google import genai
            
            # Initialize client with API key
            self.client = genai.Client(api_key=self.api_key)
            
            # Quick validation - list models to check key works
            print(f"[SUCCESS] Watsonx service initialized (Gemini: {self.model_name})")
            return self
            
        except ImportError:
            raise ImportError(
                "Google GenAI library not installed. "
                "Run: pip install google-genai"
            )
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Watsonx service: {e}")
    
    def generate_response(self, prompt, max_tokens=None, temperature=None):
        """
        Generate response using Gemini
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens (overrides default)
            temperature: Sampling temperature (overrides default)
            
        Returns:
            Generated text response
        """
        if self.client is None:
            raise RuntimeError("Service not initialized. Call initialize() first.")
        
        try:
            from google.genai import types
            
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction="You are an expert agricultural advisor for Indian farmers. Provide practical, actionable advice based on the information provided.",
                    max_output_tokens=max_tokens or LLM_MAX_TOKENS,
                    temperature=temperature if temperature is not None else LLM_TEMPERATURE,
                    top_p=LLM_TOP_P,
                ),
            )
            
            return response.text
            
        except Exception as e:
            raise RuntimeError(f"Failed to generate response: {e}")
    
    def answer_query(self, query, context_qa_pairs):
        """
        Answer agricultural query using context from FAISS search
        
        Args:
            query: User query
            context_qa_pairs: List of relevant Q&A pairs from FAISS
            
        Returns:
            Generated answer
        """
        # Build context from Q&A pairs
        context_parts = []
        for i, qa in enumerate(context_qa_pairs, 1):
            q = qa.get('question', '')
            a = qa.get('answer', '')
            context_parts.append(f"{i}. Q: {q}\n   A: {a}")
        
        context = "\n\n".join(context_parts)
        
        # Create prompt
        prompt = f"""You are an expert agricultural advisor for Indian farmers. Based on the following relevant information from the Kisan Call Centre database, provide a helpful and accurate answer to the farmer's question.

Relevant Information from Database:
{context}

Farmer's Question: {query}

Instructions:
- Provide a clear, practical answer based on the information above
- If the information contains Hindi text, you may include it for authenticity
- Focus on actionable advice that farmers can implement
- Keep the answer concise but comprehensive (2-3 paragraphs maximum)
- If multiple solutions are mentioned, summarize the key recommendations
- Use simple language that farmers can understand

Expert Answer:"""
        
        response = self.generate_response(prompt)
        return response


if __name__ == "__main__":
    print("=" * 60)
    print("KrishiMind AI - Watsonx Service Test")
    print("=" * 60)
    
    try:
        service = WatsonxService()
        service.initialize()
        
        test_query = "How to control aphids in mustard?"
        mock_context = [
            {
                'question': 'How to control aphids in mustard crop?',
                'answer': 'Spray Imidacloprid 17.8% SL @ 0.3 ml/liter or Dimethoate 30% EC @ 2 ml/liter. Repeat after 15 days if needed.'
            }
        ]
        
        print(f"\nQuery: {test_query}")
        response = service.answer_query(test_query, mock_context)
        print(f"\nResponse:\n{response}")
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
