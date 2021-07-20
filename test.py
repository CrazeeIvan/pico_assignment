import json
import xmltodict

with open ("dataset1/0001/single_case.xml") as xml_file:
	data_dict = xmltodict.parse(xml_file.read())
xml_file.close()
n = {}
n['file'] = data_dict['result']['suites']['suite']['file']
n['name'] = data_dict['result']['suites']['suite']['name']
n['timestamp'] = data_dict['result']['suites']['suite']['timestamp']
n['classname'] = data_dict['result']['suites']['suite']['cases']['case']['className']
n['testname'] = data_dict['result']['suites']['suite']['cases']['case']['testName']
n['duration'] = data_dict['result']['suites']['suite']['cases']['case']['duration']
n['skipped'] = data_dict['result']['suites']['suite']['cases']['case']['skipped']
n['passed'] = 'false' if data_dict['result']['suites']['suite']['cases']['case']['failedSince'] != 0 else 'true'
n['starttime'] = data_dict['result']['suites']['suite']['cases']['case']['className']
n['stdout'] = data_dict['result']['suites']['suite']['stdout']
n['stderr'] = data_dict['result']['suites']['suite']['stderr']
#Generate ID based on <name>_<testname>_<timestamp>
n['id'] = data_dict['result']['suites']['suite']['name']
print(n)
json_data = json.dumps(n)
with open ("data.json", "w") as json_file:
	json_file.write(json_data)
json_file.close()

