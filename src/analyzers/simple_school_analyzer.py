#!/usr/bin/env python3
"""
Simple School Analyzer - A simplified version for testing with Ollama.

This script provides a more focused analysis with shorter prompts to avoid
JSON parsing issues with smaller models.
"""

import json
import os
import argparse
import requests
from datetime import datetime
from typing import Dict, List, Any, Optional
import re


class SimpleSchoolAnalyzer:
    """Simple analyzer for school data using Ollama."""
    
    def __init__(self, ollama_url: str = "http://localhost:11434", model: str = "llama3.2:3b"):
        self.ollama_url = ollama_url
        self.model = model
        self.api_url = f"{ollama_url}/api/generate"
    
    def analyze_school_simple(self, school_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simple analysis with focused prompts."""
        school_info = school_data.get('school_info', {})
        pages = school_data.get('pages', {})
        
        # Get main content from home page
        home_page = None
        for url, page_data in pages.items():
            if page_data.get('page_type') == 'home':
                home_page = page_data
                break
        
        if not home_page:
            home_page = list(pages.values())[0] if pages else {}
        
        # Create simple prompt
        prompt = f"""
Analyze this charter school and provide key information:

School: {school_info.get('school_name', 'Unknown')}
Website: {school_info.get('website', 'Unknown')}

Main content: {home_page.get('text_content', '')[:1500]}

Provide a brief analysis in this format:
- Mission: [mission statement or purpose]
- Programs: [key programs or focus areas]
- Contact: [email, phone, or contact info]
- Unique Features: [what makes this school special]
- Enrollment: [how to enroll or apply]

Keep it concise and factual.
"""
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.1,
                "max_tokens": 1000
            }
        }
        
        try:
            print(f"🤖 Analyzing {school_info.get('school_name', 'Unknown School')}...")
            response = requests.post(self.api_url, json=payload, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            analysis_text = result.get('response', '')
            
            return {
                'success': True,
                'analysis': analysis_text,
                'model_used': self.model,
                'school_name': school_info.get('school_name', 'Unknown')
            }
                
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f'Request failed: {str(e)}',
                'model_used': self.model,
                'school_name': school_info.get('school_name', 'Unknown')
            }
    
    def analyze_schools_simple(self, data_dir: str, output_file: Optional[str] = None) -> Dict[str, Any]:
        """Analyze all schools in a directory with simple prompts."""
        if not os.path.exists(data_dir):
            raise FileNotFoundError(f"Directory not found: {data_dir}")
        
        json_files = [f for f in os.listdir(data_dir) if f.endswith('.json')]
        
        if not json_files:
            raise ValueError(f"No JSON files found in {data_dir}")
        
        print(f"📁 Found {len(json_files)} school files to analyze")
        
        results = {
            'metadata': {
                'analyzed_at': datetime.now().isoformat(),
                'model_used': self.model,
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
                
                analysis_result = self.analyze_school_simple(school_data)
                
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
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"💾 Results saved to: {output_file}")
        
        return results


def main():
    """Main function."""
    from pathlib import Path
    
    # Set default paths based on project structure
    project_root = Path(__file__).parent.parent.parent
    default_data_dir = project_root / "data" / "scraped"
    default_output_dir = project_root / "data" / "analyzed"
    
    parser = argparse.ArgumentParser(description='Simple school data analysis using Ollama')
    parser.add_argument('--data-dir', default=str(default_data_dir),
                       help='Directory containing school JSON files')
    parser.add_argument('--output', default=None,
                       help='Output file for analysis results (JSON)')
    parser.add_argument('--ollama-url', default='http://localhost:11434',
                       help='Ollama server URL')
    parser.add_argument('--model', default='llama3.2:3b',
                       help='Ollama model to use')
    
    args = parser.parse_args()
    
    print("🎓 Simple School Data Analyzer")
    print(f"🤖 Model: {args.model}")
    
    analyzer = SimpleSchoolAnalyzer(args.ollama_url, args.model)
    
    if not args.output:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        args.output = str(default_output_dir / f"simple_school_analysis_{timestamp}.json")
    
    try:
        print(f"\n📊 Analyzing schools in: {args.data_dir}")
        results = analyzer.analyze_schools_simple(args.data_dir, args.output)
        
        print(f"\n📈 Analysis Summary:")
        print(f"   🏫 Total schools: {results['metadata']['total_schools']}")
        print(f"   ✅ Successful: {results['metadata']['successful_analyses']}")
        print(f"   ❌ Failed: {results['metadata']['failed_analyses']}")
        print(f"   📊 Success rate: {results['metadata']['success_rate']:.1f}%")
        
        # Show sample analysis
        for school_name, school_data in results['schools'].items():
            if school_data.get('analysis_result', {}).get('success'):
                print(f"\n📋 Sample Analysis - {school_name}:")
                analysis = school_data['analysis_result']['analysis']
                print(analysis[:300] + "..." if len(analysis) > 300 else analysis)
                break
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")


if __name__ == "__main__":
    main()
