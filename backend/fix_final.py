# Read original file
with open('app/services/template_generator_premium.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Keep everything up to line 805 (before style_tag.string)
new_content = lines[:805]

# Add the corrected implementation
fix = """        style_tag.string = f\"\"\"
/* Modern Design - Styles existing HTML */
:root {{
    --primary: {primary_color};
    --secondary: {secondary_color};
}}
* {{ box-sizing: border-box; }}
body {{ font-family: -apple-system, sans-serif; line-height: 1.7; margin: 0; padding: 0; }}
h1, h2, h3 {{ font-weight: 700; margin-bottom: 1rem; }}
p {{ margin-bottom: 1rem; color: #4a5568; }}
a {{ color: var(--primary); text-decoration: none; }}
img {{ max-width: 100%; height: auto; border-radius: 8px; }}
button {{ padding: 12px 24px; background: var(--primary); color: white; border: none; border-radius: 8px; }}
nav, header {{ background: white; box-shadow: 0 2px 8px rgba(0,0,0,0.1); padding: 1rem; }}
section {{ padding: 3rem 1.5rem; max-width: 1200px; margin: 0 auto; }}
\"\"\"
        head.append(style_tag)
        logger.info("[REDESIGN] Added CSS to existing structure")

        # Remove problematic inline styles
        for tag in soup.find_all(style=True):
            del tag['style']

        # Add alt to images
        for img in soup.find_all('img'):
            if not img.get('alt'):
                img['alt'] = 'Image'

        improved_html = str(soup)
        logger.info(f"[REDESIGN] Styled existing HTML ({len(improved_html)} bytes)")
        return improved_html

    except Exception as e:
        logger.error(f"[REDESIGN] Error: {e}")
        return cloned_html


# Export main function
__all__ = ['generate_templates_for_business', 'TemplateGenerationError']
"""

new_content.append(fix)

# Write file
with open('app/services/template_generator_premium.py', 'w', encoding='utf-8') as f:
    f.writelines(new_content)

print("Fixed!")
