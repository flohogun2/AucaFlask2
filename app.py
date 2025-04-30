# coding: latin-1
import locale
locale.setlocale(locale.LC_ALL, 'fr_FR')

from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

from langchain_openai import ChatOpenAI

from langchain_core.messages import SystemMessage
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.messages import AIMessage, HumanMessage

from langchain.agents import  create_openai_tools_agent
from langchain.agents import  AgentExecutor
from langchain.agents import  Tool

from flask import Flask, render_template, request, redirect

import openai
import os
import time
import appointments
from datetime import date

# Set the OpenAI API key
openai.api_key = "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"

# Define the name of the bot
name = 'BOT'

# Define the role of the bot
role = 'customer service'

# Define the impersonated role with instructions
impersonated_role = f"""
    From now on, you are going to act as {name}. Your role is {role}.
    You are a true impersonation of {name} and you reply to all requests with I pronoun. You never give unknown information.
    Forward them to the website for more information.
    YOU ARE NOT AN AI MODEL!
"""

# Initialize variables for chat history
explicit_input = ""
chatgpt_output = 'Chat log: /n'
cwd = os.getcwd()
i = 1

# Find an available chat history file
while os.path.exists(os.path.join(cwd, f'chat_history{i}.txt')):
    i += 1

history_file = os.path.join(cwd, f'chat_history{i}.txt')

# Create a new chat history file
with open(history_file, 'w') as f:
    f.write('\n')

# Initialize chat history
#chat_history = ''

tools = [     
    Tool(
        name = "date_du_jour",
        func = lambda string: appointments.todayDate(),
        description="Utilisez pour obtenir la date du jour",
        ),
    Tool(
        name = "jour_de_la_semaine",
        func = lambda string: appointments.dayOfWeek(string),
        description="Utilisez pour obtenir le jour de la semaine, l'entrée est 'today' ou une date au format dd/mm/yyyy",
        ),
     Tool(
      name = 'reservation_rendez-vous',
      func = lambda string: appointments.appointment_booking(string),
      description="Utilisez pour planifier un rendez-vous pour une date et une heure données. L'entrée de cet outil doit être une liste de 3 chaînes séparées par des virgules : date et heure au format : jj/mm/aaaa, hh:mm, puis l'adresse email de l'utilisateur utilisée pour l'identification. convertissez la date et l heure dans ces formats. Par exemple, '31/12/2023, 10:00' serait l entrée pour le 31 décembre 2023 à 10h00",
            verbose=True
      ),
      Tool(
      name = 'verification_disponibilites_calendaires_rendez-vous',
      func = lambda string: appointments.appointment_checking(string),
      description="cette fonction doit être appelée lorsque l'utilisateur souhaite vérifier si un créneau calendaire pour un rendez-vous est disponible ou non. L'entrée de cet outil doit être une liste de 3 chaînes séparées par des virgules : date et heure au format : jj/mm/aaaa, hh:mm, puis l'adresse email de l'utilisateur utilisée pour l'identification. convertissez la date et l heure dans ces formats. Par exemple, '31/12/2023, 10:00' serait l entrée pour le 31 décembre 2023 à 10h00",
            verbose=True
  ) 
 
 ]

