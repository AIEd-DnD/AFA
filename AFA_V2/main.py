import yaml
import os
import sys
import openai
import resources as rsrc
import argparse
from dotenv import load_dotenv
from datetime import datetime
import json

# Update path to find .env in parent directory
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
load_dotenv(dotenv_path)
openai_api_key = os.getenv("OPENAI_API_KEY")
anthropic_key = os.getenv("ANTHROPIC_API_KEY")
client = openai.OpenAI(api_key=openai_api_key)
# Add parent directory to path so we can import modules from there
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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

def get_annotations_system_user(assembled_system_prompt, assembled_user_prompt, model="gpt-4o-2024-08-06"):
   if model.startswith("gpt"):  # Handle all OpenAI models
        response = client.chat.completions.create(
        model=model,
        temperature = 0.1,
        max_tokens = 16000,
        tools = rsrc.tools,
        tool_choice={"type": "function", "function": {"name": "get_annotated_feedback"}},
        messages = [{"role":"system","content":assembled_system_prompt},{"role": "user", "content": assembled_user_prompt}]
    )
        return response.choices[0].message.tool_calls[0].function.arguments
   elif model.startswith("claude"):
        import anthropic
        import json
        
        anthropic_client = anthropic.Anthropic(api_key=anthropic_key, timeout=360.0)
                
        # Build message content with images if available
        message_content = [
            {
                "type": "text",
                "text": assembled_system_prompt + assembled_user_prompt
            }
        ]
        
        # Claude expects a different tool format than OpenAI
        claude_tool = {
            "type": "custom",
            "name": "get_annotated_feedback",
            "description": "Use the provided list of error tags, suggested answer or rubrics to carefully analyze the student's response and return feedback in a list format with the properties required in a JSON object",
            "input_schema": {
                "type": "object",
                "properties": {
                  "annotated_response" : {
                    "type": "string",
                    "description": "The student's response with tags (using unique running number ids) enclosing specific words or phrases in the response. For example, 'The pig was <tag id=\"1\">fly</tag>. I <tag id=\"2\">is</tag> amazed."
                  },
                  "feedback_list": {
                    "type": "array",
                    "items": {
                      "type": "object",
                      "properties": {
                        "id": {
                          "type": "integer",
                          "description": "tag id"
                        },
                        "phrase": {
                          "type": "string",
                          "description": "the specific part of the sentence containing an error"
                        },
                        "error_tag": {
                          "type": "array",
                          "items": {
                            "type": "object",
                            "properties": {
                                "errorType": {
                                    "type": "string",
                                    "description": "error type"
                                }
                            }
                          },
                          "description": "list of concise error category based on error types"
                        },
                        "comment": {
                          "type": "string",
                          "description": "a concise student-friendly explanation or suggestion"
                        }
                      }
                    }
                  }
                },
                "required": [
                  "annotated_response","feedback_list"
                ]
            }
        }
        
        api_params = {
                    "model": model,
                    "max_tokens": 16000,  # Default token limit
                    "temperature": 0.1,
                    "tools": [claude_tool],
                    "messages": [
                        {
                            "role": "user",
                            "content": message_content
                        }
                    ],
                    "tool_choice": {"type": "auto"}
                }
        response = anthropic_client.messages.create(**api_params)
        
        # Extract the tool calls from Claude's response format
        for content in response.content:
            if content.type == 'tool_use':
                return content.input
                
        # Fallback if no tool use is found
        return "No tool use found in Claude's response"
   else:
        raise ValueError(f"Unsupported model: {model}. Please use an OpenAI or Claude model.")

