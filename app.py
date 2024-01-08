from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import awsgi
import boto3
from io import BytesIO
import trp.trp2 as t2
from BusinessCard import BusinessCard
import json
import os

app = Flask(__name__)



# Replace these with your AWS credentials and region
aws_access_key_id = 'AKIAVCBFWUZMA5C2ESL3'
aws_secret_access_key = 'thTIXSwKOEM/L/m10v2utwRLKy77N2aO0WjGyKka'
region_name = 'us-east-2'

# Initialize the Textract client
textract_client = boto3.client('textract', aws_access_key_id=aws_access_key_id,
                               aws_secret_access_key=aws_secret_access_key, region_name=region_name)

def analyze_business_card(file_content):
    # Call Textract API to analyze the business card
    response = textract_client.analyze_document(Document={'Bytes': file_content},
     FeatureTypes=["QUERIES"],
    QueriesConfig={"Queries":[
                {
                    'Text': 'What is the name?',
                    'Alias': 'name'
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
        print(f"{x[1]},{x[2]}")
        business_card_details[x[1]] = x[2]

    responseToReturn =   BusinessCard(business_card_details['name'],business_card_details['emailId'],business_card_details['address'],
    business_card_details['phone'])
  

    return json.dumps(responseToReturn.__dict__)

@app.route('/analyze', methods=['POST'])
def analyze_business_card_route():
    try:
        # Get the file from the request
        file = request.files['file']
        # Get the binary blob from the request
        # binary_blob = request.form['binary_blob']
        # Read the content of the file
        if file is not None:
            file_content = file.read()
        else:
            file_content =  base64.b64decode(binary_blob)
        if file_content is not None: 
            # Analyze the business card using Textract
            result = analyze_business_card(file_content)
        else:
            result = '{}'
        return result, 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def handler(event, context):
    return awsgi.response(app, event, context)


if __name__ == '__main__':
    app.run(debug=True)

