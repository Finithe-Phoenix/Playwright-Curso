"""Checkpointed local neural narration; exact sentence audio bounds drive captions."""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import time
from pathlib import Path
import numpy as np
import soundfile as sf
import onnxruntime as ort
from kokoro_onnx import Kokoro

ROOT = Path(__file__).resolve().parents[1]
RATE = 24000

def atomic_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + '.tmp')
    temp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    temp.replace(path)

def spoken(text: str) -> str:
    for a,b in [('TN3270','T N thirty two seventy'),('TNZ','T N Z'),('JUnit','J Unit'),
                ('pytest','pie test'),('API','A P I'),('UI','U I'),('CI','C I'),
                ('DB2','D B two'),('z/OS','zee O S'),('JSON','Jason')]:
        text = re.sub(r'\b' + re.escape(a) + r'\b',b,text)
    return text.replace('`','')

def sentences(text):
    return [s.strip() for s in re.split(r'(?<=[.!?])\s+(?=[A-Z0-9"“])',text) if s.strip()]

def subtitle_chunks(text, max_chars=86):
    words=text.split(); result=[]; line=[]
    for word in words:
        if line and len(' '.join(line + [word])) > max_chars:
            result.append(' '.join(line));line=[]
        line.append(word)
    if line:result.append(' '.join(line))
    return result

def timestamp(t):
    ms=round(t*1000);hours,ms=divmod(ms,3600000);minutes,ms=divmod(ms,60000);seconds,ms=divmod(ms,1000)
    return f'{hours:02}:{minutes:02}:{seconds:02},{ms:03}'

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--episode');ap.add_argument('--sample',action='store_true');ap.add_argument('--speed',type=float,default=0.88);args=ap.parse_args()
    manifest=ROOT/'models/verified-downloads.json'
    if not manifest.exists() or not json.loads(manifest.read_text(encoding='utf-8')).get('allVerified'):
        raise RuntimeError('Voice assets must finish downloading and pass models/verify.py before synthesis.')
    opts=ort.SessionOptions();opts.intra_op_num_threads=2;opts.inter_op_num_threads=1
    session=ort.InferenceSession(str(ROOT/'models/kokoro-v1.0.int8.onnx'),sess_options=opts,providers=['CPUExecutionProvider'])
    model=Kokoro.from_session(session,str(ROOT/'models/voices-v1.0.bin'))
    if args.sample:
        text='Welcome to Playwright across distributed systems. First, create isolated test data. Next, submit a transfer through the browser. Finally, use T N Z to read the same reference from our local training terminal. A passing browser assertion does not prove that the business transaction was recorded correctly.'
        started=time.monotonic();samples,rate=model.create(text,voice='af_heart',speed=args.speed,lang='en-us')
        path=ROOT/'qa/voice-sample.wav';sf.write(path,samples,rate)
        print(json.dumps({'file':str(path),'seconds':len(samples)/rate,'generation_seconds':time.monotonic()-started,'peak':float(np.max(np.abs(samples)))}),flush=True);return
    episodes=json.loads((ROOT/'scripts/episodes.json').read_text(encoding='utf-8'))
    if isinstance(episodes,dict):episodes=episodes['episodes']
    for episode in episodes:
        if args.episode and episode['id'] != args.episode:continue
        eid=episode['id'];out=ROOT/'audio'/eid;out.mkdir(parents=True,exist_ok=True)
        timeline=[];cues=[];cursor=0.;parts=[]
        for scene in episode['scenes']:
            sid=scene['id'];digest=hashlib.sha256((scene['narration']+str(args.speed)+'af_heart-v1').encode()).hexdigest()
            wav=out/f'{sid}.wav';meta=out/f'{sid}.json'
            if wav.exists() and meta.exists() and json.loads(meta.read_text())['hash']==digest:
                smeta=json.loads(meta.read_text());audio,rate=sf.read(wav,dtype='float32');print('AUDIO_REUSED '+sid,flush=True)
            else:
                local=0.6;clips=[np.zeros(round(local*RATE),dtype=np.float32)];sentence_cues=[]
                for sentence in sentences(scene['narration']):
                    audio,rate=model.create(spoken(sentence),voice='af_heart',speed=args.speed,lang='en-us')
                    if rate!=RATE:raise RuntimeError(f'Unexpected sample rate {rate}')
                    if not len(audio) or not np.isfinite(audio).all():raise RuntimeError('Invalid TTS output '+sid)
                    duration=len(audio)/RATE
                    pieces=subtitle_chunks(sentence);weight=sum(len(x) for x in pieces);point=local
                    for piece in pieces:
                        length=duration*len(piece)/weight;sentence_cues.append({'start':point,'end':point+length,'text':piece});point+=length
                    clips.extend([audio,np.zeros(round(.23*RATE),dtype=np.float32)]);local+=duration+.23
                clips.append(np.zeros(round(.65*RATE),dtype=np.float32));audio=np.concatenate(clips);rate=RATE
                peak=float(np.max(np.abs(audio)))
                if peak>.94:audio*=.94/peak
                sf.write(wav,audio,RATE,subtype='PCM_16');smeta={'hash':digest,'duration':len(audio)/RATE,'cues':sentence_cues,'peak':float(np.max(np.abs(audio))),'voice':'af_heart','speed':args.speed,'engine':'Kokoro ONNX 0.6.1'};atomic_json(meta,smeta)
                print(json.dumps({'scene':sid,'seconds':round(smeta['duration'],2),'status':'narrated'}),flush=True)
            timeline.append({**scene,'start':cursor,'duration':smeta['duration'],'audio':str(wav.relative_to(ROOT)).replace('\\','/')})
            cues.extend([{**cue,'start':cue['start']+cursor,'end':cue['end']+cursor} for cue in smeta['cues']]);cursor+=smeta['duration'];parts.append(audio)
            atomic_json(ROOT/'audio/progress.json',{'episode':eid,'scene':sid,'seconds_completed':cursor,'updated':time.strftime('%Y-%m-%d %H:%M:%S')})
        combined=np.concatenate(parts);sf.write(out/'narration.wav',combined,RATE,subtype='PCM_16')
        atomic_json(out/'timeline.json',{**episode,'duration':cursor,'scenes':timeline,'captions':cues,'voice':'Kokoro af_heart','subtitle_timing':'Sentence audio boundaries; proportional phrase boundaries within each sentence.'})
        (out/'subtitles.srt').write_text('\n\n'.join(f'{i+1}\n{timestamp(c["start"])} --> {timestamp(c["end"])}\n{c["text"]}' for i,c in enumerate(cues))+'\n',encoding='utf-8')
        print(json.dumps({'episode':eid,'duration':round(cursor,2),'scene_count':len(timeline),'status':'audio_complete','within_requested_range':360<=cursor<=480}),flush=True)

if __name__=='__main__':main()
