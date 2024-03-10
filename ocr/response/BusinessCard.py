import json
class BusinessCard:  
    def __init__(self,firstName,lastName,emailId,address,phone):
        self.firstName = firstName
        self.lastName = lastName
        self.emailId = emailId
        self.address = address
        self.phone = phone

    def toJson(self):
       return json.dumps(self, default=lambda o: o.__dict__)

    # class Address:
    #     def __init__(self,street,city,state,zipcode)
    #         self.street = street
    #         self.city = city
    #         self.state = state
    #         self.zipcode = zipcode
