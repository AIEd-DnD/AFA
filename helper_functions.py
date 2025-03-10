import streamlit as st
import openai
import resources as rsrc
import os
import json
from dotenv import load_dotenv

load_dotenv('.env')
openai_api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=openai_api_key)


# Function to create final prompt with error list & student text
def create_prompt(errors_dict, suggested_answer, student_input):
    # Convert error_dict into a formatted string
    formatted_error_list = '\n'.join([f'"{key}": "{value["description"]}"' for key, value in errors_dict.items()])

    prompt = f"""
    You are a diligent teacher identifying errors in students' responses to give them feedback.
    Your objective is to evaluate the following response and provide feedback.
    To help you evaluate, you are given the following:

    Teacher's model answer: {suggested_answer}
    Here is the error list for your reference:
    {formatted_error_list}
    
    Give your response in the format below. 
 Return a dictionary with three keys:
 1. "phrase containing error" - the specific part of the sentence containing an error.
 2. "error tag" - a concise error category based on formatted_error_list
 3. "feedback" - a concise student-friendly explanation or suggestion


Example response:
 [
 {{
     "phrase containing error": "phrase",
     "error tag": "error tag",
     "feedback": "feedback for student"
 }},
 {{
     "phrase containing error": "phrase",
     "error tag": "error tag",
     "feedback": "feedback for student"
 }},
 ]
  Read the response carefully and understand the surrounding context to avoid raising false errors. For more than 1 error, make sure you list all errors in the list in the order they appear in the student input.
  If there are no errors, respond with an empty response.

 Student response: {student_input}
    """

    return prompt

#openai.api_key = st.secrets["api"]["key"]
def get_completion(prompt, model="gpt-4o-mini", temperature=0):
 messages = [{"role": "user", "content": prompt}]
 response = openai.chat.completions.create( #originally was openai.chat.completions
     model=model,
     messages=messages,
     temperature=temperature,
 )
 return response.choices[0].message.content

#Norman's function to assemble prompt
def assemble_prompt(subject, level, question, student_answer, recipe=rsrc.recipes["Default"], suggested_answer=" ", rubrics=" ", error_tags=" "):
   assembled_prompt = rsrc.base_prompt.format(
     Subject=subject,
     Level=level,
     Question=question,
     Model_answer=suggested_answer, 
     Rubrics=rubrics, 
     Error_types=error_tags, 
     Instructions=recipe,
     Students_response=student_answer,
     #feedback_list_eg=feedback_list,
     #standard_response=standard,
     #no_error_response=no_errors
     )
   
   return assembled_prompt
   
#Norman's function to send to LLM to get annotations
def get_annotations(assembled_prompt):
   response = client.chat.completions.create(
     model="gpt-4o-2024-08-06",
     temperature = 0.1,
     max_tokens = 4000,
     tools = rsrc.tools,
     messages = [{"role": "user", "content": assembled_prompt}]
   )
   return response.choices[0].message.tool_calls[0].function.arguments

#Norman's function to convert get_annotations output into python dictionary
def display_output(json_response):
   response_dict = json.loads(json_response)
   print("Annotated Response: ")
   print(response_dict["annotated_response"])
   print(" ")
   #for annotation in response_dict["feedback_list"]:
     #print("Annotation no. " + str(annotation["id"]))
     #print("Annotated phrase: " + annotation["phrase"])
     #print("Error Tag: " + annotation["error_tag"][0]["errorType"])
     #print("Feedback: " + annotation["comment"])
     #print(" ")
