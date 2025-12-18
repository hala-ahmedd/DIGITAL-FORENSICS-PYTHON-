#Needed Library 
import base64 

#The encoded string found in vip.txt
encoded_string = "am1gd2V4M20wXGs3b2U="

#Base64 decode
decoded_bytes = base64.b64decode(encoded_string)

#XOR decrypt with key = 3
password = ""
for byte in decoded_bytes:
    password += chr(byte ^ 3)

#Print the final password
print("Recovered steghide password:", password)
