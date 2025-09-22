import http.client

conn = http.client.HTTPSConnection("hmajax.itheima.net")
payload = ''
headers = {}
conn.request("GET", "/api-s/provincesList", payload, headers)
res = conn.getresponse()
data = res.read()
print(data.decode("utf-8"))

conn = http.client.HTTPSConnection("hmajax.itheima.net")
payload = ''
headers = {}
conn.request("GET", "/api/city?pname=%E8%BE%BD%E5%AE%81%E7%9C%81", payload, headers)
res = conn.getresponse()
data = res.read()
print(data.decode("utf-8"))

conn = http.client.HTTPSConnection("hmajax.itheima.net")
payload = ''
headers = {}
conn.request("GET", "/api/area?pname=%E8%BE%BD%E5%AE%81%E7%9C%81&cname=%E5%A4%A7%E8%BF%9E%E5%B8%82", payload, headers)
res = conn.getresponse()
data = res.read()
print(data.decode("utf-8"))