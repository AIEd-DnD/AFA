import yaml
import os
import sys
import openai
import resources as rsrc
import csv
import json
import argparse
from dotenv import load_dotenv
from datetime import datetime
import concurrent.futures

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
        
        # Parse the response to get annotated response and feedback list for tag count validation
        arguments = response.choices[0].message.tool_calls[0].function.arguments
        try:
            parsed = json.loads(arguments)
            annotated_response = parsed.get("annotated_response", "")
            feedback_list = parsed.get("feedback_list", [])
            
            # Check for tag count mismatch
            tag_count = annotated_response.count("<tag id=")
            if tag_count != len(feedback_list):
                # Add warning to the response
                parsed["warning"] = f"Mismatch in tag count. Feedback list has {len(feedback_list)} items, but annotated response has {tag_count} tags."
                arguments = json.dumps(parsed)
        except Exception:
            # If there's an error parsing, just return the original arguments
            pass
            
        return arguments
        
   elif model.startswith("claude"):
        import anthropic
        
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
                # Get the tool input
                tool_input = content.input
                
                # Process tool input
                if isinstance(tool_input, dict):
                    annotated_response = tool_input.get("annotated_response", "")
                    feedback_list = tool_input.get("feedback_list", [])
                    
                    # Check for tag count mismatch
                    tag_count = annotated_response.count("<tag id=")
                    if tag_count != len(feedback_list):
                        tool_input["warning"] = f"Mismatch in tag count. Feedback list has {len(feedback_list)} items, but annotated response has {tag_count} tags."
                    
                    return tool_input
                elif isinstance(tool_input, str):
                    try:
                        parsed = json.loads(tool_input)
                        annotated_response = parsed.get("annotated_response", "")
                        feedback_list = parsed.get("feedback_list", [])
                        
                        # Check for tag count mismatch
                        tag_count = annotated_response.count("<tag id=")
                        if tag_count != len(feedback_list):
                            parsed["warning"] = f"Mismatch in tag count. Feedback list has {len(feedback_list)} items, but annotated response has {tag_count} tags."
                            return json.dumps(parsed)
                    except Exception:
                        # If there's an error parsing, just return the original string
                        pass
                
                return tool_input
                
        # Fallback if no tool use is found
        return json.dumps({"error": "No tool use found in Claude's response"})
   else:
        raise ValueError(f"Unsupported model: {model}. Please use an OpenAI or Claude model.")

