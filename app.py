from langchain.chat_models import init_chat_model
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema.runnable import Runnable
from langchain.schema.runnable.config import RunnableConfig

from typing import cast, Optional

import os
import chainlit as cl
from chainlit.input_widget import Select, Switch, Slider

# values=[
#     "mistral-medium-2505",
#     "grok-3",
#     "gpt-4o",
#     "DeepSeek-R1-0528",
#     "Llama-4-Maverick-17B-128E-Instruct-FP8",
# ]

model_dict = {'GPT-4o':'gpt-4o',
              'Deepseek R1':'DeepSeek-R1-0528',
              'Llama 4':'Llama-4-Maverick-17B-128E-Instruct-FP8',
              'Mistral':'mistral-medium-2505',
              }

@cl.set_chat_profiles
async def chat_profile():
    return [
        cl.ChatProfile(
            name='GPT-4o',
            markdown_description= 'Modelo proprietário da OpenAI, ideal para **tarefas complexas**, com alta precisão, criatividade e capacidade multimodal (texto, imagem, áudio e vídeo).',
        ),
        cl.ChatProfile(
            name='Deepseek R1',
            markdown_description='Modelo **open-source** voltado para **raciocínio lógico, análise matemática e eficiência computacional**, indicado para problemas que exigem estruturação e cálculo.',
        ),
        cl.ChatProfile(
            name='Llama 4',
            markdown_description='Modelo **open-source** de última geração, otimizado para **custo-benefício** e com ampla comunidade de suporte, indicado para aplicações gerais em linguagem natural.',
        ),
        cl.ChatProfile(
            name='Mistral',
            markdown_description='Modelo **open-source** de alto desempenho, excelente em **processamento de texto e geração de código**, com foco em **eficiência e rapidez** em aplicações práticas.',
        ),
    ]

def setup_runnable(chat_profile, settings):


    llm = init_chat_model(
        model=model_dict.get(chat_profile),
        model_provider='azure_ai',
        temperature=settings.get('temperature')
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Você é o assistente virtual da FioCruz, você deve ajudar os funcionarios da organização a resolver os seus problemas"
            ),
            MessagesPlaceholder("history"),
            ("human", "{question}"),
        ]
    )
    runnable = prompt | llm  
    cl.user_session.set("runnable", runnable)


@cl.password_auth_callback
def auth_callback(username, password):
    # Se retornar cl.User, autenticação deu certo, se retornar None,
    # deu errad

    if (username, password) == ("admin", "admin"):
        return cl.User(
            identifier="admin",
            metadata={"role": "admin", "provider": "credentials"}
        )
    else:
        return None

@cl.on_chat_start
async def on_chat_start():
    chat_profile = cl.user_session.get("chat_profile")
    chat_settings = cl.user_session.get("chat_settings")

    setup_runnable(chat_profile,chat_settings)


@cl.set_chat_profiles
async def chat_profile():
    return [
        cl.ChatProfile(
            name='GPT-4o',
            markdown_description='Modelo proprietário da OpenAI, ideal para **tarefas complexas**, com alta precisão, criatividade e capacidade multimodal (texto, imagem, áudio e vídeo).',
        ),
        cl.ChatProfile(
            name='Deepseek R1',
            markdown_description='Modelo **open-source** voltado para **raciocínio lógico, análise matemática e eficiência computacional**, indicado para problemas que exigem estruturação e cálculo.',
        ),
        cl.ChatProfile(
            name='Llama 4',
            markdown_description='Modelo **open-source** de última geração, otimizado para **custo-benefício** e com ampla comunidade de suporte, indicado para aplicações gerais em linguagem natural.',
        ),
        cl.ChatProfile(
            name='Mistral',
            markdown_description='Modelo **open-source** de alto desempenho, excelente em **processamento de texto e geração de código**, com foco em **eficiência e rapidez** em aplicações práticas.',
        ),
    ]


def get_chat_setttings():
    temp_widget = Slider(
        id="temperature",
        label="Selecione a temperatura",
        initial=1,
        min=0,
        max=2,
        step=0.1)

    return cl.ChatSettings([temp_widget])


@cl.on_message
async def main(message: cl.Message):

    runnable =  cast(Runnable,cl.user_session.get("runnable"))


    ai_msg = runnable.invoke(dict(question=message.content,
                                  history=cl.chat_context.to_openai()))

    await cl.Message(content=ai_msg.content).send()
