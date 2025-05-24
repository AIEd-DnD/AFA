import openai
import testbed_resources as rsrc
import ast
import os
import csv
from dotenv import load_dotenv
from datetime import datetime

load_dotenv('.env')
openai_api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=openai_api_key)

#These functions write the results to a csv file
def start_new_record(file_name):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"Records/AFA_{file_name}_{timestamp}.csv"
    return filename

def write_into_record_refinement(filename, data):
    header = ['Subject','Level','Recipe','Error Tags','Suggested Answer','Rubrics','Question','Student Response','LLM Annotated Response','LLM Cards','Tagged?','Number of Cards']
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerows(data)
    print(f"CSV file '{filename}' has been created successfully.")

def write_into_record_refinement_SA(filename, data):
    header = ['Subject','Level','Recipe','Suggested Answer','Question','Student Response','LLM Annotated Response','LLM Cards','Tagged?','Number of Cards']
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerows(data)
    print(f"CSV file '{filename}' has been created successfully.")

def write_into_record_refinement_Rubrics(filename, data):
    header = ['Subject','Level','Recipe','Rubrics','Question','Student Response','LLM Annotated Response','LLM Cards','Tagged?','Number of Cards']
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerows(data)
    print(f"CSV file '{filename}' has been created successfully.")

def write_into_record_refinement_Error_tags(filename, data):
    header = ['Subject','Level','Recipe','Error Tags','Question','Student Response','LLM Annotated Response','LLM Cards','Tagged?','Number of Cards']
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerows(data)
    print(f"CSV file '{filename}' has been created successfully.")

#These functions extract the parameters from the csv file
def csv_to_list_of_dicts(file_path):
    result = list()
    with open(file_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            result.append(row)
    return result

def extract_parameters_refinement(parameter_dict):
    subject = parameter_dict['subject']
    level = parameter_dict['level']
    question = parameter_dict['question']
    students_response = parameter_dict['students_response']
    recipe = parameter_dict['recipe']
    suggested_answer = parameter_dict['suggested_answer'] 
    rubrics = parameter_dict['rubrics']
    error_tags = parameter_dict['error_tags']
    return subject, level, question, students_response, recipe, suggested_answer, rubrics, error_tags

def extract_parameters_refinement_SA(parameter_dict):
    subject = parameter_dict['subject']
    level = parameter_dict['level']
    question = parameter_dict['question']
    students_response = parameter_dict['students_response']
    recipe = parameter_dict['recipe']
    suggested_answer = parameter_dict['suggested_answer'] 
    return subject, level, question, students_response, recipe, suggested_answer

def extract_parameters_refinement_Rubrics(parameter_dict):
    subject = parameter_dict['subject']
    level = parameter_dict['level']
    question = parameter_dict['question']
    students_response = parameter_dict['students_response']
    recipe = parameter_dict['recipe']
    rubrics = parameter_dict['rubrics']
    return subject, level, question, students_response, recipe, rubrics

def extract_parameters_refinement_Error_tags(parameter_dict):
    subject = parameter_dict['subject']
    level = parameter_dict['level']
    question = parameter_dict['question']
    students_response = parameter_dict['students_response']
    recipe = parameter_dict['recipe']
    error_tags = parameter_dict['error_tags']
    return subject, level, question, students_response, recipe, error_tags

# These fuctions assemble the prompts to be sent to the LLM
def assemble_system_prompt(subject, level, question, recipe=" ", suggested_answer=" ", rubrics=" ", error_tags=" "):
   assembled_system_prompt = rsrc.system_prompt.format(
     Subject=subject,
     Level=level,
     Question=question,
     Model_answer=suggested_answer, 
     Rubrics=rubrics, 
     Error_types=error_tags, 
     Instructions=recipe
     )
   return assembled_system_prompt

def assemble_user_prompt(students_response):
   assembled_user_prompt = rsrc.user_prompt.format(
     Students_response=students_response 
     )
   return assembled_user_prompt

def assemble_prompt_SA(subject, level, question, students_response, recipe=" ", suggested_answer=" "):
   assembled_prompt = rsrc.user_prompt_SA.format(
     Subject=subject,
     Level=level,
     Question=question,
     Model_answer=suggested_answer, 
     Instructions=recipe,
     Students_response=students_response 
     )
   
   return assembled_prompt

def assemble_prompt_Rubrics(subject, level, question, students_response, recipe=" ", rubrics=" "):
   assembled_prompt = rsrc.user_prompt_Rubrics.format(
     Subject=subject,
     Level=level,
     Question=question,
     Rubrics=rubrics, 
     Instructions=recipe,
     Students_response=students_response 
     )
   
   return assembled_prompt

def assemble_prompt_Error_tags(subject, level, question, students_response, recipe=" ", error_tags=" "):
   assembled_prompt = rsrc.user_prompt_Error_tags.format(
     Subject=subject,
     Level=level,
     Question=question,
     Error_types=error_tags, 
     Instructions=recipe,
     Students_response=students_response 
     )
   
   return assembled_prompt

#These functions send to LLM and extract the response in JSON string format
def get_annotations(assembled_prompt):
   response = client.chat.completions.create(
     model="gpt-4o-2024-08-06",
     temperature = 0.1, #temperature is only available to gpt models
     max_tokens = 4000, #max tokens is only available to gpt models, default max tokens is 4000. this parameter is being deprecated in favour of max_completion_tokens
     tools = rsrc.tools,
     tool_choice={"type": "function", "function": {"name": "get_annotated_feedback"}},
     messages = [{"role": "user", "content": assembled_prompt}]
   )
   return response.choices[0].message.tool_calls[0].function.arguments

def get_annotations_system_user(assembled_system_prompt, assembled_user_prompt):
   response = client.chat.completions.create(
     model="gpt-4o-2024-08-06",
     temperature = 0.1, #temperature is only available to gpt models
     max_tokens = 16000, #max tokens is only available to gpt models, default max tokens is 4000. this parameter is being deprecated in favour of max_completion_tokens
     tools = rsrc.tools,
     tool_choice={"type": "function", "function": {"name": "get_annotated_feedback"}},
     messages = [{"role":"system","content":assembled_system_prompt},{"role": "user", "content": assembled_user_prompt}]
   )
   return response.choices[0].message.tool_calls[0].function.arguments

def string_to_dict(dict_string):
    try:
        return ast.literal_eval(dict_string)
    except (ValueError, SyntaxError):
        raise ValueError("Invalid dictionary string format")
    
def extract_annotation_details_refinement(LLM_dict):
    LLM_annotated_response = LLM_dict['annotated_response']
    LLM_cards = LLM_dict['feedback_list']
    return LLM_annotated_response, LLM_cards