def get_annotations_split_system(assembled_system_prompt, assembled_user_prompt, model="gpt-4o-2024-08-06", raw_student_response=None):
   """
   Makes two separate calls to generate feedback:
   1. First call generates just the feedback list
   2. Second call generates the annotated response using the feedback list from the first call
   
   Args:
       assembled_system_prompt: The formatted system prompt
       assembled_user_prompt: The formatted user prompt for the first API call
       model: The model name to use
       raw_student_response: The original student response text from the CSV
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
        
        # Second call: Generate annotated response with RAW student response
        response2 = client.chat.completions.create(
            model=model,
            temperature=0.1,
            max_tokens=16000,
            tools=rsrc.tools_annotated_response,
            tool_choice={"type": "function", "function": {"name": "get_annotated_response"}},
            messages=[
                {"role": "system", "content": rsrc.system_prompt_annotated_response},
                {"role": "user", "content": rsrc.user_prompt_annotated_response.format(
                    Students_response=raw_student_response,
                    Feedback_list=json.dumps(feedback_list)
                )}
            ]
        )
        annotated_response_json = json.loads(response2.choices[0].message.tool_calls[0].function.arguments)
        annotated_response = annotated_response_json.get("annotated_response", "")
        
        # Validate tag count
        tag_count_in_response = annotated_response.count("<tag id=")
        if tag_count_in_response != len(feedback_list):
            warning_msg = f"Mismatch in tag count. Feedback list has {len(feedback_list)} items, but annotated response has {tag_count_in_response} tags."
            print(f"Warning: {warning_msg}")
            # Add warning to result
            result = {
                "annotated_response": annotated_response,
                "feedback_list": feedback_list,
                "warning": warning_msg
            }
        else:
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
                # Get the tool input and extract feedback list
                tool_input = content.input
                if isinstance(tool_input, str):
                    try:
                        feedback_list = json.loads(tool_input).get("feedback_list", [])
                    except json.JSONDecodeError:
                        return json.dumps({"error": "Failed to parse feedback list from Claude's response"})
                elif isinstance(tool_input, dict):
                    feedback_list = tool_input.get("feedback_list", [])
                break
                
        if not feedback_list:
            return json.dumps({"error": "No feedback list found in Claude's first response"})
            
        # For Claude, combine system and user content into a single user message
        # Using the original student response directly from CSV for annotation
        system_and_user_content = rsrc.system_prompt_annotated_response + "\n\n" + rsrc.user_prompt_annotated_response.format(
            Students_response=raw_student_response,
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
                # Get the annotated response
                tool_input = content.input
                if isinstance(tool_input, str):
                    try:
                        annotated_response = json.loads(tool_input).get("annotated_response", "")
                    except json.JSONDecodeError:
                        return json.dumps({"error": "Failed to parse annotated response from Claude's response"})
                elif isinstance(tool_input, dict):
                    annotated_response = tool_input.get("annotated_response", "")
                break
                
        if not annotated_response:
            return json.dumps({"error": "No annotated response found in Claude's second response"})
            
        # Validate tag count
        tag_count_in_response = annotated_response.count("<tag id=")
        if tag_count_in_response != len(feedback_list):
            warning_msg = f"Mismatch in tag count. Feedback list has {len(feedback_list)} items, but annotated response has {tag_count_in_response} tags."
            print(f"Warning: {warning_msg}")
            # Add warning to result
            result = {
                "annotated_response": annotated_response,
                "feedback_list": feedback_list,
                "warning": warning_msg
            }
        else:
            # Combine results
            result = {
                "annotated_response": annotated_response,
                "feedback_list": feedback_list
            }
        
        return json.dumps(result)
   else:
        raise ValueError(f"Unsupported model: {model}. Please use an OpenAI or Claude model.")

def get_annotations_split_reverse(assembled_system_prompt, assembled_user_prompt, model="gpt-4o-2024-08-06", raw_student_response=None):
   """
   Makes two separate calls to generate feedback in reverse order:
   1. First call generates the annotated response using error tags as a guide
   2. Second call generates the feedback list based on the annotations from the first call
   
   Args:
       assembled_system_prompt: The formatted system prompt
       assembled_user_prompt: The formatted user prompt for the first API call
       model: The model name to use
       raw_student_response: The original student response text from the CSV
   """
   if model.startswith("gpt"):  # Handle all OpenAI models
        # Extract the student response from the user prompt if raw_student_response is not provided
        students_response = raw_student_response or (assembled_user_prompt.split("<Student's response>")[1].split("</Student's response>")[0].strip() 
                                                   if "<Student's response>" in assembled_user_prompt 
                                                   else assembled_user_prompt)
        
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
                
                I have identified EXACTLY {len(tagged_phrases)} errors in the student's response.
                Here are all the errors I've identified:
                {json.dumps(tagged_phrases)}
                
                You MUST provide EXACTLY {len(tagged_phrases)} feedback items - one for each identified error.
                """} 
            ]
        )
        feedback_list_json = json.loads(response2.choices[0].message.tool_calls[0].function.arguments)
        feedback_list = feedback_list_json.get("feedback_list", [])
        
        # Validate tag count
        if len(feedback_list) != len(tagged_phrases):
            warning_msg = f"Mismatch in feedback count. Tagged phrases: {len(tagged_phrases)}, feedback items: {len(feedback_list)}"
            print(f"Warning: {warning_msg}")
            # Add warning to result
            result = {
                "annotated_response": annotated_response,
                "feedback_list": feedback_list,
                "warning": warning_msg
            }
        else:
            # Combine results
            result = {
                "annotated_response": annotated_response,
                "feedback_list": feedback_list
            }
        
        return json.dumps(result)
        
   elif model.startswith("claude"):
        import anthropic
        
        anthropic_client = anthropic.Anthropic(api_key=anthropic_key, timeout=360.0)
        
        # Extract the student response from the user prompt if raw_student_response is not provided
        students_response = raw_student_response or (assembled_user_prompt.split("<Student's response>")[1].split("</Student's response>")[0].strip() 
                                                   if "<Student's response>" in assembled_user_prompt 
                                                   else assembled_user_prompt)
        
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
                    try:
                        annotated_response = json.loads(tool_input).get("annotated_response", "")
                    except json.JSONDecodeError:
                        return json.dumps({"error": "Failed to parse annotated response from Claude's response"})
                elif isinstance(tool_input, dict):
                    annotated_response = tool_input.get("annotated_response", "")
                break
                
        if not annotated_response:
            return json.dumps({"error": "No annotated response found in Claude's first response"})
        
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
        
        I have identified EXACTLY {len(tagged_phrases)} errors in the student's response.
        Here are all the errors I've identified:
        {json.dumps(tagged_phrases)}
        
        You MUST provide EXACTLY {len(tagged_phrases)} feedback items - one for each identified error.
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
                    try:
                        feedback_list = json.loads(tool_input).get("feedback_list", [])
                    except json.JSONDecodeError:
                        return json.dumps({"error": "Failed to parse feedback list from Claude's response"})
                elif isinstance(tool_input, dict):
                    feedback_list = tool_input.get("feedback_list", [])
                break
                
        if not feedback_list:
            return json.dumps({"error": "No feedback list found in Claude's second response"})
        
        # Validate tag count
        if len(feedback_list) != len(tagged_phrases):
            warning_msg = f"Mismatch in feedback count. Tagged phrases: {len(tagged_phrases)}, feedback items: {len(feedback_list)}"
            print(f"Warning: {warning_msg}")
            # Add warning to result
            result = {
                "annotated_response": annotated_response,
                "feedback_list": feedback_list,
                "warning": warning_msg
            }
        else:
            # Combine results
            result = {
                "annotated_response": annotated_response,
                "feedback_list": feedback_list
            }
        
        return json.dumps(result)
   else:
        raise ValueError(f"Unsupported model: {model}. Please use an OpenAI or Claude model.")

