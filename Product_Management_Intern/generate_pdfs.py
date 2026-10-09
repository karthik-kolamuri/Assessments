import os
import subprocess
import markdown

WORKSPACE_DIR = r"d:\Josh Talks\Product_Management_Intern"
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
if not os.path.exists(CHROME_PATH):
    CHROME_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

CSS_STYLE = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');
    
    @page {
        size: A4;
        margin: 20mm 18mm 20mm 18mm;
    }
    
    body {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        color: #1e293b;
        line-height: 1.6;
        font-size: 10.5pt;
        background-color: #ffffff;
    }
    
    h1 {
        font-size: 20pt;
        font-weight: 800;
        color: #0f172a;
        border-bottom: 2px solid #e2e8f0;
        padding-bottom: 8px;
        margin-top: 0;
        margin-bottom: 12px;
        letter-spacing: -0.02em;
    }
    
    h2 {
        font-size: 14pt;
        font-weight: 700;
        color: #1e293b;
        margin-top: 20px;
        margin-bottom: 8px;
        border-bottom: 1px solid #f1f5f9;
        padding-bottom: 4px;
        page-break-after: avoid;
    }
    
    h3 {
        font-size: 12pt;
        font-weight: 600;
        color: #334155;
        margin-top: 16px;
        margin-bottom: 6px;
        page-break-after: avoid;
    }
    
    h4 {
        font-size: 11pt;
        font-weight: 600;
        color: #475569;
        margin-top: 12px;
        margin-bottom: 4px;
    }

    p {
        margin-bottom: 10px;
    }
    
    table {
        width: 100%;
        border-collapse: collapse;
        margin: 14px 0;
        font-size: 9.5pt;
        page-break-inside: avoid;
    }
    
    th {
        background-color: #f8fafc;
        color: #334155;
        font-weight: 600;
        text-align: left;
        padding: 8px 10px;
        border: 1px solid #cbd5e1;
        font-size: 9pt;
        text-transform: uppercase;
        letter-spacing: 0.03em;
    }
    
    td {
        padding: 7px 10px;
        border: 1px solid #e2e8f0;
        vertical-align: top;
    }
    
    tr:nth-child(even) {
        background-color: #f8fafc;
    }
    
    code {
        font-family: 'JetBrains Mono', Consolas, Monaco, monospace;
        font-size: 9pt;
        background-color: #f1f5f9;
        color: #0f172a;
        padding: 2px 5px;
        border-radius: 4px;
    }
    
    pre {
        background-color: #0f172a;
        color: #f8fafc;
        padding: 12px 14px;
        border-radius: 6px;
        overflow-x: auto;
        font-size: 8.5pt;
        line-height: 1.45;
        margin: 12px 0;
        page-break-inside: avoid;
    }
    
    pre code {
        background-color: transparent;
        color: #f8fafc;
        padding: 0;
    }
    
    blockquote {
        border-left: 4px solid #6366f1;
        background-color: #f5f3ff;
        padding: 10px 14px;
        margin: 12px 0;
        color: #312e81;
        font-style: italic;
        border-radius: 0 6px 6px 0;
    }
    
    ul, ol {
        margin-top: 4px;
        margin-bottom: 10px;
        padding-left: 22px;
    }
    
    li {
        margin-bottom: 4px;
    }
    
    hr {
        border: none;
        border-top: 1px solid #e2e8f0;
        margin: 18px 0;
    }
</style>
"""

def md_to_pdf(md_filename, pdf_filename):
    md_path = os.path.join(WORKSPACE_DIR, md_filename)
    html_temp_path = os.path.join(WORKSPACE_DIR, md_filename.replace('.md', '.html'))
    pdf_path = os.path.join(WORKSPACE_DIR, pdf_filename)
    
    with open(md_path, 'r', encoding='utf-8') as f:
        md_text = f.read()
    
    html_body = markdown.markdown(md_text, extensions=['tables', 'fenced_code', 'codehilite'])
    full_html = f"<!DOCTYPE html><html><head><meta charset='utf-8'>{CSS_STYLE}</head><body>{html_body}</body></html>"
    
    with open(html_temp_path, 'w', encoding='utf-8') as f:
        f.write(full_html)
    
    cmd = [
        CHROME_PATH,
        "--headless",
        "--disable-gpu",
        "--run-all-compositor-stages-before-draw",
        f"--print-to-pdf={pdf_path}",
        html_temp_path
    ]
    subprocess.run(cmd, check=True)
    print(f"Generated: {pdf_path}")

def render_leaderboard_mockup():
    html_path = os.path.join(WORKSPACE_DIR, "leaderboard_mockup.html")
    pdf_path = os.path.join(WORKSPACE_DIR, "Firstname_Lastname_Q1_Leaderboard_Sketch.pdf")
    png_path = os.path.join(WORKSPACE_DIR, "Firstname_Lastname_Q1_Leaderboard_Sketch.png")
    
    # PDF export
    cmd_pdf = [
        CHROME_PATH,
        "--headless",
        "--disable-gpu",
        "--run-all-compositor-stages-before-draw",
        f"--print-to-pdf={pdf_path}",
        html_path
    ]
    subprocess.run(cmd_pdf, check=True)
    print(f"Generated: {pdf_path}")
    
    # Screenshot export
    cmd_png = [
        CHROME_PATH,
        "--headless",
        "--disable-gpu",
        "--window-size=1400,1050",
        f"--screenshot={png_path}",
        html_path
    ]
    subprocess.run(cmd_png, check=True)
    print(f"Generated: {png_path}")

if __name__ == "__main__":
    print(f"Using browser executable: {CHROME_PATH}")
    md_to_pdf("Firstname_Lastname_Q1_Main.md", "Firstname_Lastname_Q1_Main.pdf")
    md_to_pdf("Firstname_Lastname_Q1_OnePager.md", "Firstname_Lastname_Q1_OnePager.pdf")
    md_to_pdf("Firstname_Lastname_Q2.md", "Firstname_Lastname_Q2.pdf")
    render_leaderboard_mockup()
    print("All deliverables generated successfully!")
