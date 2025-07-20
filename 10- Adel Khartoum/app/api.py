from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from utils.summarizer import summarize_long_text

app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


@app.get("/", response_class=HTMLResponse)
async def get_form(request: Request):

    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/stream", response_class=StreamingResponse)
async def stream_summary(user_text: str = Form(...)):
    """
    """
    def generate():
        try:
            summary = summarize_long_text(user_text)
            yield summary
        except Exception as e:
            yield f"حدث خطأ أثناء التلخيص: {str(e)}"
        yield "[DONE]"

    return StreamingResponse(generate(), media_type="text/plain")
