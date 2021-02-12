#!/usr/local/bin/python3
import json
import re
import sys

with open('data.json') as f:
  data = json.load(f)

books=['I', 'II', 'III', 'IV']

base_order= [
  # Elephants
  'El',
  # Knights
  '3Kn', '4Kn', '6Kn', 'HCh',
  # Cavalry
  'Cv', '3Cv', '6Cv',  'LCh',
  # Light Horse
  '2LH', 'LH', 'LCm', '2Cm',
  # Scythed Chariots
  'SCh',
  # Camelry
  'Cm',
  # Spears
  'Sp', '8Sp',
  # Pikes
  '4Pk', '3Pk',
  # Blades
  '4Bd', '3Bd', '6Bd',
  # Auxilia
  '4Ax','3Ax',
  # Bows
  '4Bw','3Bw', '8Bw',
  '4Cb', '3Cb', '8Cb',
  '4Lb', '3Lb', '8Lb',
  '3Bw_Mtd', '3Bw-Mtd', '3Mtd-Bw', '3Bw:Mtd',
  '4Bw-Mtd', 'Mtd-4Bw', '4Bw_Mtd',
  '4Cb_Mtd',
  '4Lb_Mtd', '4Lb-Mtd',
  # Psiloi
  'Ps',
  # Warbands
  '4Wb','3Wb',
  # Hordes
  '7Hd', '5Hd',
  # Artillery
  'Art',
  # War Wagons
  'WWg',
  # Ceneral
  'Cp', 'CP', '3CP', 'Lit', 'CWg',
  'Camp'
]


army_name_re = re.compile("([^/]*)/(\d+)(\S*)")
def key_army_name(army_name) :
  k= list(army_name_re.match(army_name).groups())
  k[1] = int(k[1])
  return k

def key_base_order(base_name) :
  i = base_order.index(base_name)
  return i

def key_army_name_str(army_name) :
  k=key_army_name(army_name)
  return k[0] + '/' + str(k[1]) + k[2]

def army_names():
  """Return all the army names"""
  names = {}
  result=[]
  for book in books :
    book_str = "Book " + book
    for army in data['armies'][book_str] :
      # Ignore same army with plain vs models
      k = key_army_name(army)
      plain = str(k)
      
      if plain not in names :
        names[plain] = 1
        result.append(army)
  result.sort(key=key_army_name)
  return result

def remove_suffix(name, suffix) :
  l = len(suffix)
  if name[-l:] == suffix :
    return name[:-l]
  return name

def remove_general(name) :
  """Remove general suffix"""
  return remove_suffix(name, "_Gen")

def remove_mounted(name) :
  """Remove mounted suffix"""
  name = remove_suffix(name, "_Mtd")
  name = remove_suffix(name, "-Mtd")
  name = remove_suffix(name, ":Mtd")
  if name == "Mtd-4Bw" :
    return "4Bw"
  return name

def normalize_base_name(name) :
  name = remove_general(name)
  name = remove_mounted(name)
  return name

def book_from_army_name(army_name):
  k=key_army_name(army_name)
  return "Book " + k[0]
  
def army_for_bases(army_name) :
  """Return the names of the bases that are in the army, e.g aux, ps."""
  book = book_from_army_name(army_name)
  army = data['armies'][book][army_name]
  bases=[]
  for base in army:
    if base.startswith("base") :
      name=normalize_base_name(army[base]['name'])
      if name not in bases :
        bases.append(name)
  bases.sort(key=key_base_order)
  sys.stdout.write( json.dumps(bases) )
  sys.stdout.write(";\n")

def army_bases() :
  """Generate the bases for all the armies"""
  sys.stdout.write("var bases={};\n")
  for army_name in army_names() :
    k=key_army_name_str(army_name)
    sys.stdout.write("bases['%s'] = " % (k))
    army_for_bases(army_name)

print("""
<html>
<head>
<style>
.base {
  page-break-inside: avoid;
}

.lt {
  margin-top: 0px; 
  margin-bottom: 0px; 
  padding-top: 0px; 
  padding-bottom: 0px; 
}

@media print {
  .base {page-break-inside: avoid;}
}
</style>
<script>
""")
army_bases()

sys.stdout.write("var tool_tips=")
sys.stdout.write( json.dumps(data['tool_tips']) )
sys.stdout.write(";\n")

