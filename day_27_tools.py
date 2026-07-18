import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
ai_client = OpenAI()
api_key = os.getenv("OPENAI_API_KEY")

def calculate_take_home_pay(salary : int):
    print(f"Python is calculating tax for salary {salary}")
    tax = salary * 0.30
    take_home = salary - tax
    return f"Take home salary is {take_home}"

tools_menu = [
    {
        "type": "function",
        "function": {
            "name":"calculate_take_home_pay",
            "description": "Calculates the exact take-home pay after taxes for a given salary.",
            "parameters": {
                "type": "object",
                "properties":{
                    "salary": {
                        "type": "integer",
                        "description": "The gross annual salary in dollars"
                    }
                },
                "required": ["salary"]
            }
        }
    }
]

user_text = "If a candidate makes $120,000 a year, what is their exact take-home pay?"

def ai_call(user_prompt : str):
    try:
        response = ai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{
                "role":"user", "content": user_prompt,
            }],
            tools=tools_menu
        )
        if response.choices[0].message.tool_calls:
            tool_name = response.choices[0].message.tool_calls[0].function.name
            arguments = json.loads(response.choices[0].message.tool_calls[0].function.arguments)
            if tool_name == "calculate_take_home_pay":
                tool_result = calculate_take_home_pay(arguments["salary"])
                
                response2 = ai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "user", "content":user_prompt},
                        response.choices[0].message,
                        {"role":"tool",
                        "tool_call_id": response.choices[0].message.tool_calls[0].id,
                        "content": tool_result}
                        ])
                ai_said = response2.choices[0].message.content
                return ai_said
    except Exception as err:
        print(err)
    
print(ai_call(user_text))