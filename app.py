import os
import zipfile
import json
import base64
import html
import gzip
import datetime
import io
import uuid
import tempfile
from flask import Flask, request, send_file, Response, make_response
from weasyprint import HTML

# --- Configuration: Use /tmp for all temporary file operations ---
# This is the crucial fix for containerized environments like Render.
TEMP_OUTPUT_DIR = tempfile.gettempdir() # Usually resolves to /tmp

app = Flask(__name__, static_folder='static', static_url_path='/static')


HTML_TEMPLATE_START = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Recipe Collection</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400&family=Lato:wght@400;700&family=Merriweather:ital,wght@0,300;0,400;0,700;1,300&display=swap');
        
        @media print { 
            @page { 
                margin: 1.5cm;
                @bottom-center {
                    content: "Page " counter(page);
                    font-family: 'Lato', sans-serif;
                    font-size: 9pt;
                    color: #999;
                }
            } 
            
            body { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
            .no-print { display: none; }
            .page-break { page-break-after: always; }
            .avoid-break { page-break-inside: avoid; }
            
            .cover-page { 
                page-break-after: always;
                margin: 0;
                height: 100%;
            }
        }
        
        body { 
            font-family: 'Merriweather', serif; 
            color: #333; 
            line-height: 1.45; 
            margin: 0; 
            padding: 0; 
            background: #fff; 
        }
        
        .container { max-width: 900px; margin: 0 auto; padding: 20px; }

        .cover-page {
            text-align: center;
            padding: 40px 20px; 
            border: 6px double #2c3e50; 
            height: 85vh; 
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            background-color: #fdfbf7; 
            box-sizing: border-box;
            margin-bottom: 0;
        }
        
        .cover-subtitle {
            font-family: 'Lato', sans-serif;
            text-transform: uppercase;
            letter-spacing: 3px;
            font-size: 0.9rem;
            color: #e67e22;
            margin-bottom: 15px;
        }

        .cover-title {
            font-family: 'Playfair Display', serif;
            font-size: 3.8rem;
            line-height: 1.1;
            color: #2c3e50;
            margin: 10px 0;
            font-style: italic;
        }
        
        .cover-author {
            font-family: 'Playfair Display', serif;
            font-size: 1.3rem;
            color: #555;
            margin-top: 30px;
            font-weight: normal;
        }
        
        .cover-author strong {
            display: block;
            font-size: 1.8rem;
            color: #2c3e50;
            margin-top: 8px;
        }
        
        .cover-year {
            margin-top: auto; 
            font-family: 'Lato', sans-serif;
            color: #999;
            font-size: 0.8rem;
            padding-top: 20px;
        }

        .cover-icon {
            font-size: 2.5rem;
            color: #e67e22;
            margin: 15px 0;
        }

        .toc-container {
            padding: 20px 0;
        }
        .toc-title {
            font-family: 'Playfair Display', serif;
            font-size: 2.2rem;
            text-align: center;
            color: #2c3e50;
            margin-bottom: 30px;
            border-bottom: 2px solid #e67e22;
            display: inline-block;
            padding-bottom: 8px;
            width: 100%;
        }
        
        .toc-list {
            column-count: 2; 
            column-gap: 40px;
            list-style: none;
            padding: 0;
            font-family: 'Lato', sans-serif;
        }
        
        .toc-item {
            margin-bottom: 6px;
            break-inside: avoid; 
            page-break-inside: avoid;
            font-size: 0.9rem;
        }
        
        .toc-item a {
            text-decoration: none;
            color: #333;
            display: flex;
            align-items: baseline;
            width: 100%;
        }
        
        .toc-dots {
            flex-grow: 1;
            border-bottom: 1px dotted #aaa;
            margin: 0 5px;
            position: relative;
            top: -4px;
        }
        
        .toc-page {
            font-family: 'Lato', sans-serif;
            color: #666;
            font-size: 0.85rem;
            min-width: 25px;
            text-align: right;
        }
        
        .toc-page::after {
            content: target-counter(attr(href), page);
        }

        .recipe-card { 
            margin-bottom: 30px; 
            padding-bottom: 20px; 
            border-bottom: 1px dashed #ccc; 
            padding-top: 10px;
            page-break-after: always;
        }

        h1 { 
            font-family: 'Playfair Display', serif; 
            font-size: 2.0rem; 
            color: #2c3e50; 
            text-align: center; 
            margin-bottom: 5px; 
            margin-top: 0;
        }
        
        .meta-info-container { text-align: center; margin-bottom: 15px; }
        .meta-info { 
            display: inline-block; 
            font-family: 'Lato', sans-serif; 
            font-size: 0.8rem; 
            color: #e67e22; 
            text-transform: uppercase; 
            letter-spacing: 1.5px; 
            font-weight: 700;
            border-top: 1px solid #e67e22;
            border-bottom: 1px solid #e67e22;
            padding: 3px 12px;
        }

        table.layout-table { width: 100%; border-collapse: collapse; border: none; }
        td { vertical-align: top; }
        td.sidebar-cell { width: 30%; padding-right: 20px; }
        td.main-cell { width: 70%; padding-left: 15px; border-left: 1px solid #eee; }

        .sidebar-image {
            width: 100%; height: auto; border-radius: 4px;
            margin-bottom: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            border: 3px solid white;
        }

        h3 { 
            font-family: 'Lato', sans-serif; font-size: 0.95rem;
            color: #2c3e50; margin-top: 0; text-transform: uppercase; 
            border-bottom: 2px solid #e67e22; padding-bottom: 4px;
            margin-bottom: 8px; letter-spacing: 0.5px;
        }
        
        ul { padding-left: 0; margin: 0; list-style: none; }
        li { 
            margin-bottom: 4px; font-size: 0.9rem; 
            border-bottom: 1px dotted #ddd; padding-bottom: 2px; 
        }
        
        .step { 
            margin-bottom: 8px; text-align: justify; 
            position: relative; padding-left: 25px;
            font-size: 0.95rem;
        }
        .step:before {
            content: attr(data-step);
            position: absolute; left: 0; top: 0;
            font-weight: bold; color: white; background: #e67e22; 
            border-radius: 50%; width: 18px; height: 18px; 
            text-align: center; line-height: 18px; font-size: 0.7rem;
            font-family: 'Lato', sans-serif;
        }
        
        .notes { 
            margin-top: 12px; padding: 10px; background: #fffcf5; 
            font-size: 0.85rem; border-left: 3px solid #e67e22; font-style: italic;
        }

        .footer {
            text-align: center; margin-top: 50px; padding-top: 20px;
            border-top: 1px solid #eee; color: #888; font-family: 'Lato', sans-serif;
            font-size: 0.8rem;
        }
    </style>
</head>
<body>
    <div class="container">
"""

def get_cover_html(user_name):
    year = datetime.datetime.now().year
    return f"""
    <div class="cover-page">
        <div class="cover-subtitle">My Personal</div>
        <div class="cover-title">Recipe<br>Collection</div>
        <div class="cover-icon">♨</div>
        <div class="cover-author">from the kitchen of<br><strong>{html.escape(user_name)}</strong></div>
        <div class="cover-year">{year}</div>
    </div>
    """

def get_toc_html(recipes):
    list_items = ""
    for recipe in recipes:
        anchor_id = f"recipe_{hash(recipe['name'])}"
        recipe['anchor_id'] = anchor_id
        list_items += f"""
        <li class="toc-item">
            <a href="#{anchor_id}">
                <span>{html.escape(recipe["name"])}</span>
                <span class="toc-dots"></span>
                <span class="toc-page" href="#{anchor_id}"></span>
            </a>
        </li>"""

    return f"""
    <div class="toc-container">
        <div class="toc-title">Table of Contents</div>
        <ul class="toc-list">
            {list_items}
        </ul>
    </div>
    <div class="page-break"></div>
    """

def get_recipe_html(recipe):
    img_html = ""
    if recipe.get('image_data'):
        img_html = f'<img src="data:image/jpeg;base64,{recipe["image_data"]}" class="sidebar-image">'

    ing_html = "".join([f"<li>{html.escape(i)}</li>" for i in recipe['ingredients_list'] if i.strip()])
    
    dir_html = ""
    step_count = 1
    for step in recipe['directions_list']:
        if step.strip():
            dir_html += f'<div class="step" data-step="{step_count}">{html.escape(step)}</div>'
            step_count += 1

    meta = []
    if recipe.get('prep_time'): meta.append(f"Prep: {recipe['prep_time']}")
    if recipe.get('cook_time'): meta.append(f"Cook: {recipe['cook_time']}")
    if recipe.get('servings'): meta.append(f"Serv.: {recipe['servings']}")
    meta_html = " &nbsp;&bull;&nbsp; ".join(meta) if meta else "&nbsp;"
    
    notes_html = f'<div class="notes"><strong>Note:</strong> {html.escape(recipe["notes"])}</div>' if recipe.get('notes') else ""
    
    anchor_id = recipe.get('anchor_id', '')

    return f"""
    <div class="recipe-card avoid-break" id="{anchor_id}">
        <h1>{html.escape(recipe['name'])}</h1>
        <div class="meta-info-container"><div class="meta-info">{meta_html}</div></div>
        <table class="layout-table">
            <tr>
                <td class="sidebar-cell">{img_html}<h3>Ingredients</h3><ul>{ing_html}</ul></td>
                <td class="main-cell"><h3>Directions</h3>{dir_html}{notes_html}</td>
            </tr>
        </table>
    </div>
    """

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files: 
            return "No file uploaded!", 400
        file = request.files['file']
        user_name = request.form.get('name', 'A Food Lover')
        
        if file.filename == '': 
            return "No file selected", 400
        
        recipes = []
        try:
            # Save the uploaded file temporarily to disk to allow zipfile processing
            temp_zip_path = os.path.join(TEMP_OUTPUT_DIR, str(uuid.uuid4()) + ".zip")
            file.save(temp_zip_path)
            
            with zipfile.ZipFile(temp_zip_path, 'r') as z:
                all_zip_files = z.namelist()
                recipe_files = [f for f in all_zip_files if f.endswith('.paprikarecipe')]
                
                if not recipe_files:
                    os.remove(temp_zip_path)
                    return "No .paprikarecipe files found!", 400
                
                for filename in recipe_files:
                    try:
                        raw_data = z.read(filename)
                        try: 
                            json_str = gzip.decompress(raw_data).decode('utf-8')
                        except: 
                            json_str = raw_data.decode('utf-8')

                        data = json.loads(json_str)
                        recipe_name = data.get('name', 'Untitled')

                        img_b64 = data.get('photo_data') or data.get('photoData')
                        if not img_b64 and data.get('photo'):
                            target = os.path.basename(data['photo'])
                            found = next((f for f in all_zip_files if f.endswith(target)), None)
                            if found:
                                with z.open(found) as img: 
                                    img_b64 = base64.b64encode(img.read()).decode('utf-8')
                        
                        recipes.append({
                            'name': recipe_name,
                            'prep_time': data.get('prep_time', ''),
                            'cook_time': data.get('cook_time', ''),
                            'servings': data.get('servings', ''),
                            'image_data': img_b64, 
                            'ingredients_list': (data.get('ingredients') or "").split('\n'),
                            'directions_list': (data.get('directions') or "").split('\n'),
                            'notes': data.get('notes', '')
                        })
                    except Exception as e:
                        print(f"Error in {filename}: {e}")
                        pass
            
            # Clean up the temporary uploaded zip file immediately
            os.remove(temp_zip_path)


        except Exception as e:
            return f"Error reading file: {str(e)}", 400

        if not recipes:
            return "No recipes found in file!", 400
        
        recipes.sort(key=lambda x: x['name'])

        # Generate unique filename
        unique_id = str(uuid.uuid4())[:8]
        
        # Generate HTML content
        html_content = HTML_TEMPLATE_START
        html_content += get_cover_html(user_name)
        html_content += get_toc_html(recipes)
        for recipe in recipes:
            html_content += get_recipe_html(recipe)
        html_content += f'<div class="footer no-print">Compiled by {html.escape(user_name)}</div>'
        html_content += '</div></body></html>'
        
        # --- FIX 1: Save HTML to the writable /tmp directory ---
        html_name = f"Cookbook_{unique_id}.html"
        html_path = os.path.join(TEMP_OUTPUT_DIR, html_name) 
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"DEBUG: HTML saved: {html_path}")
        
        # --- FIX 1: Generate PDF version and save to the writable /tmp directory ---
        pdf_error = None
        pdf_name = f"Cookbook_{unique_id}.pdf"
        pdf_path = os.path.join(TEMP_OUTPUT_DIR, pdf_name)
        
        try:
            print(f"DEBUG: Starting PDF generation with {len(recipes)} recipes...")
            
            # Generate PDF from same HTML
            pdf_doc = HTML(string=html_content)
            pdf_doc.write_pdf(pdf_path)
            
            print(f"DEBUG: PDF saved: {pdf_path}")
            
        except Exception as e:
            print(f"DEBUG: PDF error: {e}")
            pdf_error = str(e)
            
        # --- FIX 2: Update response to link to the new download route ---
        pdf_link = ""
        if not pdf_error:
            # Link to the new dynamic download route
            pdf_link = f'<a href="/downloads/{pdf_name}" class="download pdf">Download PDF</a>'
        else:
            pdf_link = f'<p class="error">Could not create PDF: {pdf_error}</p>'
        
        return f'''
        <!doctype html>
        <html>
        <head>
            <style>
                body {{ font-family: sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; background: #f4f4f4; }}
                .card {{ background: white; padding: 40px; border-radius: 8px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); text-align: center; max-width: 500px; }}
                a.download {{ display: inline-block; background: #27ae60; color: white; padding: 15px 30px; font-size: 1.1rem; text-decoration: none; border-radius: 4px; margin: 10px; }}
                a.download:hover {{ background: #2ecc71; }}
                a.download.pdf {{ background: #e74c3c; }}
                a.download.pdf:hover {{ background: #c0392b; }}
                a.back {{ color: #e67e22; text-decoration: none; }}
                .info {{ color: #666; font-size: 0.85rem; margin-top: 20px; }}
                .error {{ color: #e74c3c; font-size: 0.85rem; }}
            </style>
        </head>
        <body>
            <div class="card">
                <h2>Cookbook Created!</h2>
                <p>{len(recipes)} recipes were processed.</p>
                <div>
                    {pdf_link}
                    <a href="/downloads/{html_name}" class="download">Download HTML</a>
                </div>
                <br>
                <a href="/" class="back">Create New Cookbook</a>
                <p class="info">PDF generation may take a while for many recipes.</p>
            </div>
        </body>
        </html>
        '''

    return """
    <!doctype html>
    <style>
        body { font-family: sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; background: #f4f4f4; }
        form { background: white; padding: 40px; border-radius: 8px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); text-align: center; }
        input { margin: 10px 0; display: block; width: 100%; padding: 10px; }
        button { background: #e67e22; color: white; border: none; padding: 15px 30px; font-size: 1.2rem; cursor: pointer; border-radius: 4px; transition: all 0.3s; }
        button:disabled { background: #ccc; cursor: not-allowed; }
        .loader { display: none; margin: 20px 0; }
        .loader.active { display: block; }
        .spinner { border: 4px solid #f3f3f3; border-top: 4px solid #e67e22; border-radius: 50%; width: 40px; height: 40px; animation: spin 1s linear infinite; margin: 0 auto 15px; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        .loader-text { color: #666; font-size: 0.95rem; }
    </style>
    <title>Paprika to PDF</title>
    <form method=post enctype=multipart/form-data onsubmit="showLoader()">
      <h2>Paprika Recipe Converter</h2>
      <label>Your name for the cover:</label>
      <input type=text name=name placeholder="Your Name" value="A Food Lover">
      <br>
      <label>Select your .paprikarecipes file:</label>
      <input type=file name=file>
      <br>
      <button type=submit id="submitBtn">Create Cookbook</button>
      <div class="loader" id="loader">
        <div class="spinner"></div>
        <div class="loader-text">Creating cookbook... (may take a moment)</div>
      </div>
    </form>
    <script>
      function showLoader() {
        document.getElementById('loader').classList.add('active');
        document.getElementById('submitBtn').disabled = true;
      }
    </script>
    """

# --- FIX 2: New route to serve files from the temporary directory ---
@app.route('/downloads/<filename>')
def serve_download(filename):
    """Serves the requested file from the temporary directory (/tmp)."""
    # Use os.path.join to securely construct the path within the allowed directory
    safe_path = os.path.join(TEMP_OUTPUT_DIR, filename)

    # Check if the file exists and is in the /tmp directory (for security)
    if os.path.exists(safe_path) and safe_path.startswith(TEMP_OUTPUT_DIR):
        # We use 'as_attachment=True' to force a download dialogue
        response = send_file(safe_path, as_attachment=True, download_name=filename)
        
        # Schedule cleanup: It's good practice to try and remove the temp file
        # after it's been sent, though this is difficult in Flask after send_file.
        # For simplicity in this example, we rely on the OS/container to clean /tmp.
        
        return response
    
    return "File not found or access denied.", 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
