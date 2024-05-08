import boto3

comprehend = boto3.client('comprehend',region_name='us-east-2')
class AIAnalysis:
    def detect_expense_categories(self,text):
    
        # Call the DetectEntities API to extract entities (like expenses) from the text
        print('text')
        print(text)
        response_entities = comprehend.detect_entities(Text=text, LanguageCode='en')
        entities = response_entities['Entities']
        print(entities)
        # Extract the expense categories from the entities
        expense_categories = []
        for entity in entities:
            if entity['Type'] == 'EXPENSE':
                return entity['Text']

        return None