def get_annotations_split_system(assembled_system_prompt, assembled_user_prompt, model="gpt-4o-2024-08-06"):
   """
   Makes two separate calls to generate feedback:
   1. First call generates just the feedback list
   2. Second call generates the annotated response using the feedback list from the first call
   """
   if model.startswith("gpt"):  # Handle all OpenAI models
        # First call: Generate feedback list
        response1 = client.chat.completions.create(
            model=model,
            temperature=0.1,
            max_tokens=16000,
            tools=rsrc.tools_feedback_list,
            tool_choice={"type": "function", "function": {"name": "get_feedback_list"}},
            messages=[
                {"role": "system", "content": rsrc.system_prompt_feedback_list.format(
                    Subject=assembled_system_prompt.split("Subject=")[1].split(",")[0] if "Subject=" in assembled_system_prompt else "",
                    Level=assembled_system_prompt.split("Level=")[1].split(",")[0] if "Level=" in assembled_system_prompt else "",
                    Question=assembled_system_prompt.split("Question=")[1].split(",")[0] if "Question=" in assembled_system_prompt else "",
                    Model_answer=assembled_system_prompt.split("Model_answer=")[1].split(",")[0] if "Model_answer=" in assembled_system_prompt else "",
                    Rubrics=assembled_system_prompt.split("Rubrics=")[1].split(",")[0] if "Rubrics=" in assembled_system_prompt else "",
                    Error_types=assembled_system_prompt.split("Error_types=")[1].split(",")[0] if "Error_types=" in assembled_system_prompt else "",
                    Instructions=assembled_system_prompt.split("Instructions=")[1] if "Instructions=" in assembled_system_prompt else ""
                )},
                {"role": "user", "content": assembled_user_prompt}
            ]
        )
        feedback_list_json = json.loads(response1.choices[0].message.tool_calls[0].function.arguments)
        feedback_list = feedback_list_json.get("feedback_list", [])
        
        # Second call: Generate annotated response
        response2 = client.chat.completions.create(
            model=model,
            temperature=0.1,
            max_tokens=16000,
            tools=rsrc.tools_annotated_response,
            tool_choice={"type": "function", "function": {"name": "get_annotated_response"}},
            messages=[
                {"role": "system", "content": rsrc.system_prompt_annotated_response},
                {"role": "user", "content": rsrc.user_prompt_annotated_response.format(
                    Students_response=assembled_user_prompt.split("Students_response=")[1] if "Students_response=" in assembled_user_prompt else assembled_user_prompt,
                    Feedback_list=json.dumps(feedback_list)
                )}
            ]
        )
        annotated_response_json = json.loads(response2.choices[0].message.tool_calls[0].function.arguments)
        annotated_response = annotated_response_json.get("annotated_response", "")
        
        # Validate tag count
        tag_count_in_response = annotated_response.count("<tag id=")
        if tag_count_in_response != len(feedback_list):
            print(f"Warning: Mismatch in tag count. Feedback list has {len(feedback_list)} items, but annotated response has {tag_count_in_response} tags.")
            # Could implement retry logic here if needed
        
        # Combine results
        result = {
            "annotated_response": annotated_response,
            "feedback_list": feedback_list
        }
        
        return json.dumps(result)
        
   elif model.startswith("claude"):
        import anthropic
        
        anthropic_client = anthropic.Anthropic(api_key=anthropic_key, timeout=360.0)
        
        # First call: Generate feedback list
        # Format the system prompt and user content for Claude which doesn't take system role
        system_content = rsrc.system_prompt_feedback_list.format(
            Subject=assembled_system_prompt.split("Subject=")[1].split(",")[0] if "Subject=" in assembled_system_prompt else "",
            Level=assembled_system_prompt.split("Level=")[1].split(",")[0] if "Level=" in assembled_system_prompt else "",
            Question=assembled_system_prompt.split("Question=")[1].split(",")[0] if "Question=" in assembled_system_prompt else "",
            Model_answer=assembled_system_prompt.split("Model_answer=")[1].split(",")[0] if "Model_answer=" in assembled_system_prompt else "",
            Rubrics=assembled_system_prompt.split("Rubrics=")[1].split(",")[0] if "Rubrics=" in assembled_system_prompt else "",
            Error_types=assembled_system_prompt.split("Error_types=")[1].split(",")[0] if "Error_types=" in assembled_system_prompt else "",
            Instructions=assembled_system_prompt.split("Instructions=")[1] if "Instructions=" in assembled_system_prompt else ""
        )
        
        message_content1 = [
            {
                "type": "text",
                "text": system_content + assembled_user_prompt
            }
        ]
        
        claude_tool1 = {
            "type": "custom",
            "name": "get_feedback_list",
            "description": "Generate a list of feedback items based on error analysis of the student's response",
            "input_schema": {
                "type": "object",
                "properties": {
                    "feedback_list": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {
                                    "type": "integer",
                                    "description": "tag id"
                                },
                                "phrase": {
                                    "type": "string",
                                    "description": "the specific part of the sentence containing an error"
                                },
                                "error_tag": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "errorType": {
                                                "type": "string",
                                                "description": "error type"
                                            }
                                        }
                                    },
                                    "description": "list of concise error category based on error types"
                                },
                                "comment": {
                                    "type": "string",
                                    "description": "a concise student-friendly explanation or suggestion"
                                }
                            }
                        }
                    }
                },
                "required": ["feedback_list"]
            }
        }
        
        api_params1 = {
            "model": model,
            "max_tokens": 16000,
            "temperature": 0.1,
            "tools": [claude_tool1],
            "messages": [
                {
                    "role": "user",
                    "content": message_content1
                }
            ],
            "tool_choice": {"type": "auto"}
        }
        
        response1 = anthropic_client.messages.create(**api_params1)
        
        feedback_list = None
        for content in response1.content:
            if content.type == 'tool_use':
                # Fix JSON parsing issue - check if input is already a dict or needs parsing
                tool_input = content.input
                if isinstance(tool_input, str):
                    feedback_list = json.loads(tool_input).get("feedback_list", [])
                elif isinstance(tool_input, dict):
                    feedback_list = tool_input.get("feedback_list", [])
                break
                
        if not feedback_list:
            return "No feedback list found in Claude's first response"
            
        # Second call: Generate annotated response
        students_response = assembled_user_prompt.split("Students_response=")[1] if "Students_response=" in assembled_user_prompt else assembled_user_prompt
        
        # For Claude, combine system and user content into a single user message
        system_and_user_content = rsrc.system_prompt_annotated_response + "\n\n" + rsrc.user_prompt_annotated_response.format(
            Students_response=students_response,
            Feedback_list=json.dumps(feedback_list)
        )
        
        message_content2 = [
            {
                "type": "text",
                "text": system_and_user_content
            }
        ]
        
        claude_tool2 = {
            "type": "custom",
            "name": "get_annotated_response",
            "description": "Apply annotation tags to a student response based on the provided feedback list",
            "input_schema": {
                "type": "object",
                "properties": {
                    "annotated_response": {
                        "type": "string",
                        "description": "The student's response with tags (using unique running number ids) enclosing specific words or phrases in the response"
                    }
                },
                "required": ["annotated_response"]
            }
        }
        
        api_params2 = {
            "model": model,
            "max_tokens": 16000,
            "temperature": 0.1,
            "tools": [claude_tool2],
            "messages": [
                {
                    "role": "user",
                    "content": message_content2
                }
            ],
            "tool_choice": {"type": "auto"}
        }
        
        response2 = anthropic_client.messages.create(**api_params2)
        
        annotated_response = None
        for content in response2.content:
            if content.type == 'tool_use':
                # Fix JSON parsing issue - check if input is already a dict or needs parsing
                tool_input = content.input
                if isinstance(tool_input, str):
                    annotated_response = json.loads(tool_input).get("annotated_response", "")
                elif isinstance(tool_input, dict):
                    annotated_response = tool_input.get("annotated_response", "")
                break
                
        if not annotated_response:
            return "No annotated response found in Claude's second response"
            
        # Validate tag count
        tag_count_in_response = annotated_response.count("<tag id=")
        if tag_count_in_response != len(feedback_list):
            print(f"Warning: Mismatch in tag count. Feedback list has {len(feedback_list)} items, but annotated response has {tag_count_in_response} tags.")
            # Could implement retry logic here if needed
        
        # Combine results
        result = {
            "annotated_response": annotated_response,
            "feedback_list": feedback_list
        }
        
        return json.dumps(result)
   else:
        raise ValueError(f"Unsupported model: {model}. Please use an OpenAI or Claude model.")

