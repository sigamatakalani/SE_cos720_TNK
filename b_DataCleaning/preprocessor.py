import shutil
import os
import sys
import random
import anonymiser
import traceback
import utils

def joinSubjectHeaderIntoOneLine(line, handlingHeader, joinedLine, replaceLine):
	searchLine = line.lower()
	if handlingHeader == False and searchLine.find("subject:") > -1:
		handlingHeader = True
		joinedLine += anonymiser.replaceDigit(line.replace("\n", ""))
	elif handlingHeader and (searchLine.find("cc:") == -1 and searchLine.find("mime-version:") == -1):
		joinedLine += anonymiser.replaceDigit(line.replace("\n", ""))
	elif handlingHeader:
		if joinedLine.find("\n") == -1:
			joinedLine += "\n"
		handlingHeader = False
		replaceLine = True

	return joinedLine, handlingHeader, replaceLine

def joinEmailHeaderList(line, handlingHeader, headerList, header, nextHeader=None, excludeString=None, alternativeNextHeader=None):
	searchLine = line.lower()
	if handlingHeader == False and searchLine.find(header.lower()) > -1 and (True if excludeString is None else searchLine.find(excludeString.lower()) == -1) and searchLine.find("x-"+header.lower()) == -1:
		handlingHeader = True
		headerList.append(line)
	elif handlingHeader and (nextHeader is not None and searchLine.find(nextHeader.lower()) == -1 and
	(True if alternativeNextHeader is None else searchLine.find(alternativeNextHeader.lower()) == -1)):
		headerList.append(line)
	elif handlingHeader and nextHeader is None and searchLine != "\n":
		headerList.append(line)
	elif handlingHeader:
		handlingHeader = False

	return headerList, handlingHeader


def joinSubjectHeaderToString(input, subjectLine):
	headerResult = [i for i in input if "subject:" in i.lower()]
	ccHeaderResult = [i for i in input if "cc:" in i.lower() and "bcc:" not in i.lower() and "x-cc:" not in i.lower()]
	mimeHeaderResult = [i for i in input if "mime-version:" in i.lower()]

	if len(headerResult) > 0:
		headerIndexInInput = input.index(headerResult[0])
		if len(ccHeaderResult) > 0:
			nextHeaderIndexInInput = input.index(ccHeaderResult[0])
		else:
			nextHeaderIndexInInput = input.index(mimeHeaderResult[0])

		for i in range(headerIndexInInput, nextHeaderIndexInInput):
			input.pop(headerIndexInInput)

		input.insert(headerIndexInInput, subjectLine)

	return input


def joinEmailHeaderListsToString(input, list, header, nextHeader, exludeHeader=None, alternativeNextHeader=None):
	if exludeHeader is None:
		headerResult = [i for i in input if header.lower() in i.lower() and "x-"+header.lower() not in i.lower()]
		nextHeaderResult = [i for i in input if nextHeader.lower() in i.lower() and "x-"+nextHeader.lower() not in i.lower()]
	else:
		headerResult = [i for i in input if header.lower() in i.lower() and exludeHeader.lower() not in i.lower() and "x-"+header.lower() not in i.lower()]
		nextHeaderResult = [i for i in input if nextHeader.lower() in i.lower() and "x-"+nextHeader.lower() not in i.lower()]

	if alternativeNextHeader is not None:
		alternativeNextHeaderResult = [i for i in input if alternativeNextHeader.lower() in i.lower()]

	if len(headerResult) > 0:
		headerIndexInInput = input.index(headerResult[0])

		if len(nextHeaderResult) > 0:
			nextHeaderIndexInInput = input.index(nextHeaderResult[0])			
		elif alternativeNextHeader is not None and len(alternativeNextHeaderResult) > 0:
			nextHeaderIndexInInput = input.index(alternativeNextHeaderResult[0])			
		else:
			nextHeaderIndexInInput = len(input)			

		for i in range(headerIndexInInput, nextHeaderIndexInInput):			
			input.pop(headerIndexInInput)

		combinedHeader = ''.join(list)
		input.insert(headerIndexInInput, combinedHeader)

	return input


def removeBody(infile, shouldRemoveBody):
	emailFileLines = []
	emailHeaderLines = []

	handlingFromHeader = False
	handlingToHeader = False
	handlingCcHeader = False
	handlingBccHeader = False
	handlingSubjectHeader = False
	replaceSubjectLine = False

	handlingXFromHeader = False
	handlingXToHeader = False
	handlingXCcHeader = False
	handlingXBccHeader = False

	fromHeaderList = []
	toHeaderList = []
	ccHeaderList = []
	bccHeaderList = []

	xfromHeaderList = []
	xtoHeaderList = []
	xccHeaderList = []
	xbccHeaderList = []

	joinedSubjectLine = ""

	# Remove body first and preprocess before preprocessing headers	
	for line in infile:		
		if shouldRemoveBody and (line.find("X-FileName:") == -1 and line != "\n"):
			emailFileLines.append(line)

			joinedSubjectLine, handlingSubjectHeader, replaceSubjectLine = joinSubjectHeaderIntoOneLine(line, handlingSubjectHeader, joinedSubjectLine, replaceSubjectLine)
			if replaceSubjectLine:
				joinSubjectHeaderToString(emailFileLines, joinedSubjectLine)
				replaceSubjectLine = False

			fromHeaderList, handlingFromHeader = joinEmailHeaderList(line, handlingFromHeader, fromHeaderList, "from:", "to:", "subject", "subject:")
			toHeaderList, handlingToHeader = joinEmailHeaderList(line, handlingToHeader, toHeaderList, "to:", "subject:", "subject:")
			ccHeaderList, handlingCcHeader = joinEmailHeaderList(line, handlingCcHeader, ccHeaderList, "cc:", "mime-version:", "bcc:")
			bccHeaderList, handlingBccHeader = joinEmailHeaderList(line, handlingBccHeader, bccHeaderList, "bcc:", "x-from:", "x-bcc:")

			xfromHeaderList, handlingXFromHeader = joinEmailHeaderList(line, handlingXFromHeader, xfromHeaderList, "x-from:", "x-to:")
			xtoHeaderList, handlingXToHeader = joinEmailHeaderList(line, handlingXToHeader, xtoHeaderList, "x-to:", "x-cc:")
			xccHeaderList, handlingXCcHeader = joinEmailHeaderList(line, handlingXCcHeader, xccHeaderList, "x-cc:", "x-bcc:")
			xbccHeaderList, handlingXBccHeader = joinEmailHeaderList(line, handlingXBccHeader, xbccHeaderList, "x-bcc:", "x-folder:")
		elif not shouldRemoveBody:
			emailFileLines.append(line)

			joinedSubjectLine, handlingSubjectHeader, replaceSubjectLine = joinSubjectHeaderIntoOneLine(line, handlingSubjectHeader, joinedSubjectLine, replaceSubjectLine)
			if replaceSubjectLine:
				joinSubjectHeaderToString(emailFileLines, joinedSubjectLine)
				replaceSubjectLine = False

			fromHeaderList, handlingFromHeader = joinEmailHeaderList(line, handlingFromHeader, fromHeaderList, "from:", "to:", "subject", "subject:")
			toHeaderList, handlingToHeader = joinEmailHeaderList(line, handlingToHeader, toHeaderList, "to:", "subject:", "subject:")
			ccHeaderList, handlingCcHeader = joinEmailHeaderList(line, handlingCcHeader, ccHeaderList, "cc:", "mime-version:", "bcc:")
			bccHeaderList, handlingBccHeader = joinEmailHeaderList(line, handlingBccHeader, bccHeaderList, "bcc:", "x-from:", "x-bcc:")

			xfromHeaderList, handlingXFromHeader = joinEmailHeaderList(line, handlingXFromHeader, xfromHeaderList, "x-from:", "x-to:")
			xtoHeaderList, handlingXToHeader = joinEmailHeaderList(line, handlingXToHeader, xtoHeaderList, "x-to:", "x-cc:")
			xccHeaderList, handlingXCcHeader = joinEmailHeaderList(line, handlingXCcHeader, xccHeaderList, "x-cc:", "x-bcc:")
			xbccHeaderList, handlingXBccHeader = joinEmailHeaderList(line, handlingXBccHeader, xbccHeaderList, "x-bcc:", "x-folder:")
		else:
			emailFileLines.append(line)
			break
	
	for line in emailFileLines:				
		emailHeaderLines.append(line)

			

	joinEmailHeaderListsToString(emailHeaderLines, fromHeaderList, "from:", "to:", "subject:", "subject:")
	joinEmailHeaderListsToString(emailHeaderLines, toHeaderList, "to:", "subject:", "subject:")
	joinEmailHeaderListsToString(emailHeaderLines, ccHeaderList, "cc:", "mime-version:", "bcc:")
	joinEmailHeaderListsToString(emailHeaderLines, bccHeaderList, "bcc:", "x-from:")
	joinEmailHeaderListsToString(emailHeaderLines, xfromHeaderList, "x-from:", "x-to:")
	joinEmailHeaderListsToString(emailHeaderLines, xtoHeaderList, "x-to:", "x-cc:")
	joinEmailHeaderListsToString(emailHeaderLines, xccHeaderList, "x-cc:", "x-bcc:")
	joinEmailHeaderListsToString(emailHeaderLines, xbccHeaderList, "x-bcc:", "x-folder:")

	return emailHeaderLines


def search_directory(directory, outputDirectory, shouldRemoveBody):
	countFiles = 0
	currentFileIndex = 0
	print("Discovering files...")
	for root, directories, files in os.walk(directory):
		countFiles += len(files)
	
	for root, directories, files in os.walk(directory):
		outputPath = os.path.join(outputDirectory, root[len(directory)+1:])
		if not os.path.isdir(outputPath):
			os.mkdir(outputPath)

		utils.log("\rAnonymising " + root + " " + str(round((currentFileIndex/countFiles)*100, 2)) + "%")		
		for file in os.listdir(root):
			filePath = os.path.join(root,file)
			outputFilePath = os.path.join(outputPath,file)
			if os.path.isfile(filePath):
				currentFileIndex += 1
				with open(filePath, "r") as fileToCopy:
					with open(outputFilePath, "w+") as fileToWrite:
						try:
							removedBodyFromEmail = removeBody(fileToCopy, shouldRemoveBody)
							fileSize = os.path.getsize(filePath)
							removedBodyFromEmail.append("X-Filesize: " + str(fileSize))
							modifiedNamesAndSurnames = anonymiser.anonymiseSenderAndReceiver(removedBodyFromEmail)							
							fileToWrite.writelines(modifiedNamesAndSurnames)
						except Exception:
							print("Error on ", filePath)
							traceback.print_exc()
							sys.exit(1)
	
	print("\nDone")


search_directory('../a_DataAquisition/raw_maildir', 'clean_AND_anonymised', True)
