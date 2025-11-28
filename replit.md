# Paprika Recipe Converter

## Overview
A Flask web application that converts Paprika recipe export files (.paprikarecipes) into beautifully formatted PDF cookbooks.

## Features
- Upload .paprikarecipes export files
- Personalized cover page with your name
- Automatic table of contents
- Beautiful typography using Google Fonts (Playfair Display, Lato, Merriweather)
- Recipe cards with images, ingredients, and step-by-step directions
- Metadata display (prep time, cook time, servings)
- Professional A4 PDF output with page numbers

## How to Use
1. Enter your name for the cookbook cover
2. Select your .paprikarecipes file (exported from Paprika app)
3. Click "Buch generieren (PDF)" to generate your cookbook
4. The PDF will automatically download

## Tech Stack
- Python 3.11
- Flask (web framework)
- WeasyPrint (PDF generation)
- Google Fonts for typography

## Project Structure
- `app.py` - Main Flask application with all routes and PDF generation logic

## Recent Changes
- 2025-11-28: Initial setup of Paprika Recipe Converter
