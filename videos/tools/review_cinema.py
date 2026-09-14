"""Check cinematic exports and extract one frame inside each editorial close-up."""
from pathlib import Path
import hashlib,json,re,subprocess
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1];O=ROOT/'motion/cinema';L=ROOT/'motion/local-results/cinema-review'
def review(eid):
 movie=O/f'{eid}-cinema.mp4';meta=O/f'{eid}-cinema.json';report=json.loads(meta.read_text());sha=hashlib.file_digest(movie.open('rb'),'sha256').hexdigest();assert sha==report['sha256']
 if report.get('audioDecode')=='passed':return
 probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-of','json',str(movie)]));v=next(s for s in probe['streams'] if s['codec_type']=='video');assert(v['width'],v['height'],v['codec_name'],v['avg_frame_rate'])==(1920,1080,'h264','24/1')
 decoded=subprocess.run(['ffmpeg','-hide_banner','-nostats','-xerror','-i',str(movie),'-vn','-af','volumedetect','-f','null','NUL'],capture_output=True,text=True,check=True)
 mean=float(re.search(r'mean_volume: ([\-\d.]+)',decoded.stderr)[1]);peak=float(re.search(r'max_volume: ([\-\d.]+)',decoded.stderr)[1]);assert -45<mean<-5 and peak<0
 shots=json.loads((O/f'{eid}-direction.json').read_text())['shots'];folder=L/eid;folder.mkdir(parents=True,exist_ok=True)
 sheet=Image.new('RGB',(1440,((len(shots)+1)//2)*425),'#080D1C');draw=ImageDraw.Draw(sheet);font=ImageFont.truetype(str(ROOT/'assets/SourceSans3-Semibold.ttf'),20)
 samples=[]
 for i,s in enumerate(shots):
  at=(s['start']+s['end'])/2;frame=folder/f'{i:02}.png'
  subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-ss',str(at),'-i',str(movie),'-frames:v','1',str(frame)],check=True)
  x=(i%2)*720;y=(i//2)*425
  with Image.open(frame) as im:sheet.paste(im.resize((720,405)),(x,y+20))
  draw.text((x+6,y),f'{s["scene"]} / {at:.1f}s',font=font,fill='#DCE8FF');samples.append(at)
 sheet.save(O/f'{eid}-review.jpg',quality=92)
 report.update(audioDecode='passed',audioMeanDb=mean,audioPeakDb=peak,sampledFrames=len(samples),sampleTimes=samples,fullPlaybackReview='not performed');meta.write_text(json.dumps(report,indent=2));print(json.dumps({'episode':eid,'samples':len(samples),'audioPeakDb':peak}),flush=True)
if __name__=='__main__':
 for p in sorted(O.glob('*-cinema.json')):review(p.name.replace('-cinema.json',''))
