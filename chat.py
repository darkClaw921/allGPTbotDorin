from langchain.llms import OpenAI
from langchain.docstore.document import Document
import requests
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import CharacterTextSplitter
from langchain.prompts import PromptTemplate
import ipywidgets as widgets
from oauth2client.service_account import ServiceAccountCredentials
import re
from pprint import pprint
import os
from dotenv import load_dotenv
load_dotenv()
from langchain.schema.messages import (
    AIMessage,
    AIMessageChunk,
    BaseMessage,
    ChatMessage,
    HumanMessage,
    SystemMessage,
)
from openai import OpenAI
key = os.environ.get('OPENAI_API_KEY')
client = OpenAI(api_key=key)

import tiktoken
import sys
from loguru import logger
#import workGS
#logger.add(sys.stderr, format="{time} {level} {message}", level="INFO")
#logger.add("file_1.log", rotation="50 MB")
#sheet = workGS.Sheet('kgtaprojects-8706cc47a185.json','цены на дома 4.0 актуально ')
# from gigachat2 import gigaChat1
# from yandex1 import llmYandex
# from tokenGenerate import get_iam_token

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class GPT():
  modelVersion = ''
  MODEL = 'OPEN_AI'
  
  def __init__(self,modelVersion:str = 'gpt-3.5-turbo-16k'):
    self.modelVersion = modelVersion
    pass

  @classmethod
  #def set_key(cls):
  def set_key(cls, key):
      
      password_input = widgets.Password(
          description='Введите пароль:', 
          layout=widgets.Layout(width='500px'),
          style={'description_width': 'initial', 'white-space': 'pre-wrap', 'overflow': 'auto'})
      login_button = widgets.Button(description='Авторизация')
      output = widgets.Output()

      #login_button.on_click(on_button_clicked)
      #display(widgets.VBox([password_input, login_button, output]))

  def load_search_indexes(self, url: str,gsText:str = '') -> str:
    # Extract the document ID from the URL
    print('попали в load_serch_index')
    match_ = re.search('/document/d/([a-zA-Z0-9-_]+)', url)
    if match_ is None:
        raise ValueError('Invalid Google Docs URL')
    doc_id = match_.group(1)

    # Download the document as plain text
    response = requests.get(f'https://docs.google.com/document/d/{doc_id}/export?format=txt')
    response.raise_for_status()
    text = response.text
    #для получения данных из таблицы
    #gsText = sheet.get_gs_text()
    #gsText = ''
    #print(f'{gsText=}')
    text1 = text + gsText
    #print(f'{text1=}')
    return self.create_embedding(text1)

  def load_prompt(self, 
                  url: str) -> str:
    # Extract the document ID from the URL
    match_ = re.search('/document/d/([a-zA-Z0-9-_]+)', url)
    if match_ is None:
        raise ValueError('Invalid Google Docs URL')
    doc_id = match_.group(1)

    # Download the document as plain text
    response = requests.get(f'https://docs.google.com/document/d/{doc_id}/export?format=txt')
    response.raise_for_status()
    text = response.text
    return f'{text}'


  def create_image(self, promt:str) -> str:
    # PROMPT = "An eco-friendly computer from the 90s in the style of vaporwave"


    response = client.images.generate(prompt=promt,
    n=1,
    size="256x256")

    # print(response["data"][0]["url"])
    return response.data[0].url

  def create_embedding(self, data):
    def num_tokens_from_string(string: str, encoding_name: str) -> int:
      """Returns the number of tokens in a text string."""
      encoding = tiktoken.get_encoding(encoding_name)
      num_tokens = len(encoding.encode(string))
      return num_tokens

    source_chunks = []
    #splitter = CharacterTextSplitter(separator="\n", chunk_size=1524, chunk_overlap=0)
    splitter = CharacterTextSplitter(separator="==========", chunk_size=1024, chunk_overlap=300)

    for chunk in splitter.split_text(data):
      source_chunks.append(Document(page_content=chunk, metadata={}))

    # Создание индексов документа
    search_index = Chroma.from_documents(source_chunks, OpenAIEmbeddings(), )
    search_index.similarity_search
    count_token = num_tokens_from_string(' '.join([x.page_content for x in source_chunks]), "cl100k_base")
    print('\n ===========================================: ')
    print('Количество токенов в документе :', count_token)
    print('ЦЕНА запроса:', 0.0004*(count_token/1000), ' $')
    return search_index

  #def answer(self, system, topic, temp = 1):    
  @logger.catch
  def answer(self, system, topic:list, temp = 1, MODEL = 'OPEN_AI'):
    """messages = [
      {"role": "system", "content": system},
      {"role": "user", "content": topic}
      ]
    """
    messages = [
      {"role": "system", "content": system },
      #{"role": "user", "content": topic}
      #{"role": "user", "content": context}
      ]
    messages.extend(topic)
    mess = []
    if MODEL == 'giga':
        for message in messages:
            if message['role'] == 'user':
                mess.append(HumanMessage(content=message['content']))
            
            elif message['role'] == 'system':
                mess.append(SystemMessage(content=message['content']))
            
            elif message['role'] == 'assistant':
                mess.append(AIMessage(content=message['content']))
        
        res = gigaChat1(mess)
        # res.content - ответ
        return res.content, 0, 0
        
    if MODEL == 'open_ai_assign':

        assistant ='asst_wjD2L6Ymgq3tCO834BwwJSip' 
        # openai.('')
        
        thread = client.beta.threads.create()
        text = topic[-1]['content']
        message = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=text,
        )

        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant,
            instructions=""
        )

        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
            )
        pprint(run.status)

        while run.status != 'completed':
            run = client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )
            logger.debug(run.status)
        messages = client.beta.threads.messages.list(
            thread_id=thread.id
            )

        # logger.info(f'{messages=}')
        # logger.info(f'{messages.content=}')
        logger.info(f'{messages.data[0].content[0].text.value=}')
        answerText = messages.data[0].content[0].text.value 
        return answerText, 0, 0

    if MODEL == 'gpt':
        completion = client.chat.completions.create(model=self.modelVersion,
        messages=messages,
        temperature=temp)
        # allToken = f'{completion["usage"]["total_tokens"]} токенов использовано всего (вопрос-ответ).'
        # allTokenPrice = f'ЦЕНА запроса с ответом :{0.002*(completion["usage"]["total_tokens"]/1000)} $'
        #return f'{completion.choices[0].message.content}\n\n{allToken}\n{allTokenPrice}', completion["usage"]["total_tokens"], 0.002*(completion["usage"]["total_tokens"]/1000)
        return f'{completion.choices[0].message.content}', 0, 0
    
    if MODEL == 'yandex':
        global llmYandex 
        messages = ' '.join([x['content'] for x in topic])
        llmYandex.instruction_text = system
        try:
            answer = llmYandex._call(messages)
        except Exception as e :
            logger.critical(e)
            llmYandex.iam_token=get_iam_token()
            answer = llmYandex._call(messages) 
           
        
        return answer, 0, 0
        # pass


  @logger.catch
  def num_tokens_from_messages(self, messages, model="gpt-3.5-turbo-0301"):
    """Returns the number of tokens used by a list of messages."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")
    if model == "gpt-3.5-turbo-0301":  # note: future models may deviate from this
        num_tokens = 0
        for message in messages:
            num_tokens += 4  # every message follows <im_start>{role/name}\n{content}<im_end>\n
            #logger.error(f'{messages}')
            for key, value in message.items():
                num_tokens += len(encoding.encode(value))
                if key == "name":  # if there's a name, the role is omitted
                    num_tokens += -1  # role is always required and always 1 token
        num_tokens += 2  # every reply is primed with <im_start>assistant
        return num_tokens
    else:
        raise NotImplementedError(f"""num_tokens_from_messages() is not presently implemented for model {model}.
