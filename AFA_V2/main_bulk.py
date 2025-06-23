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
            
            # Enhanced character difference analysis
            if abs(original_length - stripped_length) <= 10:  # Only for small differences
                print("DEBUG: Analyzing character differences...")
                
                # Common escape sequence transformations
                escape_sequences = {
                    '\\\\': '\\',     # Double backslash to single
                    '\\n': '\n',      # Literal \n to newline
                    '\\t': '\t',      # Literal \t to tab
                    '\\"': '"',       # Escaped quote to quote
                    "\\'": "'",       # Escaped apostrophe to apostrophe
                    '\\r': '\r',      # Literal \r to carriage return
                }
                
                # Check for specific transformations
                for escaped, actual in escape_sequences.items():
                    if escaped in raw_student_response and actual in stripped_response:
                        count_original = raw_student_response.count(escaped)
                        # Check if the difference matches the transformation
                        expected_diff = count_original * (len(escaped) - len(actual))
                        if expected_diff == (original_length - stripped_length):
                            print(f"DEBUG: Identified transformation: '{escaped}' -> '{actual}' ({count_original} occurrences)")
                            print(f"DEBUG: This accounts for the {expected_diff} character difference")
                            break
                
                # Check for quote transformations
                straight_quotes = ['"', "'"]
                curly_quotes = ['"', '"', ''', ''']
                
                for straight in straight_quotes:
                    for curly in curly_quotes:
                        if straight in raw_student_response and curly in stripped_response:
                            count_straight = raw_student_response.count(straight)
                            count_curly = stripped_response.count(curly)
                            if count_straight > 0 and count_curly > 0:
                                print(f"DEBUG: Possible quote transformation: '{straight}' -> '{curly}'")
            
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

CHINESE TEXT PROCESSING RULES:
- DO NOT count individual Chinese characters as separate errors
- Only identify actual linguistic errors (wrong words, grammar mistakes, etc.)
- If you tag 5 phrases, create exactly 5 feedback items
- If you tag 10 phrases, create exactly 10 feedback items
- DO NOT create feedback for every character in the text
- Focus on meaningful errors, not character-by-character analysis

