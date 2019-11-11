# input and output file name

# find all recording ids present in the stm file
recoid_dict= {}
for line in open('/Users/ashisharora/Desktop/chime6/input/stm'):
  parts = line.strip().split()
  reco_id = parts[0].split('-')[0]
  if reco_id == ';;':
      continue
  if reco_id not in list(recoid_dict.keys()):
    recoid_dict[reco_id]=list()
  recoid_dict[reco_id].append(line)
print(recoid_dict.keys())

# split stm file based on the recording id
for record_id in sorted(recoid_dict.keys()):
  stm_file = '/Users/ashisharora/Desktop/chime6/output/stm_' + str(record_id)
  stm_fh = open(stm_file, 'w')
  text = recoid_dict[record_id]
  for line in text:
    stm_fh.write(line)
  stm_fh.close()


# find all spkr id present in the splitted stm file
# spliting of stm file was performed based on the recording id
for record_id in sorted(recoid_dict.keys()):
  spkrid_dict = {}
  stm_file = '/Users/ashisharora/Desktop/chime6/output/stm_' + str(record_id)
  for line in open(stm_file):
    parts = line.strip().split()
    spkr_id = parts[2]
    if spkr_id == 'NONE':
      continue
    if spkr_id not in list(spkrid_dict.keys()):
      spkrid_dict[spkr_id] = list()
    spkrid_dict[spkr_id].append(line)
  print(spkrid_dict.keys())

  # split already splitted stm file based on the spkr id
  for spkr_id in sorted(spkrid_dict.keys()):
    stm_file = '/Users/ashisharora/Desktop/chime6/output/stm_' + str(record_id) + '_' + str(spkr_id)
    stm_fh = open(stm_file, 'w')
    text = spkrid_dict[spkr_id]
    for line in text:
      stm_fh.write(line)
    stm_fh.close()