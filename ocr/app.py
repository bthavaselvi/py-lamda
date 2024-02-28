from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import awsgi
import boto3
from io import BytesIO
import trp.trp2 as t2
from BusinessCard import BusinessCard
import json
import os
import base64

app = Flask(__name__)



# Replace these with your AWS credentials and region
aws_access_key_id = 'AKIAVCBFWUZMP3YK2JJ4'
aws_secret_access_key = 'N44tPbUbPLHPIRB920t23abL9+vAaWBQNX54+ljR'
region_name = 'us-east-2'

# Initialize the Textract client

textract_client = boto3.client('textract', region_name=region_name)

def analyze_business_card(file_content):
    # Call Textract API to analyze the business card
    response = textract_client.analyze_document(Document={'Bytes': file_content},
     FeatureTypes=["QUERIES"],
    QueriesConfig={"Queries":[
                {
                    'Text': 'What is the person first name?',
                    'Alias': 'firstName'
                },
                {
                    'Text': 'What is the person last name?',
                    'Alias': 'lastName'
                },
                {
                    'Text': 'What is the emailId?',
                    'Alias': 'emailId'
                },
                {
                    
                    'Text': 'What is the address?',
                    'Alias': 'address'

                },
                {
                    'Text': 'What is the phone number?',
                    'Alias': 'phone'
                },
            ]
    })

    d = t2.TDocumentSchema().load(response)
    page = d.pages[0]
    query_answers = d.get_query_answers(page=page)

    business_card_details = {}
    for x in query_answers:
       business_card_details[x[1]] = x[2]

    print(business_card_details)

    responseToReturn =   BusinessCard(business_card_details['firstName'],business_card_details['lastName'],business_card_details['emailId'],business_card_details['address'],
    business_card_details['phone'])
  
    return json.dumps(responseToReturn.__dict__)

def analyze_invoice(file_content):
     return textract_client.analyze_expense(Document={'Bytes': file_content})
    

def is_base64_encoded(data):
    try:
        # Attempt to decode the string
        decoded_bytes = base64.b64decode(data)

        # Encode it back to check if it's a valid base64 encoding
        # reencoded_bytes = base64.b64encode(decoded_bytes)
        
        # # Compare the original string with the re-encoded string
        # return reencoded_bytes == s.encode()
        return True
        
    except Exception as e:
        return False


@app.route('/analyze', methods=['POST'])
def analyze_business_card_route():
    try:
        # Get the file from the request
        file = request.files['file']
        document_type = request.form.get('documentType')
        file_content = file.read()

        # if is_base64_encoded(file_content) is True:
        #     print('I am here')
        #     file_content = base64.b64decode(file_content)
        # Analyze the business card using Textract
        result = None
        if document_type.casefold() == 'Invoice'.casefold():
          
           result= analyze_invoice(file_content)
          
        else:
           result = analyze_business_card(file_content)
        return result, 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/', methods=['GET'])
def sayHello():
    try:
      
        return jsonify({'say': 'hi'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    
    
def handler(event, context):
    return awsgi.response(app, event, context)

if __name__ == '__main__':
    app.run(debug=True)

