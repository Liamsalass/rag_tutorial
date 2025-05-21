import ollama
"""
This script uses the `ollama` library to generate a response from the "llama3.2" model
given a simple prompt ("Hello world!"). The generated response is extracted from the
output and printed to the console.

Modules:
    ollama: Used for interacting with language models.

Workflow:
    1. Sends a prompt to the "llama3.2" model using `ollama.generate`.
    2. Retrieves the generated response from the output dictionary.
    3. Prints the response to the standard output.
"""

output = ollama.generate(
    model="llama3",
    prompt="Hello world!"
)

response = output["response"]

print   (response)