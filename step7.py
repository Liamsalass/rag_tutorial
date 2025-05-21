import ollama
from colorama import Fore, Style, init
init(autoreset=True)
import chromadb
from chromadb.errors import NotFoundError
import psycopg
from psycopg.rows import dict_row

# new lib
import ast
from tqdm import tqdm

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








# System prompt to initiate the conversation
system_prompt = (
    "You are an AI asistant that has memory of conversations with the user. "
    "On every prompt from the user, the system has checked for relevant messages you have already had."
    "If any embedded previous conversation is attached, use them for context to respond to the user, "
    "if the context is relevant and useful to responding. If the recalled context is not useful, "
    "ignore it and respond to the user as you would without any context. Do not talk about recalling conversations. "
    "Juast use any useful data from the previous conversations and respond normally as an intelligent AI assistant. "
)
# The system prompt is used to set the context for the conversation
convo = [{'role': 'system', 'content': system_prompt}]










# WE make a change here removing the first line
def stream_response(prompt):

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

# change this to now use queries
def retrieve_embeddings(queries, results_per_query=5):
    embeddings = set()

    for query in tqdm(queries):
        response = ollama.embeddings(model='nomic-embed-text', prompt=query)
        query_embedding = response['embedding']
        vector_db = client.get_collection(name='conversations')
        results = vector_db.query(
            query_embeddings=[query_embedding],
            n_results=results_per_query
        )
        best_embeddings = results['documents'][0]


        for best in best_embeddings:
            if best not in embeddings:
                if 'yes' in classify_embedding(query=query, context=best):
                    embeddings.add(best)

    return embeddings



# we can now have the llm create a list of queries to gather context form the database,
# allowing for pulling of multiple needles in the haystack as opposed to just one.
def create_queries(prompt):
    query_msg = (
        "You are a first principle reasoning search query AI agent. Your list of search queries will be used to search a vector database. "
        "With first principle reasoning create a python list of search queries to search the vector database for any data that would be necessary "
        "to have access to in order to correctly respond to the user prompt. Your response must be a Python list of strings with NO syntax errors. "
        "Do not explain anything and do not ever generate anything but a perfect syntax Python list. "
    )

    # we should be finetunning the model for this task, however for now we will use mutishot learning. 
    query_convo = [
        {
            'role': 'system',
            'content': query_msg
        },
        {
            'role': 'user',
            'content': 'Write an email to my car insurance company and create a requiest for them to lower my monthly payments.'
        },
        {
            'role': 'assistant',
            'content': '["What is the users name?", "What is the users car insurance company?", "What is the users current monthly payment?", "What is the users car insurance policy number?"]'
        },
        {
            'role': 'user',
            'content': 'How can I convert the speak function in my llama3 python voice assistant to use pyttsx3 instead of openai?'
        },
        {
            'role': 'assistant',
            'content': '["Llama3 voice assistant", "Python voice assistant", "OpenAI TTS", "pyttsx3"]'
        },
        {
            'role': 'user',
            'content': 'How long should I put a frozen pizza in the oven for and at what temperature?'
        },
        {
            'role': 'assistant',
            'content': '["Frozen pizza", "Oven temperature for frozen pizza", "Cooking time for frozen pizza"]'
        },
        {
            'role': 'user',
            'content': prompt
        }
    ]

    response = ollama.chat(model='llama3', messages=query_convo)
    print (Fore.YELLOW + '\nVector DB Queries: \n' + Style.RESET_ALL + response['message']['content'])

    try:
        return ast.literal_eval(response['message']['content'])
    except:
        print (Fore.RED + 'Error: Could not parse the response into a Python list. \n' + Style.RESET_ALL)
        return [prompt]



# new function to take the llm query and determine if the embedding is relevant to the user prompt
def classify_embedding(query, context):
    classify_msg = (
        'You are a embedding classification AI agent. Your input will be a prompt and one embedded chunk of text. '
        'You  will not respond as an AI assistant. You only respond with "yes" or "no". '
        'Determine whether the context contains data that directly is related to the search query. '
        'If the context is seemingly exactly what the search query needs, respond "yes". if it anything but directly ' 
        'related to the search query, respond "no". Do not respond "yes" unless the context is exactly what the search query needs. '
        'Your response must be "yes" or "no" with no other text, do not explain anything. '
    )
    # we will use mutishot learning for this as well
    classify_convo = [
        {
            'role': 'system',
            'content': classify_msg
        },
        {
            'role': 'user',
            'content': 'SEARCH QUERY: What is the users name? CONTEXT FROM EMBEDDINGS: The users name is Liam how are you?'
        }, 
        {
            'role': 'assistant',
            'content': 'yes'
        },
        {
            'role': 'user',
            'content': 'SEARCH QUERY: What is the users name? CONTEXT FROM EMBEDDINGS: The users car insurance policy number is 123456789.'
        },
        {
            'role': 'assistant',
            'content': 'no'
        },
        {
            'role': 'user',
            'content': f'SEARCH QUERY: {query} \n\nEMBEDDED CONTEXT: {context}'
        }
    ]

    response = ollama.chat(model='llama3', messages=classify_convo)

    return response['message']['content'].strip().lower()


# recall function to take the prompt as input and create a list of queries to search the embedding database
def recall(prompt):
    queries = create_queries(prompt=prompt)
    print (f'\n{len(queries)} queries created to search the database.\n')
    embeddings = retrieve_embeddings(queries=queries)
    convo.append(
            {
                "role": "user",
                "content": f"MEMORIES: {embeddings} \n\n USER PROMPT: {prompt}"
            }
        )
    print (f'\n{len(embeddings)} relevant memories found in the database.\n')



# add a function to remove the last conversation from the database
def remove_last_conversation():
    conn = connect_db()
    with conn.cursor() as cursor:
        cursor.execute("DELETE FROM conversations WHERE id = (SELECT MAX(id) FROM conversations)")
        conn.commit()
    conn.close()

    # convo.pop()
    print (fetch_conversations())
    print (Fore.YELLOW + 'Last conversation removed from the database.\n' + Style.RESET_ALL)

conversations = fetch_conversations()
create_vector_db(conversations=conversations)
print (fetch_conversations())


# change how this fucntions
while True:
    prompt = input(Fore.YELLOW + 'USER: \n' + Style.RESET_ALL)
    if prompt.lower() == 'exit':
        break

    if prompt[:2] == '/f':
        remove_last_conversation()

    else:
        recall(prompt=prompt)
        stream_response(prompt=prompt)