CRITICAL CHARACTER PRESERVATION - CLAUDE OFTEN FAILS HERE:
- DO NOT convert straight quotes (") to curly quotes (" ")
- DO NOT convert straight apostrophes (') to curly apostrophes (' ')
- CRITICAL: If you see \\" in text, keep it as \\" - DO NOT convert to "
- CRITICAL: If you see \\' in text, keep it as \\' - DO NOT convert to '
- Keep ALL punctuation exactly as it appears in the original text
- Preserve ALL whitespace, capitalization, and special characters exactly
- Only add tags - do NOT modify any existing characters
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
                    "description": "The student's response with tags (using unique running number ids) enclosing specific words or phrases IN PLACE where errors occur. Tags must be inserted exactly where the error appears in the original text, not at the end. For example: '小明在<tag id=\"1\">课室</tag>里玩球' not '小明在课室里玩球<tag id=\"1\">课室</tag>'. Preserve ALL original characters including Chinese characters, punctuation, and spacing exactly. CRITICAL: Do NOT convert straight quotes (\") to curly quotes or straight apostrophes (') to curly apostrophes. Keep punctuation exactly as it appears in the original."
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

def get_annotations_single_call(assembled_system_prompt, assembled_user_prompt, model="gpt-4o-2024-08-06", enable_char_validation=True, raw_student_response=None, max_retries=3):
    """
    Single call annotation function with optional character validation and enhanced prompting.
    
    Args:
        assembled_system_prompt: The formatted system prompt
        assembled_user_prompt: The formatted user prompt
        model: The model name to use
        enable_char_validation: Whether to perform character preservation validation
        raw_student_response: The original student response for validation
        max_retries: Number of retries if validation fails (now always 1)
    """
    try:
        # Enhanced system prompt with preservation rules (same for both w and wo)
        enhanced_system_prompt = assembled_system_prompt + """

CRITICAL PRESERVATION RULES:
1. You MUST preserve EVERY character including:
   - All whitespace (spaces, tabs, newlines) 
   - All punctuation marks
   - All capitalization
   - All special characters
   - All escape sequences (backslashes, quotes, etc.)
2. ONLY insert tags, do NOT modify ANY other part of the text
3. After removing tags, the result must be IDENTICAL to the original
4. DO NOT interpret, normalize, or "fix" any part of the text
5. Preserve ALL escape sequences exactly as they appear (e.g., \\", \\', \\\\)

QUOTE AND APOSTROPHE PRESERVATION - CRITICAL:
- DO NOT convert straight quotes (") to curly quotes (")
- DO NOT convert straight apostrophes (') to curly apostrophes (')
- Keep ALL punctuation marks EXACTLY as they appear in the original
- If the original has straight quotes/apostrophes, use straight quotes/apostrophes
- If the original has curly quotes/apostrophes, use curly quotes/apostrophes
- NO SMART PUNCTUATION CONVERSION ALLOWED


CRITICAL ESCAPE SEQUENCE PRESERVATION - THIS IS THE #1 SOURCE OF ERRORS:
- If you see \\" in the text, it MUST remain as \\" (backslash + quote = 2 characters)
- Do NOT convert \\" to " (this removes 1 character and breaks preservation)
- If you see \\' in the text, it MUST remain as \\' (backslash + apostrophe = 2 characters)  
- Do NOT convert \\' to ' (this removes 1 character and breaks preservation)
- If you see \\n in the text, keep it as \\n (two characters) - do NOT convert to actual newline
- If you see \\t in the text, keep it as \\t (two characters) - do NOT convert to actual tab
- If you see \\\\ in the text, keep it as \\\\ (two characters) - do NOT convert to single \

QUOTE PRESERVATION EXAMPLES:
- Original: 'He said \\"Hello\\" to me' → Keep: 'He said \\"Hello\\" to me' (NOT: 'He said "Hello" to me')
- Original: 'It\\'s time to go' → Keep: 'It\\'s time to go' (NOT: 'It's time to go')

These are LITERAL ESCAPE SEQUENCES, not formatting instructions
Character count must be preserved EXACTLY
QUOTE PRESERVATION REQUIREMENTS:
- Copy punctuation marks EXACTLY from the original text
"""
        
        # Enhanced user prompt - different based on char validation mode
        if enable_char_validation and raw_student_response:
            # Mode "w" - WITH base64 encoding and character counting
            encoded_student_response = base64.b64encode(raw_student_response.encode('utf-8')).decode('ascii')
            
            # Analyze problematic sequences in the text
            problematic_sequences = []
            escape_sequences = ['\\"', "\\'", '\\n', '\\t', '\\\\']
            for seq in escape_sequences:
                count = raw_student_response.count(seq)
                if count > 0:
                    problematic_sequences.append(f"- Found {count} occurrence(s) of '{seq}' - MUST keep as '{seq}' (DO NOT convert)")
            
            warning_text = ""
            if problematic_sequences:
                warning_text = f"""
⚠️ CRITICAL WARNING - ESCAPE SEQUENCES DETECTED:
{chr(10).join(problematic_sequences)}
These sequences are LITERAL TEXT, not formatting commands. Keep them EXACTLY as shown.
"""
            
            enhanced_user_prompt = f"""
Here is the student's response that needs to be analyzed:

ORIGINAL TEXT (analyze this text):
{raw_student_response}

BASE64 ENCODED VERSION (for exact character reference):
{encoded_student_response}
{warning_text}
CRITICAL INSTRUCTIONS FOR ANNOTATION:
1. The student's response has EXACTLY {len(raw_student_response)} characters
2. Use ONLY the ORIGINAL TEXT above for creating your annotated response
3. The BASE64 version is provided for exact character verification - decode it if needed to verify exact characters
4. CRITICAL: If the original has \\n (backslash-n), keep it as \\n, NOT as actual newline
5. Only add <tag id="X">phrase</tag> markers - do not change any other characters
6. The text between tags must be IDENTICAL to the original, character-by-character
7. After removing tags, your annotated response must have exactly {len(raw_student_response)} characters

FORBIDDEN TRANSFORMATIONS - THESE WILL BREAK THE SYSTEM:
❌ \\" → " (NEVER convert escaped quotes to regular quotes)
❌ \\' → ' (NEVER convert escaped apostrophes to regular apostrophes)  
❌ \\n → actual newline (NEVER convert literal \\n to line break)
❌ \\t → actual tab (NEVER convert literal \\t to tab character)
❌ \\\\ → \\ (NEVER convert double backslash to single)

CORRECT EXAMPLES:
✅ If original has: 'She said \\"Hello\\" to me'
✅ Your output: 'She said \\"Hello\\" to me' (keep \\" as \\")
✅ If original has: 'It\\'s a nice day'  
✅ Your output: 'It\\'s a nice day' (keep \\' as \\')

CHARACTER COUNT VERIFICATION:
- Original text has {len(raw_student_response)} characters
- After removing your tags, result MUST have {len(raw_student_response)} characters
- If counts don't match, you made a forbidden transformation

QUOTE PRESERVATION REQUIREMENTS:
- Copy punctuation marks EXACTLY from the original text

Please analyze the student's response and provide feedback while preserving the text exactly.
"""
        else:
            # Mode "wo" - WITHOUT base64 encoding and character counting  
            # Analyze problematic sequences in the text
            problematic_sequences = []
            escape_sequences = ['\\"', "\\'", '\\n', '\\t', '\\\\']
            for seq in escape_sequences:
                count = raw_student_response.count(seq)
                if count > 0:
                    problematic_sequences.append(f"- Found {count} occurrence(s) of '{seq}' - MUST keep as '{seq}' (DO NOT convert)")
            
            warning_text = ""
            if problematic_sequences:
                warning_text = f"""
⚠️ CRITICAL WARNING - ESCAPE SEQUENCES DETECTED:
{chr(10).join(problematic_sequences)}
These sequences are LITERAL TEXT, not formatting commands. Keep them EXACTLY as shown.
"""
            
            enhanced_user_prompt = f"""
Here is the student's response that needs to be analyzed:

ORIGINAL TEXT (analyze this text):
{raw_student_response}
{warning_text}
CRITICAL INSTRUCTIONS FOR ANNOTATION:
1. Only add <tag id="X">phrase</tag> markers - do not change any other characters
2. The text between tags must be IDENTICAL to the original, character-by-character

FORBIDDEN TRANSFORMATIONS - THESE WILL BREAK THE SYSTEM:
❌ \\" → " (NEVER convert escaped quotes to regular quotes)
❌ \\' → ' (NEVER convert escaped apostrophes to regular apostrophes)  
❌ \\n → actual newline (NEVER convert literal \\n to line break)
❌ \\t → actual tab (NEVER convert literal \\t to tab character)
❌ \\\\ → \\ (NEVER convert double backslash to single)

CORRECT EXAMPLES:
✅ If original has: 'She said \\"Hello\\" to me'
✅ Your output: 'She said \\"Hello\\" to me' (keep \\" as \\")
✅ If original has: 'It\\'s a nice day'  
✅ Your output: 'It\\'s a nice day' (keep \\' as \\')

Please analyze the student's response and provide feedback while preserving the text exactly.
"""
        
        # Get annotations using the working system_user function
        response = get_annotations_system_user(enhanced_system_prompt, enhanced_user_prompt, model)
        
        # Parse response for validation - ALWAYS validate for both w and wo modes
        if raw_student_response:
            if isinstance(response, str):
                response_dict = json.loads(response)
            else:
                response_dict = response
            
            annotated_response = response_dict.get("annotated_response", "")
            
            # Validate preservation for both modes
            is_valid, error_info = validate_annotation_preservation(annotated_response, raw_student_response)
            
            if not is_valid:
                # Store validation error but don't retry (for both w and wo modes)
                response_dict["validation_failed"] = True
                response_dict["validation_error"] = error_info
                return json.dumps(response_dict)
        
        return response
        
    except Exception as e:
        print(f"Error in get_annotations_single_call: {e}")
        return json.dumps({"error": f"Processing failed: {str(e)}"})

def generate_output_filename(model_name, char_mode, output_dir):
    """Generate an output filename based on model name, character mode, and timestamp."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Clean up model name for the filename
    if model_name.startswith("gpt-4o"):
        model_short = "gpt4o"
    elif model_name.startswith("claude"):
        model_short = "claude"
    else:
        model_short = "model"
    
    char_suffix = "with_char" if char_mode == "w" else "wo_char"
        
    return os.path.join(output_dir, f"{model_short}_single_{char_suffix}_{timestamp}.csv")

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

def process_csv_file(input_csv_path, model_name="gpt-4o-2024-08-06", char_mode="w", start_row=1, end_row=None):
    """
    Process a CSV file line by line and send each line to the API using single call method.
    
    Args:
        input_csv_path (str): Path to the input CSV file
        model_name (str): Name of the model to use for processing
        char_mode (str): Character validation mode - 'w' for with, 'wo' for without
        start_row (int): Row number to start processing from (1-based, excluding header)
        end_row (int): Row number to end processing at (1-based, inclusive, None for all rows)
    """
    # Create output directory in the same location as input file
    output_dir = os.path.dirname(input_csv_path)
    output_csv_path = generate_output_filename(model_name, char_mode, output_dir)
    
    # Determine if character validation should be enabled
    enable_char_validation = (char_mode == "w")
    
    # Open input and output CSV files
    with open(input_csv_path, 'r', encoding='utf-8') as input_file, \
         open(output_csv_path, 'w', encoding='utf-8', newline='') as output_file:
        
        # Create CSV reader and writer
        csv_reader = csv.DictReader(input_file)
        csv_writer = csv.writer(output_file)
        
        # Write header to output CSV
        csv_writer.writerow(["students_response", "annotated_response", "feedback_list", "model", "char_validation", "warnings", "model_details"])
        
        # Process each row with row range control
        current_row = 0
        for row in csv_reader:
            current_row += 1
            
            # Skip rows before start_row
            if current_row < start_row:
                continue
                
            # Stop processing if we've reached end_row
            if end_row is not None and current_row > end_row:
                break
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
                
                # Get annotations using single call
                response = get_annotations_single_call(
                    system_prompt, 
                    user_prompt, 
                    model=model_name,
                    enable_char_validation=enable_char_validation,
                    raw_student_response=students_response
                )
                
                # Always run check_results to fix any issues
                response = check_results(response, students_response)
                
                # Parse JSON response
                response_dict = {}
                if isinstance(response, str):
                    if response.startswith("No") and "Claude" in response:
                        raise Exception(response)
                    try:
                        response_dict = json.loads(response)
                        if "error" in response_dict:
                            warnings.append(response_dict["error"])
                        if "warning" in response_dict:
                            warnings.append(response_dict["warning"])
                        # Capture validation errors if present
                        if response_dict.get("validation_failed", False) and "validation_error" in response_dict:
                            warnings.append(f"Character validation failed: {response_dict['validation_error']}")
                    except json.JSONDecodeError as e:
                        raise Exception(f"Failed to parse JSON response: {e}, Response: {response[:100]}...")
                elif isinstance(response, dict):
                    response_dict = response
                    if "error" in response_dict:
                        warnings.append(response_dict["error"])
                    if "warning" in response_dict:
                        warnings.append(response_dict["warning"])
                    # Capture validation errors if present
                    if response_dict.get("validation_failed", False) and "validation_error" in response_dict:
                        warnings.append(f"Character validation failed: {response_dict['validation_error']}")
                else:
                    raise Exception(f"Unexpected response type: {type(response)}")
                
                # Extract data from response
                annotated_response = response_dict.get("annotated_response", "")
                feedback_list = response_dict.get("feedback_list", [])
                
                # Enhanced Chinese character handling
                try:
                    if isinstance(feedback_list, str):
                        feedback_list = json.loads(feedback_list)
                    
                    # Fix Unicode encoding issues in Chinese feedback
                    if isinstance(feedback_list, list):
                        for item in feedback_list:
                            if isinstance(item, dict):
                                for key, value in item.items():
                                    if isinstance(value, str):
                                        try:
                                            decoded_value = value.encode().decode('unicode_escape').encode('latin1').decode('utf-8')
                                            if decoded_value != value:
                                                item[key] = decoded_value
                                        except:
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
                
                # Final tag count check
                tag_count_in_response = annotated_response.count("<tag id=")
                if tag_count_in_response != len(feedback_list) and not any("Mismatch in tag count" in warning for warning in warnings):
                    warning_msg = f"Mismatch in tag count. Feedback list has {len(feedback_list)} items, but annotated response has {tag_count_in_response} tags."
                    warnings.append(warning_msg)
                    print(f"Warning: {warning_msg}")
                
                # Get a friendly model name for display
                model_details = model_name
                if model_name.startswith("gpt-4o"):
                    model_details = "GPT-4o"
                elif model_name.startswith("claude"):
                    model_details = "Claude 4 Sonnet"
                
                # Join warnings into a single string
                warnings_str = "; ".join(warnings) if warnings else ""
                
                # Ensure proper UTF-8 encoding for Chinese characters in JSON
                try:
                    feedback_json = json.dumps(feedback_list, ensure_ascii=False)
                except Exception as e:
                    print(f"Warning: Failed to encode Chinese characters in JSON: {e}")
                    feedback_json = json.dumps(feedback_list)
                
                # Write to output CSV
                csv_writer.writerow([
                    students_response,
                    annotated_response,
                    feedback_json,
                    model_name,
                    char_mode,
                    warnings_str,
                    model_details
                ])
                
                print(f"Processed row {current_row} with model {model_name}, char_validation={enable_char_validation}, student response: {students_response[:30]}...")
                
            except Exception as e:
                print(f"Error processing row {current_row} with {model_name}, char_validation={enable_char_validation}: {e}")
                # Write error row
                csv_writer.writerow([
                    row.get("students_response", ""),
                    f"Error: {str(e)}",
                    "[]",
                    model_name,
                    char_mode,
                    str(e),
                    model_name
                ])
    
    print(f"Processing complete. Processed rows {start_row} to {end_row if end_row else 'end'}. Output saved to: {output_csv_path}")
    return output_csv_path

def run_all_combinations(input_csv_path, char_mode="w", start_row=1, end_row=None):
    """Run all combinations of the 2 models with the specified character validation mode."""
    models = [
        "gpt-4o-2024-08-06",
        "claude-sonnet-4-20250514"
    ]
    
    results = {}
    
    # Using concurrent.futures to process combinations in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        future_to_combo = {}
        
        # Submit all tasks for the specified character mode
        for model in models:
            future = executor.submit(process_csv_file, input_csv_path, model, char_mode, start_row, end_row)
            future_to_combo[future] = (model, char_mode)
        
        # Process results as they complete
        for future in concurrent.futures.as_completed(future_to_combo):
            model, char_mode = future_to_combo[future]
            try:
                output_path = future.result()
                results[(model, char_mode)] = output_path
                print(f"Completed: {model} with character validation {char_mode}")
            except Exception as e:
                print(f"Error with {model}, char_validation {char_mode}: {e}")
    
    return results

def main():
    """Main function to process CSV data with single call API and character validation options."""
    # Get the directory containing the current script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description='AI Feedback Assistant (AFA): Process student responses with single call API using GPT-4o and Claude Sonnet 4',
        epilog='''
Examples:
  python main_bulk.py                                     # Process all models with character validation (default)
  python main_bulk.py --csv my_data.csv --model gpt4o     # Process only with GPT-4o model with character validation
  python main_bulk.py --char wo                           # Process all models without character validation
  python main_bulk.py --model claude --char wo            # Process only Claude without character validation
  python main_bulk.py --start 10 --end 20                 # Process only rows 10-20
  python main_bulk.py --rows 5:15                         # Process rows 5-15 (alternative syntax)
  python main_bulk.py --rows 25:                          # Process from row 25 to end
  python main_bulk.py --rows 8                            # Process only row 8
  python main_bulk.py --count                             # Count total rows and exit
        '''
    )
    parser.add_argument('--csv', 
                      help='Path to input CSV file with student responses (defaults to afa_data.csv in the current directory)')
    parser.add_argument('--model', choices=['gpt4o', 'claude', 'all'], default='all', 
                      help='''Model to use for processing:
                      gpt4o: GPT-4o (OpenAI)
                      claude: Claude 4 Sonnet (Anthropic)
                      all: Run with both models (default)''')
    parser.add_argument('--char', choices=['w', 'wo'], default='w',
                      help='''Character validation mode:
                      w: With character counting validation (default)
                      wo: Without character counting validation''')
    parser.add_argument('--start', type=int, default=1,
                      help='Row number to start processing from (1-based, excluding header row, default: 1)')
    parser.add_argument('--end', type=int, default=None,
                      help='Row number to end processing at (1-based, inclusive, default: process all rows)')
    parser.add_argument('--rows', type=str, default=None,
                      help='Row range in format "start:end" (e.g., "5:10" for rows 5-10, "5:" for row 5 to end)')
    parser.add_argument('--count', action='store_true',
                      help='Count total rows in the CSV file and exit (useful for planning row ranges)')
    
    args = parser.parse_args()
    
    # Map argument choices to actual model names
    model_mapping = {
        'gpt4o': 'gpt-4o-2024-08-06',
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
        
        # Handle row counting
        if args.count:
            with open(input_csv, 'r', encoding='utf-8') as f:
                csv_reader = csv.DictReader(f)
                row_count = sum(1 for _ in csv_reader)
                print(f"Total rows in CSV (excluding header): {row_count}")
                return
        
        # Parse row range arguments
        start_row = args.start
        end_row = args.end
        
        # Handle --rows argument (overrides --start and --end)
        if args.rows:
            try:
                if ':' in args.rows:
                    start_str, end_str = args.rows.split(':', 1)
                    start_row = int(start_str) if start_str else 1
                    end_row = int(end_str) if end_str else None
                else:
                    # Single row number
                    start_row = end_row = int(args.rows)
            except ValueError:
                raise ValueError(f"Invalid row range format: {args.rows}. Use format 'start:end' or single number")
        
        # Validate row range
        if start_row < 1:
            raise ValueError("Start row must be 1 or greater")
        if end_row is not None and end_row < start_row:
            raise ValueError("End row must be greater than or equal to start row")
        
        print(f"Processing rows {start_row} to {end_row if end_row else 'end'}")
        
        # Process according to arguments
        if args.model == 'all':
            # Run all combinations with the specified character mode
            results = run_all_combinations(input_csv, args.char, start_row, end_row)
            for (model, char_mode), output_path in results.items():
                print(f"Results for {model} with character validation {char_mode} saved to: {output_path}")
        else:
            # Run specific model with specified character mode
            model = model_mapping[args.model]
            output_path = process_csv_file(input_csv, model, args.char, start_row, end_row)
            print(f"Results for {model} with character validation {args.char} saved to: {output_path}")
        
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()