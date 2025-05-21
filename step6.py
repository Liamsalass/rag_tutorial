import ollama
from colorama import Fore, Style, init
init(autoreset=True)
import chromadb
from chromadb.errors import NotFoundError
import psycopg
from psycopg.rows import dict_row


DB_PARAMS = {
    'dbname' : 'rag_agent',
    'user' : 'example_user',
    'password' : '123456',
    'host' : 'localhost',
    'port' : '5432'
}

def connect_db():
    conn = psycopg.connect(**DB_PARAMS)
    return conn

def fetch_conversations():
    conn = connect_db()
    with conn.cursor(row_factory=dict_row) as cursor:
        cursor.execute("SELECT * FROM conversations")
        conversations = cursor.fetchall()
    conn.close()
    return conversations




## This function is used to store the conversation in the database
## It takes the prompt and response as input and inserts them into the conversations table
## The function uses the psycopg library to connect to the database and execute the insert query

def store_conversation(prompt, response):
    conn = connect_db()
    with conn.cursor() as cursor:
        cursor.execute(
            "INSERT INTO conversations (timestamp, prompt, response) VALUES (CURRENT_TIMESTAMP, %s, %s)",
            (prompt, response)
        )
        conn.commit()
    conn.close()


client = chromadb.Client()

convo = []


# we make a change here
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
    # we make a change here by adding the following
    # here we store the conversation in the database
    store_conversation(prompt=prompt, response=response)
    convo.append(
        {
            "role": "assistant",
            "content": response
        }
    )










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




conversations = fetch_conversations()
create_vector_db(conversations=conversations)
print (fetch_conversations())

while True:
    prompt = input(Fore.YELLOW + 'USER: \n' + Style.RESET_ALL)
    if prompt.lower() == 'exit':
        break


    context = retrieve_embeddings(prompt=prompt)
    prompt = f"USER PROMPT: {prompt} CONTEXT FROM EMBEDDINGS: {context}"


    stream_response(prompt=prompt)