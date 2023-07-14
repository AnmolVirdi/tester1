import asyncio
from flask import Flask, render_template, request
import requests
app = Flask(__name__)

async def process_text(input_text):
    url = 'http://141.148.197.26:5000/process'
    data = {'text': input_text} 
    response = await asyncio.get_event_loop().run_in_executor(None, requests.post, url, data)
    if response.status_code == 200:
        output_text = response.text
        return output_text
    else:
        return 'Request failed with status code' + str(response.status_code)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        input_text = request.form['input_text']
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        output_text = loop.run_until_complete(process_text(input_text))
        loop.close()
        output_text = "URL: " + input_text + "\n" + output_text
        return render_template('index.html', input_text=input_text, output_text=output_text)
    return render_template('index.html')

@app.template_filter('nl2br')
def nl2br_filter(value):
    """Convert newlines to HTML br tags."""
    return value.replace('\n', '<br>\n')

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)
