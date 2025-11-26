"""
Modernization Prompts for AI Template Generation
Story 4.10: Enhanced HTML Scraping and AI-Driven Template Modernization
"""

# CSS Framework-Specific Instructions
CSS_FRAMEWORK_INSTRUCTIONS = {
    "tailwind": """
    **Tailwind CSS Implementation:**
    - Include Tailwind CSS v3.x via CDN: <script src="https://cdn.tailwindcss.com"></script>
    - Use utility classes extensively: flex, grid, p-*, m-*, text-*, bg-*, rounded-*, shadow-*
    - Modern color utilities: bg-gradient-to-r, from-*, to-*
    - Spacing scale: Use consistent spacing (p-4, p-6, p-8, etc.)
    - Responsive prefixes: sm:, md:, lg:, xl:
    - Hover states: hover:shadow-xl, hover:scale-105
    - Example navigation: <nav class="sticky top-0 bg-white shadow-md z-50"><div class="container mx-auto px-6 py-4 flex justify-between items-center">
    - Example card: <div class="bg-white rounded-lg shadow-md hover:shadow-xl transition-shadow duration-300 p-6">
    """,

    "bootstrap": """
    **Bootstrap 5 Implementation:**
    - Include Bootstrap 5.x via CDN: <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    - Use component classes: .navbar, .card, .btn, .form-control, .row, .col-*
    - Grid system: container, row, col-md-6, col-lg-4
    - Utilities: .shadow, .rounded, .p-3, .m-2, .bg-light, .text-primary
    - Components: .btn-primary, .card-body, .navbar-expand-lg
    - Spacing: p-3, py-5, m-4, mx-auto
    - Example navigation: <nav class="navbar navbar-expand-lg navbar-light bg-light sticky-top shadow-sm">
    - Example card: <div class="card shadow-sm hover-shadow"><div class="card-body">
    """,

    "material": """
    **Material Design Implementation:**
    - Include Material Design Lite or similar: <link rel="stylesheet" href="https://code.getmdl.io/1.3.0/material.indigo-pink.min.css">
    - Or use Material Design CSS principles with custom classes
    - Elevation: Use box-shadow for depth (elevation-1 through elevation-24)
    - Ripple effects on buttons (simulated with CSS)
    - Material color palette: Use vibrant, bold accent colors alongside brand colors
    - Typography: Roboto font family
    - Components: Floating action buttons, elevated cards, material input fields
    - Example card: <div class="mdl-card mdl-shadow--4dp" style="box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
    - Example button: <button class="mdl-button mdl-js-button mdl-button--raised mdl-button--colored">
    """
}