See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens.""")
        
  def insert_newlines(self, text: str, max_len: int = 170) -> str:
    words = text.split()
    lines = []
    current_line = ""
    for word in words:
        if len(current_line + " " + word) > max_len:
            lines.append(current_line)
            current_line = ""
        current_line += " " + word
    lines.append(current_line)
    return "\n".join(lines)

  def search_project(self,search_index, topic:str, k:int=4, verbose = 0):
    #self.create_embedding(text1)
    docs = search_index.similarity_search(topic, k=k)
    #print(f'{docs[0].metadata=}')
    #1/0
    if (verbose): print('\n ===========================================: ')
    message_content = re.sub(r'\n{2}', ' ', '\n '.join([f'\nОтрывок документа №{i+1}\n=====================' + doc.page_content + '\n' for i, doc in enumerate(docs)]))
    if (verbose): print('message_content :\n ======================================== \n', message_content)
    logger.info(f'{message_content=}')
    return message_content
 

  def answer_index(self, system, topic, history:list, search_index, temp = 1, verbose = 0):
    
    #Выборка документов по схожести с вопросом 
    docs = search_index.similarity_search(topic, k=4)
    if (verbose): print('\n ===========================================: ')
    message_content = re.sub(r'\n{2}', ' ', '\n '.join([f'\nОтрывок документа №{i+1}\n=====================' + doc.page_content + '\n' for i, doc in enumerate(docs)]))
    if (verbose): print('message_content :\n ======================================== \n', message_content)

    systemMess = 'Данные, на основании которых нужно продолжить диалог:'
    messages = [
      {"role": "system", "content": system + f"{systemMess} {message_content}"},
      {"role": "user", "content": 'Диалог с клиентом, который нужно продолжить:'},
      #{"role": "user", "content": context}
      ]
    messages.extend(history)

    # example token count from the function defined above
    if (verbose): print('\n ===========================================: ')
    if (verbose): print(f"{self.num_tokens_from_messages(messages, 'gpt-3.5-turbo-0301')} токенов использовано на вопрос")

    completion = client.chat.completions.create(model=self.modelVersion,
    #model="gpt-3.5-turbo",
    messages=messages,
    temperature=temp)
    if (verbose): print('\n ===========================================: ')
    if (verbose): print(f'{completion["usage"]["total_tokens"]} токенов использовано всего (вопрос-ответ).')
    if (verbose): print('\n ===========================================: ')
    if (verbose): print('ЦЕНА запроса с ответом :', 0.002*(completion["usage"]["total_tokens"]/1000), ' $')
    if (verbose): print('\n ===========================================: ')
    print('ОТВЕТ : \n', self.insert_newlines(completion.choices[0].message.content))

    answer = completion.choices[0].message.content
    #allToken = f'{completion["usage"]["total_tokens"]} токенов использовано всего (вопрос-ответ).'
    #allTokenPrice = f'ЦЕНА запроса с ответом :{0.002*(completion["usage"]["total_tokens"]/1000)} $'
    
    return f'{answer}', completion["usage"]["total_tokens"], 0.002*(completion["usage"]["total_tokens"]/1000), docs

#    return answer
  
  def get_summary(self, history:list, 
                  promtMessage = 'Write a concise summary of the following and CONCISE SUMMARY IN RUSSIAN:',
                  temp = 0.3):    
    """messages = [
      {"role": "system", "content": system},
      {"role": "user", "content": topic}
      ]
    """
    #promtMessage = """Write a concise summary of the following and CONCISE SUMMARY IN RUSSIAN:"""
    messages = [
      {"role": "system", "content": promtMessage},
      #{"role": "user", "content": topic}
      #{"role": "user", "content": context}
      ]
    messages.extend(history)
    logger.info(f'answer message get_summary {messages}')
    completion = client.chat.completions.create(model=self.modelVersion,
    #model="gpt-3.5-turbo",
    messages=messages,
    temperature=temp)
    logger.info(f'{completion["usage"]["total_tokens"]=}')
    logger.info(f'{completion["usage"]=}')
    answer =completion.choices[0].message.content  
    logger.info(answer)
    roleAsnwer= {'role': 'user', 'content': answer}
    return roleAsnwer

  def summarize_podborka(self,promt:str, history:list):
    # Применяем модель gpt-3.5-turbo-0613 для саммаризации вопросов
    messages = [
        {"role": "system", "content": promt},
        {"role": "user", "content": "Суммаризируй следующий диалог менеджера и клиента: "},
    ]
    #messages.extend(history[:-1])
    messages.extend(history[:-1])

    completion = client.chat.completions.create(model=self.modelVersion,
    messages=messages,
    temperature=0.3)
    answer = completion.choices[0].message.content
    logger.info(f'Саммари диалога: {answer}')
    roleAsnwer= {'role': 'user', 'content': answer}
    return roleAsnwer
   
  def summarize_questions(self,history:list):
    # Применяем модель gpt-3.5-turbo-0613 для саммаризации вопросов
    messages = [
        {"role": "system", "content": "Ты - ассистент компании, основанный на AI. Ты умеешь профессионально суммаризировать присланные тебе диалоги менеджера и клиента. Твоя задача - суммаризировать диалог, который тебе пришел."},
        {"role": "user", "content": "Суммаризируй следующий диалог менеджера и клиента: "}
    ]
    #messages.extend(history[:-1])
    messages.extend(history[:-1])

    completion = client.chat.completions.create(model=self.modelVersion,
    messages=messages,
    temperature=0.3)
    answer = completion.choices[0].message.content
    logger.info(f'Саммари диалога: {answer}')
    roleAsnwer= {'role': 'user', 'content': answer}
    return roleAsnwer

  def get_chatgpt_ansver3(self, system, topic, search_index, temp = 1):

    
    messages = [
      {"role": "system", "content": system},
      {"role": "user", "content": topic}
      ]

    completion = client.chat.completions.create(model=self.modelVersion,
    #model="gpt-3.5-turbo",
    messages=messages,
    temperature=temp)
    print('ОТВЕТ : \n', self.insert_newlines(completion.choices[0].message.content))



# from openai import OpenAI


# from openai import OpenAI
# assistant ='asst_iFpmwH8rOc2faiQ0pH3mgPTR' 
# # openai.('')

# thread = client.beta.threads.create()

# message = client.beta.threads.messages.create(
#     thread_id=thread.id,
#     role="user",
#     content="ты кто?"
# )

# run = client.beta.threads.runs.create(
#     thread_id=thread.id,
#     assistant_id=assistant,
#     instructions=""
# )

# run = client.beta.threads.runs.retrieve(
#     thread_id=thread.id,
#     run_id=run.id
#     )
# pprint(run.status)

# while run.status != 'completed':
#     run = client.beta.threads.runs.retrieve(
#         thread_id=thread.id,
#         run_id=run.id
#     )
#     logger.debug(run.status)
#     # logger.debug(run)
    
# messages = client.beta.threads.messages.list(
#     thread_id=thread.id
#     )

# logger.info(f'{messages=}')
# logger.info(f'{messages.data[0].content[0].text.value=}')


# import time
# time.sleep(1)
# messages = client.beta.threads.messages.list(
#     thread_id=thread.id
#     )
# # logger.info(f'{messages=}')
# logger.info(f'{message.content[0].text=}')
# run = client.beta.threads.runs.retrieve(
#     thread_id=thread.id,
#     run_id=run.id
#     )
# pprint(run.status)

# import time
# messages = []
# while True:
#     time.sleep(1)
#     messages = client.beta.threads.messages.list(
#     thread_id=thread.id
#     )
    
#     logger.info(f'{messages=}')
