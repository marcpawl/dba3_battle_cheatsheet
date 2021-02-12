
package.path ="json.lua/?.lua"
function dofile (filename)
  local f = assert(loadfile(filename))
  return f()

end
dofile("dba3_tts/scripts/data/data_cheat_sheet.ttslua")
armies={}
dofile("dba3_tts/scripts/data/data_armies_book_I.ttslua")
dofile("dba3_tts/scripts/data/data_armies_book_II.ttslua")
dofile("dba3_tts/scripts/data/data_armies_book_III.ttslua")
dofile("dba3_tts/scripts/data/data_armies_book_IV.ttslua")

json = require "json"

data = {}
data['armies']=armies
data['tool_tips'] = base_tool_tips

print(json.encode(data))
