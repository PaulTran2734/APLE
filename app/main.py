import os
import requests
import json
import codecs
import re
from flask import Flask, render_template, request, redirect, session, url_for

aple_url = 'http://paultran2734.pythonanywhere.com/'
viettelai_url = "https://viettelgroup.ai/nlp/api/v1/spell-checking"
blank_load = json.dumps({'input_text': ""},ensure_ascii=False)
blank = requests.post(url=aple_url,json=blank_load)

del blank
del blank_load

app = Flask(__name__,static_folder="static")

def format_result(results,lang="vi"):
    eng = ["Argumentative","Expository","Anecdote","Narrative","Descriptive"]
    results = results.json()
    out_html = ""
    index = 0
    for key, value in results.items():
        if lang == "en":
            key = eng[index]
            index += 1
        value_class = int(round(value,1) * 100)
        out_html += f'''
        <div class="skillbar">
            <div class="annotate">
            <div class="label">{key}</div>
            <div class="value">{value:.2%}</div>
            </div>
            <div class="skillBarContainer">
            <div class="skillBarValue value-{value_class}"></div>
            </div>
        </div>
        '''
    return out_html
        

@app.route('/en',methods=["GET"])
def en_main_page():
    try:
        state = json.loads(request.args['state'])
        default_text = state['result']
    except: 
        default_text = None   
    template_path = f"./en/index.html"
    is_new = False
    if default_text is None:
        is_new = True
        default_text = '''
        Please type your essay in the textarea in the left. <br>
        Make sure you type more than 10 words.
        '''
    default = (True if is_new else False)

    return render_template(template_path,result=default_text,text=None,default=default,placeholder="Type your essay here")

@app.route('/vi', methods=["GET"])
def vi_main_page():
    try:
        state = json.loads(request.args['state'])
        default_text = state['result']
    except: 
        default_text = None   
    template_path = f"./vi/index.html"
    is_new = False
    if default_text is None:
        is_new = True
        default_text = '''
        H??y nh???p b??i v??n c???a b???n ??? trong v??ng b??n tr??i <br>
        C??c b???n nh??? vi???t nhi???u h??n 10 t??? nh??!
        '''
    default = (True if is_new else False)

    return render_template(template_path,result=default_text,text=None,default=default,placeholder="Type your essay here")  


@app.route('/')
def main():
    default_path = "./vi"
    return redirect(default_path)

@app.route('/en', methods=["POST"])
def process_result():
    
    template_path = "./en/result.html"
    input_essay = request.form["input_essay"]
    try:
        force = request.form['force']
    except:
        force = False
    else:
        force = True
    try:
        alt_input = request.form["submit_suggest"]
    except:
        alt_input = None
    else: 
        alt_input = request.form["submit_suggest"]

    if alt_input != None:
        input_essay = re.sub('<[^<]+?>', '',alt_input)
        force = True
    
    if len(input_essay.strip()) < 10:
        state = json.dumps({"result":'<span class="warning">Please type your essay before submitting! <br> (or write more than 10 characters)</span>'})
        return redirect(url_for(".en_main_page",state=state))
    display_essay = input_essay
    payload = json.dumps({'input_text':input_essay},ensure_ascii=False)
    spell_load = {'sentence':input_essay}
    spellcheck = requests.post(url=viettelai_url,json=spell_load).json()
    suggestions = spellcheck['result']['suggestions']
    if len(suggestions) == 0 or force:
        result = requests.post(url=aple_url,json=payload)
        display_essay = format_result(results=result,lang="en")
    else:
        template_path = f"./en/spellcor.html"
        alt_essay = display_essay
        cache = []
        for i in suggestions:
            original = i['originalText']
            suggestion = i['suggestion']
            if original in cache:
                continue                
            else:
                cache.append(original)
                alt_essay = alt_essay.replace(original,suggestion)
                display_essay = display_essay.replace(original,
                                                      f'<span class="tooltip">{suggestion}<span class="tooltiptext">{original}</span></span>')
            alert = "We have detected some spelling errors in your essay.<br> Either you submit our suggested corrections, or manually fix your spelling and submit again."
        return render_template(template_path,result=display_essay,default=False,alert=alert,placeholder=input_essay,alt_essay=alt_essay)
            

    
    return render_template(template_path,result=display_essay,default=False,placeholder=input_essay)


@app.route('/vi', methods=["POST"])
def process_result_vi():
    
    template_path = "./vi/result.html"
    input_essay = request.form["input_essay"]
    try:
        force = request.form['force']
    except:
        force = False
    else:
        force = True
    try:
        alt_input = request.form["submit_suggest"]
    except:
        alt_input = None
    else: 
        alt_input = request.form["submit_suggest"]

    if alt_input != None:
        input_essay = re.sub('<[^<]+?>', '',alt_input)
        force = True
    
    if len(input_essay.strip()) < 10:
        state = json.dumps({"result":'<span class="warning">Vui l??ng nh???p b??i vi???t tr?????c khi g???i! <br> (ho???c vi???t nhi???u h??n 10 k?? t???)</span>'})
        return redirect(url_for(".vi_main_page",state=state))
    display_essay = input_essay
    payload = json.dumps({'input_text':input_essay},ensure_ascii=False)
    spell_load = {'sentence':input_essay}
    spellcheck = requests.post(url=viettelai_url,json=spell_load).json()
    suggestions = spellcheck['result']['suggestions']
    if len(suggestions) == 0 or force:
        result = requests.post(url=aple_url,json=payload)
        display_essay = format_result(results=result,lang="vi")
    else:
        template_path = f"./vi/spellcor.html"
        alt_essay = display_essay
        cache = []
        for i in suggestions:
            original = i['originalText']
            suggestion = i['suggestion']
            if original in cache:
                continue                
            else:
                cache.append(original)
                alt_essay = alt_essay.replace(original,suggestion)
                display_essay = display_essay.replace(original,
                                                      f'<span class="tooltip">{suggestion}<span class="tooltiptext">{original}</span></span>')
            alert = "Ch??ng t??i ???? ph??t hi???n l???i trong b??i vi???t c???a b???n.<br> B???n c?? th??? g???i b??i theo g???i ?? c???a ch??ng t??i, ho???c s???a l???i ??? v??ng nh???p b???n v?? n???p l???i b??i c???a b???n."
        return render_template(template_path,result=display_essay,default=False,alert=alert,placeholder=input_essay,alt_essay=alt_essay)
            

    
    return render_template(template_path,result=display_essay,default=False,placeholder=input_essay)