print("""
function rules(node, key, title, tip) {
  if (! (key in tip)) {
    return
  }
  var list = tip[key]
  if ( list.length <= 0 ) {
    return;
  }
  var div = document.createElement("DIV")
  node.appendChild(div);
  var div_class = document.createAttribute("class");
  div_class.value = "lt";
  div.setAttributeNode(div_class)

  div.appendChild(document.createTextNode(title + ":"));
  var ul = document.createElement("UL")
  node.appendChild(ul)
  var ul_class = document.createAttribute("class");
  ul_class.value = "lt";
  ul.setAttributeNode(ul_class)

  for (i in list ) {
    var li = document.createElement("LI")
    ul.appendChild(li)
    li.appendChild(document.createTextNode(list[i]));
  }
}

function can_quick_kill(node, tip) {
  rules(node, 'can_quick_kill', 'Quick Kills', tip)
}

function quick_killed_by(node, tip) {
  rules(node, 'quick_killed_by', 'Quick Killed By', tip)
}

function only_killed_by(node, tip) {
  rules(node, 'only_killed_by', 'Only Killed By', tip)
}

function makes_flee(node, tip) {
  rules(node, 'makes_flee', 'Makes Flee', tip)
}

function flees_from(node, tip) {
  rules(node, 'flees_from', 'Flees From', tip)
}

function cannot_destroy(node, tip) {
  rules(node, 'cannot_destroy', 'Cannot Destroy', tip)
}

function combat_notes(node, tip) {
  rules(node, 'combat_notes', 'Combat', tip)
}

function movement_notes(node, tip) {
  rules(node, 'movement_notes', 'Movement', tip)
}

function deployment_notes(node, tip) {
  rules(node, 'deployment_notes', 'Deployment', tip)
}

function victory_notes(node, tip) {
  rules(node, 'victory_notes', 'Victory', tip)
}

function add_tool_tips(elem, base_name) {
  if ( ! (base_name in tool_tips) ) {
    return;
  }
  var tip = tool_tips[base_name];
  var base_node = document.createElement("P");
  elem.appendChild(base_node);
  var base_node_class = document.createAttribute("class");
  base_node_class.value = "base";
  base_node.setAttributeNode(base_node_class)

  var base_name_node = document.createTextNode(base_name);
  base_node.appendChild(base_name_node);
  base_node.appendChild(document.createTextNode(" "));
  var name_node = document.createTextNode(tip['name']);
  base_node.appendChild(name_node);
  base_node.appendChild(document.createTextNode(" ["));
  if (('mounted' in tip) && (tip['mounted'])) {
    base_node.appendChild(document.createTextNode(" mounted"));
  }
  if (('solid' in tip) &&  (tip['solid'])) {
    base_node.appendChild(document.createTextNode(" solid"));
  }
  if (('fast' in tip) && (tip['fast'])) {
    base_node.appendChild(document.createTextNode(" fast"));
  }
  base_node.appendChild(document.createTextNode(" ]"));
  base_node.appendChild(document.createElement("BR"))

  var speed = tip['speed'];
  var gg = speed['GG'];
  var gg_str = gg.toString(10);
  var bg = speed['BG'];
  var bg_str = bg.toString(10);
  var speed_text = "speed " + gg_str + "/" + bg_str;
  var speed_node = document.createTextNode(speed_text);
  base_node.appendChild(speed_node);

  base_node.appendChild(document.createTextNode(" "));

  var combat = tip['combat'];
  var combat_text = "combat ";
  if ( 'foot' in combat ) {
    combat_text = combat_text + combat['foot'].toString(10);
  }
  combat_text = combat_text + "/"
  if ( 'mounted' in combat ) {
    combat_text = combat_text + combat['mounted'].toString(10);
  }
  combat_text = combat_text + "/"
  var shot_at = ( 'shot_at' in combat ) ? combat['shot_at'] : combat['foot']
  combat_text = combat_text + shot_at.toString(10);
  var combat_node = document.createTextNode(combat_text);
  base_node.appendChild(combat_node);
  base_node.appendChild(document.createElement("BR"))

  // wins
  can_quick_kill(base_node, tip)
  makes_flee(base_node, tip)
  cannot_destroy(base_node, tip)

  // looses
  quick_killed_by(base_node, tip)
  only_killed_by(base_node, tip)
  flees_from(base_node, tip)

  combat_notes(base_node, tip)
  movement_notes(base_node, tip)
  victory_notes(base_node, tip)
  deployment_notes(base_node, tip)
}

function red_selected() {
  console.log("red_selected");
  var army_key = document.getElementById('red').value
  var army_elem = document.getElementById('red_army');
  army_elem.innerHTML = "RED ARMY " + army_key;
  var base_names = bases[army_key]
  for (i in base_names) {
    console.log(i)
    var base_name = base_names[i]
    add_tool_tips(army_elem, base_name)
  }
}
""")
print("""
</script>
</head>
<body>
<form>
""")

print('<select name="red" id="red" onchange="red_selected()">')
print('<option value="">None</option>')
for army_name in army_names() :
  k=key_army_name_str(army_name)
  print('<option value="%s">%s</option>' % (k, army_name))
print('</select>')

print("""
</form>
<p id="red_army">
</p>
</body>
</html>
""")
