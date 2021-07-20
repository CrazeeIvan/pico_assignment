import json
import xmltodict

with open ("dataset1/0001/single_case.xml") as xml_file:
	data_dict = xmltodict.parse(xml_file.read())
xml_file.close()
#print(data_dict['result'])
#data_dict['result']['@plugin']="hello"
#print(data_dict['result'])
a = '{'
a += '"file" : "' + data_dict['result']['suites']['suite']['file'] + '"'
a += '}'
n = json.loads(a)
json_data = json.dumps(n)
with open ("data.json", "w") as json_file:
	json_file.write(json_data)
json_file.close()

