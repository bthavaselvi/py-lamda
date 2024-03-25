from abc import ABC, abstractmethod


from textractor.parsers import response_parser

from response.BusinessCard import BusinessCard
import traceback
import logging
import boto3
from response.ExpenseDocument import ReceiverBillTo,ReceverShipTo,Vendor,LineItem,ExpenseDocument,SummaryFields
from response.Address import Address
from response.IDResponse import IDDocument


log = logging.getLogger('my-logger')

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

    def toExpense(self,expense_filed) -> LineItem:
        quantity = None
        expense_row = None
        item = None
        unit_price = None
        price = None
        product_code = None


        for expense in expense_filed:
            if expense.type.text == 'EXPENSE_ROW':
                expense_row = expense.value
            elif expense.type == 'ITEM':
                item = expense.value
            elif expense.type == 'QUANTITY':
                quantity = expense.value
            elif expense.type == 'UNIT_PRICE':
                unit_price = expense.value
            elif expense.type == 'PRICE':
                price = expense.value
            elif expense.type == 'PRODUCT_CODE':
                product_code = expense.value
        
        return LineItem(expense_row=expense_row,item=item,quantity=quantity,
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
             if summary.type == 'INVOICE_RECEIPT_DATE':
                 invoiceReceiptDt = summary.value
             elif summary.type == 'INVOICE_RECEIPT_ID':
                 invoiceReceiptId = summary.value
             elif summary.type == 'PO_NUMBER':
                  poNumber = summary.value
             elif summary.type == 'PAYMENT_TERMS':
                  paymentTerms = summary.value
             elif summary.type ==  'SUBTOTAL':
                  subTotal = summary.value
             elif summary.type == 'TOTAL':
                  total = summary.value
             elif summary.type == 'TAX':
                 tax = summary.value
            
        return SummaryFields(invoiceReceiptDate=invoiceReceiptDt,invoiceReceiptId=invoiceReceiptId,
                             poNumber=poNumber,paymentTerm=paymentTerms,subTotal=subTotal,total=total,tax=tax)


    def toExpenseDocument(self,expenseDocument):
       field_group =  expenseDocument.summary_groups
       print(field_group)
       receiver_bill_to = field_group['RECEIVER_BILL_TO']
       print(receiver_bill_to)
       if receiver_bill_to is not None:
            receiver_bill_address = Address(receiver_bill_to.get('NAME'),receiver_bill_to.get('STREET'),
                                            receiver_bill_to.get('CITY'),receiver_bill_to.get('STATE'),
                                            receiver_bill_to.get('ZIP_CODE' ))
       
       receiver_ship_to = field_group.get('RECEIVER_SHIP_TO')
       print(receiver_ship_to)
       if receiver_ship_to is not None:
            receiver_ship_address = Address(receiver_ship_to.get('NAME'),receiver_ship_to.get('STREET'),
                                            receiver_ship_to.get('CITY'),receiver_ship_to.get('STATE'),
                                            receiver_ship_to.get('ZIP_CODE' ))
            
       vendor = field_group.get('VENDOR')
       if vendor is not None:
            vendor_address =  Address(vendor.get('NAME'),vendor.get('STREET'),
                                            vendor.get('CITY'),vendor.get('STATE'),
                                            vendor.get('ZIP_CODE'))
       
       line_items  = []
       print(expenseDocument.line_items_groups)
       print(type( expenseDocument.line_items_groups))
       for line_item in expenseDocument.line_items_groups:
           line_items.append(self.toExpense(line_item.expenses))

       summary_fields  = self.toSummaryFields(self,expenseDocument.summary_fields)

       print(summary_fields)
       print(type(summary_fields))

       return ExpenseDocument(summaryFields=summary_fields,
                       lineItems=line_items,receiverBillTo = ReceiverBillTo(receiver_bill_address),
                       receiverShipTo=ReceverShipTo(receiver_ship_address),vendor=Vendor(vendor_address))
       
           

    def analyze_document(self, data: bytes):
        
            response =  textract_client.analyze_expense(Document={'Bytes': data})   
            expense_document = response_parser.parser_analyze_expense_response(response).expense_documents[0]   
            print(type(expense_document))
            print(expense_document)    
            expense_doc_to_return =  self.toExpenseDocument(expense_document)
            return expense_doc_to_return
            
      
class IDService(OCR):
    
    def analyze_document(self, data: bytes):
       try:
           
            document = textract_client.analyze_id(DocumentPages=[{'Bytes': data}]) 
            print(document)
            
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

         

        
