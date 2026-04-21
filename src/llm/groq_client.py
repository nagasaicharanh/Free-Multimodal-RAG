"""
Groq API client for LLM-powered text synthesis and table summarization.
Uses Groq's free tier (6k tokens/min, unlimited requests).
"""
from typing import Optional
from groq import Groq
from src.config import GROQ_API_KEY, GROQ_MODEL_NAME, MAX_TABLE_SUMMARY_LENGTH


class GroqClient:
    """Interface to Groq API for text synthesis."""

    def __init__(self, api_key: str = GROQ_API_KEY, model: str = GROQ_MODEL_NAME):
        """
        Initialize Groq client.
        
        Args:
            api_key: Groq API key
            model: Model name (default: llama-3.3-70b-versatile)
        """
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable not set")
        
        self.client = Groq(api_key=api_key)
        self.model = model

    def summarize_table(self, table_markdown: str) -> str:
        """
        Generate a summary of a table.
        
        Args:
            table_markdown: Table in markdown format
            
        Returns:
            Natural language summary of the table
        """
        prompt = f"""
You are a data analyst. Summarize the following table in 1-2 sentences, highlighting key insights.

Table:
{table_markdown}

Summary:
"""
        return self._call_api(prompt, max_tokens=MAX_TABLE_SUMMARY_LENGTH)

    def synthesize_answer(self, context: str, question: str) -> str:
        """
        Generate an answer to a question based on context.
        
        Args:
            context: Retrieved context chunks
            question: User's question
            
        Returns:
            Generated answer
        """
        prompt = f"""
Based on the following context, answer the question concisely and accurately.

Context:
{context}

Question: {question}

Answer:
"""
        return self._call_api(prompt, max_tokens=500)

    def _call_api(self, prompt: str, max_tokens: int = 500, temperature: float = 0.7) -> str:
        """
        Make a call to Groq API.
        
        Args:
            prompt: The prompt to send
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature
            
        Returns:
            Generated text
        """
        try:
            message = self.client.chat.completions.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return message.choices[0].message.content
        except Exception as e:
            print(f"Error calling Groq API: {e}")
            return f"Error: {str(e)}"


if __name__ == "__main__":
    # Example usage (requires GROQ_API_KEY)
    try:
        client = GroqClient()
        
        # Test table summarization
        sample_table = """
| Product | Q1 | Q2 | Q3 | Q4 |
|---------|----|----|----|----|
| Widget A | 100 | 150 | 200 | 250 |
| Widget B | 80 | 100 | 120 | 140 |
| Widget C | 50 | 75 | 100 | 150 |
"""
        summary = client.summarize_table(sample_table)
        print(f"Table Summary: {summary}")
        
        # Test answer synthesis
        context = "The weather is sunny and warm. Temperature is 25°C."
        answer = client.synthesize_answer(context, "What is the current weather?")
        print(f"Answer: {answer}")
    except ValueError as e:
        print(f"Setup error: {e}")