def get_annotations_split_reverse(assembled_system_prompt, assembled_user_prompt, model="gpt-4o-2024-08-06"):
   """
   Makes two separate calls to generate feedback in reverse order:
   1. First call generates the annotated response using error tags as a guide
   2. Second call generates the feedback list based on the annotations from the first call
   """
   if model.startswith("gpt"):  # Handle all OpenAI models
        # Extract the student response from the user prompt
        students_response = assembled_user_prompt.split("<Student's response>")[1].split("</Student's response>")[0].strip() if "<Student's response>" in assembled_user_prompt else assembled_user_prompt
        
        # First call: Generate annotated response using error tags as guide
        response1 = client.chat.completions.create(
            model=model,
            temperature=0.1,
            max_tokens=16000,
            tools=rsrc.tools_annotated_response,
            tool_choice={"type": "function", "function": {"name": "get_annotated_response"}},
            messages=[
                {"role": "system", "content": rsrc.system_prompt_annotated_response},
                {"role": "user", "content": f"""
                Here is the student's response that needs to be annotated:
                {students_response}
                
                Use the error types from the following list to guide your annotation:
                {assembled_system_prompt.split("Error list: ")[1].split("Additional Error type instructions")[0] if "Error list: " in assembled_system_prompt else ""}
                
                Please annotate the student's response by identifying errors and inserting tags around problematic phrases.
                <task>
                Analyze the student's response and identify errors based on the error types provided.
                Insert tags around phrases that contain errors: <tag id="1">error phrase</tag>
                Use ascending ID numbers starting from 1 for each tag.
                Return the student's response exactly as it is, with only the tags inserted.
                </task>
                """}
            ]
        )
        annotated_response_json = json.loads(response1.choices[0].message.tool_calls[0].function.arguments)
        annotated_response = annotated_response_json.get("annotated_response", "")
        
        # Count the tags to determine how many errors were identified
        tag_ids = []
        current_pos = 0
        while True:
            tag_start = annotated_response.find('<tag id="', current_pos)
            if tag_start == -1:
                break
            id_start = tag_start + 9  # Length of '<tag id="'
            id_end = annotated_response.find('"', id_start)
            tag_id = annotated_response[id_start:id_end]
            tag_ids.append(tag_id)
            current_pos = id_end
        
        # Extract the tagged phrases
        tagged_phrases = []
        for tag_id in tag_ids:
            tag_start = annotated_response.find(f'<tag id="{tag_id}">')
            content_start = tag_start + len(f'<tag id="{tag_id}">')
            content_end = annotated_response.find('</tag>', content_start)
            phrase = annotated_response[content_start:content_end]
            tagged_phrases.append({"id": int(tag_id), "phrase": phrase})
        
        # Second call: Generate feedback list based on the annotated response
        response2 = client.chat.completions.create(
            model=model,
            temperature=0.1,
            max_tokens=16000,
            tools=rsrc.tools_feedback_list,
            tool_choice={"type": "function", "function": {"name": "get_feedback_list"}},
            messages=[
                {"role": "system", "content": rsrc.system_prompt_feedback_list.format(
                    Subject=assembled_system_prompt.split("Subject=")[1].split(",")[0] if "Subject=" in assembled_system_prompt else "",
                    Level=assembled_system_prompt.split("Level=")[1].split(",")[0] if "Level=" in assembled_system_prompt else "",
                    Question=assembled_system_prompt.split("Question=")[1].split(",")[0] if "Question=" in assembled_system_prompt else "",
                    Model_answer=assembled_system_prompt.split("Model_answer=")[1].split(",")[0] if "Model_answer=" in assembled_system_prompt else "",
                    Rubrics=assembled_system_prompt.split("Rubrics=")[1].split(",")[0] if "Rubrics=" in assembled_system_prompt else "",
                    Error_types=assembled_system_prompt.split("Error_types=")[1].split(",")[0] if "Error_types=" in assembled_system_prompt else "",
                    Instructions=assembled_system_prompt.split("Instructions=")[1] if "Instructions=" in assembled_system_prompt else ""
                )},
                {"role": "user", "content": f"""
                This is the student's response: <Student's response> {students_response} </Student's response>
                
                I have already identified the following errors in the student's response:
                {json.dumps(tagged_phrases)}
                
                For each identified error, provide an appropriate error type and a concise, student-friendly comment.
                """} 
            ]
        )
        feedback_list_json = json.loads(response2.choices[0].message.tool_calls[0].function.arguments)
        feedback_list = feedback_list_json.get("feedback_list", [])
        
        # Validate tag count
        if len(feedback_list) != len(tagged_phrases):
            print(f"Warning: Mismatch in feedback count. Tagged phrases: {len(tagged_phrases)}, feedback items: {len(feedback_list)}")
            # Could implement adjustment logic here if needed
        
        # Combine results
        result = {
            "annotated_response": annotated_response,
            "feedback_list": feedback_list
        }
        
        return json.dumps(result)
        
   elif model.startswith("claude"):
        import anthropic
        
        anthropic_client = anthropic.Anthropic(api_key=anthropic_key, timeout=360.0)
        
        # Extract the student response from the user prompt
        students_response = assembled_user_prompt.split("<Student's response>")[1].split("</Student's response>")[0].strip() if "<Student's response>" in assembled_user_prompt else assembled_user_prompt
        
        # First call: Generate annotated response using error tags as guide
        error_types = assembled_system_prompt.split("Error list: ")[1].split("Additional Error type instructions")[0] if "Error list: " in assembled_system_prompt else ""
        
        # For Claude, combine system and user content into a single user message
        system_and_user_content = rsrc.system_prompt_annotated_response + "\n\n" + f"""
        Here is the student's response that needs to be annotated:
        {students_response}
        
        Use the error types from the following list to guide your annotation:
        {error_types}
        
        Please annotate the student's response by identifying errors and inserting tags around problematic phrases.
        <task>
        Analyze the student's response and identify errors based on the error types provided.
        Insert tags around phrases that contain errors: <tag id="1">error phrase</tag>
        Use ascending ID numbers starting from 1 for each tag.
        Return the student's response exactly as it is, with only the tags inserted.
        </task>
        """
        
        message_content1 = [
            {
                "type": "text",
                "text": system_and_user_content
            }
        ]
        
        claude_tool1 = {
            "type": "custom",
            "name": "get_annotated_response",
            "description": "Apply annotation tags to a student response based on provided error types",
            "input_schema": {
                "type": "object",
                "properties": {
                    "annotated_response": {
                        "type": "string",
                        "description": "The student's response with tags (using unique running number ids) enclosing specific words or phrases in the response"
                    }
                },
                "required": ["annotated_response"]
            }
        }
        
        api_params1 = {
            "model": model,
            "max_tokens": 16000,
            "temperature": 0.1,
            "tools": [claude_tool1],
            "messages": [
                {
                    "role": "user",
                    "content": message_content1
                }
            ],
            "tool_choice": {"type": "auto"}
        }
        
        response1 = anthropic_client.messages.create(**api_params1)
        
        annotated_response = None
        for content in response1.content:
            if content.type == 'tool_use':
                # Fix JSON parsing issue - check if input is already a dict or needs parsing
                tool_input = content.input
                if isinstance(tool_input, str):
                    annotated_response = json.loads(tool_input).get("annotated_response", "")
                elif isinstance(tool_input, dict):
                    annotated_response = tool_input.get("annotated_response", "")
                break
                
        if not annotated_response:
            return "No annotated response found in Claude's first response"
        
        # Extract the tagged phrases
        tag_ids = []
        current_pos = 0
        while True:
            tag_start = annotated_response.find('<tag id="', current_pos)
            if tag_start == -1:
                break
            id_start = tag_start + 9  # Length of '<tag id="'
            id_end = annotated_response.find('"', id_start)
            tag_id = annotated_response[id_start:id_end]
            tag_ids.append(tag_id)
            current_pos = id_end
        
        tagged_phrases = []
        for tag_id in tag_ids:
            tag_start = annotated_response.find(f'<tag id="{tag_id}">')
            content_start = tag_start + len(f'<tag id="{tag_id}">')
            content_end = annotated_response.find('</tag>', content_start)
            phrase = annotated_response[content_start:content_end]
            tagged_phrases.append({"id": int(tag_id), "phrase": phrase})
        
        # Second call: Generate feedback list based on the annotated response
        system_content = rsrc.system_prompt_feedback_list.format(
            Subject=assembled_system_prompt.split("Subject=")[1].split(",")[0] if "Subject=" in assembled_system_prompt else "",
            Level=assembled_system_prompt.split("Level=")[1].split(",")[0] if "Level=" in assembled_system_prompt else "",
            Question=assembled_system_prompt.split("Question=")[1].split(",")[0] if "Question=" in assembled_system_prompt else "",
            Model_answer=assembled_system_prompt.split("Model_answer=")[1].split(",")[0] if "Model_answer=" in assembled_system_prompt else "",
            Rubrics=assembled_system_prompt.split("Rubrics=")[1].split(",")[0] if "Rubrics=" in assembled_system_prompt else "",
            Error_types=assembled_system_prompt.split("Error_types=")[1].split(",")[0] if "Error_types=" in assembled_system_prompt else "",
            Instructions=assembled_system_prompt.split("Instructions=")[1] if "Instructions=" in assembled_system_prompt else ""
        )
        
        user_content = f"""
        This is the student's response: <Student's response> {students_response} </Student's response>
        
        I have already identified the following errors in the student's response:
        {json.dumps(tagged_phrases)}
        
        For each identified error, provide an appropriate error type and a concise, student-friendly comment.
        """
        
        message_content2 = [
            {
                "type": "text",
                "text": system_content + "\n\n" + user_content
            }
        ]
        
        claude_tool2 = {
            "type": "custom",
            "name": "get_feedback_list",
            "description": "Generate a list of feedback items based on pre-identified errors in the student's response",
            "input_schema": {
                "type": "object",
                "properties": {
                    "feedback_list": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {
                                    "type": "integer",
                                    "description": "tag id"
                                },
                                "phrase": {
                                    "type": "string",
                                    "description": "the specific part of the sentence containing an error"
                                },
                                "error_tag": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "errorType": {
                                                "type": "string",
                                                "description": "error type"
                                            }
                                        }
                                    },
                                    "description": "list of concise error category based on error types"
                                },
                                "comment": {
                                    "type": "string",
                                    "description": "a concise student-friendly explanation or suggestion"
                                }
                            }
                        }
                    }
                },
                "required": ["feedback_list"]
            }
        }
        
        api_params2 = {
            "model": model,
            "max_tokens": 16000,
            "temperature": 0.1,
            "tools": [claude_tool2],
            "messages": [
                {
                    "role": "user",
                    "content": message_content2
                }
            ],
            "tool_choice": {"type": "auto"}
        }
        
        response2 = anthropic_client.messages.create(**api_params2)
        
        feedback_list = None
        for content in response2.content:
            if content.type == 'tool_use':
                # Fix JSON parsing issue - check if input is already a dict or needs parsing
                tool_input = content.input
                if isinstance(tool_input, str):
                    feedback_list = json.loads(tool_input).get("feedback_list", [])
                elif isinstance(tool_input, dict):
                    feedback_list = tool_input.get("feedback_list", [])
                break
                
        if not feedback_list:
            return "No feedback list found in Claude's second response"
        
        # Validate tag count
        if len(feedback_list) != len(tagged_phrases):
            print(f"Warning: Mismatch in feedback count. Tagged phrases: {len(tagged_phrases)}, feedback items: {len(feedback_list)}")
            # Could implement adjustment logic here if needed
        
        # Combine results
        result = {
            "annotated_response": annotated_response,
            "feedback_list": feedback_list
        }
        
        return json.dumps(result)
   else:
        raise ValueError(f"Unsupported model: {model}. Please use an OpenAI or Claude model.")

