

index.html : data.json
index.html : .gitmodules
index.html : to_html.py
	python3 to_html.py > index.html

data.json: to_json.lua 
data.json: .gitmodules 
data.json: dba3_tts
data.json: json.lua
data.json:
	lua to_json.lua > data.json  

dba3_tts: dba3_tts/main.ttslua
	touch $<

dba3_tts/main.ttslua:
	git submodule init dba3_tts
	cd dba3_tts && git fetch && git submodule update

json.lua: json.lua/json.lua
	touch $<

json.lua/json.lua:
	git submodule init json.lua
	cd json.lua && git fetch && git submodule update

clean:
	rm data.json index.html


.DELETE_ON_ERROR:
