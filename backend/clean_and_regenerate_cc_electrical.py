"""
Clean all old templates for C.C Electrical and regenerate with NEW WOW factor system
"""
import sys
sys.path.insert(0, 'C:\\Users\\rabia\\Documents\\project AutoWeb Outreach AI\\AutoWeb_Outreach_AI\\backend')

from app.database import SessionLocal
from app.services.template_modernization_service import TemplateModernizationService
from app.models.business import Business
from app.models.template import Template

# Business ID for C.C Electrical
BUSINESS_ID = '8f92f1dc-a9e7-4685-95f1-aa0c8a908d62'

db = SessionLocal()

print('='  * 80)
print('CLEAN & REGENERATE: C.C Electrical & Sons')
print('=' * 80)

# Load business
business = db.query(Business).filter(Business.id == BUSINESS_ID).first()

if not business:
    print('ERROR: Business not found')
    sys.exit(1)

print(f'\nBusiness: {business.name}')
print(f'Components: {business.component_count}')
print(f'Images: {len(business.image_urls or [])}')

# Step 1: Delete ALL old templates
print('\n' + '=' * 80)
print('STEP 1: Deleting ALL old templates...')
print('=' * 80)

old_templates = db.query(Template).filter(Template.business_id == BUSINESS_ID).all()
print(f'Found {len(old_templates)} old templates')

for template in old_templates:
    print(f'  Deleting template {template.id} (variant {template.variant_number})')
    db.delete(template)

db.commit()
print(f'\nDeleted {len(old_templates)} old templates')

# Step 2: Generate NEW template with WOW factor
print('\n' + '=' * 80)
print('STEP 2: Generating NEW ULTIMATE TEMPLATE...')
print('=' * 80)
print('Using: GPT-4o with 16384 max tokens')
print('Temperature: 0.95 (maximum creativity)')
print('Framework: Tailwind CSS + custom animations')
print('Please wait 2-5 minutes...\n')

try:
    service = TemplateModernizationService(db)
    templates = service.generate_modernized_templates(str(business.id), force_rescrape=False)

    print('\n' + '=' * 80)
    print(f'SUCCESS! Generated {len(templates)} template(s)')
    print('=' * 80)

    for template in templates:
        print(f'\nTemplate ID: {template.id}')
        print(f'Variant: {template.variant_number}')
        print(f'HTML Length: {len(template.html_content):,} characters')
        print(f'Generated at: {template.generated_at}')

        # Quality checks
        html = template.html_content.lower()
        has_animations = '@keyframes' in html
        has_tailwind = 'tailwindcss' in html
        has_hover = 'hover:' in html
        has_transitions = 'transition' in html

        print(f'\nQuality Checks:')
        print(f'  Animations: {"YES" if has_animations else "NO"}')
        print(f'  Tailwind: {"YES" if has_tailwind else "NO"}')
        print(f'  Hover effects: {"YES" if has_hover else "NO"}')
        print(f'  Transitions: {"YES" if has_transitions else "NO"}')

    print('\n' + '=' * 80)
    print('COMPLETE! You can now view the template in your frontend.')
    print('It should show ONLY 1 professional, modern template with animations.')
    print('=' * 80)

except Exception as e:
    print(f'\nERROR: {str(e)}')
    import traceback
    traceback.print_exc()

db.close()
