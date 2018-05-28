import hashlib
import re

def hashString(string):
	md5 = hashlib.md5(string.encode())

	return md5.hexdigest()

def replaceDigit(string):
	return re.sub(r"(\d[ +]*){6,16}", "0000000000", string)

def shuffleEmailAddress(emailAddress):
	shiftedEmail = ""
	if emailAddress.find("@") > -1:
		localPart = emailAddress.split("@")
		
		shiftedEmail = hashString(localPart[0])	+ "@" + localPart[1]
	else:
		shiftedEmail = hashString(emailAddress)

	return shiftedEmail

def shuffleHeaderWithXHeader(input, header, xHeader, excludeHeader=None):
	result = [i for i in input if header.replace(" ", "").lower() in i.lower() and (True if excludeHeader is None else excludeHeader.replace(" ", "").lower() not in i.lower())]	
	if len(result) > 1:
		headerEmailAddressIndexInInput = input.index(result[0])
		splitHeader = result[0].split(header)
		if len(splitHeader) > 1:			
			headerValue = splitHeader[1].replace("\n", "").replace("\t", "")
			emailAddresses = headerValue.split(", ")				

			emailAddressesLength = len(emailAddresses)
			for i in range(emailAddressesLength):
				emailAddress = emailAddresses[i]

				if emailAddress.find("@") > -1:
					localPart = emailAddresses[i].split("@")
					
					shiftedEmail = hashString(localPart[0])	+ "@" + localPart[1]
				else:
					shiftedEmail = hashString(emailAddress)

				if i != emailAddressesLength - 1:					
					emailAddresses[i] = shiftedEmail + ", "
				else:
					emailAddresses[i] = shiftedEmail

			result[0] = header + "".join(emailAddresses) + "\n"

			xHeaderResultIndexInInput = input.index(result[1])
			xHeaderResult = result[1].split(xHeader)[1]
			if xHeaderResult.find("<") > -1 and xHeaderResult.find(">") > -1:
				xHeaderValues = xHeaderResult.split(">, ")
				xHeaderValuesLength = len(xHeaderValues)
				for i in range(xHeaderValuesLength):
					value = xHeaderValues[i]
					leftAngularBracketPosition = value.find("<") #Find position of <				
					
					name = value[:leftAngularBracketPosition-1].lower().replace('\"', '').replace(" ", "").replace("\n", "")
					email = value[leftAngularBracketPosition+1:].replace("\n", "")
					shiftedName = '\"' + hashString(name) + '\"'

					if leftAngularBracketPosition > -1:
						if email.find("@") > -1:
							localPart = email.split("@")								
							shiftedEmail = "<" + hashString(localPart[0]) + "@" + localPart[1] + ">"
						else:
							shiftedEmail = "<" + hashString(email) + ">"
					else:
						if email.find("@") > -1:
							localPart = email.split("@")								
							shiftedEmail = hashString(localPart[0]) + "@" + localPart[1]
						else:
							shiftedEmail = hashString(email)

					if i != xHeaderValuesLength - 1:
						xHeaderValues[i] = shiftedName + " " + shiftedEmail + ", "
					else:
						xHeaderValues[i] = shiftedName + " " + shiftedEmail

				result[1] = xHeader + "".join(xHeaderValues)

				if "\n" not in result[1]:
					result[1] = result[1] + "\n"
			else:
				xHeaderValues = xHeaderResult.lower().replace("\n", "").split(", ")
				xHeaderValuesLength = len(xHeaderValues)
				for i in range(xHeaderValuesLength):
					value = xHeaderValues[i].replace(" ", "")

					if value.find("@") > -1:
						localPart = value.split("@")
						shiftedValue = 	hashString(localPart[0]) + "@" + localPart[1]
					else:
						shiftedValue = hashString(value)

					if i != xHeaderValuesLength - 1:
						xHeaderValues[i] = shiftedValue + ", "
					else:
						xHeaderValues[i] = shiftedValue

				result[1] = xHeader + "".join(xHeaderValues)
				if "\n" not in result[1]:
					result[1] = result[1] + "\n"

			input[headerEmailAddressIndexInInput] = result[0]
			input[xHeaderResultIndexInInput] = result[1]

	return input


def anonymiseSenderAndReceiver(input):
	input = shuffleHeaderWithXHeader(input, "From: ", "X-From: ", "Subject: ")
	input = shuffleHeaderWithXHeader(input, "To: ", "X-To: ", "Subject: ")
	input = shuffleHeaderWithXHeader(input, "Cc: ", "X-cc: ", "Bcc: ")
	input = shuffleHeaderWithXHeader(input, "Bcc: ", "X-bcc: ")	

	return input


def removeHeader(input, header):
	result = [i for i in input if header.replace(" ", "").lower() in i.lower()]
	if len(result) >= 1:
		xHeaderResultIndexInInput = input.index(result[0])
		result[0] = ""

		input[xHeaderResultIndexInInput] = result[0]

	return input

def removeUnneededHeaders(input):
	input = removeHeader(input, "X-Folder:")
	input = removeHeader(input, "X-FileName:")
	input = removeHeader(input, "X-Origin:")

	return input