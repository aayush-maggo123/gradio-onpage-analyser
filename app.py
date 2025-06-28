import gradio as gr
from agents import Agent, Runner, function_tool
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
import asyncio
import nest_asyncio

# Load environment variables
load_dotenv()

# Apply nest_asyncio to handle nested event loops
nest_asyncio.apply()

@function_tool
def scrape_webpage_seo(url: str, primary_keyword: str, secondary_keyword: str, brand_name: str) -> str:
    """
    Scrape SEO data from a webpage and analyze on-page optimization for specific keywords.
    
    Args:
        url (str): The URL of the webpage to analyze (must include http:// or https://)
        primary_keyword (str): The main keyword to optimize for
        secondary_keyword (str): The secondary keyword to include
        brand_name (str): The brand name to include in title if space allows
        
    Returns:
        str: A detailed on-page SEO analysis report focusing on keyword optimization
    """
    try:
        # Send HTTP request with enhanced headers
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.google.com/",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "DNT": "1",
            "Cookie": "testcookie=1"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract meta title
        meta_title = ""
        title_tag = soup.find('title')
        if title_tag:
            meta_title = title_tag.get_text().strip()
        
        # Extract meta description
        meta_description = ""
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            meta_description = meta_desc.get('content', '').strip()
        
        # Extract all header tags
        headers_data = {'h1': [], 'h2': [], 'h3': [], 'h4': [], 'h5': [], 'h6': []}
        for i in range(1, 7):
            header_tags = soup.find_all(f'h{i}')
            headers_data[f'h{i}'] = [tag.get_text().strip() for tag in header_tags if tag.get_text().strip()]
        
        # Extract main content
        for script in soup(["script", "style"]):
            script.decompose()
        
        text_content = soup.get_text()
        lines = (line.strip() for line in text_content.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        content = ' '.join(chunk for chunk in chunks if chunk)
        
        # Calculate SEO metrics
        word_count = len(content.split())
        title_length = len(meta_title)
        desc_length = len(meta_description)
        
        # Keyword analysis
        primary_kw_count = content.lower().count(primary_keyword.lower())
        secondary_kw_count = content.lower().count(secondary_keyword.lower())
        brand_count = content.lower().count(brand_name.lower())
        
        # Check keyword presence in title
        title_has_primary = primary_keyword.lower() in meta_title.lower()
        title_has_secondary = secondary_keyword.lower() in meta_title.lower()
        title_has_brand = brand_name.lower() in meta_title.lower()
        
        # Check keyword presence in description
        desc_has_primary = primary_keyword.lower() in meta_description.lower()
        desc_has_secondary = secondary_keyword.lower() in meta_description.lower()
        
        # Check keyword presence in headers
        h1_has_primary = any(primary_keyword.lower() in h1.lower() for h1 in headers_data['h1'])
        h2_has_primary = any(primary_keyword.lower() in h2.lower() for h2 in headers_data['h2'])
        h2_has_secondary = any(secondary_keyword.lower() in h2.lower() for h2 in headers_data['h2'])
        
        # Generate on-page SEO analysis report
        report = f"""
=== ON-PAGE SEO ANALYSIS FOR {url} ===

TARGET KEYWORDS:
- Primary Keyword: {primary_keyword}
- Secondary Keyword: {secondary_keyword}
- Brand Name: {brand_name}

META TITLE ANALYSIS:
- Current Title: {meta_title}
- Title Length: {title_length} characters (Target: 60-70 characters)
- Primary Keyword in Title: {'✅ YES' if title_has_primary else '❌ NO'}
- Secondary Keyword in Title: {'✅ YES' if title_has_secondary else '❌ NO'}
- Brand Name in Title: {'✅ YES' if title_has_brand else '❌ NO'}

META DESCRIPTION ANALYSIS:
- Current Description: {meta_description}
- Description Length: {desc_length} characters (Target: 150-160 characters)
- Primary Keyword in Description: {'✅ YES' if desc_has_primary else '❌ NO'}
- Secondary Keyword in Description: {'✅ YES' if desc_has_secondary else '❌ NO'}

HEADER TAG ANALYSIS:
- H1 Tags: {len(headers_data['h1'])} found
- H2 Tags: {len(headers_data['h2'])} found
- Primary Keyword in H1: {'✅ YES' if h1_has_primary else '❌ NO'}
- Primary Keyword in H2: {'✅ YES' if h2_has_primary else '❌ NO'}
- Secondary Keyword in H2: {'✅ YES' if h2_has_secondary else '❌ NO'}

CONTENT ANALYSIS:
- Word Count: {word_count} words
- Primary Keyword Count: {primary_kw_count} times
- Secondary Keyword Count: {secondary_kw_count} times
- Brand Name Count: {brand_count} times

ON-PAGE SEO RECOMMENDATIONS:
"""
        
        # Title recommendations
        if not title_has_primary:
            report += f"- ❌ PRIMARY KEYWORD MISSING: Add '{primary_keyword}' at the beginning of the title\n"
        elif not meta_title.lower().startswith(primary_keyword.lower()):
            report += f"- ⚠️ PRIMARY KEYWORD POSITION: Move '{primary_keyword}' to the beginning of the title\n"
        else:
            report += "- ✅ Primary keyword is correctly positioned at the beginning\n"
        
        if not title_has_secondary:
            report += f"- ❌ SECONDARY KEYWORD MISSING: Add '{secondary_keyword}' to the title\n"
        else:
            report += "- ✅ Secondary keyword is present in title\n"
        
        if title_length < 50:
            report += "- ⚠️ TITLE TOO SHORT: Add more content to reach 60-70 characters\n"
        elif title_length > 70:
            report += "- ⚠️ TITLE TOO LONG: Shorten to 60-70 characters\n"
        else:
            report += "- ✅ Title length is optimal (60-70 characters)\n"
        
        if not title_has_brand and title_length < 60:
            report += f"- 💡 BRAND OPPORTUNITY: Add '{brand_name}' to the title if space allows\n"
        
        # Description recommendations
        if not desc_has_primary:
            report += f"- ❌ PRIMARY KEYWORD MISSING: Include '{primary_keyword}' in meta description\n"
        else:
            report += "- ✅ Primary keyword is present in description\n"
        
        if not desc_has_secondary:
            report += f"- ❌ SECONDARY KEYWORD MISSING: Include '{secondary_keyword}' in meta description\n"
        else:
            report += "- ✅ Secondary keyword is present in description\n"
        
        if desc_length < 120:
            report += "- ⚠️ DESCRIPTION TOO SHORT: Expand to 150-160 characters\n"
        elif desc_length > 170:
            report += "- ⚠️ DESCRIPTION TOO LONG: Shorten to 150-160 characters\n"
        else:
            report += "- ✅ Description length is optimal\n"
        
        # Header recommendations
        if not h1_has_primary:
            report += f"- ❌ PRIMARY KEYWORD MISSING: Include '{primary_keyword}' in H1 tag\n"
        else:
            report += "- ✅ Primary keyword is present in H1\n"
        
        if not h2_has_primary:
            report += f"- ⚠️ PRIMARY KEYWORD: Consider adding '{primary_keyword}' to some H2 tags\n"
        else:
            report += "- ✅ Primary keyword is present in H2 tags\n"
        
        if not h2_has_secondary:
            report += f"- ❌ SECONDARY KEYWORD MISSING: Include '{secondary_keyword}' in H2 tags\n"
        else:
            report += "- ✅ Secondary keyword is present in H2 tags\n"
        
        # Content recommendations
        if primary_kw_count < 3:
            report += f"- ⚠️ PRIMARY KEYWORD DENSITY: Increase usage of '{primary_keyword}' in content\n"
        else:
            report += "- ✅ Primary keyword density is good\n"
        
        if secondary_kw_count < 2:
            report += f"- ⚠️ SECONDARY KEYWORD DENSITY: Increase usage of '{secondary_keyword}' in content\n"
        else:
            report += "- ✅ Secondary keyword density is good\n"
        
        # Suggested title format
        suggested_title = f"{primary_keyword} | {secondary_keyword} | {brand_name}"
        report += f"""
SUGGESTED TITLE FORMAT:
"{suggested_title}"
(Length: {len(suggested_title)} characters)
"""
        
        return report
        
    except requests.RequestException as e:
        return f"Error: Failed to fetch URL {url}. Error: {str(e)}"
    except Exception as e:
        return f"Error: Unexpected error while analyzing {url}. Error: {str(e)}"

# Create the on-page SEO agent
agent = Agent(
    name="On-Page SEO Keyword Analyst", 
    instructions="""You are a specialized on-page SEO analyst focused on keyword optimization and content structure. 
    You analyze web pages for proper keyword placement in titles, meta descriptions, headers, and content.
    
    Your analysis focuses ONLY on on-page elements:
    1. Meta Title optimization (60-70 characters, primary keyword first, secondary keyword, brand name)
    2. Meta Description optimization (150-160 characters, include both keywords naturally)
    3. H1 tag optimization (must contain primary keyword)
    4. H2 tag optimization (should contain both primary and secondary keywords)
    5. Content keyword density and natural placement
    
    DO NOT analyze technical SEO, page speed, backlinks, or off-page factors.
    Focus purely on content structure and keyword optimization.
    
    When analyzing, use the scrape_webpage_seo tool with the provided keywords and brand name.
    Provide specific, actionable recommendations for improving on-page keyword optimization.""",
    model="gpt-4o-mini",
    tools=[scrape_webpage_seo]
)

def analyze_seo(url, primary_keyword, secondary_keyword, brand_name):
    """
    Function to analyze SEO for the Gradio interface
    """
    try:
        # Validate inputs
        if not url or not primary_keyword or not secondary_keyword or not brand_name:
            return "❌ Please fill in all fields: URL, Primary Keyword, Secondary Keyword, and Brand Name."
        
        # Ensure URL has protocol
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # Create new event loop for this thread
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        # Run the analysis
        result = Runner.run_sync(
            agent, 
            f"Please analyze the on-page SEO for this website: {url}. Focus on optimizing for primary keyword '{primary_keyword}', secondary keyword '{secondary_keyword}', and brand name '{brand_name}'. Provide specific recommendations for title, description, headers, and content optimization."
        )
        
        return result.final_output
        
    except Exception as e:
        return f"❌ Error occurred during analysis: {str(e)}"

# Create Gradio interface
def create_interface():
    with gr.Blocks(
        title="On-Page SEO Keyword Analyzer",
        theme=gr.themes.Soft(),
        css="""
        .gradio-container {
            max-width: 1200px !important;
        }
        .output-text {
            font-family: 'Courier New', monospace;
            white-space: pre-wrap;
        }
        """
    ) as demo:
        gr.Markdown(
            """
            # 🔍 On-Page SEO Keyword Analyzer
            
            Analyze your webpage's on-page SEO optimization for specific keywords. This tool focuses on:
            - **Meta Title** optimization (60-70 characters)
            - **Meta Description** optimization (150-160 characters)  
            - **H1 & H2** tag keyword placement
            - **Content** keyword density and natural placement
            
            ---
            """
        )
        
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### 📝 Input Parameters")
                
                url_input = gr.Textbox(
                    label="🌐 Website URL",
                    placeholder="https://example.com or example.com",
                    info="Enter the full URL of the webpage to analyze"
                )
                
                primary_keyword = gr.Textbox(
                    label="🎯 Primary Keyword",
                    placeholder="e.g., business loans",
                    info="The main keyword you want to rank for"
                )
                
                secondary_keyword = gr.Textbox(
                    label="🎯 Secondary Keyword", 
                    placeholder="e.g., commercial finance",
                    info="The secondary keyword to include"
                )
                
                brand_name = gr.Textbox(
                    label="🏢 Brand Name",
                    placeholder="e.g., Your Company Name",
                    info="Your brand name to include in title if space allows"
                )
                
                analyze_btn = gr.Button(
                    "🚀 Analyze SEO",
                    variant="primary",
                    size="lg"
                )
                
                gr.Markdown(
                    """
                    ### 💡 Tips:
                    - **Primary Keyword**: Should appear at the beginning of the title
                    - **Secondary Keyword**: Should be included naturally in title and content
                    - **Brand Name**: Will be suggested for title if there's space
                    - **H1 Tags**: Must contain your primary keyword
                    - **H2 Tags**: Should contain both primary and secondary keywords
                    """
                )
            
            with gr.Column(scale=2):
                gr.Markdown("### 📊 Analysis Results")
                
                output = gr.Textbox(
                    label="SEO Analysis Report",
                    lines=25,
                    max_lines=50,
                    interactive=False,
                    elem_classes=["output-text"]
                )
                
                gr.Markdown(
                    """
                    ### 📈 Understanding the Results:
                    - ✅ **Green checks**: Elements are optimized correctly
                    - ❌ **Red X**: Critical issues that need immediate attention
                    - ⚠️ **Yellow warnings**: Areas that could be improved
                    - 💡 **Blue suggestions**: Opportunities for optimization
                    """
                )
        
        # Connect the button to the function
        analyze_btn.click(
            fn=analyze_seo,
            inputs=[url_input, primary_keyword, secondary_keyword, brand_name],
            outputs=output
        )
        
        # Example inputs
        gr.Examples(
            examples=[
                [
                    "https://www.ppmfinance.com.au/",
                    "business loans",
                    "commercial finance", 
                    "PPM Finance"
                ],
                [
                    "https://www.example.com",
                    "digital marketing",
                    "online advertising",
                    "Example Corp"
                ]
            ],
            inputs=[url_input, primary_keyword, secondary_keyword, brand_name]
        )
    
    return demo

# Create and launch the interface
if __name__ == "__main__":
    demo = create_interface()
    demo.launch(
        server_name="localhost",
        server_port=7861,  # Changed port to avoid conflicts
        share=False,  # Disable sharing to avoid antivirus issues
        show_error=True
    ) 