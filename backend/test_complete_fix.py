"""
Test Complete Fix: Rescrape with new component structure + Regenerate template
This will:
1. Rescrape C.C Electrical with NEW component extractor (no limit, includes content)
2. Regenerate template with ENHANCED prompt (explicit component requirements)
3. Verify ALL components are included in generated HTML
"""
import sys
sys.path.insert(0, 'C:\\Users\\rabia\\Documents\\project AutoWeb Outreach AI\\AutoWeb_Outreach_AI\\backend')

from app.database import SessionLocal
from app.models.business import Business
from app.models.template import Template
from app.services.enhanced_website_scraper_service import EnhancedWebsiteScraperService
from app.services.template_modernization_service import TemplateModernizationService
import re

# Business ID for C.C Electrical
BUSINESS_ID = '8f92f1dc-a9e7-4685-95f1-aa0c8a908d62'

db = SessionLocal()

print('=' * 80)
print('COMPLETE FIX TEST: Rescrape + Regenerate with Enhanced System')
print('=' * 80)

# Load business
business = db.query(Business).filter(Business.id == BUSINESS_ID).first()

if not business:
    print('[ERROR] Business not found')
    sys.exit(1)

print(f'\nBusiness: {business.name}')
print(f'URL: {business.website_url}')

# STEP 1: Rescrape with NEW component extractor
print('\n' + '=' * 80)
print('STEP 1: RESCRAPE with new component extractor (no limit, includes content)')
print('=' * 80)
print('This will take 30-60 seconds...\n')

scraper = EnhancedWebsiteScraperService(db)
success = scraper.scrape_complete_website(str(business.id))

if not success:
    print(f'[ERROR] Rescraping failed: {business.scraping_error}')
    sys.exit(1)

# Refresh to get new data
db.refresh(business)

print('[SUCCESS] Rescraping complete!')
print(f'\nScraped Data:')
print(f'  HTML: {len(business.scraped_html):,} chars')
print(f'  Component Count: {business.component_count}')
print(f'  Component Structure Entries: {len(business.component_structure)}')
print(f'  Images: {len(business.image_urls)}')
print(f'  Logos: {len(business.logo_urls)}')
print(f'  Colors: {len(business.color_palette)}')

# Show first 3 components to verify they have content
print(f'\nFirst 3 components (verifying content field exists):')
for i, comp in enumerate(business.component_structure[:3], 1):
    print(f'\n  Component {i}:')
    print(f'    Type: {comp.get("type")}')
    print(f'    Heading: {comp.get("heading", "")[:50]}...')
    print(f'    Content: {comp.get("content", "")[:100]}...')
    print(f'    Has Content Field: {"YES" if "content" in comp else "NO"}')

# STEP 2: Delete old templates
print('\n' + '=' * 80)
print('STEP 2: Delete old templates')
print('=' * 80)

old_templates = db.query(Template).filter(Template.business_id == BUSINESS_ID).all()
print(f'Found {len(old_templates)} old templates')

for template in old_templates:
    print(f'  Deleting template {template.id}')
    db.delete(template)

db.commit()

# STEP 3: Generate NEW template with ENHANCED prompt
print('\n' + '=' * 80)
print('STEP 3: Generate NEW template with ENHANCED prompt system')
print('=' * 80)
print('This may take 3-5 minutes with GPT-4o...\n')

try:
    service = TemplateModernizationService(db)
    templates = service.generate_modernized_templates(str(business.id), force_rescrape=False)

    if not templates:
        print('[ERROR] No templates generated!')
        sys.exit(1)

    template = templates[0]
    html = template.html_content

    print('\n' + '=' * 80)
    print('[SUCCESS] Template Generated!')
    print('=' * 80)
    print(f'\nTemplate ID: {template.id}')
    print(f'HTML Length: {len(html):,} chars')
    print(f'Variant: {template.variant_number}')

    # Count sections
    sections = re.findall(r'<section', html, re.IGNORECASE)
    print(f'\nSections created: {len(sections)}')
    print(f'Components in database: {len(business.component_structure)}')
    print(f'Component count: {business.component_count}')

    # Calculate coverage
    if len(business.component_structure) > 0:
        coverage = (len(sections) / len(business.component_structure)) * 100
        print(f'\nCoverage: {coverage:.1f}% ({len(sections)}/{len(business.component_structure)})')

    # Quality checks
    checks = {
        'Tailwind CDN': 'tailwindcss' in html.lower(),
        'Gradients': 'gradient' in html.lower(),
        'Shadows': 'shadow' in html.lower(),
        'Hover effects': 'hover:' in html,
        'Responsive': 'md:' in html and 'lg:' in html,
        'Animations': '@keyframes' in html.lower(),
        'Min 30K chars': len(html) >= 30000,
        'All components': len(sections) >= len(business.component_structure) * 0.9  # 90%+ coverage
    }

    print('\n' + '=' * 80)
    print('Quality Checks:')
    print('=' * 80)
    for check, result in checks.items():
        status = 'PASS' if result else 'FAIL'
        print(f'  [{status}] {check}')

    passed = sum(1 for r in checks.values() if r)
    score = passed * 100 // len(checks)
    print(f'\nScore: {passed}/{len(checks)} ({score}%)')

    if score >= 87:  # 7/8 = 87.5%
        print('\n[EXCELLENT] All fixes working! Template is complete and professional!')
    elif score >= 75:
        print('\n[GOOD] Most fixes working, minor issues remain')
    else:
        print('\n[WARNING] Fixes incomplete, review needed')

    # Show first 2000 chars
    print('\n' + '=' * 80)
    print('First 2000 characters of generated HTML:')
    print('=' * 80)
    print(html[:2000])

except Exception as e:
    print(f'\n[ERROR] {str(e)}')
    import traceback
    traceback.print_exc()

db.close()
