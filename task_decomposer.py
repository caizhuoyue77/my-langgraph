import json
from langchain_ollama import OllamaLLM

class Decomposer:
    CATEGORIES = [
        "Health", "Commerce", "Sports", 
        "Food", "Weather", "Education", 
        "Entertainment"
    ]
    
    def __init__(self, model_name: str, query: str):
        self.query = query
        self.llm = OllamaLLM(model=model_name)
        self.sub_tasks = []

    def run(self) -> list:
        """Generate subtasks based on the provided query."""
        prompt = self._create_prompt()
        
        self.sub_tasks = self.llm.invoke(prompt)
        
        # Convert the returned string to JSON object
        try:
            self.sub_tasks = json.loads(self.sub_tasks)
        except json.JSONDecodeError:
            print("JSON decode error: Returning an empty list.")
            self.sub_tasks = []

        return self.sub_tasks
        
    def _create_prompt(self) -> str:
        """Create the prompt for the LLM."""
        categories_str = self._parse_categories()
        return f"""
Please breakdown this task or query into subtasks. Each having its own category from the following categories.

# Task
{self.query}

# categories
{categories_str}

# instruction
You should breakdown the task into atomic subtasks (in English). Each subtask should follow the following format:

[{{"name":"","description":"","category":""}},..]
"""

    def _parse_categories(self) -> str:
        """Parse the categories into a string."""
        return "\n".join(self.CATEGORIES)
    
    
if __name__ == "__main__":
    decomposer = Decomposer("qwen2.5:7b", "可乐鸡翅怎么做，然后今天天气如何？")
    ans = decomposer.run()
    print(ans)
