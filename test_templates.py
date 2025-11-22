"""
Test script to verify all three CV templates can generate PDFs
"""
import asyncio
import sys
from services.cv_service import CVService

# Sample profile data
sample_profile = {
    'personalInfo': {
        'firstName': 'John',
        'lastName': 'Doe',
        'email': 'john.doe@example.com',
        'phone': '+1 234 567 8900',
        'location': 'New York, USA',
        'linkedin': 'linkedin.com/in/johndoe'
    },
    'aboutMe': 'Experienced software engineer with 5+ years in full-stack development.',
    'workExperience': [
        {
            'title': 'Senior Software Engineer',
            'company': 'Tech Corp',
            'location': 'New York, USA',
            'startDate': '2020-01-01',
            'endDate': 'now',
            'description': 'Led development of microservices architecture'
        }
    ],
    'education': [
        {
            'degree': 'Bachelor of Science in Computer Science',
            'institution': 'University of Technology',
            'startDate': '2015-09-01',
            'endDate': '2019-06-01',
            'gpa': '3.8'
        }
    ],
    'skills': ['Python', 'JavaScript', 'React', 'Node.js', 'MongoDB'],
    'languages': [
        {'name': 'English', 'proficiency': 'Native'},
        {'name': 'Spanish', 'proficiency': 'B2'}
    ],
    'projects': [
        {
            'name': 'Open Source Project',
            'technologies': ['Python', 'FastAPI'],
            'description': 'Built a REST API for data processing',
            'link': 'https://github.com/user/project'
        }
    ]
}

sample_settings = {
    'sections': {
        'workExperience': True,
        'education': True,
        'skills': True,
        'languages': True,
        'projects': True
    }
}

async def test_template(template_name):
    """Test a specific template"""
    print(f"\n🧪 Testing {template_name.upper()} template...")
    try:
        cv_service = CVService()
        pdf_bytes = await cv_service.generate_cv(
            profile=sample_profile,
            settings=sample_settings,
            template=template_name
        )
        
        if pdf_bytes and len(pdf_bytes) > 0:
            print(f"   ✅ {template_name.upper()} template generated PDF ({len(pdf_bytes)} bytes)")
            return True
        else:
            print(f"   ❌ {template_name.upper()} template generated empty PDF")
            return False
    except Exception as e:
        print(f"   ❌ {template_name.upper()} template failed: {str(e)}")
        return False

async def main():
    """Test all templates"""
    print("=" * 60)
    print("CV Generator - Template Testing")
    print("=" * 60)
    
    templates = ['modern', 'classic', 'europass']
    results = {}
    
    for template in templates:
        results[template] = await test_template(template)
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    all_passed = all(results.values())
    
    for template, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}  {template.upper()} template")
    
    print("=" * 60)
    
    if all_passed:
        print("\n🎉 All templates working correctly!")
        print("Ready to deploy to FastMCP Cloud!")
        return 0
    else:
        print("\n❌ Some templates failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
