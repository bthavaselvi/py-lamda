from flask import Flask, request, jsonify
import awsgi
from common.OCRServiceFactory import OCRServiceFactory

from io import BytesIO
import traceback

import json
import os
import base64
from common.DocumentType import DocumentType

print('i ma here')
app = Flask(__name__)

# @app.route('/analyze', methods=['POST'])
# def analyze_document():
#     try:
#         # Get the file from the request
#         file = request.files['file']
#         document_type = request.form.get('documentType')
#         file_content = file.read()
#         return jsonify(OCRServiceFactory.create_OCR_service(document_type).analyze_document(file_content)),200
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500
print('2')
@app.route('/sayHello', methods=['GET'])
def sayHello():
    print('3')
    try:
      
        return jsonify({'say': 'hi'}), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
    
def lambda_handler(event, context):
    print('4')
    return awsgi.response(app, event, context)

if __name__ == '__main__':
    lambda_function.run(debug=True)