# Variant-Specific Instructions
VARIANT_INSTRUCTIONS = {
    1: {
        "type": "ULTIMATE Modern Design - Maximum WOW Factor with Complete Preservation",
        "css_framework": "tailwind + custom animations",
        "framework_instructions": """
        **ULTIMATE CSS Framework Implementation:**
        - Include Tailwind CSS v3.x via CDN: <script src="https://cdn.tailwindcss.com"></script>
        - PLUS custom CSS animations for WOW factor
        - Use utility classes: flex, grid, p-*, m-*, text-*, bg-*, rounded-*, shadow-*
        - Modern gradients: bg-gradient-to-r, from-*, to-*
        - Responsive: sm:, md:, lg:, xl: prefixes
        - Advanced hover: hover:shadow-2xl, hover:scale-105, hover:-translate-y-2
        - Smooth animations: transition-all duration-500 ease-in-out
        """,
        "detailed": """
        **Design Philosophy:** ULTIMATE modern design with MAXIMUM visual impact while PERFECTLY preserving every component

        🎨 **CRITICAL: WOW FACTOR STYLING REQUIREMENTS:**

        1. **ANIMATIONS EVERYWHERE:**
           - Fade-in animations on scroll (use CSS @keyframes fadeInUp)
           - Smooth hover effects on ALL interactive elements
           - Scale transforms on cards (hover:scale-105)
           - Slide-in animations for sections
           - Parallax effects for hero section
           - Smooth page transitions

        2. **MODERN VISUAL EFFECTS:**
           - Glassmorphism: backdrop-blur-lg bg-white/30
           - Gradient overlays on hero: bg-gradient-to-br from-brand-color/90 to-brand-color-dark
           - Box shadows with color: shadow-2xl shadow-brand-color/20
           - Rounded corners everywhere: rounded-2xl, rounded-3xl
           - Border gradients for premium feel

        3. **PROFESSIONAL TYPOGRAPHY:**
           - Google Fonts: Inter (headings) + Open Sans (body)
           - Large, bold headings: text-5xl md:text-7xl font-bold
           - Proper text hierarchy with color contrast
           - Letter spacing for headings: tracking-tight

        4. **ADVANCED COMPONENTS:**
           - Sticky navbar with blur effect and shadow on scroll
           - Hero with animated gradient background
           - Cards with hover lift effect and glow
           - Buttons with ripple effect simulation
           - Image galleries with lightbox effect
           - Testimonial carousel with smooth transitions
           - Contact forms with floating labels
           - Footer with social icons that animate on hover

        5. **RESPONSIVE PERFECTION:**
           - Mobile-first approach
           - Smooth breakpoint transitions
           - Touch-friendly elements (min 44x44px)
           - Responsive images with lazy loading

        6. **COLOR & SPACING:**
           - Use EXACT brand colors from palette
           - Generous whitespace: p-12, py-20
           - Consistent spacing rhythm
           - Color gradients for visual interest

        7. **MICRO-INTERACTIONS:**
           - Button hover states with scale and shadow
           - Link underline animations
           - Icon rotations on hover
           - Form input focus states with glow
           - Smooth scroll behavior

        **RESULT:** STUNNING, PROFESSIONAL, MODERN website that makes business owners say "WOW! I NEED THIS!" while preserving EVERY component, image, video, and content from the original.
        """
    },

    2: {
        "type": "Variant 2: Bootstrap 5 - Polished Professional Components",
        "css_framework": "bootstrap",
        "framework_instructions": CSS_FRAMEWORK_INSTRUCTIONS["bootstrap"],
        "detailed": """
        **Design Philosophy:** Component-rich professional design with polished UI elements

        **Styling Approach:**
        - Use Bootstrap's pre-built components for rapid professional appearance
        - Color scheme: Brand colors as btn-primary, bg-primary; light grays for sections
        - Typography: Lato or Source Sans Pro from Google Fonts
        - Spacing: Bootstrap spacing utilities (p-4, py-5, mb-3)
        - Components: Use .card, .btn, .navbar, .form-control classes
        - Shadows: Bootstrap shadows (.shadow-sm, .shadow) with custom hover effects
        - Buttons: Bootstrap button variants (.btn-primary, .btn-lg) with brand colors
        - Grid: Responsive grid (.row, .col-md-6, .col-lg-4) for layouts
        - Animations: Add custom transitions for hover states

        **Result:** Polished, corporate-ready design perfect for established businesses
        """
    },

    3: {
        "type": "Variant 3: Material Design - Bold Modern Elevation",
        "css_framework": "material",
        "framework_instructions": CSS_FRAMEWORK_INSTRUCTIONS["material"],
        "detailed": """
        **Design Philosophy:** Bold Google Material Design with elevation and vibrant interactions

        **Styling Approach:**
        - Apply Material Design principles: elevation, bold colors, geometric shapes
        - Color scheme: Brand colors as primary, use material color palette for accents
        - Typography: Roboto from Google Fonts (Material Design standard)
        - Elevation: Strong shadows for depth (box-shadow: 0 4px 8px rgba(0,0,0,0.2))
        - Buttons: Raised buttons with shadows, bold colors, ripple effects (CSS animations)
        - Cards: Elevated cards (mdl-shadow--4dp equivalent) with strong shadows
        - FAB: Consider floating action button for primary CTA
        - Interactions: Bold hover effects with scale and shadow changes
        - Animations: Material motion (ease-out timing, quick transforms)

        **Result:** Bold, modern, eye-catching design perfect for creative/tech businesses
        """
    }
}

