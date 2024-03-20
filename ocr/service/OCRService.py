from abc import ABC, abstractmethod


from textractor.parsers import response_parser

from response.BusinessCard import BusinessCard
import traceback
import logging
import boto3
from response.ExpenseDocument import Address,ReceiverBillTo,ReceverShipTo,Vendor,LineItem,ExpenseDocument

log = logging.getLogger("my-logger")

region_name = 'us-east-2'
textract_client =boto3.client('textract', region_name=region_name)


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

    def toExpenseDocument(self,expenseDocument):
       field_group =  expenseDocument.summary_groups
       receiver_bill_to = field_group['RECEIVER_BILL_TO']
       receiver_bill_address = Address(receiver_bill_to['NAME'],receiver_bill_to['STREET'],
                                       receiver_bill_to['CITY'],receiver_bill_to['STATE'],
                                       receiver_bill_to['ZIP_CODE'] )
       
       receiver_ship_to = field_group['RECEIVER_SHIP_TO']
       receiver_ship_address = Address(receiver_ship_to['NAME'],receiver_ship_to['STREET'],
                                       receiver_ship_to['CITY'],receiver_ship_to['STATE'],
                                       receiver_ship_to['ZIP_CODE'] )
       
       vendor = field_group['VENDOR']
       vendor_address =  Address(vendor['NAME'],vendor['STREET'],
                                       vendor['CITY'],vendor['STATE'],
                                       vendor['ZIP_CODE'] )
       
       line_items  = []
       for line_item in expenseDocument.line_items_groups:
          line = LineItem(line_item['EXPENSE_ROW'],line_item['ITEM'],
                    line_item['QUANTITY'],line_item['UNIT_PRICE'],line_item['PRICE'],
                    line_item['PRODUCT_CODE'])
          line_item.append(line)

       summary_fields  = expenseDocument.summary_fields

       return ExpenseDocument(summary_fields['INVOICE_RECEIPT_DATE'],summary_fields['INVOICE_RECEIPT_ID'],
                       summary_fields['PO_NUMBER'],summary_fields['PAYMENT_TERMS'],
                       summary_fields['SUBTOTAL'],summary_fields['TAX'],summary_fields['TOTAL'],
                       line_items,receiverBillTo = ReceiverBillTo(receiver_bill_address),
                       receiverShipTo=ReceverShipTo(receiver_ship_address),vendor=Vendor(vendor_address))
       
           

    def analyze_document(self, data: bytes):
         try:
            response =  textract_client.analyze_expense(Document={'Bytes': data})   
            expense_document = response_parser.parser_analyze_expense_response(response).expense_documents[0]       
            expense_doc_to_return =  toExpenseDocument(expense_document)
            return expense_doc_to_return
         except Exception as e:
             traceback.print_exc()
             raise
         

        
