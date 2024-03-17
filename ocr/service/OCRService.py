from abc import ABC, abstractmethod
from textractor import Textractor
from textractor.data.constants import TextractFeatures
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
        try:
            queries = [ 'What is the person first name?',
                    'What is the person last name?',
                    'What is the emailId?',
                    'What is the address?',
                    'What is the phone number?'
                    ]
            response = textract_client.analyze_document(fil_source=data,
                                features=[TextractFeatures.QUERIES],
                                queries= queries)

    
            query_answers = response.queries
            business_card_details = {}
            if query_answers[0].result:
                business_card_details['firstName'] = query_answers[0].result.answer
            else:
                business_card_details['firstName'] = ''
           
            if query_answers[1].result:
                business_card_details['lastName'] = query_answers[1].result.answer
            else:
                business_card_details['lastName'] = ''

            if query_answers[2].result:
                business_card_details['emailId'] = query_answers[2].result.answer
            else:
                business_card_details['emailId'] = ''
            
            if query_answers[3].result:
                business_card_details['address'] = query_answers[3].result.answer
            else:
                business_card_details['address'] = ''
            if query_answers[4].result:
                business_card_details['phone'] = query_answers[4].result.answer
            else:
                business_card_details['phone'] = ''

            return  BusinessCard(business_card_details['firstName'],business_card_details['lastName'],
                                business_card_details['emailId'],business_card_details['address'],
                                business_card_details['phone'])
        except  Exception as e:
             traceback.print_exc()
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