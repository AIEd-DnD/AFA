# CSV Processing for AFA

This document describes how to use the CSV processing functionality to analyze student responses in bulk.

## Overview

The CSV processor allows you to process multiple student responses from a CSV file. The system will:

1. Read each row from the input CSV file
2. Process each student response using the annotation system
3. Output the results to a new CSV file with the student's response, annotated response, and feedback list

## Expected CSV Format

The input CSV file should have the following columns:
- `s/n` - Serial number
- `subject` - Subject (e.g., "English")
- `level` - Education level (e.g., "Primary 6")
- `question` - The question/prompt given to students
- `students_response` - The student's response to be analyzed
- `recipe` - Recipe for analysis (optional)
- `suggested_answer` - Suggested answer (optional)
- `rubrics` - Rubrics for evaluation (optional)
- `error_tags` - Error tags to use in the analysis (optional)

## Usage

### Method 1: Using the process_csv.py Script

```bash
python AFA_V2/process_csv.py [path_to_csv]
```

Where `[path_to_csv]` is the path to your input CSV file. If not provided, it will default to `afa_data.csv` in the current directory.

### Method 2: Using main_bulk.py Directly

```bash
python AFA_V2/main_bulk.py --process-csv [path_to_csv]
```

## Output

The system will create a new CSV file with a timestamp in the name (e.g., `afa_data_output_20240515_123045.csv`). The output CSV will contain three columns:

1. `students_response` - The original student response
2. `annotated_response` - The annotated response with tags
3. `feedback_list` - A JSON string containing the feedback list

## Example

```bash
# Process a CSV file named "my_data.csv"
python AFA_V2/process_csv.py my_data.csv

# Process the default "afa_data.csv" file
python AFA_V2/process_csv.py
``` 