# Automatic-CV-Processing-with-AI-Agent
A tool that reads uploaded CVs and ranks them against a job description. It pulls the text out of each CV, compares the candidate's skills and experience to what the job needs, and gives back a ranked list you can export as a PDF or Excel file. It works with English, Arabic, and Kurdish CVs.

This was my BSc graduation project.

## About this repository

The source code isn't included here. This repo only has the sample data — example CVs and job descriptions — so you can see the kind of input the system takes and what it's built to handle. The actual code is kept private.

## What it does

- Reads text from PDF and Word CVs
- Handles English, Arabic, and Kurdish, including matching across languages
- Detects the CV's language and normalizes the wording before comparing
- Scores and ranks candidates against a job using NLP and the Claude API, with a dictionary-based fallback if the API is off
- Logs in with Google or with email + an OTP code; passwords are hashed
- Exports the ranked results as PDF or Excel

## Built with

Python and FastAPI on the backend, SQLite for storage, and scikit-learn plus a custom trilingual dictionary for the matching. PyMuPDF and python-docx read the files, ReportLab and openpyxl make the exports, and the Claude API does the smarter matching. Deployed on Railway.

## Sample data

The uploads folder has example CVs in English, Arabic, and Kurdish across a few different jobs. They show the file format the system accepts and the mix of languages it's meant to deal with.

## How it works

1. You upload the CVs and set up a job with its required skills.
2. The text is pulled out of each CV.
3. The language is detected and the wording is normalized (and translated if needed).
4. Each candidate is scored against the job.
5. The candidates are ranked and the results are exported.
