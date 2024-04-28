from abc import ABC, abstractmethod


from textractor.parsers import response_parser

from response.BusinessCard import BusinessCard
import traceback
import logging
import boto3
from response.ExpenseDocument import ReceiverBillTo,ReceverShipTo,Vendor,LineItem,ExpenseDocument,SummaryFields
from response.Address import Address
from response.IDResponse import IDDocument
from textractor.entities.expense_field import ExpenseField
import time
from collections import ChainMap

log = logging.getLogger('my-logger')
bucket_name  = 'eazeitocrdocuments'
region_name = 'us-east-2'
textract_client =boto3.client('textract', region_name=region_name)

class OCR:
    @abstractmethod
    def analyze_document(self,data: bytes,raw:bool,file_name: str):
        pass

class BusinessCardService(OCR):

    def analyze_document(self, data: bytes,raw:bool,file_name:str):
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

    def toExpense(self,expense_filed) -> LineItem:
        quantity = None
        expense_row = None
        item = None
        unit_price = None
        price = None
        product_code = None
        for expense in expense_filed:
          
            if expense.type.text == 'EXPENSE_ROW':
                expense_row = expense.value.text
            elif expense.type.text == 'ITEM':
                item = expense.value.text
            elif expense.type.text == 'QUANTITY':
                quantity = expense.value.text
            elif expense.type.text == 'UNIT_PRICE':
                unit_price = expense.value.text
            elif expense.type.text == 'PRICE':
                price = expense.value.text
            elif expense.type.text == 'PRODUCT_CODE':
                product_code = expense.value.text
        
        return LineItem(expenseRowNumber=expense_row,item=item,quantity=quantity,
                        unitPrice= unit_price,price=price,productCode=product_code)

    def toSummaryFields(self,summary_fields) -> SummaryFields:
       
        invoiceReceiptDt = None
        invoiceReceiptId = None
        poNumber = None
        paymentTerms = None
        subTotal = None
        tax = None
        total = None

        for summary in summary_fields:
            
             if isinstance(summary,ExpenseField):
                if summary.type.text == 'INVOICE_RECEIPT_DATE':
                    invoiceReceiptDt = summary.value.text
                elif summary.type.text == 'INVOICE_RECEIPT_ID':
                    invoiceReceiptId = summary.value.text
                elif summary.type.text == 'PO_NUMBER':
                    poNumber = summary.value.text
                elif summary.type.text == 'PAYMENT_TERMS':
                    paymentTerms = summary.value.text
                elif summary.type.text ==  'SUBTOTAL':
                    subTotal = summary.value.text
                elif summary.type.text == 'TOTAL':
                    total = summary.value.text
                elif summary.type.text == 'TAX':
                    tax = summary.value.text
            
        return SummaryFields(invoiceReceiptDate=invoiceReceiptDt,invoiceReceiptId=invoiceReceiptId,
                             poNumber=poNumber,paymentTerm=paymentTerms,subTotal=subTotal,total=total,tax=tax)


    def extract_address(self,blocks) -> Address:
        street = ''
        city = ''
        state = ''
        zip_code = ''
        name = ''
        address_block = ''
        for block in blocks:
            for expense_field in block:
                if isinstance(expense_field,ExpenseField):
                    print(expense_field.type.text)
                    if expense_field.type.text == 'STREET':
                        street = expense_field.value.text
                    if expense_field.type.text == 'CITY':
                        city = expense_field.value.text
                    if expense_field.type.text == 'STATE':
                        state = expense_field.value.text
                    if expense_field.type.text == 'ZIP_CODE':
                        zip_code = expense_field.value.text
                    if expense_field.type.text == 'ADDRESS_BLOCK':
                        city = expense_field.value.text
                    if expense_field.type.text == 'NAME':
                        name = expense_field.value.text

        return Address(name=name,street=street,city=city,state=state,zip_code=zip_code,address=address_block)

    def toExpenseDocument(self,expenseDocument):
       field_group =  expenseDocument.summary_groups
       receiver_bill_address = None
       receiver_ship_address = None
       vendor_address = None

       receiver_bill_to = field_group.get('RECEIVER_BILL_TO')
  
       if receiver_bill_to is not None:
     
            receiver_bill_address = self.extract_address(receiver_bill_to.values())
      
       
       receiver_ship_to = field_group.get('RECEIVER_SHIP_TO')
  
       if receiver_ship_to is not None:

            receiver_ship_address =  self.extract_address(receiver_ship_to.values())
      
            
       vendor = field_group.get('VENDOR')
      
       if vendor is not None:
            vendor_address =  self.extract_address(vendor.values())
       
       line_items  = []
      
       for line_item_group in expenseDocument.line_items_groups:
           for row in line_item_group.rows:
                line_items.append(self.toExpense(row.expenses))

       summary_fields  = self.toSummaryFields(expenseDocument.summary_fields_list)

       return ExpenseDocument(summaryFields=summary_fields,
                       lineItems=line_items,receiverBillTo = ReceiverBillTo(receiver_bill_address),
                       receiverShipTo=ReceverShipTo(receiver_ship_address),vendor=Vendor(vendor_address))
       
           

    def analyze_document(self, data: bytes,raw:bool,file_name:str):
        
            response =  textract_client.analyze_expense(Document={'Bytes': data})   
          
            expense_document = response_parser.parser_analyze_expense_response(response).expense_documents[0]   
            if raw:
             return expense_document
            expense_doc_to_return =  self.toExpenseDocument(expense_document)
            return expense_doc_to_return
            
      
