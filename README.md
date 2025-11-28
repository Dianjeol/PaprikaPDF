# Paprika Recipe Converter

Convert your Paprika recipe export files (`.paprikarecipes`) into beautifully formatted **HTML and PDF cookbooks** with personalized cover pages, automatic table of contents, and professional recipe cards.

## Features

✨ **Beautiful Cookbook Generation**
- Personalized cover page with your name
- Automatic table of contents with page numbers
- Professional recipe card layout with images, ingredients, and directions
- One recipe per page in PDF format
- Responsive design for both screen viewing and printing

📊 **Supported Export Format**
- Paprika app `.paprikarecipes` files (ZIP format with JSON recipe data)

🎨 **Output Formats**
- **HTML** - for web viewing and editing
- **PDF** - for printing and distribution

## Getting Started

### Prerequisites
- Python 3.11+
- pip or uv package manager

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/paprika-recipe-converter.git
cd paprika-recipe-converter
```

2. Install dependencies:
```bash
pip install -r requirements.txt
# or with uv:
uv pip install -r requirements.txt
```

### Running Locally

```bash
python app.py
```

The app will start at `http://localhost:5000`

## Usage

1. Open the application in your browser
2. Enter your name (will appear on the cookbook cover)
3. Select your `.paprikarecipes` file from Paprika app
4. Click "Create Cookbook"
5. Download the generated HTML or PDF files

## Deployment

### On Replit (Free)
- Works in development mode while the Replit project is open
- Perfect for quick use without installation

### Other Platforms
The app requires a paid hosting plan on platforms like Replit (Autoscale) to run continuously. Alternatively, host on:
- Railway
- Render
- PythonAnywhere
- Your own server

## Project Structure

```
├── app.py              # Main Flask application
├── pyproject.toml      # Project dependencies
├── .gitignore          # Git ignore rules
├── static/
│   └── downloads/      # Generated PDF/HTML files (temporary)
└── README.md           # This file
```

## Technical Details

- **Framework**: Flask
- **PDF Generation**: WeasyPrint
- **Recipe Format**: Paprika JSON (gzip compressed or plain)
- **Image Handling**: Base64 embedded in HTML/PDF

## Features in Detail

### Cover Page
- Personalized with your name
- Current year
- Elegant typography with custom fonts
- Decorative border and icon

### Table of Contents
- Automatically generated from recipe names
- Two-column layout
- CSS target-counter for page numbers
- Dotted lines connecting recipe names to page numbers

### Recipe Cards
- Recipe title and metadata (prep time, cook time, servings)
- Recipe image (if available)
- Ingredients list
- Step-by-step directions with numbered steps
- Optional notes section
- Page break after each recipe (PDF)

## License

This project is available for personal and educational use.

## Support

For issues or feature requests, please use the GitHub issues section.

---

**Note**: This tool is designed for personal use. Respect copyright when using recipes from others.
