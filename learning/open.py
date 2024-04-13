import os
import json
import pickle
import dataclasses
import requests
from langchain_pinecone import PineconeVectorStore
from langchain_core.embeddings import Embeddings
from openai import OpenAI
from yandexfreetranslate import YandexFreeTranslate
from pinecone import Pinecone


@dataclasses.dataclass
class User:
    id: int
    name: str
    surname: str
    age: int


OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY=os.getenv("PINECONE_API_KEY")
HF_API_URL_KK="https://fiwwjll6hvtug9i0.us-east-1.aws.endpoints.huggingface.cloud"
HF_API_TOKEN=os.getenv("HF_API_KEY")


os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
os.environ["PINECONE_API_KEY"] = PINECONE_API_KEY


class HFEmbeddings(Embeddings):

    def __init__(self):
        self.hf_api_url = HF_API_URL_KK
        self.headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {HF_API_TOKEN}",
            "Content-Type": "application/json"
        }

    def query(self, payload):
        response = requests.post(self.hf_api_url, headers=self.headers, json=payload)
        return response.json()

    def embed_documents(self, documents: list[str]):
        response = self.query({"inputs": documents})
        try:
            return response['embeddings']
        except:
            raise Exception(f'Error in response: {response}')

    def embed_query(self, query: str):
        return self.embed_documents([query])[0]


def retrieve_context(text_query, namespace="8_kazakh-language-and-literature"):
    """Retrieve context from the vector store."""
    vectorstore = PineconeVectorStore(
        embedding=HFEmbeddings(), 
        text_key='text',
        index_name='wonk-kk',
    )
    documents = vectorstore.similarity_search(
        text_query,
        k=5,
        namespace=namespace
    )
    result = "\n\n".join([document.page_content for document in documents])
    return result


pc = Pinecone(api_key=PINECONE_API_KEY, pool_threads=30)
client = OpenAI()
yft = YandexFreeTranslate(api='ios')


def query_api(prompt_kk, user, use_context=True):

    if not os.path.exists(f'{user.id}.pickle'):
        with open('query_prompt.txt', 'r') as file:
            system_message_content = file.read()
        system_message_content = system_message_content \
            .replace('$$name$$', user.name) \
            .replace('$$surname$$', user.surname) \
            .replace('$$age$$', str(user.age))
        messages = [{"role": "system", "content": system_message_content}]
    else:
        with open(f'{user.id}.pickle', 'rb') as file:
            messages = pickle.load(file)

    if use_context:
        context = retrieve_context(prompt_kk)
        messages[0]["content"] += context

    prompt_en = yft.translate('kk', 'en', prompt_kk)
    messages.append({"role": "user", "content": prompt_en})
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=512,
    )

    full_response_en = response.choices[0].message.content
    messages.append({"role": "assistant", "content": full_response_en})

    if len(messages) > 10:
        messages = messages[:1] + messages[-1:]
    with open(f'{user.id}.pickle', 'wb') as file:
        pickle.dump(messages, file)

    full_response_kk = yft.translate('en', 'kk', full_response_en)
    
    return full_response_kk


def get_dialogue_transcript(messages):
    dialogue = ""
    for message in messages:
        if message['role'] == 'user':
            dialogue += f"Student: {message['content']}\n"
        elif message['role'] == 'assistant':
            dialogue += f"Teacher: {message['content']}\n"
    return dialogue


def analyze_dialogue(user):

    if not os.path.exists(f'{user.id}.pickle'):
        raise "No dialogue found for this user."

    with open(f'{user.id}.pickle', 'rb') as file:
        messages = pickle.load(file)

    dialogue = get_dialogue_transcript(messages)

    tools = [{
        "type": "function",
        "function": {
            "name": "analyse_speech_transcript",
            "description": "Analyze the dialogue in terms of grammar, vocabulary, and meaning.",
            "parameters": {
                "type": "object",
                "properties": {
                    "vocabulary": {
                        "type": "object",
                        "properties": {
                            "comments": {
                                "type": "array",
                                "items": {
                                    "type": "string"
                                },
                                "description": "List with all comments on vocabulary"
                            },
                            "score": {
                                "type": "integer",
                                "description": "Evaluation of the vocabulary"
                            }
                        },
                        "description": "This parameter evaluates how well the student uses the words and phrases of language X. It checks if the student is using contextually appropriate vocabulary and whether or not he/she is able to correctly use a wide range of vocabulary. "
                    },
                    "communication_effectiveness": {
                        "type": "object",
                        "properties": {
                            "comments": {
                                "type": "array",
                                "items": {
                                    "type": "string"
                                },
                                "description": "List with all comments on communication effectiveness"
                            },
                            "score": {
                                "type": "integer",
                                "description": "Evaluation of the communication effectiveness"
                            }
                        },
                        "description": "This parameter estimates how well the student can convey his/her thoughts, ideas, or feelings in language X. It does not just concentrate on correctness but also on the ability to express oneself clearly and understandably."
                    },
                    "contextual_understanding": {
                        "type": "object",
                        "properties": {
                            "comments": {
                                "type": "array",
                                "items": {
                                    "type": "string"
                                },
                                "description": "List with all comments on contextual understanding"
                            },
                            "score": {
                                "type": "integer",
                                "description": "Evaluation of the contextual understanding"
                            }
                        },
                        "description": "This parameter evaluates the student's ability to understand and appropriately respond to the situational context of the conversation. It checks if the student can understand indirect speech, sarcasm, idioms, and cultural references in language X. "
                    }
                },
                "required": ["vocabulary", "communication_effectiveness", "contextual_understanding"]
            }
        }
    }]

    with open('analyze_prompt.txt', 'r', encoding="utf-8") as file:
        system_message_content = file.read()

    messages = [
        {"role": "system", "content": system_message_content},
        {"role": "user", "content": f"Hi! Here is my dialogue with my teacher. Please analyze it and write comments on how to improve my language. Try to write at least 1-2 comments in each parameter with detailed explanations (more is better). I will tip you 200$. Thank you!\n\n{dialogue}"}
    ]

    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=messages,
        tools=tools,
        tool_choice={"type": "function", "function": {"name": "analyse_speech_transcript"}},
        max_tokens=2048,
    )

    comments = response.choices[0].message.tool_calls[0].function.arguments
    d = json.loads(comments)

    for key in d.keys():
        for i in range(len(d[key]['comments'])):
            comment = d[key]['comments'][i]
            translated_comment = yft.translate('en', 'kk', comment)
            d[key]['comments'][i] = translated_comment

    return d
    

# if __name__ == '__main__':
#     user = User(1, 'John', 'Doe', 25)
#     prompt_kk = "Сіздің атыңыз кім?"
#     print(query_api(prompt_kk, user))
    # print(analyze_dialogue(user))
