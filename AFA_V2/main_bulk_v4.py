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
import re
import difflib
import base64

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

def enhanced_strip_tags(annotated_response):
    """
    Enhanced function to strip tags while preserving exact original formatting.
    Handles edge cases like nested quotes, special characters, and whitespace.
    """
    result = annotated_response
    
    # Pattern to match tags more precisely
    tag_pattern = r'<tag\s+id\s*=\s*["\']?\d+["\']?\s*>(.*?)</tag>'
    
    # Replace all tags with their content
    while re.search(tag_pattern, result, re.DOTALL):
        result = re.sub(tag_pattern, r'\1', result, count=1)
    
    return result

def validate_annotation_preservation(annotated_response, raw_student_response):
    """
    Validates that the annotated response preserves the original text exactly
    when tags are removed, with enhanced Unicode support for Chinese characters.
    
    Returns:
        is_valid (bool): True if validation passes
        error_info (str): Error message if validation fails
    """
    try:
        # Remove tags using the enhanced strip function
        stripped_response = enhanced_strip_tags(annotated_response)
        
        # Calculate lengths using proper Unicode character counting
        original_length = len(raw_student_response)
        stripped_length = len(stripped_response)
        
        # For debugging Chinese character issues
        print(f"DEBUG: Original length: {original_length}, Stripped length: {stripped_length}")
        print(f"DEBUG: Original (first 100 chars): {repr(raw_student_response[:100])}")
        print(f"DEBUG: Stripped (first 100 chars): {repr(stripped_response[:100])}")
        
        # Check if lengths match
        if original_length != stripped_length:
            error_msg = f"Length mismatch: original has {original_length} characters, stripped has {stripped_length} characters"
            print(f"DEBUG: {error_msg}")
            return False, error_msg
        
        # Check character-by-character comparison for exact match
        if raw_student_response != stripped_response:
            # Find the first difference
            for i, (orig_char, stripped_char) in enumerate(zip(raw_student_response, stripped_response)):
                if orig_char != stripped_char:
                    error_msg = f"Character mismatch at position {i}: expected '{repr(orig_char)}', got '{repr(stripped_char)}'"
                    print(f"DEBUG: {error_msg}")
                    
                    # Show context around the mismatch
                    start_pos = max(0, i - 10)
                    end_pos = min(len(raw_student_response), i + 10)
                    print(f"DEBUG: Context - Original: {repr(raw_student_response[start_pos:end_pos])}")
                    print(f"DEBUG: Context - Stripped: {repr(stripped_response[start_pos:end_pos])}")
                    return False, error_msg
            
            # If no character differences found but strings don't match, there might be a subtle issue
            error_msg = "Strings don't match but no character difference found - possible Unicode normalization issue"
            print(f"DEBUG: {error_msg}")
            return False, error_msg
        
        print("DEBUG: Validation passed - text preserved correctly")
        return True, "Valid"
        
    except Exception as e:
        error_msg = f"Validation error: {str(e)}"
        print(f"DEBUG: {error_msg}")
        return False, error_msg

def get_annotations_with_validation(assembled_system_prompt, assembled_user_prompt, model="gpt-4o-2024-08-06", raw_student_response=None, max_retries=3):
    """
    Enhanced annotation function with validation and retry logic.
    """
    for attempt in range(max_retries):
        try:
            # Get annotations using the appropriate method
            response = get_annotations_system_user(assembled_system_prompt, assembled_user_prompt, model)
            
            # Parse response
            if isinstance(response, str):
                response_dict = json.loads(response)
            else:
                response_dict = response
            
            annotated_response = response_dict.get("annotated_response", "")
            
            # Validate preservation
            is_valid, error_info = validate_annotation_preservation(annotated_response, raw_student_response)
            
            if is_valid:
                return response
            else:
                # Log the error
                print(f"Attempt {attempt + 1}: Annotation preservation failed - {error_info}")
                
                # Modify prompt for retry with stronger constraints
                if attempt < max_retries - 1:
                    # Add stronger preservation instructions
                    enhanced_user_prompt = assembled_user_prompt + f"""

CRITICAL INSTRUCTION: The student's response MUST be preserved EXACTLY character-by-character. 
Only add tags, do not modify ANY part of the text including:
- Whitespace (spaces, tabs, newlines)
- Punctuation
- Capitalization
- Special characters
- Character encoding

The original response has exactly {len(raw_student_response)} characters.
After removing tags, your annotated response must also have exactly {len(raw_student_response)} characters."""
                    
                    assembled_user_prompt = enhanced_user_prompt
                
        except Exception as e:
            print(f"Attempt {attempt + 1} failed with error: {e}")
            if attempt == max_retries - 1:
                raise
    
    # If all retries failed, return the last response with a warning
    response_dict["validation_failed"] = True
    response_dict["validation_error"] = error_info
    return json.dumps(response_dict)