# Main Modernization Prompt Template
MODERNIZATION_PROMPT = """
You are an EXPERT web designer specializing in modernizing outdated websites while PERFECTLY preserving their exact structure, content, and brand identity. Your goal is to create STUNNING, PROFESSIONAL modern designs that make business owners EXCITED to upgrade their websites.

**Original Website HTML:**
{scraped_html}

**Original CSS:**
{scraped_css}

**Component Structure Analysis:**
- Total Components/Sections: {component_count}
- Component Details (YOU MUST CREATE ALL OF THESE IN YOUR OUTPUT):

{component_details}

**Brand Colors (MUST PRESERVE EXACTLY - use these EXACT hex codes):**
{color_palette}

**Media Assets (MUST EMBED ALL in EXACT same positions):**
- Logos: {logo_urls}
- Images: {image_urls}
- Videos: {video_urls}
- Maps: {map_embeds}

**Business Information:**
- Name: {business_name}
- Category: {category}
- Description: {description}

**Identified Website Problems to Fix:**
{problems_list}

═══════════════════════════════════════════════════════════════════
🚨 CRITICAL MODERNIZATION RULES - FOLLOW EXACTLY 🚨
═══════════════════════════════════════════════════════════════════

1. **🚨 ABSOLUTE PRESERVATION REQUIREMENTS - DO NOT SKIP ANYTHING! 🚨**

   ✓ **EXACT Component Count:** Original has {component_count} components/sections. Your output MUST have ALL {component_count} components. DO NOT SKIP ANY SECTION, DIV, OR COMPONENT. Count them carefully!

   ✓ **EVERY SINGLE DIV/SECTION:** Go through the original HTML line by line. For EVERY div, section, article, aside - you MUST include it in your redesigned HTML with modern styling. DO NOT SIMPLIFY. DO NOT SKIP.

   ✓ **EXACT Content Text:** Copy ALL text content word-for-word from EVERY component. Do NOT paraphrase, summarize, or change any wording. Include EVERYTHING.

   ✓ **EXACT HTML Structure:** Preserve the exact DOM hierarchy, semantic tags, and information architecture. If original has a nested structure, keep it nested.

   ✓ **EXACT Brand Colors:** Use the EXACT hex codes from {color_palette}. Do NOT create new colors or variations. These are the brand's identity.

   ✓ **EVERY SINGLE LOGO:** Embed EVERY logo from {logo_urls} in the EXACT same positions. Count: {logo_urls} has X logos - your output must have X logos in the same places.

   ✓ **EVERY SINGLE IMAGE:** Embed EVERY image from {image_urls} in the EXACT same positions with same alt text. Count them! If original has 15 images, your output MUST have 15 images.

   ✓ **EVERY SINGLE VIDEO:** Embed EVERY video from {video_urls} with same functionality. If original has videos, your output MUST have those exact videos embedded.

   ✓ **EVERY MAP:** Embed EVERY map from {map_embeds} in the EXACT same locations.

   ✓ **ALL Links & Navigation:** Preserve EVERY link, menu item, button target, and navigation element exactly as original.

   ✓ **EXACT Content Hierarchy:** Maintain the same heading structure (H1, H2, H3), same content order, same sections in same order.

   🚨 **CRITICAL WARNING:** If you skip even ONE component, ONE image, ONE video, or ONE section, the output will be REJECTED. Go through the original HTML component by component and ensure you've included EVERYTHING with modern styling.

2. **🚨 WHAT YOU MUST MODERNIZE - RADICAL VISUAL TRANSFORMATION 🚨**

   🎨 **CSS Framework Application ({css_framework}):**
   {framework_specific_instructions}

   ✨ **MANDATORY MODERN TRANSFORMATIONS FOR EVERY COMPONENT:**

   **NAVIGATION BAR - MUST INCLUDE:**
   - Sticky navigation with backdrop-blur-md and shadow on scroll
   - Smooth transitions: transition-all duration-300
   - Hover effects on links: hover:text-primary-color hover:scale-105
   - Mobile menu with smooth slide-in animation
   - Logo with subtle hover animation

   **HERO SECTION - MUST INCLUDE:**
   - Full-screen height with min-h-screen
   - Animated gradient background: bg-gradient-to-br from-primary to-secondary
   - Fade-in animation for heading: @keyframes fadeInUp
   - CTA buttons with hover lift: hover:shadow-2xl hover:-translate-y-1
   - Parallax effect or animated background shapes
   - Large, bold typography: text-6xl md:text-8xl

   **CONTENT CARDS - MUST INCLUDE:**
   - Shadow elevation: shadow-xl
   - Rounded corners: rounded-2xl
   - Hover transform: hover:scale-105 hover:shadow-2xl transition-all duration-500
   - Gradient borders or glow effects
   - Smooth image zoom on hover

   **BUTTONS - MUST INCLUDE:**
   - Gradient backgrounds: bg-gradient-to-r from-primary to-primary-dark
   - Shadow with glow: shadow-lg shadow-primary/50
   - Hover effects: hover:scale-110 hover:shadow-2xl
   - Smooth transitions: transition-all duration-300
   - Ripple effect simulation with pseudo-elements

   **FORMS - MUST INCLUDE:**
   - Floating labels that animate on focus
   - Input focus glow: focus:ring-2 focus:ring-primary focus:border-transparent
   - Smooth transitions on all states
   - Modern validation styling with animated check marks

   **IMAGE GALLERIES - MUST INCLUDE:**
   - CSS Grid layout: grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4
   - Hover zoom effect: hover:scale-110 overflow-hidden
   - Smooth opacity transitions
   - Optional lightbox effect simulation

   **TESTIMONIALS - MUST INCLUDE:**
   - Card design with user photos
   - Quote styling with modern typography
   - Slider/carousel indicators if multiple testimonials
   - Hover effects and smooth transitions

   **FOOTER - MUST INCLUDE:**
   - Multi-column layout with CSS Grid
   - Social icons with hover animations: hover:scale-125 hover:rotate-12
   - Gradient divider line
   - Modern spacing and typography

   **Typography: Apply modern web font pairings (e.g., Inter + Merriweather, Poppins + Open Sans)**

   🎬 **MANDATORY CSS ANIMATIONS - MUST INCLUDE IN <style> TAG:**

   Add this CSS in your <head> section inside a <style> tag:

   /* REQUIRED: Smooth scroll behavior */
   html {{
     scroll-behavior: smooth;
   }}

   /* REQUIRED: Fade in up animation */
   @keyframes fadeInUp {{
     from {{
       opacity: 0;
       transform: translateY(30px);
     }}
     to {{
       opacity: 1;
       transform: translateY(0);
     }}
   }}

   /* REQUIRED: Scale in animation */
   @keyframes scaleIn {{
     from {{
       opacity: 0;
       transform: scale(0.9);
     }}
     to {{
       opacity: 1;
       transform: scale(1);
     }}
   }}

   /* REQUIRED: Slide in from left */
   @keyframes slideInLeft {{
     from {{
       opacity: 0;
       transform: translateX(-50px);
     }}
     to {{
       opacity: 1;
       transform: translateX(0);
     }}
   }}

   /* REQUIRED: Slide in from right */
   @keyframes slideInRight {{
     from {{
       opacity: 0;
       transform: translateX(50px);
     }}
     to {{
       opacity: 1;
       transform: translateX(0);
     }}
   }}

   /* REQUIRED: Apply animations to sections */
   section {{
     animation: fadeInUp 0.8s ease-out;
   }}

   /* REQUIRED: Smooth transitions on all interactive elements */
   button, a, input, .card, img {{
     transition: all 0.3s ease-in-out;
   }}

   📐 **Modern Layout Patterns:**
   - Use CSS Grid for complex layouts (e.g., gallery grids, multi-column sections)
   - Use Flexbox for navigation, cards, button groups, content alignment
   - Strategic whitespace: Generous padding/margins for breathing room
   - Visual balance: Proper alignment, consistent spacing rhythm

   📱 **Mobile-First Responsive Design:**
   - Breakpoints: Mobile (<640px), Tablet (640-1024px), Desktop (>1024px)
   - Smooth transitions between breakpoints
   - Touch-friendly interactive elements (min 44x44px)

   🎭 **Modern Interactions:**
   - Smooth hover effects on buttons, cards, links
   - Elegant CSS transitions (0.2-0.3s duration)
   - Subtle scale transforms on hover
   - Shadow elevation changes for depth

   🎯 **Visual Hierarchy Enhancements:**
   - Clear focal points with size, color, contrast
   - Proper heading scale (font-size, weight, spacing)
   - Strategic use of whitespace for content grouping
   - Color contrast for accessibility (WCAG AA minimum)

3. **CSS FRAMEWORK & VARIANT INSTRUCTIONS:**

   **{variant_type}**
   {variant_detailed_instructions}

═══════════════════════════════════════════════════════════════════
🎯 OUTPUT REQUIREMENTS - DELIVER PERFECTION 🎯
═══════════════════════════════════════════════════════════════════

✓ Complete, valid HTML5 document with DOCTYPE declaration
✓ {css_framework} CSS properly integrated (CDN link or embedded styles)
✓ EXACT {component_count} components/sections as original
✓ ALL logos from {logo_urls} embedded in exact positions
✓ ALL images from {image_urls} embedded with proper alt text
✓ ALL videos from {video_urls} embedded and functional
✓ ALL maps from {map_embeds} embedded in correct locations
✓ EXACT brand colors {color_palette} used throughout
✓ ALL original text content preserved word-for-word
✓ Semantic HTML5 tags (header, nav, main, section, article, aside, footer)
✓ Responsive meta viewport tag for mobile
✓ Modern, professional aesthetic with "WOW FACTOR" visual impact
✓ Production-ready code (NO placeholders, NO "Lorem ipsum", NO dummy content)
✓ Google Fonts integrated for modern typography
✓ Smooth CSS transitions and hover effects
✓ Accessibility: proper ARIA labels, semantic structure, color contrast

═══════════════════════════════════════════════════════════════════
💼 BUSINESS GOAL: IMPRESS THE BUSINESS OWNER 💼
═══════════════════════════════════════════════════════════════════

This modernized website will be shown to the business owner as a demonstration of what their upgraded website could look like. Your design MUST:

🌟 **Make them say "WOW, this is AMAZING!"**
🌟 **Show DRAMATIC, RADICAL transformation from the old website**
🌟 **Look COMPLETELY DIFFERENT visually - modern, sleek, animated**
🌟 **Feel PROFESSIONAL, MODERN, and PREMIUM**
🌟 **Maintain their BRAND IDENTITY (same colors, same content, same structure)**
🌟 **Make them EXCITED and CONFIDENT to invest in the website redesign**

🚨 **CRITICAL WARNING ABOUT VISUAL TRANSFORMATION:**

The original website looks OLD and OUTDATED. Your job is to make it look COMPLETELY MODERN AND PROFESSIONAL.

❌ **DO NOT** just copy the old HTML with minor CSS changes
❌ **DO NOT** keep the old layout style
❌ **DO NOT** make it look similar to the original

✅ **DO** create a COMPLETELY new visual design
✅ **DO** add extensive animations and effects
✅ **DO** use modern layout patterns (CSS Grid, Flexbox)
✅ **DO** make it look like a 2024 premium website
✅ **DO** add gradients, shadows, blur effects, animations
✅ **DO** make every section visually stunning

**COMPARISON:**
- Original: Old, static, plain, no animations, basic layout
- Your Output: MODERN, animated, beautiful, professional, stunning visual effects

Your success metric: Would a business owner be THRILLED to pay for this upgrade? If the visual transformation isn't DRAMATIC, start over!

═══════════════════════════════════════════════════════════════════
🚨 CRITICAL OUTPUT FORMAT - READ CAREFULLY 🚨
═══════════════════════════════════════════════════════════════════

**IMPORTANT - YOUR RESPONSE FORMAT:**

You MUST respond with ONLY the complete HTML code.

❌ DO NOT include ANY explanatory text before the HTML
❌ DO NOT include ANY explanatory text after the HTML
❌ DO NOT include ANY comments about what you changed
❌ DO NOT include ANY notes or descriptions
❌ DO NOT wrap the HTML in markdown code blocks (no ```)

✓ START your response with: <!DOCTYPE html>
✓ END your response with: </html>
✓ OUTPUT PURE HTML ONLY - NOTHING ELSE

Your ENTIRE response should be the complete, valid HTML document. The first line should be <!DOCTYPE html> and the last line should be </html>. Everything else is invalid.

═══════════════════════════════════════════════════════════════════
📋 MANDATORY STEP-BY-STEP COMPONENT CHECKLIST 📋
═══════════════════════════════════════════════════════════════════

BEFORE YOU START WRITING HTML, you MUST create this mental checklist:

**STEP 1: COUNT ALL COMPONENTS**
- Original has {component_count} components
- I will create {component_count} modern styled components
- I will NOT skip any component

**STEP 2: LIST ALL COMPONENTS FROM COMPONENT DETAILS ABOVE**
Go through the Component Details section above ONE BY ONE.
For EACH component listed:
- [ ] Component 1: [type] - [heading] - CREATE modern version with ALL content shown
- [ ] Component 2: [type] - [heading] - CREATE modern version with ALL content shown
- [ ] Component 3: [type] - [heading] - CREATE modern version with ALL content shown
... (continue for ALL {component_count} components - they are all listed above!)

**STEP 3: COUNT AND VERIFY ALL MEDIA**
- Logo URLs: {logo_urls} - I will embed ALL of these
- Image URLs: {image_urls} - I will embed ALL of these
- Video URLs: {video_urls} - I will embed ALL of these
- Map embeds: {map_embeds} - I will embed ALL of these

**STEP 4: GO THROUGH ORIGINAL HTML SECTION BY SECTION**
For EACH major section/div in the original HTML:
1. Identify its purpose (hero, services, about, contact, etc.)
2. Extract ALL text content word-for-word
3. Extract ALL images/videos from that section
4. Create modern styled version with {css_framework}
5. Verify I didn't skip anything
6. Move to next section

**STEP 5: FINAL VERIFICATION BEFORE OUTPUT**
Before you output the HTML, verify:
✓ Did I include ALL {component_count} components? (Count them!)
✓ Did I include ALL logos from {logo_urls}? (Count them!)
✓ Did I include ALL images from {image_urls}? (Count them!)
✓ Did I include ALL videos from {video_urls}? (Count them!)
✓ Did I use the EXACT brand colors {color_palette}?
✓ Is my HTML starting with <!DOCTYPE html> and ending with </html>?
✓ Did I include ZERO explanatory text?

If ANY answer is "No", DO NOT SUBMIT - go back and fix it!

Now, follow this checklist carefully and generate the COMPLETE, STUNNING, PROFESSIONAL, MODERN HTML that includes EVERY SINGLE component, image, and video:
"""
