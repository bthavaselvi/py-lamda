from flask import Flask, request, jsonify
import awsgi
from common.OCRServiceFactory import OCRServiceFactory

from io import BytesIO

import json
import os
import base64

app = Flask(__name__)
   
def lambda_handler(event, context):
    return awsgi.response(app, event, context)

if __name__ == '__main__':
    lambda_function.run(debug=True)


@app.route('/analyze', methods=['POST'])
def analyze_document():
    try:
        # Get the file from the request
        file = request.files['file']
        document_type = request.form.get('documentType')
        file_content = file.read()
        return jsonify(OCRServiceFactory.create_OCR_service(document_type=document_type).analyze_document(file_content)),200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/sayHello', methods=['GET'])
def sayHello():
    try:
      
        return jsonify({'say': 'hi'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    