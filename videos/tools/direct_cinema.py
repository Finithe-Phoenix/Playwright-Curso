"""Add editorial close-ups and restrained transition sound to the Hyperframes edition.
The original video and captions remain the source of every visible demonstration.
"""
from pathlib import Path
import argparse, hashlib, json, re, subprocess, textwrap
import numpy as np
import soundfile as sf
ROOT=Path(__file__).resolve().parents[1];M=ROOT/'motion';O=M/'cinema';L=M/'local-results/cinema'

def make(eid):
    out=O/f'{eid}-cinema.mp4';O.mkdir(exist_ok=True);local=L/eid;local.mkdir(parents=True,exist_ok=True)
    source=M/'renders'/f'{eid}-motion.mp4';edit=json.loads((M/'compositions'/eid/'edit.json').read_text(encoding='utf-8'))
    timeline=M/'audio'/eid/'timeline.json'
    if not timeline.exists():timeline=ROOT/'audio'/eid/'timeline.json'
    scenes=edit.get('scenes') or json.loads(timeline.read_text(encoding='utf-8'))['scenes']
    page=(M/'compositions'/eid/'index.html').read_text(encoding='utf-8')
    shots=[]
    for i,s in enumerate(scenes):
        live=next((x for x in edit['overlays'] if x['scene']==s['id']),None)
        title=s['title'];label='READ THE\nCODE';note='Executable contract / teaching walkthrough'
        start=s['start']+s['duration']*.34;end=s['start']+s['duration']*.85
        if live:
            geom=(live['x'],live['y'],live['width'],live['height']);label='WATCH IT\nHAPPEN';note='Recorded local browser / original speed'
            start=live['start']+.2;end=s['start']+s['duration']-.7
        elif eid=='showcase':
            if i==1:geom=(210,275,1500,560);label='MAKE IT\nPRECISE';note='Reusable prompt / teaching input'
            elif i==2:geom=(210,275,1500,560)
            elif i==6:geom=(210,275,1500,560);label='SAME ID.\nSAME STATE.';note='Captured successful TNZ lookup / local simulator'
            else:continue
        else:
            sid='m'+s['id'].replace('-','');match=re.search(r'<section class="scene ([^"]*)" id="'+sid+'">',page)
            layout=match[1] if match else ''
            if 'workbench' in layout and s.get('code'):geom=(65,228,998,654)
            elif i in (6,7,8,9) and eid in ('09','10','11'):
                geom=(65,228,1200,654) if 'fullstage' in layout else (671,228,1184,654)
                label='FOLLOW\nTHE ID';note='Captured successful TNZ lookup / local simulator'
            elif 'PROMPT WORKSHOP' in page.split(f'id="{sid}"',1)[-1].split('</section>',1)[0]:
                geom=(65,228,1790,654) if 'fullstage' in layout else (671,228,1184,654)
                label='ASK WITH\nEVIDENCE';note='Reusable prompt / teaching input'
            else:continue
        # Fit the entire original panel; never crop assertions or terminal fields.
        x,y,w,h=geom;factor=min(1250/w,770/h);dw=int(w*factor)//2*2;dh=int(h*factor)//2*2
        shots.append(dict(scene=s['id'],title=title,start=round(start,3),end=round(end,3),crop=geom,width=dw,height=dh,label=label,note=note))
    duration=edit['duration'];sample_rate=24000;fx=np.zeros(round((duration+.1)*sample_rate),dtype=np.float32)
    rng=np.random.default_rng(317)
    for shot in shots:
        for at in (shot['start'],shot['end']):
            count=int(.28*sample_rate);t=np.arange(count)/sample_rate
            wave=(np.sin(2*np.pi*(180*t+1800*t*t))*.35+rng.normal(0,.25,count))*np.sin(np.pi*t/.28)**2*.013
            pos=int(at*sample_rate);fx[pos:pos+count]+=wave[:len(fx[pos:pos+count])]
    sf.write(local/'transitions.wav',fx,sample_rate,subtype='PCM_16')
    expressions='+'.join(f'between(t,{s["start"]},{s["end"]})' for s in shots) or '0'
    groups={}
    for i,shot in enumerate(shots):groups.setdefault(tuple(shot['crop'])+(shot['width'],shot['height']),[]).append(i)
    filters=[f'[0:v]split={len(groups)+1}[base]'+''.join(f'[g{i}]' for i in range(len(groups)))]
    for gi,(key,ids) in enumerate(groups.items()):
        x,y,w,h,dw,dh=key
        targets=''.join(f'[p{i}]' for i in ids)
        filters.append(f'[g{gi}]crop={w}:{h}:{x}:{y},scale={dw}:{dh}:flags=lanczos,setsar=1'+(f',split={len(ids)}' if len(ids)>1 else '')+targets)
    filters.append(f"[base]drawbox=x=0:y=0:w=1920:h=956:color=0x080D1C:t=fill:enable='{expressions}'[b0]")
    last='b0';font='videos/assets/SourceSans3-Semibold.ttf';mono='videos/assets/JetBrainsMono.ttf'
    for i,s in enumerate(shots):
        a,b=s['start'],s['end'];enable=f'between(t,{a},{b})';x,y,w,h=s['crop'];dw,dh=s['width'],s['height'];dx=630+(1250-dw)//2;dy=165+(770-dh)//2
        filters.append(f"[{last}][p{i}]overlay=x='{dx}+70*max(0,1-(t-{a})/0.45)':y={dy}:enable='{enable}':eof_action=pass[o{i}]")
        label=local/f'{i}-label.txt';label.write_text(s['label'].split('\n')[0],encoding='utf-8')
        label2=local/f'{i}-label2.txt';label2.write_text(s['label'].split('\n')[-1],encoding='utf-8')
        heading=local/f'{i}-title.txt';heading.write_text(s['title'],encoding='utf-8')
        note=local/f'{i}-note.txt';note.write_text('\n'.join(textwrap.wrap(s['note'],29)),encoding='utf-8')
        def rel(p):return p.relative_to(ROOT.parent).as_posix()
        filters.append(f"[o{i}]drawbox=x=70:y=155:w=525:h=730:color=0x10203B:t=fill:enable='{enable}',drawbox=x=64:y=155:w=4:h=730:color=0x587DFF:t=fill:enable='{enable}',drawbox=x=630:y=940:w=1250:h=2:color=0x5475AD:t=fill:enable='{enable}',drawtext=fontfile={font}:textfile={rel(heading)}:x=65:y=58:fontsize=44:fontcolor=0xEAF2FF:enable='{enable}',drawtext=fontfile={font}:textfile={rel(label)}:x=100:y=310:fontsize=78:fontcolor=0xEAF2FF:alpha='min(1,max(0,(t-{a})/0.35))':enable='{enable}',drawtext=fontfile={font}:textfile={rel(label2)}:x=100:y=405:fontsize=78:fontcolor=0x9DBAFF:enable='{enable}',drawtext=fontfile={mono}:textfile={rel(note)}:x=104:y=600:fontsize=20:line_spacing=10:fontcolor=0xAFC5F7:enable='{enable}',drawtext=fontfile={mono}:text='FOCUS / {i+1:02}':x=104:y=200:fontsize=20:fontcolor=0x8BACFF:enable='{enable}'[v{i}]")
        last=f'v{i}'
    filters.append('[0:a][1:a]amix=inputs=2:duration=first:normalize=0[a]')
    graph=local/'filter.txt';graph.write_text(';\n'.join(filters),encoding='utf-8')
    tmp=out.with_suffix('.building.mp4')
    cmd=['ffmpeg','-hide_banner','-loglevel','error','-y','-threads','2','-i',str(source),'-i',str(local/'transitions.wav'),'-filter_complex_threads','2','-filter_complex_script',str(graph),'-map',f'[{last}]','-map','[a]','-t',str(duration),'-c:v','libx264','-preset','veryfast','-crf','18','-threads','4','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-movflags','+faststart',str(tmp)]
    (O/f'{eid}-direction.json').write_text(json.dumps({'source':str(source.relative_to(ROOT)),'shots':shots,'captionPolicy':'Original caption band remains fixed and uncropped.','sound':'Low-level synthesized editorial transition cues; original narration retained.'},indent=2))
    print(json.dumps({'episode':eid,'stage':'rendering','focusShots':len(shots)}),flush=True)
    subprocess.run(cmd,check=True);tmp.replace(out)
    probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(out)]))
    assert abs(float(probe['format']['duration'])-duration)<.3
    report={'episode':eid,'duration':float(probe['format']['duration']),'sha256':hashlib.file_digest(out.open('rb'),'sha256').hexdigest(),'focusShots':len(shots),'visualReview':'pending'}
    out.with_suffix('.json').write_text(json.dumps(report,indent=2));print(json.dumps({'episode':eid,'stage':'exported'}),flush=True)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--episode',default='showcase');a=p.parse_args()
    for eid in (['showcase']+[f'{n:02}' for n in range(1,13)] if a.episode=='all' else [a.episode]):make(eid)
