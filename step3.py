import ollama
from colorama import Fore, Style, init
init(autoreset=True)

convo = []

# This function is used to stream the response from the model
# It takes a prompt as input and appends it to the conversation history
# It then calls the ollama.chat function with the conversation history
# and streams the response back to the user
# The response is printed in real-time as it is received
# The function also appends the assistant's response to the conversation history

def stream_response(prompt):
    convo.append(
            {
                "role": "user",
                "content": prompt
            }
        )
    response = ''
    steam = ollama.chat(
        model="llama3.2",
        messages=convo,
        stream=True
    )
    print ("\n" + Fore.GREEN + "ASSISTANT: \n" + Style.RESET_ALL, end='')
    for chunk in steam:
        content = chunk['message']['content']
        response += content
        print (content, end='', flush=True)
    print ("\n")
    convo.append(
        {
            "role": "assistant",
            "content": response
        }
    )

# Main loop to get user input and call the stream_response function
# The loop continues until the user types 'exit'
while True:
    prompt = input(Fore.YELLOW + 'USER: \n' + Style.RESET_ALL)
    if prompt.lower() == 'exit':
        break
    stream_response(prompt=prompt)