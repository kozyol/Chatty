from huggingface_hub import InferenceClient

# Zephyr chat client
def zephyr_chat(messages, kwargs):
    CLIENT: InferenceClient = InferenceClient(
        "mistralai/Mistral-7B-Instruct-v0.2"
    )

    # Initialize Zephyr response
    response: str = ""

    # Send request to client
    for chunk in CLIENT.text_generation(
        messages,
        **kwargs
    ):
        # Add chunks to response 
        response += chunk.token.text
        yield response