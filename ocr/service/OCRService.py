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
            response = textract_client.analyze_document(Document={'Bytes',data},
                                features=[TextractFeatures.QUERIES],
                                queries= queries)

    
            query_answers = response.queries
            business_card_details = {}
            for query in query_answers:
                
                if query.result:
                    business_card_details[query.alias] = query.result.answer

            return  BusinessCard(business_card_details['firstName'],business_card_details['lastName'],
                                business_card_details['emailId'],business_card_details['address'],
                                business_card_details['phone'])
        except  Exception as e:
             traceback.print_exc()

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