def get_annotations_system_user(assembled_system_prompt, assembled_user_prompt, model="gpt-4o-2024-08-06"):
   if model.startswith("gpt"):  # Handle all OpenAI models
        response = client.chat.completions.create(
        model=model,
        temperature = 0.0,  # Reduced from 0.1 for more deterministic output
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
                "text": assembled_system_prompt + assembled_user_prompt + """

CRITICAL TAGGING INSTRUCTIONS FOR CLAUDE:
1. You MUST place tags exactly where errors occur in the text, not at the beginning or end
2. For Chinese text, identify specific incorrect words/phrases and tag them inline
3. Examples:
   - CORRECT: '小明在<tag id="1">课室</tag>里玩球' (tags "课室" where it appears)
   - WRONG: '小明在课室里玩球<tag id="1">课室</tag>' (tags at end)
   - WRONG: '<tag id="1">小明在课室里玩球</tag>' (tags entire text)

4. Look for these common Chinese errors:
   - Wrong characters: 课室→教室, 哪位→那位, 服满→充满
   - Grammar errors: 一而三再而三→一而再再而三
   - Missing characters: 不到钱→不道歉, 一后→以后

5. If no errors exist, return empty feedback_list: []
6. DO NOT create 613 or 1274 feedback items - create only what you actually tag
"""
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
                    "description": "The student's response with tags (using unique running number ids) enclosing specific words or phrases IN PLACE where errors occur. Tags must be inserted exactly where the error appears in the original text, not at the end. For example: '小明在<tag id=\"1\">课室</tag>里玩球' not '小明在课室里玩球<tag id=\"1\">课室</tag>'. Preserve ALL original characters including Chinese characters, punctuation, and spacing exactly."
                  },
                  "feedback_list": {
                    "type": "array",
                    "items": {
                      "type": "object",
                      "properties": {
                        "id": {
                          "type": "integer",
                          "description": "tag id corresponding to the tag in annotated_response"
                        },
                        "phrase": {
                          "type": "string",
                          "description": "the specific part of the sentence containing an error (exactly as it appears in the original text)"
                        },
                        "error_tag": {
                          "type": "array",
                          "items": {
                            "type": "object",
                            "properties": {
                                "errorType": {
                                    "type": "string",
                                    "description": "error type (use Chinese error types for Chinese text: 语言, 内容, 语法, 词汇, etc.)"
                                }
                            }
                          },
                          "description": "list of concise error category based on error types"
                        },
                        "comment": {
                          "type": "string",
                          "description": "a concise student-friendly explanation or suggestion (use Chinese for Chinese text)"
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
            "max_tokens": 16000,
            "temperature": 0.0,
            "tools": [claude_tool],
            "messages": [
                {
                    "role": "user",
                    "content": message_content
                }
            ],
            "tool_choice": {"type": "tool", "name": "get_annotated_feedback"}
        }
        response = anthropic_client.messages.create(**api_params)
        
        # Enhanced Claude response parsing with debug info
        for content in response.content:
            if content.type == 'tool_use':
                # Get the tool input
                tool_input = content.input
                
                # Process tool input
                if isinstance(tool_input, dict):
                    annotated_response = tool_input.get("annotated_response", "")
                    feedback_list = tool_input.get("feedback_list", [])
                    
                    # Check for tag count mismatch with debug info
                    tag_count = annotated_response.count("<tag id=")
                    if tag_count != len(feedback_list):
                        warning_msg = f"Mismatch in tag count. Feedback list has {len(feedback_list)} items, but annotated response has {tag_count} tags."
                        print(f"DEBUG: {warning_msg}")
                        print(f"DEBUG: Feedback list length calculation: {len(feedback_list)}")
                        print(f"DEBUG: Sample feedback items: {feedback_list[:3] if len(feedback_list) > 3 else feedback_list}")
                        tool_input["warning"] = warning_msg
                    
                    return tool_input
                elif isinstance(tool_input, str):
                    try:
                        parsed = json.loads(tool_input)
                        annotated_response = parsed.get("annotated_response", "")
                        feedback_list = parsed.get("feedback_list", [])
                        
                        # Check for tag count mismatch with debug info
                        tag_count = annotated_response.count("<tag id=")
                        if tag_count != len(feedback_list):
                            warning_msg = f"Mismatch in tag count. Feedback list has {len(feedback_list)} items, but annotated response has {tag_count} tags."
                            print(f"DEBUG: {warning_msg}")
                            print(f"DEBUG: Feedback list length calculation: {len(feedback_list)}")
                            parsed["warning"] = warning_msg
                            return json.dumps(parsed)
                    except Exception as e:
                        # If there's an error parsing, log it and return the original string
                        print(f"DEBUG: Error parsing Claude tool input: {e}")
                        pass
                
                return tool_input
            elif content.type == 'text':
                # Claude sometimes returns text instead of tool use
                text_content = content.text
                print(f"DEBUG: Claude returned text instead of tool use: {text_content[:200]}...")
                
                # Try to extract JSON from the text content
                try:
                    # Look for JSON-like content in the text
                    import re
                    json_match = re.search(r'\{.*\}', text_content, re.DOTALL)
                    if json_match:
                        json_str = json_match.group()
                        parsed = json.loads(json_str)
                        return json.dumps(parsed)
                except Exception as e:
                    print(f"DEBUG: Failed to extract JSON from text: {e}")
                
        # Fallback with more debug info
        print(f"DEBUG: Claude response content types: {[content.type for content in response.content]}")
        print(f"DEBUG: Full Claude response: {response}")
        return json.dumps({"error": "No tool use found in Claude's response", "debug": "Check Claude response format"})
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
            temperature=0.0,  # Reduced for consistency
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
        
        # Enhanced prompt for annotation with character preservation
        enhanced_annotation_prompt = rsrc.system_prompt_annotated_response + f"""

CRITICAL PRESERVATION RULES:
1. The student's response has EXACTLY {len(raw_student_response)} characters
2. You MUST preserve EVERY character including:
   - All whitespace (spaces, tabs, newlines) 
   - All punctuation marks
   - All capitalization
   - All special characters
   - All escape sequences (backslashes, quotes, etc.)
3. ONLY insert tags, do NOT modify ANY other part of the text
4. After removing tags, the result must be IDENTICAL to the original
5. DO NOT interpret, normalize, or "fix" any part of the text
6. Preserve ALL escape sequences exactly as they appear (e.g., \\", \\', \\\\)

IMPORTANT: The text may contain escape sequences like \\", \\', \\\\. These must be preserved EXACTLY as written.
"""
        
        # Encode the raw student response in base64 to preserve exact characters
        encoded_student_response = base64.b64encode(raw_student_response.encode('utf-8')).decode('ascii')
        
        # Create a special prompt that includes both the original text and base64 encoded version
        annotation_user_prompt = f"""
Here is the student's response that needs to be annotated:

ORIGINAL TEXT (use this for annotation):
{raw_student_response}

BASE64 ENCODED VERSION (for exact character reference):
{encoded_student_response}

Here is the feedback list that identifies errors to tag:
{json.dumps(feedback_list)}

CRITICAL INSTRUCTIONS:
1. Use ONLY the ORIGINAL TEXT above for creating your annotated response
2. The BASE64 version is provided for exact character verification - decode it if needed to verify exact characters
3. Preserve ALL characters exactly, including escape sequences like \\", \\', \\\\
4. Only add <tag id="X">phrase</tag> markers - do not change any other characters
5. The text between tags must be IDENTICAL to the original, character-by-character

Please return the annotated response with appropriate tags inserted.
"""
        
        # Second call: Generate annotated response with RAW student response
        response2 = client.chat.completions.create(
            model=model,
            temperature=0.0,
            max_tokens=16000,
            tools=rsrc.tools_annotated_response,
            tool_choice={"type": "function", "function": {"name": "get_annotated_response"}},
            messages=[
                {"role": "system", "content": enhanced_annotation_prompt},
                {"role": "user", "content": annotation_user_prompt}
            ]
        )
        annotated_response_json = json.loads(response2.choices[0].message.tool_calls[0].function.arguments)
        annotated_response = annotated_response_json.get("annotated_response", "")
        
        # Enhanced validation
        is_valid, error_info = validate_annotation_preservation(annotated_response, raw_student_response)
        
        # Prepare result
        result = {
            "annotated_response": annotated_response,
            "feedback_list": feedback_list
        }
        
        # Add warnings if needed
        warnings = []
        
        # Tag count validation
        tag_count_in_response = annotated_response.count("<tag id=")
        if tag_count_in_response != len(feedback_list):
            warning_msg = f"Mismatch in tag count. Feedback list has {len(feedback_list)} items, but annotated response has {tag_count_in_response} tags."
            warnings.append(warning_msg)
            print(f"Warning: {warning_msg}")
        
        # Preservation validation
        if not is_valid:
            warning_msg = f"Text preservation error: {error_info}"
            warnings.append(warning_msg)
            print(f"Warning: {warning_msg}")
        
        if warnings:
            result["warning"] = "; ".join(warnings)
        
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
            "temperature": 0.0,  # Reduced for consistency
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
        
        # Enhanced annotation prompt for Claude
        enhanced_annotation_prompt = rsrc.system_prompt_annotated_response + f"""

CRITICAL PRESERVATION RULES:
1. The student's response has EXACTLY {len(raw_student_response)} characters
2. You MUST preserve EVERY character including:
   - All whitespace (spaces, tabs, newlines) 
   - All punctuation marks
   - All capitalization
   - All special characters
   - All escape sequences (backslashes, quotes, etc.)
3. ONLY insert tags, do NOT modify ANY other part of the text
4. After removing tags, the result must be IDENTICAL to the original
5. DO NOT interpret, normalize, or "fix" any part of the text
6. Preserve ALL escape sequences exactly as they appear (e.g., \\", \\', \\\\)

IMPORTANT: The text may contain escape sequences like \\", \\', \\\\. These must be preserved EXACTLY as written.
"""
            
        # Encode the raw student response in base64 to preserve exact characters
        encoded_student_response = base64.b64encode(raw_student_response.encode('utf-8')).decode('ascii')
        
        # Create a special prompt that includes both the original text and base64 encoded version
        annotation_user_prompt = f"""
Here is the student's response that needs to be annotated:

ORIGINAL TEXT (use this for annotation):
{raw_student_response}

BASE64 ENCODED VERSION (for exact character reference):
{encoded_student_response}

Here is the feedback list that identifies errors to tag:
{json.dumps(feedback_list)}

CRITICAL INSTRUCTIONS:
1. Use ONLY the ORIGINAL TEXT above for creating your annotated response
2. The BASE64 version is provided for exact character verification - decode it if needed to verify exact characters
3. Preserve ALL characters exactly, including escape sequences like \\", \\', \\\\
4. Only add <tag id="X">phrase</tag> markers - do not change any other characters
5. The text between tags must be IDENTICAL to the original, character-by-character

Please return the annotated response with appropriate tags inserted.
"""
            
        # For Claude, combine system and user content into a single user message
        # Using the original student response directly from CSV for annotation
        system_and_user_content = enhanced_annotation_prompt + "\n\n" + annotation_user_prompt
        
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
            "temperature": 0.0,
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
        
        # Enhanced validation
        is_valid, error_info = validate_annotation_preservation(annotated_response, raw_student_response)
        
        # Prepare result
        result = {
            "annotated_response": annotated_response,
            "feedback_list": feedback_list
        }
        
        # Add warnings if needed
        warnings = []
        
        # Tag count validation
        tag_count_in_response = annotated_response.count("<tag id=")
        if tag_count_in_response != len(feedback_list):
            warning_msg = f"Mismatch in tag count. Feedback list has {len(feedback_list)} items, but annotated response has {tag_count_in_response} tags."
            warnings.append(warning_msg)
            print(f"Warning: {warning_msg}")
        
        # Preservation validation
        if not is_valid:
            warning_msg = f"Text preservation error: {error_info}"
            warnings.append(warning_msg)
            print(f"Warning: {warning_msg}")
        
        if warnings:
            result["warning"] = "; ".join(warnings)
        
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
        
        # Enhanced annotation prompt
        enhanced_annotation_prompt = rsrc.system_prompt_annotated_response + f"""

CRITICAL PRESERVATION RULES:
1. The student's response has EXACTLY {len(students_response)} characters
2. You MUST preserve EVERY character including:
   - All whitespace (spaces, tabs, newlines) 
   - All punctuation marks
   - All capitalization
   - All special characters
   - All escape sequences (backslashes, quotes, etc.)
3. ONLY insert tags, do NOT modify ANY other part of the text
4. After removing tags, the result must be IDENTICAL to the original
5. DO NOT interpret, normalize, or "fix" any part of the text
6. Preserve ALL escape sequences exactly as they appear (e.g., \\", \\', \\\\)

IMPORTANT: The text may contain escape sequences like \\", \\', \\\\. These must be preserved EXACTLY as written.
"""
        
        # Encode the student response in base64 to preserve exact characters
        encoded_student_response = base64.b64encode(students_response.encode('utf-8')).decode('ascii')
        
        # Create enhanced annotation prompt
        annotation_task_prompt = f"""
Here is the student's response that needs to be annotated:

ORIGINAL TEXT (use this for annotation):
{students_response}

BASE64 ENCODED VERSION (for exact character reference):
{encoded_student_response}

Use the error types from the following list to guide your annotation:
{assembled_system_prompt.split("Error list: ")[1].split("Additional Error type instructions")[0] if "Error list: " in assembled_system_prompt else ""}

Please annotate the student's response by identifying errors and inserting tags around problematic phrases.

<task>
CRITICAL INSTRUCTIONS:
1. Use ONLY the ORIGINAL TEXT above for creating your annotated response
2. The BASE64 version is provided for exact character verification - decode it if needed to verify exact characters
3. Preserve ALL characters exactly, including escape sequences like \\", \\', \\\\
4. Only add <tag id="X">phrase</tag> markers - do not change any other characters
5. The text between tags must be IDENTICAL to the original, character-by-character

Analyze the student's response and identify errors based on the error types provided.
Insert tags around phrases that contain errors: <tag id="1">error phrase</tag>
Use ascending ID numbers starting from 1 for each tag.
Return the student's response exactly as it is, with only the tags inserted.
The text must be preserved character-by-character.
</task>
"""
        
        # First call: Generate annotated response using error tags as guide
        response1 = client.chat.completions.create(
            model=model,
            temperature=0.0,
            max_tokens=16000,
            tools=rsrc.tools_annotated_response,
            tool_choice={"type": "function", "function": {"name": "get_annotated_response"}},
            messages=[
                {"role": "system", "content": enhanced_annotation_prompt},
                {"role": "user", "content": annotation_task_prompt}
            ]
        )
        annotated_response_json = json.loads(response1.choices[0].message.tool_calls[0].function.arguments)
        annotated_response = annotated_response_json.get("annotated_response", "")
        
        # Validate preservation
        is_valid, error_info = validate_annotation_preservation(annotated_response, students_response)
        
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
            temperature=0.0,
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
        
        # Prepare result
        result = {
            "annotated_response": annotated_response,
            "feedback_list": feedback_list
        }
        
        # Add warnings if needed
        warnings = []
        
        # Tag count validation
        tag_count_in_response = annotated_response.count("<tag id=")
        if tag_count_in_response != len(feedback_list):
            warning_msg = f"Mismatch in tag count. Feedback list has {len(feedback_list)} items, but annotated response has {tag_count_in_response} tags."
            warnings.append(warning_msg)
            print(f"Warning: {warning_msg}")
        
        # Preservation validation
        if not is_valid:
            warning_msg = f"Text preservation error: {error_info}"
            warnings.append(warning_msg)
            print(f"Warning: {warning_msg}")
        
        if warnings:
            result["warning"] = "; ".join(warnings)
        
        return json.dumps(result)
        
   elif model.startswith("claude"):
        # Claude implementation would go here
        # For now, just raise an error indicating it's not implemented
        raise ValueError(f"Claude support not yet implemented for split_reverse method. Please use an OpenAI model.")
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

def check_results(results_json, raw_student_response):
    """
    Check and fix results to ensure tag count matches feedback list count.
    
    Args:
        results_json (str): JSON string containing the results
        raw_student_response (str): Original student response for validation
        
    Returns:
        str: Corrected JSON string
    """
    try:
        # Parse the results
        if isinstance(results_json, str):
            results = json.loads(results_json)
        else:
            results = results_json
            
        annotated_response = results.get("annotated_response", "")
        feedback_list = results.get("feedback_list", [])
        
        # Count tags in annotated response
        tag_count = annotated_response.count("<tag id=")
        feedback_count = len(feedback_list)
        
        # If counts match, return as is
        if tag_count == feedback_count:
            return json.dumps(results) if isinstance(results_json, str) else results
        
        print(f"Fixing mismatch: {tag_count} tags vs {feedback_count} feedback items")
        
        # Extract tag IDs and their corresponding phrases
        tag_pattern = r'<tag id="(\d+)">(.*?)</tag>'
        matches = re.findall(tag_pattern, annotated_response)
        
        if len(matches) != tag_count:
            print(f"Warning: Regex found {len(matches)} matches but counted {tag_count} tags")
        
        # Create a mapping of tag IDs to phrases
        tag_phrases = {}
        for tag_id, phrase in matches:
            tag_phrases[int(tag_id)] = phrase
        
        # If we have more feedback than tags, trim the feedback list
        if feedback_count > tag_count:
            print(f"Trimming feedback list from {feedback_count} to {tag_count} items")
            # Keep only feedback items that have corresponding tags
            valid_feedback = []
            for feedback_item in feedback_list:
                if feedback_item.get("id") in tag_phrases:
                    valid_feedback.append(feedback_item)
            results["feedback_list"] = valid_feedback[:tag_count]
        
        # If we have more tags than feedback, create minimal feedback entries
        elif tag_count > feedback_count:
            print(f"Adding {tag_count - feedback_count} minimal feedback items")
            existing_ids = {item.get("id") for item in feedback_list}
            
            for tag_id, phrase in tag_phrases.items():
                if tag_id not in existing_ids:
                    # Create a minimal feedback entry
                    feedback_list.append({
                        "id": tag_id,
                        "phrase": phrase,
                        "error_tag": [{"errorType": "Error"}],
                        "comment": "Error identified"
                    })
            
            results["feedback_list"] = feedback_list
        
        # Add a warning about the fix
        existing_warning = results.get("warning", "")
        fix_warning = f"Fixed tag count mismatch (was {feedback_count} feedback items for {tag_count} tags)"
        
        if existing_warning:
            results["warning"] = f"{existing_warning}; {fix_warning}"
        else:
            results["warning"] = fix_warning
        
        return json.dumps(results) if isinstance(results_json, str) else results
        
    except Exception as e:
        print(f"Error in check_results: {e}")
        # Return original if fixing fails
        return results_json

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
                
                # Enhanced Chinese character handling
                try:
                    # If feedback_list is a string, try to parse it as JSON
                    if isinstance(feedback_list, str):
                        feedback_list = json.loads(feedback_list)
                    
                    # Fix Unicode encoding issues in Chinese feedback
                    if isinstance(feedback_list, list):
                        for item in feedback_list:
                            if isinstance(item, dict):
                                # Ensure all string fields are properly decoded
                                for key, value in item.items():
                                    if isinstance(value, str):
                                        # If it contains Unicode escape sequences, decode them
                                        try:
                                            decoded_value = value.encode().decode('unicode_escape').encode('latin1').decode('utf-8')
                                            if decoded_value != value:
                                                item[key] = decoded_value
                                        except:
                                            # If decoding fails, keep original value
                                            pass
                except Exception as e:
                    print(f"Warning: Failed to process Chinese characters in feedback: {e}")
                
                # Chinese character count validation and fixing
                if any(ord(char) > 127 for char in students_response):  # Contains non-ASCII (likely Chinese)
                    tag_count_in_response = annotated_response.count("<tag id=")
                    feedback_count = len(feedback_list)
                    
                    # If there's a massive mismatch (like 613 vs 5), likely a character counting bug
                    if feedback_count > 100 and tag_count_in_response < 20:
                        print(f"Detected Chinese character counting bug: {feedback_count} items vs {tag_count_in_response} tags")
                        
                        # Extract actual tagged phrases from annotated response
                        import re
                        tag_pattern = r'<tag id="(\d+)">(.*?)</tag>'
                        matches = re.findall(tag_pattern, annotated_response, re.DOTALL)
                        
                        if len(matches) == tag_count_in_response:
                            # Create corrected feedback list based on actual tags
                            corrected_feedback = []
                            for i, (tag_id, phrase) in enumerate(matches):
                                corrected_feedback.append({
                                    "id": int(tag_id),
                                    "phrase": phrase,
                                    "error_tag": [{"errorType": "语言"}],
                                    "comment": f"错误已标识：{phrase}"
                                })
                            
                            feedback_list = corrected_feedback
                            warnings.append(f"Fixed Chinese character counting bug: reduced from {feedback_count} to {len(corrected_feedback)} items")
                
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
                
                # Ensure proper UTF-8 encoding for Chinese characters in JSON
                try:
                    feedback_json = json.dumps(feedback_list, ensure_ascii=False)
                except Exception as e:
                    print(f"Warning: Failed to encode Chinese characters in JSON: {e}")
                    feedback_json = json.dumps(feedback_list)  # Fallback with ASCII encoding
                
                # Write to output CSV
                csv_writer.writerow([
                    students_response,
                    annotated_response,
                    feedback_json,
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
    parser = argparse.ArgumentParser(
        description='AI Feedback Assistant (AFA): Process student responses with AI-generated feedback using multiple LLM models',
        epilog='''
Examples:
  python main_bulk.py                                     # Process all models and methods using default CSV
  python main_bulk.py --csv my_data.csv --model gpt4o     # Process only with GPT-4o model
  python main_bulk.py --method split --check              # Process with split method only and validate results
        '''
    )
    parser.add_argument('--csv', 
                      help='Path to input CSV file with student responses (defaults to afa_data.csv in the current directory)')
    parser.add_argument('--model', choices=['gpt4o', 'gpt41', 'claude', 'all'], default='all', 
                      help='''Model to use for processing:
                      gpt4o: GPT-4o (OpenAI)
                      gpt41: GPT-4.1 Turbo (OpenAI)
                      claude: Claude 4 Sonnet (Anthropic)
                      all: Run with all available models (default)''')
    parser.add_argument('--method', choices=['single', 'split', 'reverse', 'all'], default='all',
                      help='''Feedback generation method:
                      single: Single API call that generates both annotations and feedback at once
                      split: Two API calls - first generates feedback list, then applies annotations
                      reverse: Two API calls in reverse order - first annotates text, then generates feedback
                      all: Run with all methods (default)''')
    parser.add_argument('--reverse', action='store_true', 
                      help='Include reverse method in addition to the specified method (ignored if --method=all)')
    parser.add_argument('--check', action='store_true', 
                      help='Enable validation and fixing of annotation results (corrects mismatches between tags and feedback)')
    
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