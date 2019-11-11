# input and output file name

# find all recording ids present in the stm file
recoid_dict= {}
for line in open('/Users/ashisharora/Desktop/chime6/input/ctm'):
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
  stm_file = '/Users/ashisharora/Desktop/chime6/output/ctm_' + str(record_id)
  stm_fh = open(stm_file, 'w')
  text = recoid_dict[record_id]
  for line in text:
    stm_fh.write(line)
  stm_fh.close()


rttm_dict= {}
for line in open('/Users/ashisharora/Desktop/chime6/input/rttm'):
  parts = line.strip().split()
  reco_id = parts[1].split('-')[0]
  reco_id = reco_id + '.ENH'
  if reco_id not in list(rttm_dict.keys()):
    rttm_dict[reco_id]=list()
  rttm_dict[reco_id].append(line)
print(rttm_dict.keys())


def get_spkr_id_from_rttm(record_id, tbeg, tdur):
  # print(record_id)
  found = False
  for line in rttm_dict[record_id]:
    parts = line.strip().split()
    if float(parts[3])<=float(tbeg)+0.01 and float(parts[3]) + float(parts[4]) >= float(tbeg) + float(tdur):
      # print(parts[7])
      found = True
      return parts[7]
  if not found:
    print(str(float(tbeg)), str(float(tdur)), str(float(tbeg) + float(tdur)))
    print('error')

# find all spkr id present in the splitted stm file
# spliting of stm file was performed based on the recording id
for record_id in sorted(recoid_dict.keys()):
  spkrid_dict = {}
  stm_file = '/Users/ashisharora/Desktop/chime6/output/ctm_' + str(record_id)
  for line in open(stm_file):
    parts = line.strip().split()
    tbeg = parts[2]
    tdur = parts[3]
    # find spkr id
    if tdur == '*' or tbeg == '*':
      continue
    spkr_id = get_spkr_id_from_rttm(str(record_id), tbeg, tdur)
    if spkr_id not in list(spkrid_dict.keys()):
      spkrid_dict[spkr_id] = list()
    spkrid_dict[spkr_id].append(line)
  print(spkrid_dict.keys())

  # split already splitted stm file based on the spkr id
  for spkr_id in sorted(spkrid_dict.keys()):
    stm_file = '/Users/ashisharora/Desktop/chime6/output/ctm_' + str(record_id) + '_' + str(spkr_id)
    stm_fh = open(stm_file, 'w')
    text = spkrid_dict[spkr_id]
    for line in text:
      stm_fh.write(line)
    stm_fh.close()