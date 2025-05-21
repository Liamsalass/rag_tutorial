import ollama
from colorama import Fore, Style, init
init(autoreset=True)

# This code is used to create a vector database using ChromaDB
# It uses the Ollama library to generate embeddings for the conversations
import chromadb
from chromadb.errors import NotFoundError

client = chromadb.Client()


# example message history
message_history = [
    {
        'id': 1,
        'prompt' : 'What is the user name?',
        'response' : 'The user name is Liam Salass.'
    },
    {
        'id': 2,
        'prompt' : 'What is the user age?',
        'response' : 'The user age is 25.'
    },
    {
        'id': 3,
        'prompt' : 'What is the user location?',
        'response' : 'The user location is Waterloo.'
    },
    {
        'id': 4,
        'prompt' : 'What is the user occupation?',
        'response' : 'The user occupation is Master student.'
    }
]


#====== Stays the same ======
convo = []

def stream_response(prompt):
    convo.append(
            {
                "role": "user",
                "content": prompt
            }
        )
    response = ''
    steam = ollama.chat(
        model="llama3",
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






# This function creates a vector database using the ChromaDB client
# It takes a list of conversations as input
# It serializes each conversation into a string format
# It then generates an embedding for each serialized conversation using the ollama embeddings model
# It adds the embeddings to the vector database along with the serialized conversation
# The vector database is named 'conversations'
# If the vector database already exists, it is deleted before creating a new one
def create_vector_db(conversations):
    vector_db_name = 'conversations'
    try:
        client.delete_collection(name=vector_db_name)
        print (f"Deleted existing collection: {vector_db_name}")
    except NotFoundError:
        pass

    vector_db = client.create_collection(name=vector_db_name)

    for c in conversations:
        serialized_convo = f"prompt: {c['prompt']} response: {c['response']}"
        response = ollama.embeddings(model='nomic-embed-text', prompt=serialized_convo)
        embedding = response['embedding']

        vector_db.add(
            ids=[str(c['id'])],
            embeddings=[embedding],
            documents=[serialized_convo]
        )


# This function retrieves the best embedding from the vector database
# It takes a prompt as input
# It generates an embedding for the prompt using the ollama embeddings model
# It queries the vector database for the best matching embedding
# It returns the best matching embedding

def retrieve_embeddings(prompt):
    response = ollama.embeddings(model='nomic-embed-text', prompt=prompt)
    prompt_embedding = response['embedding']

    vector_db = client.get_collection(name='conversations')

    results = vector_db.query(
        query_embeddings=[prompt_embedding],
        n_results=1
    )

    best_embedding = results['documents'][0][0]

    return best_embedding






create_vector_db(message_history)

while True:
    prompt = input(Fore.YELLOW + 'USER: \n' + Style.RESET_ALL)
    if prompt.lower() == 'exit':
        break



    

    # Now we will retrieve the best embedding from the vector database
    # and append it to the prompt
    context = retrieve_embeddings(prompt=prompt)
    prompt = f"USER PROMPT: {prompt} CONTEXT FROM EMBEDDINGS: {context}"



    stream_response(prompt=prompt)