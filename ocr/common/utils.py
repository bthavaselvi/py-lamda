import base64
def is_base64_encoded(data):
    try:
        # Attempt to decode the string
        decoded_bytes = base64.b64decode(data)

        # Encode it back to check if it's a valid base64 encoding
        # reencoded_bytes = base64.b64encode(decoded_bytes)
        
        # # Compare the original string with the re-encoded string
        # return reencoded_bytes == s.encode()
        return True
        
    except Exception as e:
        return False
    
def decode_file(self,data):
    try:
        return   base64.b64decode(data)
    except Exception as e:
         raise Exception('Content is not encoded')