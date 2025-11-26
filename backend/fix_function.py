"""Script to fix the _apply_ai_improvements_to_html function"""

# Read the file
with open('app/services/template_generator_premium.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find where to truncate (right after style_tag.string = f""")
truncate_at = None
for i, line in enumerate(lines):
    if 'style_tag.string = f"""' in line:
        truncate_at = i + 1
        break

if not truncate_at:
    print("Could not find style_tag.string line")
    exit(1)

# Keep everything up to that line
new_lines = lines[:truncate_at]

# Add the rest of the function (no leading spaces - it's in an f-string)
rest_of_function = """    --text-dark: #1a202c;
    --text-light: #4a5568;
    --bg-light: #f7fafc;
    --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.08);
    --shadow-md: 0 8px 24px rgba(0, 0, 0, 0.12);
    --shadow-lg: 0 16px 48px rgba(0, 0, 0, 0.16);
    --radius: 12px;
    --transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}}

/* Modern Typography - Style ALL text elements */
body {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
    line-height: 1.7;
    color: var(--text-dark);
    background: #ffffff;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    overflow-x: hidden;
    margin: 0;
    padding: 0;
}}

html {{ scroll-behavior: smooth; }}

/* Style ALL headings */
h1, h2, h3, h4, h5, h6 {{
    font-weight: 700;
    line-height: 1.3;
    margin-bottom: 1rem;
    color: var(--text-dark);
}}

h1 {{ font-size: 2.5rem; }}
h2 {{ font-size: 2rem; }}
h3 {{ font-size: 1.75rem; }}

/* Style ALL paragraphs */
p {{
    margin-bottom: 1rem;
    line-height: 1.7;
    color: var(--text-light);
}}

/* Style ALL links */
a {{
    color: var(--primary-color);
    text-decoration: none;
    transition: var(--transition);
}}

a:hover {{
    color: var(--secondary-color);
}}

/* Style ALL images */
img {{
    max-width: 100%;
    height: auto;
    border-radius: var(--radius);
    box-shadow: var(--shadow-sm);
    transition: var(--transition);
}}

img:hover {{
    transform: translateY(-4px);
    box-shadow: var(--shadow-md);
}}

/* Style ALL buttons */
button, input[type="submit"], input[type="button"],
[class*="btn"], [class*="button"] {{
    padding: 12px 32px;
    border-radius: var(--radius);
    border: none;
    background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
    color: white;
    font-weight: 600;
    cursor: pointer;
    transition: var(--transition);
}}

button:hover {{
    transform: translateY(-2px);
    box-shadow: var(--shadow-md);
}}

/* Style ALL navigation */
nav, header, [class*="nav"], [class*="menu"] {{
    padding: 1.25rem 0;
    background: rgba(255, 255, 255, 0.95);
    box-shadow: var(--shadow-sm);
}}

/* Style ALL sections */
section, article, main {{
    padding: 3rem 1.5rem;
    max-width: 1200px;
    margin: 0 auto;
}}

section:nth-child(even) {{
    background: var(--bg-light);
}}

/* Style ALL cards */
div[class*="card"], div[class*="box"], article {{
    background: white;
    border-radius: var(--radius);
    padding: 2rem;
    box-shadow: var(--shadow-sm);
    transition: var(--transition);
}}

div[class*="card"]:hover {{
    transform: translateY(-4px);
    box-shadow: var(--shadow-md);
}}

/* Style ALL forms */
input, textarea, select {{
    padding: 0.75rem 1rem;
    border: 2px solid #e2e8f0;
    border-radius: var(--radius);
    font-family: inherit;
    transition: var(--transition);
}}

input:focus, textarea:focus {{
    outline: none;
    border-color: var(--primary-color);
}}

/* Responsive */
@media (max-width: 768px) {{
    h1 {{ font-size: 2rem; }}
    section {{ padding: 2rem 1rem; }}
}}
"""
        head.append(style_tag)
        logger.info("[REDESIGN] Added modern CSS that preserves structure")

        # Step 4: Clean up problematic inline styles
        for tag in soup.find_all(style=True):
            style = tag.get('style', '')
            if 'position: fixed' in style or ('width:' in style and 'px' in style):
                del tag['style']

        # Step 5: Add alt tags to images
        for img in soup.find_all('img'):
            if not img.get('alt'):
                img['alt'] = 'Image'

        # Step 6: Return improved HTML (same structure, better styling)
        improved_html = str(soup)
        logger.info(f"[REDESIGN] Applied modern styling, preserved structure ({{len(improved_html)}} bytes)")
        return improved_html

    except Exception as e:
        logger.error(f"[REDESIGN] Error: {{e}}")
        return cloned_html


# Export main function
__all__ = ['generate_templates_for_business', 'TemplateGenerationError']
"""

new_lines.append(rest_of_function)

# Write the file
with open('app/services/template_generator_premium.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("Function fixed successfully!")
