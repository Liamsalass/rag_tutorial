import ollama
from colorama import Fore, Style, init
init(autoreset=True)

convo = []


while True:
    # Prompt the user for input
    prompt = input('USER: \n')
    convo.append(
        {
            "role": "user",
            "content": prompt
        }
    )
    
    output = ollama.chat(
        model="llama3",
        messages=convo
    )

    response = output["message"]['content']

    print ("\n" + Fore.GREEN + "ASSISTANT: \n" + Style.RESET_ALL + response + "\n")

    convo.append(
        {
            "role": "assistant",
            "content": response
        }
    )