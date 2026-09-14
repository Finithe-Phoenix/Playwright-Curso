"""Package the comparative video library after all cinematic exports pass review."""
from pathlib import Path
import hashlib,json,zipfile
ROOT=Path(__file__).resolve().parents[2];M=ROOT/'videos/motion';C=M/'cinema'
records=[]
for eid in ['showcase']+[f'{i:02}' for i in range(1,13)]:
 d=json.loads((C/f'{eid}-cinema.json').read_text());p=C/f'{eid}-cinema.mp4'
 assert d['audioDecode']=='passed' and d['visualReview']!='pending',eid
 assert hashlib.file_digest(p.open('rb'),'sha256').hexdigest()==d['sha256'],eid
 assert eid=='showcase' or 360<=d['duration']<=480,eid
 records.append(d)
summary={'videos':13,'focusShots':sum(d['focusShots'] for d in records),'reviewedFrames':sum(d['sampledFrames'] for d in records),'fullPlaybackReview':'not performed','episodes':records}
(C/'summary.json').write_text(json.dumps(summary,indent=2))
files=[M/'index.html',M/'catalog.json',M/'README.md',ROOT/'README.md',ROOT/'videos/tools/serve-course.mjs']
files+=list(C.glob('*'))+list((M/'renders').glob('*motion.mp4'))+list((M/'transcripts').glob('*.md'))+list((ROOT/'docs').glob('*'))
files+=list((ROOT/'videos/assets').glob('*.ttf'))+list((ROOT/'videos/assets').glob('*LICENSE.txt'))
files=[p for p in files if p.is_file() and '.building.' not in p.name and 'preview' not in p.name]
out=ROOT/'videos/delivery/Playwright-Cinematic-Edition.zip'
with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=1) as z:
 for p in files:z.write(p,p.relative_to(ROOT))
print(json.dumps({'archive':str(out),'bytes':out.stat().st_size,'focusShots':summary['focusShots'],'reviewedFrames':summary['reviewedFrames']}))
