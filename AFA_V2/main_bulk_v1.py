import yaml
import os
import sys
import openai
import resources as rsrc
import csv
import json
from dotenv import load_dotenv
from datetime import datetime

# Update path to find .env in parent directory
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
load_dotenv(dotenv_path)
openai_api_key = os.getenv("OPENAI_API_KEY")
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

def get_annotations_system_user(assembled_system_prompt, assembled_user_prompt):
   response = client.chat.completions.create(
     model="gpt-4o-2024-08-06",
     #model="o3-mini",
     #reasoning_effort="medium",
     temperature = 0.1, #temperature is only available to gpt models
     max_tokens = 16000, #max tokens is only available to gpt models, default max tokens is 4000. this parameter is being deprecated in favour of max_completion_tokens
     #max_completion_tokens=8000,
     tools = rsrc.tools,
     tool_choice={"type": "function", "function": {"name": "get_annotated_feedback"}},
     messages = [{"role":"system","content":assembled_system_prompt},{"role": "user", "content": assembled_user_prompt}]
   )
   return response.choices[0].message.tool_calls[0].function.arguments


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



def process_csv_file(input_csv_path):
    """
    Process a CSV file line by line and send each line to the get_annotations_system_user function.
    Output the results to a new CSV file with student_response, annotated_response, and feedback_list columns.
    
    Args:
        input_csv_path (str): Path to the input CSV file
    """
    # Create output file path based on input file name with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Extract base name without extension and directory
    base_name = os.path.splitext(os.path.basename(input_csv_path))[0]
    
    # Create output path in the same directory as the input file
    output_dir = os.path.dirname(input_csv_path)
    output_csv_path = os.path.join(output_dir, f"{base_name}_output_{timestamp}.csv")
    
    # Open input and output CSV files
    with open(input_csv_path, 'r', encoding='utf-8') as input_file, \
         open(output_csv_path, 'w', encoding='utf-8', newline='') as output_file:
        
        # Create CSV reader and writer
        csv_reader = csv.DictReader(input_file)
        csv_writer = csv.writer(output_file)
        
        # Write header to output CSV
        csv_writer.writerow(["students_response", "annotated_response", "feedback_list"])
        
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
                
                # Get annotations
                response = get_annotations_system_user(system_prompt, user_prompt)
                
                # Parse JSON response
                response_dict = json.loads(response)
                
                # Extract data from response
                annotated_response = response_dict.get("annotated_response", "")
                feedback_list = response_dict.get("feedback_list", [])
                
                # Write to output CSV
                csv_writer.writerow([
                    students_response,
                    annotated_response,
                    json.dumps(feedback_list)
                ])
                
                print(f"Processed row with student response: {students_response[:30]}...")
                
            except Exception as e:
                print(f"Error processing row: {e}")
                # Write error row
                csv_writer.writerow([
                    row.get("students_response", ""),
                    f"Error: {str(e)}",
                    "[]"
                ])
    
    print(f"Processing complete. Output saved to: {output_csv_path}")
    return output_csv_path

def main():
    """Main function to load and analyze YAML data."""
    # Get the directory containing the current script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    try:
        # Check if the command-line argument for CSV processing is provided
        if len(sys.argv) > 1 and sys.argv[1] == "--process-csv":
            # Use command-line parameter for input CSV file if provided, otherwise use default
            if len(sys.argv) > 2:
                # Check if the provided path is absolute or relative
                input_csv = sys.argv[2]
                if not os.path.isabs(input_csv) and not os.path.isfile(input_csv):
                    # Try relative to script directory
                    alt_path = os.path.join(current_dir, input_csv)
                    if os.path.isfile(alt_path):
                        input_csv = alt_path
            else:
                # Default path is in the AFA_V2 directory
                input_csv = os.path.join(current_dir, "afa_data.csv")
            
            # Check if file exists
            if not os.path.isfile(input_csv):
                raise FileNotFoundError(f"CSV file not found: {input_csv}")
                
            # Process the CSV file
            output_csv = process_csv_file(input_csv)
            print(f"CSV processing complete. Results saved to: {output_csv}")
        else:   
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
            
            
            # Original functionality - process single response from YAML
            system_msg = assemble_system_prompt(subject, level, question, error_tags=error_tags_str)
            user_msg = assemble_user_prompt(el_response)
            response = get_annotations_system_user(system_msg, user_msg)
            print(response)
         
    except FileNotFoundError as e:
        print(f"Error: File not found: {e}")
    except yaml.YAMLError as e:
        print(f"Error parsing the YAML file: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
