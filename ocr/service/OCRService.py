from abc import ABC, abstractmethod
from textractor import Textractor
from response.BusinessCard import BusinessCard
import traceback
region_name = 'us-east-2'
textract_client = Textractor(profile_name=region_name)

class OCR:
    @abstractmethod
    def analyze_document(self,data: bytes):
        pass

class BusinessCardService(OCR):

    def analyze_document(self, data: bytes):
        response = textract_client.analyze_document(fil_source=data,
                            FeatureTypes=["QUERIES"],
                            QueriesConfig={"Queries":[
                                        {
                                            'query': 'What is the person first name?',
                                            'alias': 'firstName'
                                        },
                                        {
                                            'query': 'What is the person last name?',
                                            'alias': 'lastName'
                                        },
                                        {
                                            'query': 'What is the emailId?',
                                            'alias': 'emailId'
                                        },
                                        {
                                            
                                            'query': 'What is the address?',
                                            'alias': 'address'

                                        },
                                        {
                                            'query': 'What is the phone number?',
                                            'alias': 'phone'
                                        },
                                    ]
                            })

  
        query_answers = response.queries
        business_card_details = {}
        for query in query_answers:
            
            if query.result:
                business_card_details[query.alias] = query.result.answer

        return  BusinessCard(business_card_details['firstName'],business_card_details['lastName'],
                             business_card_details['emailId'],business_card_details['address'],
                             business_card_details['phone'])

class InvoiceService(OCR):
    def analyze_document(self, data: bytes):
         try:
             response =  textract_client.analyze_expense(Document={'Bytes': data})
             expense = t2.TAnalyzeExpenseDocumentSchema().load(response)
             print(expense)
             return expense
            
         except Exception as e:
             traceback.print_exc()
             raise