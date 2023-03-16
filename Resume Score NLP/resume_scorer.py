from io import BytesIO
from typing import List, Dict

import docx2txt
import PyPDF2
import spacy
from fastapi import FastAPI, File, UploadFile

app = FastAPI()

nlp = spacy.load("en_core_web_sm")

@app.post("/score")
async def score_resume(job_description: UploadFile = File(...), resumes: List[UploadFile] = File(...)):
    jd_text = docx2txt.process(BytesIO(await job_description.read()))
    jd_doc = nlp(jd_text)

    scores = []

    for resume in resumes:
        # Extract text from docx or pdf file
        if resume.content_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
            resume_text = docx2txt.process(BytesIO(await resume.read()))
        elif resume.content_type == 'application/pdf':
            pdf_reader = PyPDF2.PdfFileReader(BytesIO(await resume.read()))
            resume_text = ''
            for page in range(pdf_reader.getNumPages()):
                resume_text += pdf_reader.getPage(page).extractText()
        else:
            return {"error": f"{resume.filename} has an unsupported file type."}

        resume_doc = nlp(resume_text)

        # Calculate similarity score between JD and resume
        score = jd_doc.similarity(resume_doc)
        score = score*100

       

        scores.append({"resume": resume.filename, "score": score})

    sorted_scores = sorted(scores, key=lambda x: x["score"], reverse=True)

    return {"scores": sorted_scores}
