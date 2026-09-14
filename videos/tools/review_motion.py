"""Media integrity and sampled-frame evidence for completed motion exports."""
from pathlib import Path
import argparse, hashlib, json, re, subprocess
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'motion'
def run(eid):
    movie=OUT/'renders'/f'{eid}-motion.mp4'
    edit=json.loads((OUT/'compositions'/eid/'edit.json').read_text())
    qa=OUT/'qa';qa.mkdir(exist_ok=True)
    sha=hashlib.file_digest(movie.open('rb'),'sha256').hexdigest()
    report_path=qa/f'{eid}.json'
    if report_path.exists() and json.loads(report_path.read_text()).get('sha256')==sha:return
    probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(movie)]))
    video=next(s for s in probe['streams'] if s['codec_type']=='video');audio=next(s for s in probe['streams'] if s['codec_type']=='audio')
    assert video['width']==1920 and video['height']==1080 and video['avg_frame_rate']=='24/1'
    assert video['codec_name']=='h264' and audio['codec_name']=='aac'
    actual=float(probe['format']['duration']);assert abs(actual-edit['duration'])<.3
    decoded=subprocess.run(['ffmpeg','-hide_banner','-nostats','-xerror','-i',str(movie),'-vn','-af','volumedetect','-f','null','NUL'],capture_output=True,text=True,check=True)
    mean=float(re.search(r'mean_volume: ([\-\d.]+)',decoded.stderr)[1]);peak=float(re.search(r'max_volume: ([\-\d.]+)',decoded.stderr)[1])
    assert -45<mean<-5 and peak<=0,'Audio is silent, unusually quiet or clipped.'
    timeline_path=OUT/'audio'/eid/'timeline.json'
    if not timeline_path.exists():timeline_path=ROOT/'audio'/eid/'timeline.json'
    scenes=edit.get('scenes') or json.loads(timeline_path.read_text(encoding='utf-8'))['scenes']
    local=OUT/'local-results/review'/eid;local.mkdir(parents=True,exist_ok=True)
    font=ImageFont.truetype(str(ROOT/'assets/SourceSans3.ttf'),18)
    sheet=Image.new('RGB',(1920,((len(scenes)+2)//3)*386),'#080F22');draw=ImageDraw.Draw(sheet)
    samples=[]
    for i,scene in enumerate(scenes):
        at=scene['start']+scene['duration']/2
        frame=local/f'{i+1:02}.png'
        subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-ss',str(at),'-i',str(movie),'-frames:v','1',str(frame)],check=True)
        with Image.open(frame) as img:thumb=img.convert('RGB').resize((640,360),Image.Resampling.LANCZOS)
        x=(i%3)*640;y=(i//3)*386
        draw.text((x+9,y+3),f'{i+1:02} / {at:.2f}s / {scene["title"][:55]}',font=font,fill='#EAF2FF');sheet.paste(thumb,(x,y+26))
        samples.append({'scene':scene['id'],'time':at,'frame':str(frame.relative_to(ROOT))})
    sheet.save(qa/f'{eid}-contact.jpg',quality=94)
    result={'episode':eid,'sha256':sha,'duration':actual,'dimensions':[1920,1080],'fps':24,'audioMeanDb':mean,'audioPeakDb':peak,
        'audioDecode':'passed','sampleCount':len(samples),'samples':samples,'contactSheet':str((qa/f'{eid}-contact.jpg').relative_to(ROOT)),
        'visualReview':'pending','fullPlaybackReview':'not performed'}
    report_path.write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps({'episode':eid,'media':'passed','frames':len(samples)}),flush=True)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--episode');a=p.parse_args()
    if a.episode:run(a.episode)
    else:
        progress=json.loads((OUT/'progress.json').read_text())
        for eid,record in sorted(progress['episodes'].items()):
            if record['stage']=='exported':run(eid)
