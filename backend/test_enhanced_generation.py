"""
Test Enhanced Template Generation with Explicit Component Instructions
This test creates a MORE EXPLICIT prompt that forces GPT-4o to create ALL components
"""
import sys
sys.path.insert(0, 'C:\\Users\\rabia\\Documents\\project AutoWeb Outreach AI\\AutoWeb_Outreach_AI\\backend')

from app.database import SessionLocal
from app.models.business import Business
from app.models.template import Template
from app.services.template_modernization_service import TemplateModernizationService

# Business ID for C.C Electrical
BUSINESS_ID = '8f92f1dc-a9e7-4685-95f1-aa0c8a908d62'

db = SessionLocal()

print('=' * 80)
print('ENHANCED TEMPLATE GENERATION TEST')
print('=' * 80)

# Load business
business = db.query(Business).filter(Business.id == BUSINESS_ID).first()

if not business:
    print('[ERROR] Business not found')
    sys.exit(1)

print(f'\nBusiness: {business.name}')
print(f'Scraped HTML: {len(business.scraped_html or "")} chars')
print(f'Component count: {business.component_count}')
print(f'Component structure entries: {len(business.component_structure) if business.component_structure else 0}')
print(f'Images: {len(business.image_urls or [])}')
print(f'Logos: {len(business.logo_urls or [])}')
print(f'Colors: {business.color_palette}')

# Delete old template
print('\n' + '=' * 80)
print('STEP 1: Delete old template')
print('=' * 80)

old_template = db.query(Template).filter(Template.business_id == BUSINESS_ID).first()
if old_template:
    print(f'Deleting template {old_template.id}')
    db.delete(old_template)
    db.commit()

# Generate NEW template with enhanced service
print('\n' + '=' * 80)
print('STEP 2: Generate NEW template with EXPLICIT component requirements')
print('=' * 80)
print('This may take 3-5 minutes...\n')

try:
    service = TemplateModernizationService(db)
    templates = service.generate_modernized_templates(str(business.id), force_rescrape=False)

    if templates:
        template = templates[0]
        html = template.html_content

        print('\n' + '=' * 80)
        print('SUCCESS!')
        print('=' * 80)
        print(f'Template ID: {template.id}')
        print(f'HTML Length: {len(html):,} chars')
        print(f'Variant: {template.variant_number}')

        # Count sections
        import re
        sections = re.findall(r'<section', html, re.IGNORECASE)
        print(f'\nSections created: {len(sections)}')
        print(f'Components available: {len(business.component_structure) if business.component_structure else 0}')

        # Quality checks
        checks = {
            'Tailwind CDN': 'tailwindcss' in html.lower(),
            'Gradients': 'gradient' in html.lower(),
            'Shadows': 'shadow' in html.lower(),
            'Hover effects': 'hover:' in html,
            'Responsive': 'md:' in html and 'lg:' in html,
            'Animations': '@keyframes' in html.lower(),
            'Min 30K chars': len(html) >= 30000
        }

        print('\nQuality Checks:')
        for check, result in checks.items():
            status = 'PASS' if result else 'FAIL'
            print(f'  [{status}] {check}')

        passed = sum(1 for r in checks.values() if r)
        print(f'\nScore: {passed}/{len(checks)} ({passed*100//len(checks)}%)')

        # Show first 2000 chars
        print('\n' + '=' * 80)
        print('First 2000 characters:')
        print('=' * 80)
        print(html[:2000])

    else:
        print('[ERROR] No templates generated!')

except Exception as e:
    print(f'\n[ERROR] {str(e)}')
    import traceback
    traceback.print_exc()

db.close()
