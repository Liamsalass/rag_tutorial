import ollama

output = ollama.generate(
    model="llama3.2",
    prompt="Hello world!"
)

response = output["response"]

print   (response)