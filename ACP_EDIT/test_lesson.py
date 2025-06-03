#!/usr/bin/env python3

import json
import os
from main import LessonGenerator

def test_lesson_generation():
    """Test the lesson generation with predefined inputs"""
    
    print("=" * 60)
    print("TESTING LESSON GENERATOR WITH SAMPLE DATA")
    print("=" * 60)
    
    # Create sample lesson details
    lesson_details = {
        "lesson_title": "Introduction to Poetry",
        "subject": "English",
        "topic": "Poetic Techniques",
        "level_grade": "Secondary 2",
        "additional_instructions": "Focus on collaborative learning and scaffolding",
        "num_sections": 3,
        "max_activities": 1
    }
    
    print("Sample lesson details:")
    for key, value in lesson_details.items():
        print(f"  {key}: {value}")
    
    generator = LessonGenerator()
    
    # Test the parsing function with sample content
    sample_content = """**SELECTED SLS TOOLS FOR THIS LESSON:**
1. Interactive Thinking Tool – for annotation and highlighting poetic devices
2. Discussion Board – for collaborative analysis and sharing insights
3. Free Response Question – for creative writing and reflection
4. Rubrics – for peer evaluation and structured feedback

**RECOMMENDED KEY APPLICATIONS OF TECHNOLOGY (KAT):**
1. Facilitate learning together – Using collaborative tools enables students to construct understanding collectively
2. Embed scaffolding – Digital prompts and structured questions guide learners progressively

**LESSON PLAN ACTIVITIES:**

Activity 1: Exploring Poetic Techniques
Section: Section 1: Discovering Poetic Techniques
Interaction Type: Student-Content
Duration: 15 minutes
Learning Objectives:
• Identify examples of simile, metaphor, personification and alliteration
• Explain the literal and figurative meanings of each example

Instructions:
1. Open the curated poem in SLS
2. Use the Interactive Thinking Tool to highlight one example of each device
3. For each highlight, click the embedded tooltip and answer scaffolded prompts
4. Be prepared to share one highlighted example aloud

KAT Alignment:
Embed scaffolding – step-by-step prompts in the annotation tool guide identification
Facilitate learning together – volunteers share highlights and build collective understanding

SLS Tools:
Interactive Thinking Tool
Tooltip

Data Analysis:
Monitor Assignment Page and Heatmap to track completion
SLS Learning Progress Dashboard to monitor responses

Teaching Notes:
Model one example live, demonstrate annotation workflow, circulate to support students

---

Activity 2: Analyzing Techniques in Context
Section: Section 2: Analyzing Techniques in Context
Interaction Type: Student-Student
Duration: 20 minutes
Learning Objectives:
• Analyze how poetic techniques create imagery, mood and emphasis
• Articulate the writer's purpose in using specific techniques

Instructions:
1. In assigned pairs, open the Discussion Board thread for your technique
2. Respond to guiding questions about how the device shapes meaning
3. Debate interpretations and co-author a summary
4. Read another pair's post and leave constructive feedback

KAT Alignment:
Embed scaffolding – targeted questions focus student reasoning
Facilitate learning together – structured threads promote shared sense-making

SLS Tools:
Discussion Board

Data Analysis:
SLS Data Assistant to monitor post frequency and depth
SLS Feedback Assistants to flag posts needing intervention

Teaching Notes:
Assign techniques evenly, monitor for off-track reasoning, highlight strong posts

---

Activity 3: Creating with Poetic Techniques
Section: Section 3: Creating with Poetic Techniques
Interaction Type: Student-Student
Duration: 25 minutes
Learning Objectives:
• Apply at least two poetic techniques in original poetry
• Reflect on how chosen techniques enhance meaning and style

Instructions:
1. Draft original poetic lines using the Free Response Question
2. Exchange drafts with a partner and apply Rubrics for evaluation
3. Review feedback and revise your lines accordingly
4. Submit final version with reflection on feedback received

KAT Alignment:
Embed scaffolding – rubric criteria guide composition and review
Facilitate learning together – peer-review workflows foster collaborative improvement

SLS Tools:
Free Response Question
Rubrics

Data Analysis:
SLS Learning Progress Dashboard to track submission cycles
Annotated Feedback Assistant to review peer feedback patterns

Teaching Notes:
Share model rubric assessment, remind students to cite techniques by name

---"""

    print("\n" + "=" * 60)
    print("TESTING JSON PARSING")
    print("=" * 60)
    
    # Test parsing
    structured_data = generator.parse_activities_to_json(sample_content, lesson_details)
    
    # Create complete data structure
    complete_data = {
        'lesson_details': lesson_details,
        'sections_response': 'Sample sections content...',
        'reasoning_summary': 'Sample reasoning for sections...',
        'activities_response': sample_content,
        'activities_reasoning_summary': 'Sample reasoning for activities...',
        'structured_activities': structured_data
    }
    
    # Test saving
    filename = generator.save_final_output(complete_data)
    
    if filename:
        print(f"\n" + "=" * 60)
        print("JSON OUTPUT VERIFICATION")
        print("=" * 60)
        
        # Verify the JSON structure
        try:
            with open(filename, 'r') as f:
                output_data = json.load(f)
            
            print("✅ JSON file created successfully")
            print(f"✅ Structured activities: {len(output_data['generation_process']['step_2_activities']['structured_activities']['activities'])} activities")
            print(f"✅ SLS tools: {len(output_data['generation_process']['step_2_activities']['structured_activities']['selected_sls_tools'])} tools")
            print(f"✅ KAT items: {len(output_data['generation_process']['step_2_activities']['structured_activities']['recommended_kat'])} items")
            
            # Check activities by section
            activities = output_data['generation_process']['step_2_activities']['structured_activities']['activities']
            sections = {}
            for activity in activities:
                section = activity.get('section', 'Unknown')
                if section not in sections:
                    sections[section] = 0
                sections[section] += 1
            
            print(f"✅ Activities by section:")
            for section, count in sections.items():
                print(f"   - {section}: {count} activities")
            
            print(f"\n📁 Test file saved as: {filename}")
            print("🎯 Ready to test with HTML viewer!")
            
        except Exception as e:
            print(f"❌ Error reading JSON file: {e}")
    else:
        print("❌ Failed to create JSON file")

if __name__ == "__main__":
    test_lesson_generation() 