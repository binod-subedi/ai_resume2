import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()

def calculate_take_home_pay(salary : int):
    print(f'AI is Calculating Takehome Pay for Salary {salary}')
    tax_amount = salary * 0.30
    takehome_pay = salary - tax_amount
    return f'Takehome Pay is {takehome_pay}'

def lookup_candidate_base_salary(user_name : str):
    db = {"binod":130000, "alice":95000}
    print(f'AI is looking up for your salary in the database.')
    return db.get(user_name.lower(),70000)

tools_menu = [
    {
        "type":"function",
        "function" : {
            "name" : "lookup_candidate_base_salary",
            "description": "Look up database to find the exact gross salary in dollars.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_name": {
                        "type":"string",
                        "description": "The name of the candidate to find the salry in database."
                    }
                },
                "required": ["user_name"]
            }
        },
    },
    {
        "type":"function",
        "function" : {
            "name" : "calculate_take_home_pay",
            "description": "Calculate the exact take-home pay after taxes for a given salary.",
            "parameters": {
                "type": "object",
                "properties": {
                    "salary": {
                        "type":"integer",
                        "description": "The gross annual salary in dollars."
                    }
                },
                "required": ["salary"]
            }
        },
    },
]

def orchestrate_agent(user_prompt):
    conversation_history = [{
        'role':'user',
        'content':user_prompt
    }]
    
    while True:
        response = client.chat.completions.create(
            model='gpt-4o-mini',
            messages=conversation_history,
            tools=tools_menu
        )
        ai_message = response.choices[0].message
        conversation_history.append(ai_message)
        
        if ai_message.content and not ai_message.tool_calls:
            return ai_message.content
        
        if ai_message.tool_calls:
            for tool in ai_message.tool_calls:
                tool_name = tool.function.name
                tool_call_id = tool.id
                argument = json.loads(tool.function.arguments)
                
                if tool_name == 'calculate_take_home_pay':
                    take_home_pay = calculate_take_home_pay(argument['salary'])
                    conversation_history.append({
                        "role":"tool",
                        "tool_call_id":tool_call_id,
                        "content":str(take_home_pay)
                    })
                    
                elif tool_name == 'lookup_candidate_base_salary':
                    salary_lookup= lookup_candidate_base_salary(argument['user_name'])
                    conversation_history.append({
                        "role":"tool",
                        "tool_call_id":tool_call_id,
                        "content":str(salary_lookup)
                    })

# complex_prompt = "What is Binod's take-home pay after taxes?" 
complex_prompt = "Look up Alice's salary. Then calculate her take-home pay if the tax rate suddenly became 43.725%. You must use the calculator tool for the math."
print(orchestrate_agent(complex_prompt))