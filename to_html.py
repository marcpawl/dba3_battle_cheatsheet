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
  
def bases_for_army(army_name) :
  """Write out the javascript for the names of the bases that are in the army, e.g aux, ps."""
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
    bases_for_army(army_name)

print("""
<html>
<head>
<style>
.base {
  margin-top: 20px; 
  page-break-inside: avoid;
  border-style: double;
  width: 100%;
}

.red {
  color: red;
}

.blue {
  color: blue;
}

.lt {
  margin-top: 0px; 
  margin-bottom: 0px; 
  padding-top: 0px; 
  padding-bottom: 0px; 
}

ul { padding-left: 1.2em; }

.li {
  margin-top: 0px; 
  margin-bottom: 0px; 
  margin-left: 0px; 
  border-left: 0px; 
  padding-top: 0px; 
  padding-bottom: 0px; 
  padding-left: 0px; 
}

.col {
  vertical-align: top;
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
    var li_class = document.createAttribute("class");
    li_class.value = "li";
    li.setAttributeNode(li_class)
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

function speed(node, tip) {
  var speed = tip['speed'];
  var gg = speed['GG'];
  var gg_str = gg.toString(10);
  var bg = speed['BG'];
  var bg_str = bg.toString(10);
  var speed_text = "speed  GG: " + gg_str + "BW BG/RG: " + bg_str + "BW";
  var speed_node = document.createTextNode(speed_text);
  node.appendChild(speed_node);
}

function combat(node, tip) {
  var combat = tip['combat'];
  var combat_text = "combat foot: ";
  if ( 'foot' in combat ) {
    combat_text = combat_text + combat['foot'].toString(10);
  }
  combat_text = combat_text + " mounted: "
  if ( 'mounted' in combat ) {
    combat_text = combat_text + combat['mounted'].toString(10);
  }
  combat_text = combat_text + " shot at: "
  var shot_at = ( 'shot_at' in combat ) ? combat['shot_at'] : combat['foot']
  combat_text = combat_text + shot_at.toString(10);
  var combat_node = document.createTextNode(combat_text);
  node.appendChild(combat_node);
}

function add_tool_tips(elem, base_name) {
  if ( ! (base_name in tool_tips) ) {
    return;
  }
  var tip = tool_tips[base_name];
  var table_node = document.createElement("table");
  elem.appendChild(table_node);
  var base_node_class = document.createAttribute("class");
  base_node_class.value = "base";
  table_node.setAttributeNode(base_node_class);

  var tbody = document.createElement("tbody");
  table_node.appendChild(tbody);

  var title_tr = document.createElement("tr")
  tbody.appendChild(title_tr)
  var title_base_name_td = document.createElement("td")
  var title_base_attributes_td = document.createElement("td")
  title_tr.appendChild(title_base_name_td)
  title_tr.appendChild(title_base_attributes_td)
  
  var base_name_node = document.createTextNode(base_name);
  title_base_name_td.appendChild(base_name_node);
  title_base_name_td.appendChild(document.createTextNode(" "));
  var name_node = document.createTextNode(tip['name']);
  title_base_name_td.appendChild(name_node);

  title_base_attributes_td.appendChild(document.createTextNode(" ["));
  if (('mounted' in tip) && (tip['mounted'])) {
    title_base_attributes_td.appendChild(document.createTextNode(" mounted"));
  }
  if (('solid' in tip) &&  (tip['solid'])) {
   title_base_attributes_td.appendChild(document.createTextNode(" solid"));
  }
  if (('fast' in tip) && (tip['fast'])) {
    title_base_attributes_td.appendChild(document.createTextNode(" fast"));
  }
  title_base_attributes_td.appendChild(document.createTextNode(" ]"));

  var tr = document.createElement("tr");
  tbody.appendChild(tr);
  var combat_td = document.createElement("td");
  var movement_td = document.createElement("td");
  tr.appendChild(combat_td);
  tr.appendChild(movement_td);
  var combat_td_class = document.createAttribute("class");
  combat_td_class.value = "col";
  combat_td.setAttributeNode(combat_td_class);
  var movement_td_class = document.createAttribute("class");
  movement_td_class.value = "col";
  movement_td.setAttributeNode(movement_td_class);

  speed(movement_td, tip)
  combat(combat_td, tip)


  // wins
  can_quick_kill(combat_td, tip)
  makes_flee(combat_td, tip)
  cannot_destroy(combat_td, tip)

  // looses
  quick_killed_by(combat_td, tip)
  only_killed_by(combat_td, tip)
  flees_from(combat_td, tip)

  combat_notes(combat_td, tip)

  movement_notes(movement_td, tip)
  deployment_notes(movement_td, tip)
  victory_notes(movement_td, tip)
}

function get_bases(army_key) {
  if (army_key == "None") {
    return [];
  }
  if (army_key == "All") {
""");
sys.stdout.write("return ")
sys.stdout.write( json.dumps( base_order ) )
sys.stdout.write(";")
sys.stdout.write("""
  }
  return bases[army_key]
}

function get_red_bases()
{
  var army_key = document.getElementById('red').value
  return get_bases(army_key)
}

function get_blue_bases()
{
  var army_key = document.getElementById('blue').value
  return get_bases(army_key)
}

function get_combined_bases() {
  var red = get_red_bases();
  var blue = get_blue_bases();
  var bases = [];
  bases = bases.concat(red);
  bases = bases.concat(blue);
  return bases.sort().filter(function(item, pos, ary) {
      return !pos || item != ary[pos - 1];
    });
}

function update_bases() {
  var army_elem = document.getElementById('red_army');
  army_elem.innerHTML = '';
  while (army_elem.lastElementChild) {
    army_elem.removeChild(army_elem.lastElementChild);
  }
  var base_names = get_combined_bases()
  // TODO sort the bases by base order
  for (i in base_names) {
    var base_name = base_names[i]
    add_tool_tips(army_elem, base_name)
  }
}


function red_selected() {
  update_bases();
}

function blue_selected() {
  update_bases();
}
""")
print("""
</script>
</head>
<body>
<form>
""")

def generate_army_selector(color):
  sys.stdout.write('<tr class="%s">' % (color))
  sys.stdout.write("<td>")
  sys.stdout.write('<label for="%s">%s</label>' % (color, color))
  sys.stdout.write("</td>")
  sys.stdout.write("<td>")
  sys.stdout.write('<select name="%s" id="%s" onchange="%s_selected()">\n' % (color,color,color))
  sys.stdout.write('<option value="None">None</option>\n')
  sys.stdout.write('<option value="All">All</option>\n')
  for army_name in army_names() :
    k=key_army_name_str(army_name)
    sys.stdout.write('<option value="%s">%s</option>\n' % (k, army_name))
  sys.stdout.write('</select>\n')
  sys.stdout.write("</td>")
  sys.stdout.write("</tr>")

sys.stdout.write("<table>\n")
sys.stdout.write("<tbody>\n")
generate_army_selector('red')
generate_army_selector('blue')
sys.stdout.write("</tbody>\n")
sys.stdout.write("</table>\n")

print("""
</form>
<p id="red_army">
</p>
</body>
</html>
""")
