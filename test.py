import json
import xmltodict

with open ("dataset1/0001/single_case.xml") as xml_file:
	data_dict = xmltodict.parse(xml_file.read())
xml_file.close()
a = '{'
a += '"file" : "' + data_dict['result']['suites']['suite']['file'] + '"'
a += '"name" : "' + data_dict['result']['suites']['suite']['name'] + '"'
a += '"timestamp" : "' + data_dict['result']['suites']['suite']['timestamp'] + '"'
a += '"classname" : "' + data_dict['result']['suites']['suite']['cases']['case']['classname'] + '"'
a += '"testname" : "' + data_dict['result']['suites']['suite']['cases']['case']['testname'] + '"'
a += '"duration" : "' + data_dict['result']['suites']['suite']['cases']['case']['duration'] + '"'
a += '"skipped" : "' + data_dict['result']['suites']['suite']['cases']['case']['skipped'] + '"'
a += '"passed" : "true"'
a += '"starttime" : "' + data_dict['result']['suites']['suite']['cases']['case']['classname'] + '"'
a += '"stdout" : "' + data_dict['result']['suites']['suite']['stdout'] + '"'
a += '"stderr" : "' + data_dict['result']['suites']['suite']['stderr'] + '"'
#Generate ID based on <name>_<testname>_<timestamp>
a += '"id" : "' + data_dict['result']['suites']['suite']['name'] + '"'

a += '}'
n = json.loads(a)
json_data = json.dumps(n)
with open ("data.json", "w") as json_file:
	json_file.write(json_data)
json_file.close()