functions = [
{
    "name": "appointment_booking",
    "description": "When user want to book appointment, then this function should be called.",
    "parameters": {
        "type": "object",
        "properties": {
            "date": {
                "type": "string",
                "format": "date",
                "example":"2023-07-23",
                "description": "Date, when the user wants to book an appointment. The date must be in the format of YYYY-MM-DD.",
            },
            "time": {
                "type": "string",
                "example": "20:12:45",
                "description": "time, on which user wants to book an appointment on a specified date. Time must be in %H:%M:%S format.",
            },
            "email_address": {
                "type": "string",
                "description": "email_address of the user gives for identification.",
            }
        },
        "required": ["date","time","email_address"],
    },
},
{
    "name": "appointment_reschedule",
    "description": "When user want to reschedule appointment, then this function should be called.",
    "parameters": {
        "type": "object",
        "properties": {
            "date": {
                "type": "string",
                "format": "date",
                "example":"2023-07-23",
                "description": "It is the date on which the user wants to reschedule the appointment. The date must be in the format of YYYY-MM-DD.",
            },
            "time": {
                "type": "string",
                "description": "It is the time on which user wants to reschedule the appointment. Time must be in %H:%M:%S format.",
            },
            "email_address": {
                "type": "string",
                "description": "email_address of the user gives for identification.",
            }
        },
        "required": ["date","time","email_address"],
    },
},
{
    "name": "appointment_delete",
    "description": "When user want to delete appointment, then this function should be called.",
    "parameters": {
        "type": "object",
        "properties": {
            "date": {
                "type": "string",
                "format": "date",
                "example":"2023-07-23",
                "description": "Date, on which user has appointment and wants to delete it. The date must be in the format of YYYY-MM-DD.",
            },
            "time": {
                "type": "string",
                "description": "time, on which user has an appointment and wants to delete it. Time must be in %H:%M:%S format.",
            },
            "email_address": {
                "type": "string",
                "description": "email_address of the user gives for identification.",
            }
        },
        "required": ["date","time","email_address"],
    },
},
{
    "name": "Disponibilités calendaires pour un rendez-vous",
    "description": "cette fonction doit être appelée lorsque l'utilisateur souhaite vérifier si un créneau calendaire pour un rendez-vous est disponible ou non.",
    "parameters": {
        "type": "object",
        "properties": {
            "date": {
                "type": "string",
                "format": "date",
                "example":"2023-07-23",
                "description": "Date, when the user wants to book an appointment. The date must be in the format of YYYY-MM-DD.",
            },
            "time": {
                "type": "string",
                "example": "20:12:45",
                "description": "time, on which user wants to book an appointment on a specified date. Time must be in %H:%M:%S format.",
            }
        },
        "required": ["date","time"],
    },
}]