class IDService(OCR):
    
    def analyze_document(self, data: bytes,raw:bool,file_name:str):
       try:
           
            document = textract_client.analyze_id(DocumentPages=[{'Bytes': data}]) 
            id_details = response_parser.parse_analyze_id_response(document).identity_documents[0]
            
            return IDDocument(id_details.get('FIRST_NAME'),id_details['LAST_NAME'],id_details['MIDDLE_NAME'],
                        id_details['SUFFIX'],id_details['DOCUMENT_NUMBER'],id_details['EXPIRATION_DATE'],
                        id_details['DATE_OF_BIRTH'],id_details['STATE_NAME'],id_details['COUNTY'],id_details['DATE_OF_ISSUE'],
                        id_details['CLASS'],id_details['RESTRICTIONS'],id_details['ENDORSEMENTS'],
                        id_details['ID_TYPE'],id_details['VETERAN'],id_details['PLACE_OF_BIRTH'],
                        Address(id_details['FIRST_NAME'],id_details['ADDRESS'],id_details['CITY_IN_ADDRESS'],
                                id_details['STATE_IN_ADDRESS'],id_details['ZIP_CODE_IN_ADDRESS']))
       except Exception as e:
            traceback.print_exc()
            logging.error(e)
            raise

class GeneralDocumentService(OCR):
    def analyze_document(self, data: bytes,raw:bool,file_name:str):
        try:
            
             response = textract_client.start_document_analysis( DocumentLocation={
                                'S3Object': {
                                    'Bucket': bucket_name,
                                    'Name': file_name
                                }
                            },
                            FeatureTypes=['TABLES']) 
             job_id = response['JobId']
             print("Started analysis with JobId:", job_id)
             response_document = {}
             blocks = {}
             while True:
                job_response = textract_client.get_document_analysis(JobId=job_id)
                job_status = job_response['JobStatus']
                
                if job_status == 'SUCCEEDED':
                    print("Analysis completed successfully!")
                    # Get the response JSON
                    response_document['DocumentMetadata'] =  job_response['DocumentMetadata']
                    if 'Blocks' in response:
                        for block in response['Blocks']:
                            blocks[block['Id']] = block

                    
                    nextToken = None
                    if('NextToken' in job_response):
                        nextToken = job_response['NextToken']

                    while(nextToken):
                        job_response = textract_client.get_document_analysis(JobId=job_id, NextToken=nextToken)
                        if 'Blocks' in response:
                            for block in response['Blocks']:
                                blocks[block['Id']] = block
                      
                        nextToken = None
                        if('NextToken' in job_response):
                            nextToken = job_response['NextToken']
                    response_document['Blocks'] = blocks
                    return response_parser.parse(response_document)
                elif job_status == 'FAILED':
                    print("Analysis failed!")
                    # Additional error handling code, if needed
                    break
                else:
                    print("Analysis still in progress. Current status:", job_status)
                    time.sleep(1)  # Wait for 10 seconds before checking the status again
             
        except Exception as e:
            traceback.print_exc()
            logging.error(e)
            raise

        
