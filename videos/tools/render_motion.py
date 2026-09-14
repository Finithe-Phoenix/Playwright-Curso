"""Sequential, resumable motion-edition export with source fingerprints."""
from pathlib import Path
import argparse, hashlib, json, os, subprocess, sys, time
from build_motion import build, OUT
from finish_motion import run as finish

def digest(project):
    paths=sorted(p for p in project.rglob('*') if p.is_file())
    paths+=sorted((OUT/'captures').glob('*'))
    paths+=[Path(__file__),Path(__file__).with_name('finish_motion.py')]
    h=hashlib.sha256()
    for p in paths:
        h.update(p.name.encode());h.update(p.read_bytes())
    return h.hexdigest()

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--cli',type=Path,required=True);ap.add_argument('--episode');args=ap.parse_args()
    local=OUT/'local-results';local.mkdir(exist_ok=True)
    progress_path=OUT/'progress.json'
    progress=json.loads(progress_path.read_text()) if progress_path.exists() else {'episodes':{}}
    def status(eid,stage,**extra):
        progress['episodes'].setdefault(eid,{}).update(stage=stage,updatedAt=time.strftime('%Y-%m-%dT%H:%M:%S'),**extra)
        temp=progress_path.with_suffix('.tmp');temp.write_text(json.dumps(progress,indent=2));temp.replace(progress_path)
        print(json.dumps({'episode':eid,'stage':stage,**extra}),flush=True)
    env=os.environ.copy();env.update(HYPERFRAMES_BROWSER_PATH=r'C:\Program Files\Google\Chrome\Application\chrome.exe',
        HF_STATIC_DEDUP='true',HF_STATIC_DEDUP_VERIFY='true',HF_COURSE_STATIC_VERIFY_MAX_MS='90000',PRODUCER_LOW_MEMORY_MODE='true')
    for eid in ([args.episode] if args.episode else [f'{i:02}' for i in range(1,13)]):
        build(eid)
        project=OUT/'compositions'/eid
        fingerprint=digest(project)
        final=OUT/'renders'/f'{eid}-motion.mp4'
        if progress['episodes'].get(eid,{}).get('sourceHash')==fingerprint and final.exists() and progress['episodes'][eid].get('stage')=='exported':
            print(f'REUSED {eid}',flush=True);continue
        try:
            status(eid,'checking',sourceHash=fingerprint)
            edit=json.loads((project/'edit.json').read_text());duration=edit['duration']
            times=','.join(str(round(duration*(i+.5)/12,3)) for i in range(12))
            with (local/f'check-{eid}.json').open('w',encoding='utf-8') as log:
                subprocess.run(['node',str(args.cli),'check',str(project),'--json',f'--at={times}','--timeout=20000'],env=env,stdout=log,stderr=subprocess.STDOUT,timeout=180,check=True)
            # CLI can prepend a browser diagnostic before its structured report.
            raw=(local/f'check-{eid}.json').read_text();check=json.loads(raw[raw.index('{'):]);assert check['ok']
            status(eid,'rendering')
            with (local/f'render-{eid}.log').open('w',encoding='utf-8') as log:
                subprocess.run(['node',str(args.cli),'render',str(project),f'--output={local/f"{eid}-base.mp4"}',
                    '--fps=24','--quality=high','--workers=1','--low-memory-mode','--gpu','--quiet','--no-best-effort'],env=env,stdout=log,stderr=subprocess.STDOUT,timeout=1800,check=True)
            status(eid,'compositing')
            finish(project,local/f'{eid}-base.mp4',final)
            assert digest(project)==fingerprint,'Inputs changed during render'
            status(eid,'exported',output=str(final.relative_to(OUT)),duration=duration,visualReview='pending')
        except Exception as exc:
            status(eid,'failed',error=str(exc));raise
