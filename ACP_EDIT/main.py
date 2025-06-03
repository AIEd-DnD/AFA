import json
import os
import argparse
from openai import OpenAI
from typing import Dict, List, Any
from dotenv import load_dotenv
import openai

# Update path to find .env in parent directory
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
load_dotenv(dotenv_path)
openai_api_key = os.getenv("OPENAI_API_KEY")
anthropic_key = os.getenv("ANTHROPIC_API_KEY")
client = openai.OpenAI(api_key=openai_api_key)


class LessonGenerator:
    def __init__(self, use_reasoning=True):
        # Initialize OpenAI client
        # Make sure to set your OPENAI_API_KEY environment variable
        self.client = openai.OpenAI(api_key=openai_api_key)
        self.use_reasoning = use_reasoning
        self.reasoning_model = "o4-mini"
        self.non_reasoning_model = "gpt-4o-mini-2024-07-18"
        
        # Display which mode is being used
        if self.use_reasoning:
            print(f"Using REASONING model: {self.reasoning_model}")
        else:
            print(f"Using NON-REASONING model: {self.non_reasoning_model}")
        
    def get_lesson_details(self) -> Dict[str, str]:
        """Get lesson details from user input"""
        print("=" * 60)
        print("LESSON GENERATOR - Please provide the following details:")
        print("=" * 60)
        
        lesson_title = input("1. Lesson Title: ")
        subject = input("2. Subject (e.g., Chemistry, Geography, Math): ")
        topic = input("3. Topic (specific topic to cover): ")
        level_grade = input("4. Level/Grade (e.g., Secondary 1, Grade 8): ")
        additional_instructions = input("5. Additional Instructions (optional - any specific requirements, learning objectives, or teaching approaches): ")
        
        print("\n" + "=" * 60)
        print("LESSON STRUCTURE CONFIGURATION:")
        print("=" * 60)
        
        # Get number of sections
        while True:
            try:
                num_sections = int(input("6. Number of sections (1-5): "))
                if 1 <= num_sections <= 5:
                    break
                else:
                    print("Please enter a number between 1 and 5.")
            except ValueError:
                print("Please enter a valid number.")
        
        # Get max activities per section
        while True:
            try:
                max_activities = int(input("7. Maximum activities per section (1-5): "))
                if 1 <= max_activities <= 5:
                    break
                else:
                    print("Please enter a number between 1 and 5.")
            except ValueError:
                print("Please enter a valid number.")
        
        return {
            "lesson_title": lesson_title,
            "subject": subject,
            "topic": topic,
            "level_grade": level_grade,
            "additional_instructions": additional_instructions,
            "num_sections": num_sections,
            "max_activities": max_activities
        }
    
    def _make_api_call(self, prompt: str, step_name: str):
        """Make API call with either reasoning or non-reasoning model"""
        try:
            if self.use_reasoning:
                # Use reasoning model (o4-mini)
                response = self.client.responses.create(
                    model=self.reasoning_model,
                    input=prompt,
                    reasoning={"effort": "medium", "summary": "auto"},
                    max_output_tokens=16000,
                )
                
                print(f"REASONING SUMMARY ({step_name}):")
                print("-" * 40)
                # Extract reasoning summary from the response
                reasoning_items = [item for item in response.output if item.type == 'reasoning']
                if reasoning_items and reasoning_items[0].summary:
                    for summary in reasoning_items[0].summary:
                        print(summary.text)
                else:
                    print(f"The AI is reasoning through {step_name} internally...")
                
                reasoning_summary = reasoning_items[0].summary[0].text if reasoning_items and reasoning_items[0].summary else f"Internal reasoning by {self.reasoning_model} model"
                output_text = response.output_text
                
            else:
                # Use non-reasoning model (gpt-4o-mini-2024-07-18)
                response = self.client.responses.create(
                    model=self.non_reasoning_model,
                    input=[{"role": "user", "content": prompt}],
                    max_output_tokens=16000,
                )
                
                print(f"MODEL OUTPUT ({step_name}):")
                print("-" * 40)
                print(f"Using {self.non_reasoning_model} without reasoning...")
                
                reasoning_summary = f"No reasoning - using {self.non_reasoning_model} model"
                # Fix: Handle the response structure correctly for non-reasoning model
                if hasattr(response, 'output_text'):
                    output_text = response.output_text
                elif hasattr(response, 'output') and response.output:
                    # Handle list of ResponseOutputText objects
                    if isinstance(response.output, list) and len(response.output) > 0:
                        output_text = response.output[0].text
                    else:
                        output_text = str(response.output)
                else:
                    output_text = str(response)
            
            print(f"\n{step_name.upper()} GENERATED:")
            print("-" * 40)
            print(output_text)
            
            return output_text, reasoning_summary
            
        except Exception as e:
            print(f"Error in API call for {step_name}: {e}")
            return None, f"Error: {str(e)}"
    
    def generate_high_level_plan(self, lesson_details: Dict[str, str]) -> Dict[str, Any]:
        """Generate a high-level lesson plan based on KAT framework for teacher review"""
        print("\n" + "=" * 60)
        print("STEP 1: GENERATING HIGH-LEVEL LESSON PLAN")
        print("=" * 60)
        
        prompt = f"""
        <Role>As an experienced education coach in Singapore proficient in e-Pedagogy, your role is to create a high-level lesson plan outline that references the e-pedagogy framework and active learning principles. Focus on strategic planning using the KAT framework.</Role>

        <Context>You are creating a strategic overview of a lesson before detailed planning. This high-level plan will help teachers understand the overall approach and make modifications before detailed activity generation.</Context>

        Using the following information:

        Module title: {lesson_details['lesson_title']}
        Subject: {lesson_details['subject']}
        Topic: {lesson_details['topic']}
        Level/Grade: {lesson_details['level_grade']}
        Number of sections: {lesson_details['num_sections']}
        Number of activities per section: {lesson_details['max_activities']}
        Additional Instructions: {lesson_details['additional_instructions']}

        Create a high-level lesson plan outline that focuses on strategic pedagogical decisions.

        Your output should only be rich text, do not include hyperlinks, code snippets, mathematical formulas or xml.

        Structure your response as follows:

        **LESSON OVERVIEW:**
        [Provide a comprehensive lesson overview of 3-4 sentences describing the main learning journey]

        **RECOMMENDED KEY APPLICATIONS OF TECHNOLOGY (KAT):**
        Select exactly 2 KAT from this list that are most relevant: Foster conceptual change; Support assessment for learning; Facilitate learning together; Develop metacognition; Provide differentiation; Embed scaffolding; Enable personalization; Increase motivation.

        1. [First KAT] - [Detailed explanation of why this KAT is essential for this topic and how it will be implemented]
        2. [Second KAT] - [Detailed explanation of why this KAT is essential for this topic and how it will be implemented]

        **PEDAGOGICAL APPROACH:**
        [Describe the overall pedagogical strategy, interaction patterns, and learning progression]

        **HIGH-LEVEL SECTION BREAKDOWN:**
        
        Section 1: [Title and Purpose]
        - Main Learning Focus: [What students will learn]
        - Pedagogical Strategy: [How learning will be facilitated]
        - KAT Implementation: [How the selected KAT will be applied]
        
        Section 2: [Title and Purpose]
        - Main Learning Focus: [What students will learn]
        - Pedagogical Strategy: [How learning will be facilitated]
        - KAT Implementation: [How the selected KAT will be applied]

        [Continue for all {lesson_details['num_sections']} sections]

        **ASSESSMENT STRATEGY:**
        [Describe how student learning will be monitored and assessed throughout the lesson]

        **POTENTIAL SLS TOOLS RECOMMENDATION:**
        [Suggest 3-4 SLS tools that align with the pedagogical approach and KAT implementation]
        """
        
        output_text, reasoning_summary = self._make_api_call(prompt, "high-level planning")
        
        if output_text:
            plan_data = {
                "lesson_details": lesson_details,
                "high_level_plan": output_text,
                "plan_reasoning_summary": reasoning_summary,
                "model_used": self.reasoning_model if self.use_reasoning else self.non_reasoning_model
            }
            
            return plan_data
        else:
            return {"error": reasoning_summary}
    
    def get_teacher_feedback_on_plan(self, plan_data: Dict[str, Any]) -> str:
        """Allow teacher to review and provide feedback on the high-level plan"""
        print("\n" + "=" * 60)
        print("HIGH-LEVEL PLAN REVIEW")
        print("=" * 60)
        print("Please review the high-level plan above.")
        print("You can now provide additional instructions or modifications.")
        print("These will be incorporated when generating detailed sections and activities.")
        print("\nExamples of modifications you might want:")
        print("- Adjust the pedagogical approach")
        print("- Change the focus of specific sections")
        print("- Add specific content requirements")
        print("- Modify assessment strategies")
        print("- Request different interaction patterns")
        print("=" * 60)
        
        teacher_feedback = input("\nAdditional instructions or modifications (press Enter if no changes needed): ")
        
        if teacher_feedback.strip():
            print(f"\n✓ Teacher feedback recorded: {teacher_feedback}")
        else:
            print("\n✓ No modifications requested - proceeding with original plan")
            teacher_feedback = "No additional modifications requested."
        
        return teacher_feedback

    def generate_sections(self, lesson_details: Dict[str, str], high_level_plan: str = "", teacher_feedback: str = "") -> Dict[str, Any]:
        """Generate lesson sections using selected model with KAT framework and high-level plan"""
        print("\n" + "=" * 60)
        print("STEP 2: GENERATING DETAILED LESSON SECTIONS")
        print("=" * 60)
        
        plan_context = ""
        if high_level_plan:
            plan_context = f"""
        
        IMPORTANT: Base your detailed sections on this approved high-level plan:
        
        {high_level_plan}
        
        Teacher's additional feedback/modifications:
        {teacher_feedback}
        
        Ensure your detailed sections align with the pedagogical approach and KAT implementation outlined in the high-level plan above.
        """
        
        prompt = f"""
        <Role>As an experienced education coach in Singapore proficient in e-Pedagogy, your role is to create detailed lesson sections that implement the approved high-level plan and incorporate teacher feedback.</Role>

        <Context>You are now creating detailed lesson sections based on a previously approved high-level plan. The sections should implement the pedagogical strategies and KAT framework outlined in the plan.</Context>

        Using the following information:

        Module title: {lesson_details['lesson_title']}
        Subject: {lesson_details['subject']}
        Topic: {lesson_details['topic']}
        Level/Grade: {lesson_details['level_grade']}
        Number of sections: {lesson_details['num_sections']}
        Number of activities per section: {lesson_details['max_activities']}
        Additional Instructions: {lesson_details['additional_instructions']}
        {plan_context}

        Create detailed lesson sections that implement the high-level plan. 

        IMPORTANT: You must create EXACTLY {lesson_details['num_sections']} sections, and each section will later have EXACTLY {lesson_details['max_activities']} activities.

        Your output should only be rich text, do not include hyperlinks, code snippets, mathematical formulas or xml.

        Structure your response as follows:

        **LESSON DESCRIPTION:**
        [Provide a lesson description of maximum 5 sentences that describes the lesson to the student]

        **CONFIRMED KEY APPLICATIONS OF TECHNOLOGY (KAT):**
        [List the 2 KAT from the high-level plan and confirm their implementation]

        **DETAILED LESSON SECTIONS:**

        Section 1: [Title]
        - Learning Objectives: [List specific learning objectives for this section]
        - Description: [Detailed description implementing the high-level plan]
        - Pedagogical Approach: [Specific teaching strategies to be used]
        - Teacher Notes: [Implementation guidance for teachers]
        - KAT Connection: [How this section implements the selected Key Applications of Technology]

        Section 2: [Title]
        - Learning Objectives: [List specific learning objectives for this section]
        - Description: [Detailed description implementing the high-level plan]
        - Pedagogical Approach: [Specific teaching strategies to be used]
        - Teacher Notes: [Implementation guidance for teachers]
        - KAT Connection: [How this section implements the selected Key Applications of Technology]

        [Continue for all {lesson_details['num_sections']} sections]
        """
        
        output_text, reasoning_summary = self._make_api_call(prompt, "detailed sections")
        
        if output_text:
            # Parse the response into structured format
            sections_data = {
                "lesson_details": lesson_details,
                "high_level_plan": high_level_plan,
                "teacher_feedback": teacher_feedback,
                "sections_response": output_text,
                "reasoning_summary": reasoning_summary,
                "model_used": self.reasoning_model if self.use_reasoning else self.non_reasoning_model
            }
            
            return sections_data
        else:
            return {"error": reasoning_summary}

    def generate_activities(self, sections_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate activities for each section using selected model with KAT framework and approved plan"""
        print("\n" + "=" * 60)
        print("STEP 3: GENERATING DETAILED ACTIVITIES")
        print("=" * 60)
        
        lesson_details = sections_data['lesson_details']
        sections_response = sections_data['sections_response']
        high_level_plan = sections_data.get('high_level_plan', '')
        teacher_feedback = sections_data.get('teacher_feedback', '')
        
        plan_context = ""
        if high_level_plan:
            plan_context = f"""
        
        IMPORTANT: Base your activities on this approved high-level plan and teacher feedback:
        
        HIGH-LEVEL PLAN:
        {high_level_plan}
        
        TEACHER FEEDBACK:
        {teacher_feedback}
        
        Ensure your activities implement the pedagogical strategies outlined in the plan.
        """
        
        prompt = f"""
        <Role>As an experienced education coach in Singapore proficient in e-Pedagogy, your role is to create detailed activities that implement the approved high-level plan and detailed sections.</Role>

        <Context>You are creating specific learning activities that implement the pedagogical strategies from the approved high-level plan and align with the detailed lesson sections.</Context>

        Based on the following approved lesson sections:
        
        {sections_response}
        {plan_context}
        
        Using the following information:
        Module title: {lesson_details['lesson_title']}
        Subject: {lesson_details['subject']}
        Topic: {lesson_details['topic']}
        Level/Grade: {lesson_details['level_grade']}
        Number of sections: {lesson_details['num_sections']}
        Number of activities per section: {lesson_details['max_activities']}
        Additional Instructions: {lesson_details['additional_instructions']}

        CRITICAL REQUIREMENTS:
        1. You must create EXACTLY {lesson_details['max_activities']} activities for EACH of the {lesson_details['num_sections']} sections
        2. Total activities = {lesson_details['num_sections']} sections × {lesson_details['max_activities']} activities = {lesson_details['num_sections'] * lesson_details['max_activities']} activities
        3. Each activity must be clearly numbered (Activity 1, Activity 2, etc.)
        4. Activities must implement the pedagogical approach from the high-level plan

        First, select NOT MORE than 4 unique SLS tools from this list for the overall lesson: Text/Media, Progressive Quiz, Auto-graded Quiz, Teacher-marked Quiz, Multiple-Choice/ Multiple-Response Question, Fill-in-the-blank Question, Click and Drop Question, Error Editing Question, Free Response Question, Audio Response Question, Rubrics, Tooltip, Interactive Thinking Tool, Poll, Discussion Board, Team Activities, Subgroups, Add Section Prerequisites, Set Differentiated Access, Gamification - Create Game Stories and Achievements, Gamification - Create Game Teams, Set Optional Activities and Quizzes, Speech Evaluation, Chinese Language E-Dictionary, Embed Canva, Embed Nearpod, Embed Coggle, Embed Genial.ly, Embed Quizizz, Embed Kahoot, Embed Google Docs, Embed Google Sheets, Embed Mentimeter, Embed YouTube Videos, Embed Padlet, Embed Gapminder, Embed GeoGebra, Feedback Assistant Mathematics (FA-Math), Speech Evaluation, Text-to-Speech, Embed Book Creator, Embed Simulations, Adaptive Learning System (ALS), Embed ArcGIS Storymap, Embed ArcGIS Digital Maps, Embed PhET Simulations, Embed Open Source Physics @ Singapore Simulations, Embed CK12 Simulations, Embed Desmos, Short Answer Feedback Assistant (ShortAnsFA), Gamification - Quiz leaderboard and ranking, Gamification - Create branches in game stories, Monitor Assignment Page, Insert Transcript for Video & Audio, Insert Student Tooltip, Add Notes to Audio or Video, Data Assistant, Annotated Feedback Assistant (AFA), Learning Assistant (LEA), SLS Digital Badges.

        Your output should only be rich text, do not include hyperlinks, code snippets, mathematical formulas or xml.

        Please structure your response in the following format:

        **SELECTED SLS TOOLS FOR THIS LESSON:**
        [List the 4 selected SLS tools and briefly explain why each was chosen based on the high-level plan]

        **CONFIRMED KEY APPLICATIONS OF TECHNOLOGY (KAT):**
        [List the 2 KAT from the high-level plan and explain their implementation across activities]

        **LESSON PLAN ACTIVITIES:**

        For each activity, provide the following information in this exact format:

        Activity [Number]: [Activity Title]
        Section: [Which section this belongs to]
        Interaction Type: [Student-Student/Teacher-Student/Student-Community/Student-Content]
        Duration: [X minutes]
        Learning Objectives:
        • [Objective 1]
        • [Objective 2]

        Instructions:
        [Detailed step-by-step instructions for students implementing the pedagogical approach]

        KAT Alignment:
        [How this activity implements the selected Key Applications of Technology from the plan]

        SLS Tools:
        [List of specific SLS tools used in this activity]

        Data Analysis:
        [Monitoring tools and methods for tracking learning progress]

        Teaching Notes:
        [Implementation guidance for teachers based on the approved pedagogical approach]

        ---

        IMPORTANT: 
        - You must create exactly {lesson_details['num_sections'] * lesson_details['max_activities']} activities total
        - Number activities sequentially (Activity 1, Activity 2, Activity 3, etc.)
        - Each activity must specify which section it belongs to
        - Include all required components for each activity
        - Ensure activities implement the pedagogical strategies from the high-level plan
        """
        
        output_text, reasoning_summary = self._make_api_call(prompt, "detailed activities")
        
        if output_text:
            # Parse the structured response into JSON format
            structured_activities = self.parse_activities_to_json(output_text, lesson_details)
            
            # Add activities data to existing structure
            sections_data["activities_response"] = output_text
            sections_data["activities_reasoning_summary"] = reasoning_summary
            sections_data["structured_activities"] = structured_activities
            sections_data["activities_model_used"] = self.reasoning_model if self.use_reasoning else self.non_reasoning_model
            
            return sections_data
        else:
            sections_data["activities_error"] = reasoning_summary
            return sections_data
    
    def parse_activities_to_json(self, content: str, lesson_details: Dict[str, str]) -> Dict[str, Any]:
        """Parse the structured activity response into JSON format for the HTML viewer"""
        lines = content.split('\n')
        
        structured_data = {
            "selected_sls_tools": [],
            "recommended_kat": [],
            "activities": []
        }
        
        current_activity = {}
        current_section = ""
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Parse SLS Tools
            if "SELECTED SLS TOOLS" in line:
                i += 1
                while i < len(lines):
                    line_content = lines[i].strip()
                    if "RECOMMENDED KEY APPLICATIONS" in line_content or "**RECOMMENDED" in line_content:
                        break
                    if line_content and not line_content.startswith("**") and not line_content.startswith("["):
                        structured_data["selected_sls_tools"].append(line_content)
                    i += 1
                continue
            
            # Parse KAT
            if "RECOMMENDED KEY APPLICATIONS" in line or "KEY APPLICATIONS OF TECHNOLOGY" in line:
                i += 1
                while i < len(lines):
                    line_content = lines[i].strip()
                    if "LESSON PLAN ACTIVITIES" in line_content or "**LESSON PLAN" in line_content:
                        break
                    if line_content and not line_content.startswith("**") and not line_content.startswith("["):
                        structured_data["recommended_kat"].append(line_content)
                    i += 1
                continue
            
            # Parse Activities - Handle both "Activity X:" and "**Activity X:**" formats
            activity_match = None
            if line.startswith("Activity ") and (":" in line):
                activity_match = line
            elif line.startswith("**Activity ") and (":**" in line or line.endswith("**")):
                activity_match = line.replace("**", "").strip()
            
            if activity_match:
                # Save previous activity if exists
                if current_activity and current_activity.get("title"):
                    structured_data["activities"].append(current_activity)
                
                # Start new activity
                current_activity = {
                    "title": activity_match,
                    "section": "",
                    "interaction_type": "",
                    "duration": "",
                    "learning_objectives": [],
                    "instructions": "",
                    "kat_alignment": "",
                    "sls_tools": "",
                    "data_analysis": "",
                    "teaching_notes": ""
                }
            
            elif current_activity:
                if line.startswith("Section:"):
                    current_activity["section"] = line.replace("Section:", "").strip()
                
                elif line.startswith("Interaction Type:"):
                    current_activity["interaction_type"] = line.replace("Interaction Type:", "").strip()
                
                elif line.startswith("Duration:"):
                    current_activity["duration"] = line.replace("Duration:", "").strip()
                
                elif line.startswith("Learning Objectives:"):
                    i += 1
                    while i < len(lines):
                        obj_line = lines[i].strip()
                        if obj_line.startswith("•"):
                            current_activity["learning_objectives"].append(obj_line[1:].strip())
                        elif obj_line and not obj_line.startswith(("Instructions:", "KAT Alignment:", "SLS Tools:", "Data Analysis:", "Teaching Notes:", "Activity ", "---", "**Activity")):
                            if obj_line.startswith("•"):
                                current_activity["learning_objectives"].append(obj_line[1:].strip())
                        else:
                            break
                        i += 1
                    continue
                
                elif line.startswith("Instructions:"):
                    i += 1
                    instructions = []
                    while i < len(lines):
                        inst_line = lines[i].strip()
                        if inst_line.startswith(("KAT Alignment:", "SLS Tools:", "Data Analysis:", "Teaching Notes:", "Activity ", "---", "**Activity")):
                            break
                        if inst_line:
                            instructions.append(inst_line)
                        i += 1
                    current_activity["instructions"] = "\n".join(instructions)
                    continue
                
                elif line.startswith("KAT Alignment:"):
                    i += 1
                    kat_content = []
                    while i < len(lines):
                        kat_line = lines[i].strip()
                        if kat_line.startswith(("SLS Tools:", "Data Analysis:", "Teaching Notes:", "Activity ", "---", "**Activity")):
                            break
                        if kat_line:
                            kat_content.append(kat_line)
                        i += 1
                    current_activity["kat_alignment"] = "\n".join(kat_content)
                    continue
                
                elif line.startswith("SLS Tools:"):
                    i += 1
                    sls_content = []
                    while i < len(lines):
                        sls_line = lines[i].strip()
                        if sls_line.startswith(("Data Analysis:", "Teaching Notes:", "Activity ", "---", "**Activity")):
                            break
                        if sls_line:
                            sls_content.append(sls_line)
                        i += 1
                    current_activity["sls_tools"] = "\n".join(sls_content)
                    continue
                
                elif line.startswith("Data Analysis:"):
                    i += 1
                    data_content = []
                    while i < len(lines):
                        data_line = lines[i].strip()
                        if data_line.startswith(("Teaching Notes:", "Activity ", "---", "**Activity")):
                            break
                        if data_line:
                            data_content.append(data_line)
                        i += 1
                    current_activity["data_analysis"] = "\n".join(data_content)
                    continue
                
                elif line.startswith("Teaching Notes:"):
                    i += 1
                    notes_content = []
                    while i < len(lines):
                        notes_line = lines[i].strip()
                        if notes_line.startswith(("Activity ", "---", "**Activity")) or (notes_line.startswith("**") and "Activity" not in notes_line):
                            break
                        if notes_line:
                            notes_content.append(notes_line)
                        i += 1
                    current_activity["teaching_notes"] = "\n".join(notes_content)
                    continue
            
            i += 1
        
        # Don't forget the last activity
        if current_activity and current_activity.get("title"):
            structured_data["activities"].append(current_activity)
        
        # Clean up and validate data
        for activity in structured_data["activities"]:
            # Ensure section is properly assigned
            if not activity["section"] and structured_data["activities"]:
                # Try to infer section from activity number
                try:
                    activity_num = int(activity["title"].split()[1].rstrip(":"))
                    section_num = ((activity_num - 1) // lesson_details.get('max_activities', 1)) + 1
                    activity["section"] = f"Section {section_num}"
                except:
                    activity["section"] = "Section 1"
        
        # Sort activities by activity number to ensure proper order
        def extract_activity_number(activity):
            try:
                title = activity.get("title", "")
                import re
                match = re.search(r'Activity\s*(\d+)', title, re.IGNORECASE)
                if match:
                    return int(match.group(1))
                return 0
            except:
                return 0
        
        structured_data["activities"].sort(key=extract_activity_number)
        
        print(f"\nParsing Summary:")
        print(f"- SLS Tools parsed: {len(structured_data['selected_sls_tools'])}")
        print(f"- KAT items parsed: {len(structured_data['recommended_kat'])}")
        print(f"- Activities parsed: {len(structured_data['activities'])}")
        
        # Debug: Show activity order and titles
        print(f"- Activity order: {[extract_activity_number(act) for act in structured_data['activities']]}")
        print(f"- Activity titles: {[act.get('title', 'No title')[:50] + '...' if len(act.get('title', '')) > 50 else act.get('title', 'No title') for act in structured_data['activities']]}")
        
        return structured_data
    
    def save_final_output(self, complete_data: Dict[str, Any]) -> str:
        """Save the complete lesson data to a JSON file"""
        # Use different filenames based on reasoning mode
        if self.use_reasoning:
            filename = "reasoning_lesson_output.json"
        else:
            filename = "non_reasoning_lesson_output.json"
        
        # Ensure we have structured activities data
        structured_activities = complete_data.get('structured_activities', {})
        if not structured_activities and complete_data.get('activities_response'):
            # Parse the activities response to create structured data
            structured_activities = self.parse_activities_to_json(
                complete_data['activities_response'], 
                complete_data['lesson_details']
            )
        
        # Structure the final output
        final_output = {
            "lesson_metadata": {
                "title": complete_data['lesson_details']['lesson_title'],
                "subject": complete_data['lesson_details']['subject'],
                "topic": complete_data['lesson_details']['topic'],
                "level_grade": complete_data['lesson_details']['level_grade'],
                "additional_instructions": complete_data['lesson_details']['additional_instructions'],
                "lesson_structure": {
                    "num_sections": complete_data['lesson_details']['num_sections'],
                    "max_activities_per_section": complete_data['lesson_details']['max_activities']
                },
                "generation_timestamp": str(os.popen('date').read().strip()),
                "models_used": {
                    "sections_model": complete_data.get('model_used', 'unknown'),
                    "activities_model": complete_data.get('activities_model_used', 'unknown'),
                    "reasoning_enabled": self.use_reasoning
                }
            },
            "generation_process": {
                "step_1_high_level_plan": {
                    "reasoning_summary": complete_data.get('plan_reasoning_summary', ''),
                    "generated_content": complete_data.get('high_level_plan', ''),
                    "teacher_feedback": complete_data.get('teacher_feedback', '')
                },
                "step_2_sections": {
                    "reasoning_summary": complete_data.get('reasoning_summary', ''),
                    "generated_content": complete_data.get('sections_response', '')
                },
                "step_3_activities": {
                    "reasoning_summary": complete_data.get('activities_reasoning_summary', ''),
                    "generated_content": complete_data.get('activities_response', ''),
                    "structured_activities": structured_activities
                }
            },
            "errors": {
                "activities_error": complete_data.get('activities_error')
            }
        }
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(final_output, f, indent=2, ensure_ascii=False)
            
            print(f"\n" + "=" * 60)
            print(f"FINAL OUTPUT SAVED TO: {filename}")
            print("=" * 60)
            print(f"Model used: {self.reasoning_model if self.use_reasoning else self.non_reasoning_model}")
            print(f"Reasoning enabled: {self.use_reasoning}")
            print(f"High-level plan included: {'Yes' if complete_data.get('high_level_plan') else 'No'}")
            print(f"Teacher feedback included: {'Yes' if complete_data.get('teacher_feedback') and complete_data.get('teacher_feedback') != 'No additional modifications requested.' else 'No'}")
            print(f"Structured activities included: {len(structured_activities.get('activities', []))} activities")
            print(f"SLS tools included: {len(structured_activities.get('selected_sls_tools', []))} tools")
            print(f"KAT recommendations included: {len(structured_activities.get('recommended_kat', []))} items")
            
            return filename
            
        except Exception as e:
            print(f"Error saving final output: {e}")
            return ""
    
    def generate_complete_lesson(self):
        """Main method to generate the complete lesson with high-level planning"""
        model_description = f"REASONING ({self.reasoning_model})" if self.use_reasoning else f"NON-REASONING ({self.non_reasoning_model})"
        print(f"LESSON GENERATOR WITH {model_description} MODEL")
        print("This will generate a high-level plan, then detailed sections and activities.")
        print("You'll have the opportunity to review and modify the plan before detailed generation.")
        print("Make sure your OPENAI_API_KEY environment variable is set.\n")
        
        # Step 1: Get lesson details
        lesson_details = self.get_lesson_details()
        
        # Step 2: Generate high-level plan
        plan_data = self.generate_high_level_plan(lesson_details)
        if "error" in plan_data:
            print("Failed to generate high-level plan. Exiting.")
            return
        
        # Step 3: Get teacher feedback on plan
        teacher_feedback = self.get_teacher_feedback_on_plan(plan_data)
        
        # Step 4: Generate sections with selected model
        sections_data = self.generate_sections(lesson_details, plan_data['high_level_plan'], teacher_feedback)
        if "error" in sections_data:
            print("Failed to generate sections. Exiting.")
            return
        
        # Step 5: Generate activities with selected model
        complete_data = self.generate_activities(sections_data)
        
        # Step 6: Save final output
        output_file = self.save_final_output(complete_data)
        
        if output_file:
            print(f"\nLesson generation complete! Check {output_file} for the full results.")
            print(f"\nSUMMARY OF {model_description} PROCESS:")
            print("-" * 40)
            print("1. HIGH-LEVEL PLAN: Generated strategic pedagogical framework with KAT selection")
            print("2. TEACHER REVIEW: Incorporated teacher feedback and modifications")
            if self.use_reasoning:
                print("3. SECTIONS: The AI reasoned through creating detailed sections based on the plan")
                print("4. ACTIVITIES: The AI analyzed sections and determined appropriate activities")
                print("\nAll reasoning summaries are saved in the output file.")
            else:
                print("3. SECTIONS: Generated detailed sections using standard model based on the plan")
                print("4. ACTIVITIES: Generated activities using standard model based on the plan")
                print("\nNo reasoning traces available for this model.")
        else:
            print("Failed to save final output.")

def main():
    """Main function to run the lesson generator"""
    parser = argparse.ArgumentParser(description="Run the lesson generator with or without reasoning.")
    parser.add_argument("--reasoning", action="store_true", help="Use reasoning model (o4-mini)")
    parser.add_argument("--non_reason", action="store_true", help="Use non-reasoning model (gpt-4o-mini-2024-07-18)")
    args = parser.parse_args()

    if args.reasoning and args.non_reason:
        print("Error: Please specify either --reasoning or --non_reason, but not both.")
        return

    # Default to reasoning model if no arguments provided
    use_reasoning = True if not args.non_reason else False
    
    generator = LessonGenerator(use_reasoning)
    generator.generate_complete_lesson()

if __name__ == "__main__":
    main()
