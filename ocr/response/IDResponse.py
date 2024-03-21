from response.Address import Address
class IDDocument:
   def __init__(self,firstName:str,lastName:str,middleName:str,
             suffix:str,documentNumber:str,expirationDate:str,
             dateOfBirth:str,stateName:str,county:str,dateOfIssue:str,classOfDocument:str,
             restrictions:str,endorsements:str,idType:str,veteran:str,placeOfBirth:str,address:Address):
      self.firstName = firstName
      self.lastName = lastName
      self.middleName =middleName
      self.suffix = suffix
      self.documentNumber =documentNumber
      self.expirationDate = expirationDate
      self.dateOfBirth = dateOfBirth
      self.stateName = stateName
      self.county = county
      self.dateOfIssue = dateOfIssue
      self.classOfDocument = classOfDocument
      self.restrictions = restrictions
      self.endorsements = endorsements
      self.idType = idType
      self.vetran = veteran
      self.placeOfBirth = placeOfBirth
      self.address = address