from decimal import Decimal
from Address import Address
class ReceiverBillTo:
    def __init__(self,address: Address):
        self.address = address

class ReceverShipTo:
    def __init__(self,address:Address):
        self.address = address

class Vendor:
    def __init__(self,address:Address):
        self.address = address

class LineItem:
    def __init__(self,expenseRowNumber:int,item:str,quantity: Decimal,unitPrice:Decimal,price: Decimal,
                 productCode:str):
        self.expenseRowNumber = expenseRowNumber
        self.item = item
        self.quantity = quantity
        self.unitPrice = unitPrice
        self.price = price
        self.productCode = productCode

class ExpenseDocument:
    def __init__(self,invoiceReceiptDate:str,invoiceReceiptId:str,poNumber:str,
                 paymentTerm:str, subTotal:Decimal, tax: Decimal,
                 total:Decimal,lineItems : list[LineItem],receiverBillTo:ReceiverBillTo,
                 receiverShipTo:ReceverShipTo,vendor:Vendor):
        self.lineItems = lineItems
        self.invoiceReceiptDate = invoiceReceiptDate
        self.invoiceReceiptId = invoiceReceiptId
        self.poNumber = poNumber
        self.paymentTerm = paymentTerm
        self.subTotal = subTotal
        self.tax = tax
        self.total = total
        self.lineItems = lineItems
        
        