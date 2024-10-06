def get_qwen25_7b():
    from langchain_ollama import OllamaLLM

    model = OllamaLLM(model="qwen2.5:7b")

    return model