"""Composite actual local browser recordings over a Hyperframes motion render."""
from pathlib import Path
import argparse, hashlib, json, subprocess
ROOT=Path(__file__).resolve().parents[1]
MOTION=ROOT/'motion'

def run(project, base, output):
    edit=json.loads((project/'edit.json').read_text())
    command=['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(base)]
    filters=[]
    previous='0:v'
    for i,overlay in enumerate(edit['overlays'],1):
        capture=MOTION/'captures'/f'browser-{overlay["capture"]}.webm'
        command+=['-i',str(capture)]
        start,length=overlay['start'],overlay['duration']
        filters.append(f'[{i}:v]crop=1150:650:65:250,scale={overlay["width"]}:{overlay["height"]},setsar=1,tpad=stop_mode=clone:stop_duration={length},trim=duration={length},setpts=PTS-STARTPTS+{start}/TB[c{i}]')
        filters.append(f'[{previous}][c{i}]overlay=x={overlay["x"]}:y={overlay["y"]}:enable=\'between(t,{start},{start+length})\':eof_action=pass[v{i}]')
        previous=f'v{i}'
    output.parent.mkdir(parents=True,exist_ok=True)
    if filters:
        command+=['-filter_complex',';'.join(filters),'-map',f'[{previous}]']
    else: command+=['-map','0:v']
    command+=['-map','0:a','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-r','24','-c:a','copy','-t',str(edit['duration']),'-movflags','+faststart',str(output)]
    subprocess.run(command,check=True)
    probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(output)]))
    video=next(s for s in probe['streams'] if s['codec_type']=='video')
    audio=next(s for s in probe['streams'] if s['codec_type']=='audio')
    assert (video['width'],video['height'],video['codec_name'])==(1920,1080,'h264')
    assert abs(float(probe['format']['duration'])-edit['duration'])<.3
    record={'output':str(output.relative_to(ROOT)),'sha256':hashlib.file_digest(output.open('rb'),'sha256').hexdigest(),
            'duration':float(probe['format']['duration']),'width':1920,'height':1080,'audioCodec':audio['codec_name'],
            'actualBrowserCaptures':len(edit['overlays']),'visualReview':'pending'}
    output.with_suffix('.json').write_text(json.dumps(record,indent=2))
    print(json.dumps(record),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('episode');a=p.parse_args()
    run(MOTION/'compositions'/a.episode,MOTION/'local-results'/f'{a.episode}-base.mp4',MOTION/'renders'/f'{a.episode}-motion.mp4')
