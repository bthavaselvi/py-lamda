from flask import Flask, request, jsonify
import awsgi
from common.OCRServiceFactory import OCRServiceFactory
import json
import logging
import traceback
from common.utils import utils

app = Flask(__name__)
logger = logging.getLogger()
logger.setLevel('INFO')

@app.route('/analyze', methods=['POST'])
def analyze_document():
    try:
        data = None
        raw = request.form.get('raw')
        print( request.headers['Content-Type'])
        if 'application/json' in request.headers['Content-Type'] :
             
             json_data = request.json
             if json_data is not None:
                base64_encoded_file = json_data.get('fileContent')
                document_type = json_data.get('documentType')

                if json_data is not None and base64_encoded_file is not None:
                    service_to_call = OCRServiceFactory().create_OCR_service(document_type)
                    data = service_to_call.analyze_document(data=utils.decode_file(base64_encoded_file),raw=raw)
        elif  'multipart/form-data' in request.headers['Content-Type'] :
            # Get the file from the request
            file = request.files['file']
            file_name  = file.filename
            document_type = request.form.get('documentType')
           
            file_content = file.read()
            service_to_call = OCRServiceFactory().create_OCR_service(document_type)
            data = service_to_call.analyze_document(data=file_content,raw=raw,file_name=file_name)
        else:
             return jsonify({"error": "Unsupported Media Type"}), 415
        
        return json.dumps(data, default=lambda o: o.__dict__),200,{'content-type':'application/json'}
    except Exception as e:
        logging.error(e)
        return jsonify({'error': str(e)}), 500

@app.route('/sayHello', methods=['GET'])
def sayHello():
    try:
      
        return jsonify({'say': 'hi'}), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
    
def lambda_handler(event, context):
    try:
        return awsgi.response(app, event, context)
    except Exception as e:
        logger.exception(repr(e))


if __name__ == '__main__':
    lambda_function.run(debug=True)