def check_results(results_json, raw_student_response):
    """
    Check and fix the results from annotation functions:
    1. Verify the annotated response matches the raw student response (except for tags)
    2. Ensure the number of tags matches the number of items in the feedback list
    
    Args:
        results_json (str): JSON string containing the results
        raw_student_response (str): The original student response
        
    Returns:
        str: JSON string with fixed/validated results
    """
    # Parse the JSON string to a dictionary
    if isinstance(results_json, str):
        results = json.loads(results_json)
    else:
        results = results_json  # Assume it's already a dictionary
    
    annotated_response = results.get("annotated_response", "")
    feedback_list = results.get("feedback_list", [])
    
    # Step 1: Check if the annotated response matches the raw student response (sans tags)
    # Strip all tags to get clean response
    stripped_response = annotated_response
    while "<tag id=" in stripped_response:
        tag_start = stripped_response.find("<tag id=")
        tag_end_of_opening = stripped_response.find(">", tag_start) + 1
        closing_tag_start = stripped_response.find("</tag>", tag_end_of_opening)
        closing_tag_end = closing_tag_start + 6  # Length of "</tag>"
        
        # Extract the content inside the tag
        tagged_content = stripped_response[tag_end_of_opening:closing_tag_start]
        
        # Replace the entire tag and its content with just the content
        stripped_response = stripped_response[:tag_start] + tagged_content + stripped_response[closing_tag_end:]
    
    # Clean up any extra whitespace
    stripped_response = ' '.join(stripped_response.split())
    clean_raw_response = ' '.join(raw_student_response.split())
    
    format_correct = stripped_response == clean_raw_response
    if not format_correct:
        print(f"Warning: The annotated response does not match the raw response.")
        print(f"Stripped response: {stripped_response}")
        print(f"Raw response: {clean_raw_response}")
        
        # Since this could be complex to fix automatically, we'll flag it but not attempt to fix
        results["warning"] = f"The annotated response format does not match the original response."
    
    # Step 2: Check if the number of tags matches the feedback list length
    tag_count = annotated_response.count("<tag id=")
    feedback_count = len(feedback_list)
    
    if tag_count != feedback_count:
        print(f"Mismatch in tag count. Found {tag_count} tags but {feedback_count} feedback items.")
        
        # Approach 1: If we have too many tags, remove extra ones (higher IDs first)
        if tag_count > feedback_count:
            # Extract all tags and their positions
            tag_positions = []
            position = 0
            while True:
                tag_start = annotated_response.find("<tag id=", position)
                if tag_start == -1:
                    break
                    
                # Find the tag ID
                id_start = tag_start + 9  # Length of '<tag id="'
                id_end = annotated_response.find('"', id_start)
                tag_id = int(annotated_response[id_start:id_end])
                
                # Find the content and closing tag
                tag_end_of_opening = annotated_response.find(">", tag_start) + 1
                closing_tag_start = annotated_response.find("</tag>", tag_end_of_opening)
                closing_tag_end = closing_tag_start + 6  # Length of "</tag>"
                
                # Save the tag info
                tag_positions.append({
                    "id": tag_id,
                    "start": tag_start,
                    "content_start": tag_end_of_opening,
                    "content_end": closing_tag_start,
                    "end": closing_tag_end
                })
                
                position = closing_tag_end
            
            # Sort tags by ID in descending order so we remove highest IDs first
            tag_positions.sort(key=lambda x: x["id"], reverse=True)
            
            # Remove excess tags
            extra_tags = tag_count - feedback_count
            modified_response = annotated_response
            for i in range(extra_tags):
                if i < len(tag_positions):
                    tag = tag_positions[i]
                    # Replace the entire tag with just the content
                    modified_response = (
                        modified_response[:tag["start"]] + 
                        modified_response[tag["content_start"]:tag["content_end"]] + 
                        modified_response[tag["end"]:]
                    )
            
            # Update the annotated response
            results["annotated_response"] = modified_response
            results["warning"] = f"Fixed: Removed {extra_tags} excess tags to match feedback list length."
        
        # Approach 2: If we have too few tags, more complex - would need to know where to add them
        # For now, we'll just flag this as an issue that needs manual correction
        elif tag_count < feedback_count:
            results["warning"] = f"The annotated response has fewer tags ({tag_count}) than feedback items ({feedback_count}). Manual correction needed."
    
    return json.dumps(results)

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

