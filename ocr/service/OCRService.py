from abc import ABC, abstractmethod


from textractor.parsers import response_parser

from response.BusinessCard import BusinessCard
import traceback
import logging
import boto3

log = logging.getLogger("my-logger")

region_name = 'us-east-2'
textract_client =boto3.client('textract', region_name=region_name)

response_parser = ResponseParser()

class OCR:
    @abstractmethod
    def analyze_document(self,data: bytes):
        pass

class BusinessCardService(OCR):

    def analyze_document(self, data: bytes):
        try:
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

            d = response_parser.parse(response)
           
            queries_answers = d.queries

            business_card_details = {}
            for query in queries_answers:
                business_card_details[query.alias] = query.result.answer

            return  BusinessCard(business_card_details['firstName'],business_card_details['lastName'],
                                business_card_details['emailId'],business_card_details['address'],
                                business_card_details['phone'])

        except  Exception as e:
             traceback.print_exc()
             logging.error(e)
             raise

class InvoiceService(OCR):
    def analyze_document(self, data: bytes):
         try:
            #  response =  textract_client.analyze_expense(Document={'Bytes': data})
            #  expense = t2.TAnalyzeExpenseDocumentSchema().load(response)
            #  print(expense)
            #  return expense
            print('hi')
         except Exception as e:
             traceback.print_exc()
             raise