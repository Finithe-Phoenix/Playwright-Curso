from pathlib import Path
import hashlib,json,zipfile
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'videos/motion'
catalog=json.loads((OUT/'catalog.json').read_text())
summary=[]
for entry in catalog:
 eid=entry['id'];movie=OUT/'renders'/f'{eid}-motion.mp4';report=json.loads((OUT/'qa'/f'{eid}.json').read_text())
 assert hashlib.file_digest(movie.open('rb'),'sha256').hexdigest()==report['sha256'],eid
 assert report['visualReview']!='pending' and 'revision requested' not in report['visualReview'],eid
 assert report['audioDecode']=='passed',eid
 assert eid=='showcase' or 360<=report['duration']<=480,eid
 assert abs(report['duration']-entry['duration'])<.3,eid
 assert all(0<=c['start']<report['duration'] for c in entry['chapters']),eid
 summary.append({k:report[k] for k in ['episode','sha256','duration','dimensions','fps','audioDecode','sampleCount','visualReview','fullPlaybackReview']})
progress=json.loads((OUT/'progress.json').read_text())
for item in summary:
 if item['episode']=='showcase':continue
 record=progress['episodes'][item['episode']];assert record['stage']=='exported'
 record.pop('error',None);record['visualReview']=item['visualReview']
 meta=OUT/'renders'/f'{item["episode"]}-motion.json'
 data=json.loads(meta.read_text());data['visualReview']=item['visualReview'];meta.write_text(json.dumps(data,indent=2))
(OUT/'progress.json').write_text(json.dumps(progress,indent=2))
(OUT/'qa/summary.json').write_text(json.dumps({'videos':len(summary),'sampledFrames':sum(x['sampleCount'] for x in summary),'fullPlaybackReview':'not performed','episodes':summary},indent=2))
delivery=ROOT/'videos/delivery';delivery.mkdir(exist_ok=True)
archive=delivery/'Playwright-Motion-Edition.zip'
files=[OUT/'index.html',OUT/'catalog.json',OUT/'README.md',ROOT/'README.md',ROOT/'videos/tools/serve-course.mjs']
files+=list((OUT/'renders').glob('*motion.mp4'))
files=[p for p in files if 'preview-motion' not in p.name]
files+=list((OUT/'transcripts').glob('*.md'))
files+=list((OUT/'qa').glob('*.json'))+list((OUT/'qa').glob('*contact.jpg'))
files+=list((ROOT/'docs').glob('*'))
files+=list((ROOT/'videos/assets').glob('*.ttf'))
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=1) as z:
 for p in files:
  if p.is_file():z.write(p,p.relative_to(ROOT))
print(json.dumps({'archive':str(archive),'videos':len(summary),'sampledFrames':sum(x['sampleCount'] for x in summary),'bytes':archive.stat().st_size}))
