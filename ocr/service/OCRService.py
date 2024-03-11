from abc import ABC, abstractmethod
import boto3
import trp.trp2 as t2
from response.BusinessCard import BusinessCard

region_name = 'us-east-2'
textract_client = boto3.client('textract', region_name=region_name)

class OCR:
    @abstractmethod
    def analyze_document(self,data: bytes):
        pass

class BusinessCardService(OCR):

    def analyze_document(self, data: bytes):
        response = textract_client.analyze_document(Document={'Bytes': data},
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

        return  BusinessCard(business_card_details['firstName'],business_card_details['lastName'],
                             business_card_details['emailId'],business_card_details['address'],
                             business_card_details['phone'])

class InvoiceService(OCR):
    def analyze_document(self, data: bytes):
         return textract_client.analyze_expense(Document={'Bytes': data})