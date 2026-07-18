# Code will break for second tool as it is not implementing the architecture for tool with dependency on first tool outcome 
import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()

def calculate_take_home_pay(salary : int):
    print(f"Python is calculating tax for salary {salary}")
    tax = salary * 0.30
    take_home = salary - tax
    return f"Take home salary is {take_home}"

def lookup_candidate_base_salary(name : str):
    #Fake Data(this will come from database later)
    db = {"binod":130000, "alice":95000}
    print(f"[SYSTEM] Database looking up salary for: '{name}'...")
    return db.get(name.lower(), 70000)

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

def orchestrate_agent(user_prompt: str):
    
    initial_api_call = client.chat.completions.create(
        model= 'gpt-4o-mini',
        messages=[{"role":"user", "content":user_prompt}],
        tools=tools_menu
    )
    
    if initial_api_call.choices[0].message.tool_calls:
        conversation_history = [{
            "role":"user", "content":user_prompt
        },
        initial_api_call.choices[0].message]
        
        for tool_call in initial_api_call.choices[0].message.tool_calls:
            tool_name = tool_call.function.name
            tool_call_id = tool_call.id
            arguments = json.loads(tool_call.function.arguments)
            
            if tool_name == "lookup_candidate_base_salary":
                salary_lookup = lookup_candidate_base_salary(arguments['user_name'])
                conversation_history.append({"role":"tool",
                        "tool_call_id":tool_call_id,
                        "content":str(salary_lookup)})
                
            elif tool_name == "calculate_take_home_pay":
                tax_lookup = calculate_take_home_pay(arguments['salary'])
                conversation_history.append({"role":"tool",
                        "tool_call_id":tool_call_id,
                        "content":str(tax_lookup)})
        
        second_api_call = client.chat.completions.create(
            model='gpt-4o-mini',
            messages=conversation_history,
        )
        final_response = second_api_call.choices[0].message.content
        return final_response
complex_prompt = "What is Binod's take-home pay after taxes?"
salary = orchestrate_agent(complex_prompt)
print(salary)