formatted_system_message = f"""
Vous êtes une experte en prise de rendez-vous appelée Nathalie qui travaille pour la société AUCA. Les rendez-vous concernent une séance d'essai ou un bilan personnalisé dans la salle de sport de la société AUCA offrant un large éventail de services, notamment un plateau musculation, des cours collectifs, un coaching personnalisé, et des services sur mesure adaptés à ses clients. Vous devez demander à l'utilisateur la date du rendez-vous, l'heure du rendez-vous et l'identifiant de messagerie. L'utilisateur peut prendre rendez-vous de 10h à 19h du lundi au vendredi, et de 10h à 14h le samedi. 
Vérifiez si l'heure fournie par l'utilisateur se situe dans les horaires d'ouverture, alors seulement vous pourrez procéder.
Vous devez vous rappeler que la date d'aujourd'hui au format DD/MM/YYYY est {date.today().strftime("%d/%m/%Y")} et le jour est {appointments.day_list[date.today().weekday()]}.

Instructions:
- Ne faites pas de suppositions sur les valeurs à intégrer en tant que paramètres des fonctions. Si l'utilisateur ne fournit aucun des paramètres requis, vous devez alors demander des éclaircissements.
- Assurez-vous que l'adresse email qui corespond à l'identifiant de l'utilisateur est valide et non vide.
- Si une demande d'utilisateur est ambiguë, vous devez également demander des éclaircissements.
- Lorsqu'un utilisateur demande une date ou une heure de reprogrammation du rendez-vous en cours, vous devez alors demander uniquement les détails du nouveau rendez-vous.
- Si l'utilisateur n'a pas fourni le jour, le mois en indiquant l'heure du rendez-vous souhaité, vous devrez alors demander des éclaircissements.
- Si l'utilisateur n'a pas fourni l'année en indiquant l'heure du rendez-vous souhaité, l'année est alors {date.today().strftime("%Y")}
- Si l'utilisateur propose un jour de la semaine, demander si il s'agit de cette semaine ou de la semaine prochaine. L'année du rendez-vous proposé sera {date.today().strftime("%Y")}
- Si l'utilisateur veut un rdv {appointments.day_list[appointments.tomorow.weekday()]} alors demander si il s'agit de demain.
- Si l'utilisateur veut un rdv {appointments.day_list[appointments.tomorowplus1.weekday()]} alors demander si il s'agit de {appointments.tomorowplus1.strftime("%d/%m/%Y")}.
- Si l'utilisateur veut un rdv {appointments.day_list[appointments.tomorowplus2.weekday()]} alors demander si il s'agit de {appointments.tomorowplus2.strftime("%d/%m/%Y")}.
- Si l'utilisateur veut un rdv {appointments.day_list[appointments.tomorowplus3.weekday()]} alors demander si il s'agit de {appointments.tomorowplus3.strftime("%d/%m/%Y")}.
- Si l'utilisateur veut un rdv {appointments.day_list[appointments.tomorowplus4.weekday()]} alors demander si il s'agit de {appointments.tomorowplus4.strftime("%d/%m/%Y")}.
- Si l'utilisateur veut un rdv {appointments.day_list[appointments.tomorowplus5.weekday()]} alors demander si il s'agit de {appointments.tomorowplus5.strftime("%d/%m/%Y")}.

- Lors du choix du rendez-vous, demander a l'utilisateur quel jour de la semaine serait le plus pratique pour le rendez-vous ?"  


- Demandez a l'utilisateur si il préfere un crénaux pour le rendez-vous en début ou en fin de semaine."  

- si l'utilisateur prefere en debut de semaine proposer le lundi ou le mardi.
- si l'utilisateur prefere en fin de semaine proposer le jeudi ou le vendredi.
Assurez-vous de suivre attentivement les instructions lors du traitement de la demande.

Si un utilisateur vous pose une question générale, répondez-y puis fournissez une description générique de vos capacités.
Préparez des réponses adaptées aux objections courantes.  

-Si un utilisateur indique qu'il n’a pas le temps alors répondre que c’est pour cela que nous avons des créneaux flexibles et des programmes rapides pour optimiser son temps.

-Si un utilisateur indique qu'il n'est pas sûr d’être à l’aise en salle de sport alors répondre que nous avons des espaces accueillants et un accompagnement personnalisé pour que vous vous sentiez bien dès son arrivée.

- Répondez avec une discussion naturelle, concise, et orientée vers une action immédiate, une structure claire et engageante, qui inspire confiance et facilite la prise de décision.


- Rester focalisé sur les services fitness.  
- Incluez toujours une question finale pour inciter à la prise de rendez-vous.  
- Maintenir des réponses courtes, dynamiques, et adaptées à l’interaction.


Si un utilisateur demande votre fonction, fournissez une description générique de vos capacités basée sur toutes ces informations sous la propriété « résumé ».
        """

# this is a customization of what is pulled down by hub.pull("hwchase17/openai-tools-agent")
prompt = ChatPromptTemplate.from_messages([ 
    SystemMessage(formatted_system_message),
    MessagesPlaceholder(variable_name="chat_history", optional=True),
    ("human", "{input}"), 
    MessagesPlaceholder(variable_name="agent_scratchpad")
    ])

_model = "gpt-4-turbo-preview"
llm = ChatOpenAI(model=_model,
                 temperature=0.0,
                 api_key="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", verbose=True
                 )

#memory = InMemoryChatMessageHistory(session_id="test-session")
# Create session history
store = {}

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]

agent_new = create_openai_tools_agent(llm, tools, prompt)

# Create an agent executor by passing in the agent and tools
agent_executor_new = AgentExecutor(agent=agent_new, tools=tools, verbose=False, handle_parsing_errors=True,return_intermediate_steps=True)

