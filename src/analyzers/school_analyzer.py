#!/usr/bin/env python3
"""
School Analyzer - Uses Ollama to analyze scraped school data and extract insights.

This script reads the JSON files created by the enhanced scraper and sends the content
to a locally running Ollama model to extract structured information about each school.
"""

import json
import os
import argparse
import requests
from datetime import datetime
from typing import Dict, List, Any, Optional
import re


class SchoolAnalyzer:
    """Analyzes school data using Ollama LLM."""
    
    def __init__(self, ollama_url: str = "http://localhost:11434", model: str = "llama3.1"):
        """
        Initialize the analyzer.
        
        Args:
            ollama_url: URL of the Ollama server
            model: Model name to use for analysis
        """
        self.ollama_url = ollama_url
        self.model = model
        self.api_url = f"{ollama_url}/api/generate"
        
    def check_ollama_connection(self) -> bool:
        """Check if Ollama is running and accessible."""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
    
    def get_available_models(self) -> List[str]:
        """Get list of available models from Ollama."""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags")
            if response.status_code == 200:
                data = response.json()
                return [model['name'] for model in data.get('models', [])]
            return []
        except requests.exceptions.RequestException:
            return []
    
    def prepare_school_context(self, school_data: Dict[str, Any]) -> str:
        """
        Prepare school data as context for the LLM.
        
        Args:
            school_data: School data from JSON file
            
        Returns:
            Formatted context string
        """
        school_info = school_data.get('school_info', {})
        pages = school_data.get('pages', {})
        
        context = f"""
SCHOOL INFORMATION:
- Name: {school_info.get('school_name', 'N/A')}
- CDS Code: {school_info.get('cds_code', 'N/A')}
- County: {school_info.get('county', 'N/A')}
- District: {school_info.get('district', 'N/A')}
- Email: {school_info.get('email', 'N/A')}
- Website: {school_info.get('website', 'N/A')}
- Domain: {school_info.get('domain', 'N/A')}

SCRAPED PAGES ({len(pages)} total):
"""
        
        for url, page_data in pages.items():
            page_type = page_data.get('page_type', 'unknown')
            title = page_data.get('title', 'No title')
            description = page_data.get('description', 'No description')
            text_content = page_data.get('text_content', '')
            
            # Truncate very long content for context
            if len(text_content) > 2000:
                text_content = text_content[:2000] + "... [truncated]"
            
            context += f"""
--- PAGE: {url} ({page_type.upper()}) ---
Title: {title}
Description: {description}
Content: {text_content}

"""
        
        return context.strip()
    
    def _extract_partial_info(self, text: str) -> Dict[str, Any]:
        """Extract partial information from raw response when JSON parsing fails."""
        partial_info = {}
        
        # Try to extract key information using regex patterns
        patterns = {
            'school_name': r'"name":\s*"([^"]+)"',
            'mission': r'"mission_statement":\s*"([^"]+)"',
            'enrollment': r'"enrollment":\s*"([^"]+)"',
            'grades': r'"grades_served":\s*"([^"]+)"',
            'phone': r'"phone":\s*"([^"]+)"',
            'email': r'"primary_email":\s*"([^"]+)"'
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, text)
            if match:
                partial_info[key] = match.group(1)
        
        return partial_info
    
    def create_analysis_prompt(self, school_context: str) -> str:
        """Create a comprehensive prompt for school analysis."""
        return f"""
You are an expert education analyst. Analyze the following charter school data and extract key information in a structured format.

{school_context}

Please provide a comprehensive analysis in the following JSON format:

{{
  "school_summary": {{
    "name": "School name",
    "type": "Charter school type (e.g., K-12, High School, Middle School)",
    "mission_statement": "Extracted mission statement or core purpose",
    "founded_year": "Year founded if mentioned",
    "enrollment": "Number of students if mentioned",
    "grades_served": "Grade levels served (e.g., K-5, 6-12)"
  }},
  "academic_programs": {{
    "special_programs": ["List of special programs, academies, or tracks"],
    "curriculum_focus": "Main curriculum focus or approach",
    "college_prep": "College preparation programs or statistics",
    "extracurriculars": ["List of extracurricular activities mentioned"]
  }},
  "contact_info": {{
    "primary_email": "Main contact email",
    "phone": "Phone number if found",
    "address": "Physical address if found",
    "social_media": ["Social media links found"]
  }},
  "key_features": {{
    "unique_selling_points": ["What makes this school unique"],
    "awards_recognition": ["Awards, recognitions, or achievements mentioned"],
    "partnerships": ["Community or business partnerships mentioned"]
  }},
  "enrollment_info": {{
    "enrollment_process": "How to enroll or apply",
    "deadlines": "Application deadlines if mentioned",
    "requirements": "Enrollment requirements if mentioned"
  }},
  "analysis_notes": {{
    "data_quality": "Assessment of available information quality",
    "missing_info": ["Important information that seems to be missing"],
    "confidence_level": "High/Medium/Low - confidence in the analysis"
  }}
}}

Focus on extracting factual information from the content. If information is not available, use "Not specified" or empty arrays as appropriate. Be thorough but concise.
"""
    
    def analyze_school(self, school_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a single school using Ollama.
        
        Args:
            school_data: School data from JSON file
            
        Returns:
            Analysis results
        """
        school_context = self.prepare_school_context(school_data)
        prompt = self.create_analysis_prompt(school_context)
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.1,  # Low temperature for more consistent results
                "top_p": 0.9,
                "max_tokens": 4000
            }
        }
        
        try:
            print(f"🤖 Analyzing {school_data.get('school_info', {}).get('school_name', 'Unknown School')}...")
            response = requests.post(self.api_url, json=payload, timeout=120)
            response.raise_for_status()
            
            result = response.json()
            analysis_text = result.get('response', '')
            
            # Try to extract JSON from the response
            try:
                # Clean up the response text
                analysis_text = analysis_text.strip()
                
                # Remove any leading text before the JSON
                if '```json' in analysis_text:
                    analysis_text = analysis_text.split('```json')[1].split('```')[0]
                elif '```' in analysis_text:
                    analysis_text = analysis_text.split('```')[1].split('```')[0]
                
                # Look for JSON in the response
                json_match = re.search(r'\{.*\}', analysis_text, re.DOTALL)
                if json_match:
                    json_str = json_match.group()
                    
                    # Try to fix common JSON issues
                    json_str = json_str.replace('\n', ' ').replace('\r', ' ')
                    json_str = re.sub(r'\s+', ' ', json_str)  # Normalize whitespace
                    
                    # Try to complete truncated JSON
                    if json_str.count('{') > json_str.count('}'):
                        json_str += '}' * (json_str.count('{') - json_str.count('}'))
                    
                    analysis_json = json.loads(json_str)
                    return {
                        'success': True,
                        'analysis': analysis_json,
                        'raw_response': analysis_text,
                        'model_used': self.model
                    }
                else:
                    return {
                        'success': False,
                        'error': 'No JSON found in response',
                        'raw_response': analysis_text,
                        'model_used': self.model
                    }
            except json.JSONDecodeError as e:
                # Try to extract partial information from the raw response
                partial_info = self._extract_partial_info(analysis_text)
                return {
                    'success': False,
                    'error': f'Failed to parse JSON: {str(e)}',
                    'raw_response': analysis_text,
                    'partial_info': partial_info,
                    'model_used': self.model
                }
                
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f'Request failed: {str(e)}',
                'raw_response': '',
                'model_used': self.model
            }
    
    def analyze_schools_from_directory(self, data_dir: str, output_file: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze all schools in a directory.
        
        Args:
            data_dir: Directory containing school JSON files
            output_file: Optional output file for results
            
        Returns:
            Analysis results for all schools
        """
        if not os.path.exists(data_dir):
            raise FileNotFoundError(f"Directory not found: {data_dir}")
        
        # Find all JSON files (excluding summary CSV)
        json_files = [f for f in os.listdir(data_dir) if f.endswith('.json')]
        
        if not json_files:
            raise ValueError(f"No JSON files found in {data_dir}")
        
        print(f"📁 Found {len(json_files)} school files to analyze")
        
        results = {
            'metadata': {
                'analyzed_at': datetime.now().isoformat(),
                'model_used': self.model,
                'ollama_url': self.ollama_url,
                'total_schools': len(json_files)
            },
            'schools': {}
        }
        
        successful_analyses = 0
        failed_analyses = 0
        
        for json_file in json_files:
            file_path = os.path.join(data_dir, json_file)
            school_name = json_file.replace('.json', '')
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    school_data = json.load(f)
                
                analysis_result = self.analyze_school(school_data)
                
                results['schools'][school_name] = {
                    'file': json_file,
                    'school_info': school_data.get('school_info', {}),
                    'analysis_result': analysis_result
                }
                
                if analysis_result['success']:
                    successful_analyses += 1
                    print(f"  ✅ {school_name}")
                else:
                    failed_analyses += 1
                    print(f"  ❌ {school_name}: {analysis_result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                failed_analyses += 1
                print(f"  ❌ {school_name}: Failed to process file - {str(e)}")
                results['schools'][school_name] = {
                    'file': json_file,
                    'error': str(e)
                }
        
        results['metadata']['successful_analyses'] = successful_analyses
        results['metadata']['failed_analyses'] = failed_analyses
        results['metadata']['success_rate'] = successful_analyses / len(json_files) * 100
        
        # Save results if output file specified
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"💾 Results saved to: {output_file}")
        
        return results


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Analyze school data using Ollama')
    parser.add_argument('--data-dir', default='test_scraped_data',
                       help='Directory containing school JSON files')
    parser.add_argument('--output', default=None,
                       help='Output file for analysis results (JSON)')
    parser.add_argument('--ollama-url', default='http://localhost:11434',
                       help='Ollama server URL')
    parser.add_argument('--model', default='llama3.1',
                       help='Ollama model to use')
    parser.add_argument('--check-connection', action='store_true',
                       help='Check Ollama connection and available models')
    
    args = parser.parse_args()
    
    print("🎓 School Data Analyzer with Ollama")
    print(f"🔗 Ollama URL: {args.ollama_url}")
    print(f"🤖 Model: {args.model}")
    
    analyzer = SchoolAnalyzer(args.ollama_url, args.model)
    
    # Check connection
    if args.check_connection:
        print("\n🔍 Checking Ollama connection...")
        if analyzer.check_ollama_connection():
            print("✅ Ollama is running")
            models = analyzer.get_available_models()
            if models:
                print(f"📋 Available models: {', '.join(models)}")
                if args.model not in models:
                    print(f"⚠️  Warning: Model '{args.model}' not found in available models")
            else:
                print("⚠️  No models found")
        else:
            print("❌ Cannot connect to Ollama. Make sure it's running.")
            return
    else:
        # Quick connection check
        if not analyzer.check_ollama_connection():
            print("❌ Cannot connect to Ollama. Make sure it's running.")
            print("💡 Use --check-connection to see available models")
            return
    
    # Set default output directory
    project_root = Path(__file__).parent.parent.parent
    default_output_dir = project_root / "data" / "analyzed"
    
    # Generate output filename if not provided
    if not args.output:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        args.output = str(default_output_dir / f"school_analysis_{timestamp}.json")
    
    try:
        print(f"\n📊 Analyzing schools in: {args.data_dir}")
        results = analyzer.analyze_schools_from_directory(args.data_dir, args.output)
        
        print(f"\n📈 Analysis Summary:")
        print(f"   🏫 Total schools: {results['metadata']['total_schools']}")
        print(f"   ✅ Successful: {results['metadata']['successful_analyses']}")
        print(f"   ❌ Failed: {results['metadata']['failed_analyses']}")
        print(f"   📊 Success rate: {results['metadata']['success_rate']:.1f}%")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")


if __name__ == "__main__":
    main()
