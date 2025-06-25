import os
from openai import OpenAI
import dotenv
import base64
import json
import glob

dotenv.load_dotenv()

# Function to encode image to base64
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def analyze_image(client, image_path):
    """Analyze a single image and return parsed JSON response"""
    base64_image = encode_image(image_path)
    id = 350
    response = client.chat.completions.create(
        model="o4-mini",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text":f"The presented picture is a sequence of 3 timestamps in a top-down visualization of a driving scenario in order from left to right. Only focus on the positions of the vehicle with the id {id} and whether it changes unnaturally, especially if it collides with hitboxes of other vehicles. Evaluate whether this sequence of positions is plausible and physically possible. Disregard all other vehicles and any additional markers, trajectories, etc. Return a JSON object containing the following fields: 'motion_description: string', 'plausible: boolean', 'reasoning: string'."},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{base64_image}"
                        }
                    }
                ]
            }
        ]
    )
    
    return response.choices[0].message.content

def parse_llm_response(response_text):
    """Parse LLM response and extract JSON object"""
    try:
        # Try to find JSON in the response (in case there's extra text)
        start_idx = response_text.find('{')
        end_idx = response_text.rfind('}') + 1
        
        if start_idx != -1 and end_idx != 0:
            json_str = response_text[start_idx:end_idx]
            return json.loads(json_str)
        else:
            # If no JSON brackets found, try parsing the whole response
            return json.loads(response_text)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        print(f"Raw response: {response_text}")
        return {
            "motion_description": "Error parsing response",
            "plausible": False,
            "reasoning": f"JSON parsing failed: {str(e)}"
        }

# Initialize OpenAI client
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

# Get all images from merged_images folder
merged_images_dir = "merged_images_ARG_Carcarana-12_1_T-1"
image_pattern = os.path.join(merged_images_dir, "*.png")
image_paths = sorted(glob.glob(image_pattern))

if not image_paths:
    print(f"No images found in {merged_images_dir} folder")
    exit(1)

# Store all results
analysis_results = []

print(f"Found {len(image_paths)} images to analyze")
print("=" * 50)

# Process each image
for i, image_path in enumerate(image_paths):
    filename = os.path.basename(image_path)
    print(f"Analyzing {filename} ({i+1}/{len(image_paths)})...")
    
    try:
        # Get LLM response
        raw_response = analyze_image(client, image_path)
        
        # Parse the response
        parsed_result = parse_llm_response(raw_response)
        
        # Add metadata
        result = {
            "image_file": filename,
            "image_path": image_path,
            "raw_response": raw_response,
            **parsed_result
        }
        
        analysis_results.append(result)
        
        # Print summary
        print(f"  Motion: {parsed_result.get('motion_description', 'N/A')}")
        print(f"  Plausible: {parsed_result.get('plausible', 'N/A')}")
        print(f"  Reasoning: {parsed_result.get('reasoning', 'N/A')[:100]}...")
        print("-" * 30)
        
    except Exception as e:
        print(f"Error analyzing {filename}: {e}")
        error_result = {
            "image_file": filename,
            "image_path": image_path,
            "raw_response": f"Error: {str(e)}",
            "motion_description": "Analysis failed",
            "plausible": False,
            "reasoning": f"Error during analysis: {str(e)}"
        }
        analysis_results.append(error_result)

# Save results to JSON file
output_file = "analysis_results.json"
with open(output_file, 'w') as f:
    json.dump(analysis_results, f, indent=2)

print(f"\nAnalysis complete! Results saved to {output_file}")
print(f"Total images analyzed: {len(analysis_results)}")

# Print summary statistics
plausible_count = sum(1 for result in analysis_results if result.get('plausible', False))
print(f"Plausible motions: {plausible_count}/{len(analysis_results)}")