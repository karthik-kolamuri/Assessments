import os
import subprocess
import markdown

WORKSPACE_DIR = r"d:\Josh Talks\ausindia"
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
if not os.path.exists(CHROME_PATH):
    CHROME_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

CSS_STYLE = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&family=Outfit:wght@600;700;800&display=swap');
    @page { size: A4; margin: 18mm 16mm 18mm 16mm; }
    body { font-family: 'Inter', sans-serif; color: #1e293b; line-height: 1.6; font-size: 10pt; }
    h1 { font-family: 'Outfit', sans-serif; font-size: 18pt; font-weight: 800; color: #0f172a; border-bottom: 2px solid #6366f1; padding-bottom: 6px; margin-top: 0; }
    h2 { font-family: 'Outfit', sans-serif; font-size: 13pt; font-weight: 700; color: #1e293b; margin-top: 16px; border-bottom: 1px solid #e2e8f0; padding-bottom: 4px; }
    h3 { font-size: 11pt; font-weight: 600; color: #334155; margin-top: 12px; }
    table { width: 100%; border-collapse: collapse; margin: 12px 0; font-size: 8.5pt; }
    th { background: #f1f5f9; padding: 6px 8px; border: 1px solid #cbd5e1; font-weight: 700; }
    td { padding: 6px 8px; border: 1px solid #e2e8f0; }
    code { font-family: 'JetBrains Mono', monospace; font-size: 8.5pt; background: #f1f5f9; padding: 2px 4px; border-radius: 4px; }
    pre { background: #0f172a; color: #f8fafc; padding: 10px 12px; border-radius: 6px; font-size: 8pt; overflow-x: auto; margin: 10px 0; }
    pre code { background: transparent; color: #f8fafc; }
    blockquote { border-left: 4px solid #6366f1; background: #f5f3ff; padding: 8px 12px; margin: 10px 0; }
</style>
"""

with open(os.path.join(WORKSPACE_DIR, "README.md"), "r", encoding="utf-8") as f:
    text = f.read()

html = markdown.markdown(text, extensions=['tables', 'fenced_code'])
full_html = f"<!DOCTYPE html><html><head><meta charset='utf-8'>{CSS_STYLE}</head><body>{html}</body></html>"

temp_html = os.path.join(WORKSPACE_DIR, "README.html")
with open(temp_html, "w", encoding="utf-8") as f:
    f.write(full_html)

pdf_out = os.path.join(WORKSPACE_DIR, "CertEngine_Backend_Submission.pdf")
cmd = [
    CHROME_PATH,
    "--headless",
    "--disable-gpu",
    "--run-all-compositor-stages-before-draw",
    f"--print-to-pdf={pdf_out}",
    temp_html
]
subprocess.run(cmd, check=True)
print("Generated PDF documentation:", pdf_out)