def load_yaml_data(file_path):
    """Load data from a YAML file."""
    with open(file_path, 'r', encoding='utf-8') as file:
        data = yaml.safe_load(file)
    return data

def get_data_file_path():
    """Gets the correct path to data.yaml regardless of where the script is run from"""
    # Get the directory containing the current script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Check if we're in AFA_V2 directory or parent directory
    if os.path.basename(current_dir) == 'AFA_V2':
        return os.path.join(current_dir, 'data.yaml')
    else:
        return os.path.join(current_dir, 'AFA_V2', 'data.yaml')

def main():
    """Main function to load and analyze YAML data."""
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Analyze student responses with AI feedback')
    parser.add_argument('-c', '--claude', action='store_true', help='Use Claude model for analysis')
    parser.add_argument('-g4o', '--gpt4o', action='store_true', help='Use GPT-4o model for analysis (default)')
    parser.add_argument('-g41', '--gpt41', action='store_true', help='Use GPT-4.1 model for analysis')
    parser.add_argument('-m', '--model', help='Specify a specific model name')
    parser.add_argument('-s', '--split', action='store_true', help='Use split system for generating annotations')
    parser.add_argument('-r', '--reverse', action='store_true', help='Use reverse order for split system')
    args = parser.parse_args()
    
    # Determine which model to use
    model = "gpt-4o-2024-08-06"  # Default model
    if args.claude:
        model = "claude-3-7-sonnet-20250219"
    if args.gpt41:
        model = "gpt-4.1-2025-04-14"
    if args.model:
        model = args.model  # Override with specific model if provided

    # Get the correct path to the data file
    data_file_path = get_data_file_path()
    #to load yaml data, use the following function:
    data = load_yaml_data(data_file_path)
    subject = data['education_context']['subject']
    level = data['education_context']['level']
    question = data['education_context']['questions']['english']
    # Assuming these fields exist in your YAML, if not you'll need to adjust the paths
    error_tags_list = data['response_data']['el_error_tags']
    error_tags_str = ", ".join([f"{tag['type']} - {tag['description']}" for tag in error_tags_list])
    el_response = data['response_data']['el_sample_answer_1']
    try:
        system_msg = assemble_system_prompt(subject, level, question, error_tags=error_tags_str)
        user_msg = assemble_user_prompt(el_response)
        
        if args.split and args.reverse:
            response = get_annotations_split_reverse(system_msg, user_msg, model=model)
        elif args.split:
            response = get_annotations_split_system(system_msg, user_msg, model=model)
        else:
            response = get_annotations_system_user(system_msg, user_msg, model=model)
            
        print(response)
         
    except FileNotFoundError:
        print(f"Error: The file {data_file_path} was not found.")
    except yaml.YAMLError as e:
        print(f"Error parsing the YAML file: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
