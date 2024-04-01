from dataclasses import dataclass
from decimal import Decimal
@dataclass
class LineItem:
    expenseRowNumber:int
    item: str
    quantity: Decimal
    unitPrice: Decimal
    price: Decimal
    productCode: str = ''
   