def generate_output_filename(model_name, method, output_dir):
    """Generate an output filename based on model name, method, and timestamp."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Clean up model name for the filename
    if model_name.startswith("gpt-4o"):
        model_short = "gpt4o"
    elif model_name.startswith("gpt-4.1"):
        model_short = "gpt41"
    elif model_name.startswith("claude"):
        model_short = "claude"
    else:
        model_short = "model"
        
    return os.path.join(output_dir, f"{model_short}_{method}_{timestamp}.csv")

def process_csv_file(input_csv_path, model_name="gpt-4o-2024-08-06", method="single", enable_check=False):
    """
    Process a CSV file line by line and send each line to the API.
    Output results to a CSV file with the naming convention model_name_method_datetime.csv
    
    Args:
        input_csv_path (str): Path to the input CSV file
        model_name (str): Name of the model to use for processing
        method (str): Method to use - 'single' for one API call, 'split' for two API calls, 'reverse' for reverse split
        enable_check (bool): Whether to run validation and fixing on results
    """
    # Create output directory in the same location as input file
    output_dir = os.path.dirname(input_csv_path)
    output_csv_path = generate_output_filename(model_name, method, output_dir)
    
    # Open input and output CSV files
    with open(input_csv_path, 'r', encoding='utf-8') as input_file, \
         open(output_csv_path, 'w', encoding='utf-8', newline='') as output_file:
        
        # Create CSV reader and writer
        csv_reader = csv.DictReader(input_file)
        csv_writer = csv.writer(output_file)
        
        # Write header to output CSV - add warnings and model_details columns
        csv_writer.writerow(["students_response", "annotated_response", "feedback_list", "model", "method", "warnings", "model_details"])
        
        # Process each row
        for row in csv_reader:
            try:
                # Extract data from row
                subject = row.get("subject", "")
                level = row.get("level", "")
                question = row.get("question", "")
                students_response = row.get("students_response", "")
                recipe = row.get("recipe", "")
                suggested_answer = row.get("suggested_answer", "")
                rubrics = row.get("rubrics", "")
                error_tags = row.get("error_tags", "")
                
                # Assemble prompts
                system_prompt = assemble_system_prompt(
                    subject, level, question, recipe, suggested_answer, rubrics, error_tags
                )
                user_prompt = assemble_user_prompt(students_response)
                
                # Track warnings
                warnings = []
                
                # Get annotations based on the specified method
                if method == "single":
                    response = get_annotations_system_user(system_prompt, user_prompt, model=model_name)
                elif method == "split":
                    response = get_annotations_split_system(system_prompt, user_prompt, model=model_name, raw_student_response=students_response)
                elif method == "reverse":
                    response = get_annotations_split_reverse(system_prompt, user_prompt, model=model_name, raw_student_response=students_response)
                else:
                    raise ValueError(f"Unknown method: {method}")
                
                # Check and fix results if enabled
                if enable_check:
                    response = check_results(response, students_response)
                
                # Parse JSON response - handle both string and dict responses
                response_dict = {}
                if isinstance(response, str):
                    # Check if the response is already a JSON error message
                    if response.startswith("No") and "Claude" in response:
                        raise Exception(response)
                    try:
                        response_dict = json.loads(response)
                        # Check for error in response
                        if "error" in response_dict:
                            warnings.append(response_dict["error"])
                        # Check for warning in response
                        if "warning" in response_dict:
                            warnings.append(response_dict["warning"])
                    except json.JSONDecodeError as e:
                        raise Exception(f"Failed to parse JSON response: {e}, Response: {response[:100]}...")
                elif isinstance(response, dict):
                    # If response is already a dictionary, use it directly
                    response_dict = response
                    # Check for error in response
                    if "error" in response_dict:
                        warnings.append(response_dict["error"])
                    # Check for warning in response
                    if "warning" in response_dict:
                        warnings.append(response_dict["warning"])
                else:
                    raise Exception(f"Unexpected response type: {type(response)}")
                
                # Extract data from response
                annotated_response = response_dict.get("annotated_response", "")
                feedback_list = response_dict.get("feedback_list", [])
                
                # Double check for tag count mismatch (even if already caught in the API response)
                tag_count_in_response = annotated_response.count("<tag id=")
                if tag_count_in_response != len(feedback_list) and not any("Mismatch in tag count" in warning for warning in warnings):
                    warning_msg = f"Mismatch in tag count. Feedback list has {len(feedback_list)} items, but annotated response has {tag_count_in_response} tags."
                    warnings.append(warning_msg)
                    print(f"Warning: {warning_msg}")
                
                # Get a friendly model name for display
                model_details = model_name
                if model_name.startswith("gpt-4o"):
                    model_details = "GPT-4o"
                elif model_name.startswith("gpt-4.1"):
                    model_details = "GPT-4.1"
                elif model_name.startswith("claude"):
                    model_details = "Claude 4 Sonnet"
                
                # Join warnings into a single string
                warnings_str = "; ".join(warnings) if warnings else ""
                
                # Write to output CSV
                csv_writer.writerow([
                    students_response,
                    annotated_response,
                    json.dumps(feedback_list),
                    model_name,
                    method,
                    warnings_str,
                    model_details
                ])
                
                print(f"Processed row with model {model_name}, method {method}, student response: {students_response[:30]}...")
                
            except Exception as e:
                print(f"Error processing row with {model_name}, {method}: {e}")
                # Write error row
                csv_writer.writerow([
                    row.get("students_response", ""),
                    f"Error: {str(e)}",
                    "[]",
                    model_name,
                    method,
                    str(e),
                    model_name
                ])
    
    print(f"Processing complete. Output saved to: {output_csv_path}")
    return output_csv_path

def run_all_combinations(input_csv_path, include_reverse=False, enable_check=False):
    """Run all combinations of models and methods and process the CSV file."""
    models = [
        "gpt-4o-2024-08-06",
        "gpt-4.1-2025-04-14", 
        "claude-sonnet-4-20250514"
    ]
    
    methods = ["single", "split"]
    if include_reverse:
        methods.append("reverse")
    
    results = {}
    
    # Using concurrent.futures to process combinations in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        future_to_combo = {}
        
        # Submit all tasks
        for model in models:
            for method in methods:
                future = executor.submit(process_csv_file, input_csv_path, model, method, enable_check)
                future_to_combo[future] = (model, method)
        
        # Process results as they complete
        for future in concurrent.futures.as_completed(future_to_combo):
            model, method = future_to_combo[future]
            try:
                output_path = future.result()
                results[(model, method)] = output_path
                print(f"Completed: {model} with {method} method")
            except Exception as e:
                print(f"Error with {model}, {method}: {e}")
    
    return results

def main():
    """Main function to process CSV data with different models and methods."""
    # Get the directory containing the current script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Process student responses with AI feedback using multiple models')
    parser.add_argument('--csv', help='Path to input CSV file (defaults to afa_data.csv in the current directory)')
    parser.add_argument('--model', choices=['gpt4o', 'gpt41', 'claude', 'all'], default='all', 
                      help='Model to use for processing: gpt4o, gpt41, claude, or all')
    parser.add_argument('--method', choices=['single', 'split', 'reverse', 'all'], default='all',
                      help='Method to use: single API call, split API calls, reverse split, or all methods')
    parser.add_argument('--reverse', action='store_true', help='Include reverse method in addition to the specified method')
    parser.add_argument('--check', action='store_true', help='Enable validation and fixing of annotation results')
    
    args = parser.parse_args()
    
    # Map argument choices to actual model names
    model_mapping = {
        'gpt4o': 'gpt-4o-2024-08-06',
        'gpt41': 'gpt-4.1-2025-04-14',
        'claude': 'claude-sonnet-4-20250514'
    }
    
    try:
        # Use default CSV path if none specified
        input_csv = args.csv
        if input_csv is None:
            input_csv = os.path.join(current_dir, "afa_data.csv")
            
        # Check if the provided path is absolute or relative
        if not os.path.isabs(input_csv) and not os.path.isfile(input_csv):
            # Try relative to script directory
            alt_path = os.path.join(current_dir, input_csv)
            if os.path.isfile(alt_path):
                input_csv = alt_path
                
        # Check if file exists
        if not os.path.isfile(input_csv):
            raise FileNotFoundError(f"CSV file not found: {input_csv}")
        
        # Process according to arguments
        if args.model == 'all' and (args.method == 'all' or args.reverse):
            # Run all combinations including reverse if specified
            results = run_all_combinations(
                input_csv, 
                include_reverse=True if args.method == 'all' or args.reverse else False,
                enable_check=args.check
            )
            for (model, method), output_path in results.items():
                print(f"Results for {model} with {method} method saved to: {output_path}")
        else:
            # Run specific model(s) and method(s)
            models_to_run = [model_mapping[args.model]] if args.model != 'all' else list(model_mapping.values())
            
            if args.method == 'all':
                methods_to_run = ['single', 'split', 'reverse']
            else:
                methods_to_run = [args.method]
                if args.reverse and 'reverse' not in methods_to_run:
                    methods_to_run.append('reverse')
            
            for model in models_to_run:
                for method in methods_to_run:
                    output_path = process_csv_file(input_csv, model, method, args.check)
                    print(f"Results for {model} with {method} method saved to: {output_path}")
        
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
