from fastapi import FastAPI, Request
from pydantic import BaseModel
import argostranslate.package
import argostranslate.translate
from fastapi.responses import FileResponse
app = FastAPI()

class TranslateRequest(BaseModel):
    text: str
    from_code: str
    to_code: str 

def translate_text(text, from_code="en", to_code="hi"):
    argostranslate.package.update_package_index()
    available_packages = argostranslate.package.get_available_packages()
    package_to_install = next(
        filter(
            lambda x: x.from_code == from_code and x.to_code == to_code,
            available_packages,
        )
    )
    argostranslate.package.install_from_path(package_to_install.download())
    translated_text = argostranslate.translate.translate(text, from_code, to_code)
    return translated_text

@app.post("/hindi")
def translate(req: TranslateRequest,to_code = "hi", from_code: str = "en"):
    result = translate_text(req.text, req.from_code, req.to_code)
    return {"translated_text": result}

@app.post("/english")
def translate(req: TranslateRequest,to_code = "en", from_code: str = "hi"):
    result = translate_text(req.text, req.from_code, req.to_code)
    return {"translated_text": result}

@app.get("/map")
async def serve_map():
    return FileResponse("/Users/kritlunkad/Downloads/translate/map.html")
