
import openai
class AIService:
    api_key='sk-ocr-service-0IGxmDs1Ot1mtuVTszOAT3BlbkFJindjCeNJOzLtQOc16fDE'
   
   # lets initialize the API client 1st
    client = openai.OpenAI(
        # This is the default and can be omitted
        api_key=api_key
    )
    def catagorize_expense(self,description):

         expense_categories = {
            "Operational Expenses": ["rent", "utilities", "office supplies"],
            "Employee Expenses": ["payroll", "benefits", "travel"],
            "food": ["restaurant", "grocery", "takeout", "coffee"],
            "transportation": ["taxi", "uber", "gas", "public transportation"],
            "utilities": ["electricity", "water", "internet", "phone"],
            "Administrative Expenses" : ["Office rent","Office lease","Insurance premiums"],
            "Technology Expenses": ["Software subscriptions","Hardware purchases","IT services and support"],
            "Financial Expenses": ["Interest payments","Bank fees","Loan repayments"],
            "Taxes": ["Income taxes","Sales taxes","Property taxes"]
        # Define keywords for other categories similarly
        }
         response = self.client.chat.completions.create(
                        model="gpt-3.5-turbo",  
                        messages=[
                            {
                                "role": "user",
                                "content":  f"I need to categorize the expense: '{description}'. The categories are: {list(expense_categories.keys())}. Please assign it to the appropriate category.",
                            }
                        ],
                        max_tokens=60
                )
        #  Completion.create(
        #     engine="text-davinci-003",
        #     prompt=f"I need to categorize the expense: '{description}'. The categories are: {list(expense_categories.keys())}. Please assign it to the appropriate category.",
        #     max_tokens=50
        #     )
        
      
         for category, keywords in expense_categories.items():
                    
                    for keyword in keywords:
                        print(f"keyword:{keyword},{response.choices[0].message.content}")
                        if keyword.lower() == response.choices[0].message.content.strip().lower():
                            return category
         return "Miscellaneous"  # If no matching category found

        