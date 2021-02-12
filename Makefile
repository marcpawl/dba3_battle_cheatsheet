

index.html : data.json .gitmodules to_html.py
	python3 to_html.py > index.html

data.json: to_json.lua .gitmodules dba3_tts/scripts/data/data_cheat_sheet.ttslua
	lua to_json.lua > data.json  
