import os;
import re;
import errno;
import socket;
import random;
import string;
import tldextract;

rootEmailDir = "../b_DataCleaning/clean_AND_anonymised";
foldersToExplore = [{"user": "", "path": rootEmailDir}];
filesToProcess = [];
domainIpArray = {};

csvFile = open("host_ip/host_ip_map.csv", "r");
print("Reading host-ip map...", end='', flush=True);
csvLines = csvFile.readlines();
print(" Done\nIPs found: " + str(len(csvLines)));
csvFile.close();

for r, csvRecord in enumerate(csvLines):
	if r == 0:
		continue;

	domainIpMap = csvRecord.rstrip('\n').split(',');

	domainIpArray[domainIpMap[0]] = domainIpMap[1];

while len(foldersToExplore) != 0:
	currentMap = foldersToExplore.pop(0);
	currentFolder = currentMap["path"];
	print("Exploring folder: " + currentFolder);
	insertIndex = 0;

	for folder in os.listdir(currentFolder):
		if os.path.isdir(currentFolder + "/" + folder):
			user = currentMap["user"];

			if user == "":
				user = folder;

			foldersToExplore.insert(insertIndex, {"user": user, "path": currentFolder + "/" + folder});
			insertIndex += 1;
		else:
			filesToProcess.append({"user": user, "path": currentFolder + "/" + folder});

print("Found " + str(len(filesToProcess)) + " emails.");
headers = ["user", "email path"];
csvFileContent = [];
headerPattern = re.compile('^\s.*$');

for i, emailMap in enumerate(filesToProcess):
	emailPath = emailMap["path"];
	email = open(emailPath,"r");
	emailLines = email.readlines();
	email.close();
	csvLine = {"user": emailMap["user"].replace("\"", "").replace(",", "+")};
	csvLine["email path"] = emailPath.replace("\"", "").replace(",", "+")[len(rootEmailDir) + 1:];

	for line in emailLines:
		line = line.rstrip('\n');

		if line == "":
			break;

		headerInLine, separatorInLine, valueInLine = line.partition(":");

		if separatorInLine == "" or headerPattern.match(headerInLine):
			continue;
		else:
			if headerInLine == "Date":
				csvLine[headerInLine] = valueInLine;
			elif headerInLine == "From":
				beforeAt, at, fromDomain = valueInLine.partition("@");
				domainExtract = tldextract.extract(fromDomain);
				fromDomain = domainExtract.domain + "." + domainExtract.suffix;
				csvLine["From-Domain"] = fromDomain;
				csvLine["From-IP"] = "";

				try:
					csvLine["From-IP"] = domainIpArray[fromDomain];
				except KeyError:
					print("\rCouldn't find ip for " + fromDomain + " in local cache.");
					try:
						csvLine["From-IP"] = socket.gethostbyname(fromDomain);
					except socket.gaierror as e:
						csvLine["From-IP"] = fromDomain;

					domainIpArray[fromDomain] = csvLine["From-IP"];

				csvLine[headerInLine] = valueInLine.replace("\"", "").replace(",", "+").strip();

	fabricatedEmailPath = "forged_emails/" + emailPath[13:];

	if not os.path.exists(os.path.dirname(fabricatedEmailPath)):
		try:
			os.makedirs(os.path.dirname(fabricatedEmailPath))
		except OSError as exc: # Guard against race condition
			if exc.errno != errno.EEXIST:
				raise

	fabricatedEmailFile = open(fabricatedEmailPath, "w");
	fabricatedEmailFile.write("Received1: by 184.168.221.41 with SMTP id " + ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(16)) + "; " + csvLine["Date"] + "\n");
	fabricatedEmailFile.write("Received2: from " + csvLine["From-Domain"] + " (" + csvLine["From-Domain"] + " [" + csvLine["From-IP"] + "]) by mx.google.com with ESMTPS id " + ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(14)) + ";" + csvLine["Date"] + " (version=TLS1_2 cipher=AES128-GCM-SHA256 bits=128/128); " + csvLine["Date"] + "\n");
	fabricatedEmailFile.write("X-Mailer: \n");

	for line in emailLines:
		fabricatedEmailFile.write(line);

	fabricatedEmailFile.close();
	os.chmod(fabricatedEmailPath, 0o777);

	if i % 1000 == 0:
		print("\Forged emails progress: " + str(round(i / len(filesToProcess) * 100, 2)) + "%", end='', flush=True);
		csvFile = open("host_ip/host_ip_map.csv", "w");
		csvFile.write("host,ip\n");

		for i, domainIpKey in enumerate(domainIpArray.keys()):
			csvFile.write(domainIpKey + "," + domainIpArray[domainIpKey] + "\n");

		csvFile.close();

	# if i / len(filesToProcess) * 100 > 1:
	# 	break;

print("\rForged emails progress: " + str(round(i / len(filesToProcess) * 100, 2)) + "%");

print("\nSaving host-ip file...", end='', flush=True);

csvFile = open("host_ip/host_ip_map.csv", "w");
csvFile.write("host,ip\n");

for i, domainIpKey in enumerate(domainIpArray.keys()):
	csvFile.write(domainIpKey + "," + domainIpArray[domainIpKey] + "\n");

csvFile.close();