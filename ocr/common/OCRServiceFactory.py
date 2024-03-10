from common.DocumentType import DocumentType
from service.OCRService import BusinessCardService,InvoiceService

class OCRServiceFactory:
    @staticmethod 
    def create_OCR_service(document_type):
        if document_type == DocumentType.BUSINESS_CARD.name :
            return  BusinessCardService.BusinessCardService()
        elif document_type == DocumentType.INVOICE :
            return InvoiceService()
        else:
            raise Exception('Invalid document type')