import os
import json
import pickle
import dataclasses
import requests
from langchain_pinecone import PineconeVectorStore
from langchain_core.embeddings import Embeddings
from openai import OpenAI
from pinecone import Pinecone
from google.cloud import translate_v2


@dataclasses.dataclass
class User:
    id: int
    name: str
    surname: str
    age: int


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
HF_API_URL_KK = "https://fiwwjll6hvtug9i0.us-east-1.aws.endpoints.huggingface.cloud"
HF_API_TOKEN = os.getenv("HF_API_KEY")

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r'google_key.json'
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
os.environ["PINECONE_API_KEY"] = PINECONE_API_KEY

google_translate = translate_v2.Client()
pc = Pinecone(api_key=PINECONE_API_KEY, pool_threads=30)
client = OpenAI()


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


def translate(sl: str, tl: str, text: str):
    return google_translate.translate(
        text, source_language=sl, target_language=tl
    )['translatedText']


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


def query_api(user, prompt_kk="", path_to_audio="audio.mp3", use_context=False):
    if not prompt_kk:
        if not path_to_audio:
            raise "Either prompt_kk or path_to_audio must be provided."
        audio_file = open(path_to_audio, "rb")
        prompt_kk = client.audio.translations.create(
            model="whisper-1",
            file=audio_file
        ).text

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

    prompt_en = translate('kk', 'en', prompt_kk)
    messages.append({"role": "user", "content": prompt_en})
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.5,
        max_tokens=512,
    )

    full_response_en = response.choices[0].message.content
    messages.append({"role": "assistant", "content": full_response_en})

    if len(messages) > 10:
        messages = messages[:1] + messages[-1:]
    with open(f'{user.id}.pickle', 'wb') as file:
        pickle.dump(messages, file)

    full_response_kk = translate('en', 'kk', full_response_en)

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
        {"role": "user",
         "content": f"Hi! Here is my dialogue with my teacher. Please analyze it and write comments on how to improve my English. Try to write at least 1-2 comments in each parameter with detailed explanations (the more is better). I will tip you 200$. Thank you!\n\n{dialogue}"}
    ]

    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=messages,
        temperature=0,
        tools=tools,
        tool_choice={"type": "function", "function": {"name": "analyse_speech_transcript"}},
        max_tokens=2048,
    )

    comments = response.choices[0].message.tool_calls[0].function.arguments
    d = json.loads(comments)

    for key in d.keys():
        for i in range(len(d[key]['comments'])):
            comment = d[key]['comments'][i]
            comment.replace('English', 'Kazakh').replace('english', 'kazakh')
            translated_comment = translate('en', 'kk', comment)
            d[key]['comments'][i] = translated_comment

    return d


def get_reading_task(reading_task_id):
    with open(reading_task_id + "/questions_kk.txt", "r",
              encoding="utf-8",
              errors="ignore") as file:
        questions = file.readlines()

    with open(reading_task_id + "/text_kk.txt", "r",
              encoding="utf-8",
              errors="ignore") as file:
        text = file.read()

    return questions, text


def check_reading_answers(reading_task_id, answers_kk):
    """
    Check the answers to the reading task. How much of the text was understood?
    Uses function calls to OpenAI and gives comment for each question and either 1 or 0 for correct or incorrect.
    """

    # translate all answers to english
    answers_en = [translate('kk', 'en', answer) for answer in answers_kk]

    with open(reading_task_id + "/questions_en.txt", "r",
              encoding="utf-8") as file:
        questions = file.readlines()

    with open(reading_task_id + "/text_en.txt", "r",
              encoding="utf-8") as file:
        text = file.read()

    qna = ""
    for question, answer in zip(questions, answers_en):
        qna += f"Question: {question}\nAnswer: {answer}\n\n"

    tools = [{
        "type": "function",
        "function": {
            "name": "check_reading_answers",
            "description": "Analyze the answers to the reading task. How much of the text was understood?",
            "parameters": {
                "type": "object",
                "properties": {
                    "comments": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "description": "List with all comments on the answers"
                    },
                    "scores": {
                        "type": "array",
                        "items": {
                            "type": "integer"
                        },
                        "description": "This parameter evaluates how well the student can answer the questions based on the text. It checks if the student can understand the text and answer the questions correctly. It's value is either 1 or 0."
                    }
                },
                "required": ["comments", "scores"]
            }
        }
    }]

    with open('reading_prompt.txt', 'r', encoding="utf-8") as file:
        system_message_content = file.read()

    system_message_content += "\n\n" + text

    messages = [
        {"role": "system", "content": system_message_content},
        {"role": "user",
         "content": f"Hi! Here are my answers to the reading task. Please analyze them, evaluate and write comments on each of my answer. will tip you 200$. Thank you!\n\n{qna}"}
    ]

    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=messages,
        temperature=0,
        tools=tools,
        tool_choice={"type": "function", "function": {"name": "check_reading_answers"}},
        max_tokens=2048,
    )

    comments = response.choices[0].message.tool_calls[0].function.arguments

    d = json.loads(comments)

    for i in range(len(d['comments'])):
        comment = d['comments'][i]
        comment.replace('English', 'Kazakh').replace('english', 'kazakh')
        translated_comment = translate('en', 'kk', comment)
        d['comments'][i] = translated_comment

    return d


# if __name__ == '__main__':
    # user = User(1, 'John', 'Doe', 25)
    # prompt_kk = "Қотақ сорғың келе ма?"
    # print(query_api(user))
    # print(analyze_dialogue(user))
    # print(get_reading_task("academic_1"))
    # print(check_reading_answers("academic_1",
    #                             [
    #                                 "Дұрыс жауапта кірпілердің алмаларды паразиттерді жою үшін омыртқаларына қою арқылы тазарту үшін пайдаланатынын айту керек.",
    #                                 "Қотақ сорғың келе ма?", "Қотақ сорғың келе ма?", "Қотақ сорғың келе ма?"]))