agent_with_chat_history = RunnableWithMessageHistory(
    agent_executor_new,
   get_session_history,
    input_messages_key="input",
    history_messages_key="chat_history",
    output_messages_key="output"  # Ensure this key matches the output of your agent
)
GPT_MODEL = "gpt-4-turbo-preview"

def chat_completion_request(messages, functions=None, function_call=None):
    json_data = {"model": GPT_MODEL, "messages": messages}
  
    if functions is not None:
        json_data.update({"functions": functions})
    if function_call is not None:
        json_data.update({"function_call": function_call})
    try:

        config = {"configurable": {"session_id": "test-session"}}
        completion =agent_with_chat_history.invoke(messages,config)              
           
        history = get_session_history("test-session")
     #   print (history.messages)
   
        #completion = client.chat.completions.create(
        #**json_data
        #)
        return completion
    except Exception as e:
        print("Unable to generate ChatCompletion response")
        print(f"Exception: {e}")
        return e

chat_history = []

def chatcompletion2(user_input, impersonated_role, explicit_input, chat_history):
    messages =  {"input":user_input}
  

    chat_response = chat_completion_request(
    messages, functions=functions
    )
    
    history = get_session_history("test-session")
    # history.extend([
    # HumanMessage(content=user_input),
    # AIMessage(content=chat_response["output"])
    # ])
         
    if chat_response['output']:
       return chat_response['output'];
        
    return ""

         

app = Flask(__name__)


# Function to complete chat input using OpenAI's GPT-3.5 Turbo
def chatcompletion(user_input, impersonated_role, explicit_input, chat_history):
    output = openai.ChatCompletion.create(
        model="gpt-4-turbo-preview",
        temperature=1,
        presence_penalty=0,
        frequency_penalty=0,
        max_tokens=2000,
        messages=[
            {"role": "system", "content": f"{impersonated_role}. Conversation history: {chat_history}"},
            {"role": "user", "content": f"{user_input}. {explicit_input}"},
        ]
    )

    for item in output['choices']:
        chatgpt_output = item['message']['content']

    return chatgpt_output

# Function to handle user chat input
def chat(user_input):
    global chat_history, name, chatgpt_output
    current_day = time.strftime("%d/%m", time.localtime())
    current_time = time.strftime("%H:%M:%S", time.localtime())
  #  chat_history += f'\nUser: {user_input}\n'
    chatgpt_raw_output = chatcompletion2(user_input, impersonated_role, explicit_input, chat_history).replace(f'{name}:', '')
    chatgpt_output = f'{name}: {chatgpt_raw_output}'
  #  chat_history += chatgpt_output + '\n'
    with open(history_file, 'a') as f:
        f.write('\n'+ current_day+ ' '+ current_time+ ' User: ' +user_input +' \n' + current_day+ ' ' + current_time+  ' ' +  chatgpt_output + '\n')
        f.close()
    return chatgpt_raw_output

# Function to get a response from the chatbot
def get_response(userText):
    return chat(userText)

# Make the WSGI interface available at the top level so wfastcgi can get it.
wsgi_app = app.wsgi_app


@app.route('/')
def index():
    return render_template("index.html")

@app.route("/get")
# Function for the bot response
def get_bot_response():
    userText = request.args.get('msg')
    return str(get_response(userText))

@app.route('/refresh')
def refresh():
    time.sleep(600) # Wait for 10 minutes
    return redirect('/refresh')

# Run the Flask app
#if __name__ == "__main__":
#    app.run()

# def hello():
#     """Renders a sample page."""
#     return "Hello World!"

if __name__ == '__main__':
     import os
     HOST = os.environ.get('SERVER_HOST', 'localhost')
     try:
         PORT = int(os.environ.get('SERVER_PORT', '5555'))
     except ValueError:
         PORT = 5555
   #  app.run(HOST, PORT)
     app.run()

