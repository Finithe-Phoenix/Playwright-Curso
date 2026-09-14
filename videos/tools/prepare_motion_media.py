"""Promote verified local recordings and update the changed English narration scene."""
from pathlib import Path
import asyncio, base64, copy, json, shutil
import soundfile as sf
import numpy as np
from synthesize_edge import synthesize_scene, timestamp
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'motion'

def captures():
    report=json.loads((OUT/'local-results/capture-results.json').read_text())
    assert report['stats']['expected']==3 and report['stats']['unexpected']==0
    dest=OUT/'captures';dest.mkdir(exist_ok=True)
    for scenario in ('success','insufficient','unavailable'):
        folder=OUT/'local-results/capture'/f'record-record-{scenario}'
        shutil.copy2(folder/'video.webm',dest/f'browser-{scenario}.webm')
        shutil.copy2(folder/'final.png',dest/f'browser-{scenario}.png')
    shutil.copy2(OUT/'local-results/capture/record-record-success/terminal.txt',dest/'terminal-success.txt')
    def walk(suites):
        for suite in suites:
            for spec in suite.get('specs',[]):
                for test in spec.get('tests',[]):
                    for result in test.get('results',[]):
                        for attachment in result.get('attachments',[]):
                            if attachment['name'] in ('capture-events','terminal-result'):
                                data=json.loads(base64.b64decode(attachment['body']))
                                name=f"events-{data['scenario']}" if attachment['name']=='capture-events' else 'terminal-result'
                                (dest/f'{name}.json').write_text(json.dumps(data,indent=2),encoding='utf-8')
            yield from walk(suite.get('suites',[]))
    list(walk(report['suites']))
    (dest/'verification.json').write_text(json.dumps({'stats':report['stats'],'source':'recording/record.spec.ts',
        'environment':'Local synthetic services; browser 503 is intercepted, not a real service outage.',
        'captureHolds':'Editorial reading pauses; business assertions use Playwright waits.'},indent=2))

async def voice():
    folder=OUT/'audio/07';folder.mkdir(parents=True,exist_ok=True)
    ep=json.loads((ROOT/'audio/07/timeline.json').read_text(encoding='utf-8'))
    old=ep['scenes'][1];new=copy.deepcopy(old)
    new['narration']=old['narration'].replace('a documented Spanish message','a documented English message')
    meta=await synthesize_scene(new,folder,ep['voice'],ep['rate'])
    audio,rate=sf.read(ROOT/'audio/07/narration.wav',dtype='float32')
    replacement,replacement_rate=sf.read(folder/(new['id']+'.wav'),dtype='float32')
    assert rate==replacement_rate
    start=old['start'];end=start+old['duration'];delta=meta['duration']-old['duration']
    combined=np.concatenate([audio[:round(start*rate)],replacement,audio[round(end*rate):]])
    sf.write(folder/'narration.wav',combined,rate,subtype='PCM_16')
    new['duration']=meta['duration'];ep['scenes'][1]=new
    for sc in ep['scenes'][2:]:sc['start']+=delta
    ep['captions']=[c for c in ep['captions'] if c['end']<=start]+[{**c,'start':c['start']+start,'end':c['end']+start} for c in meta['cues']]+[{**c,'start':c['start']+delta,'end':c['end']+delta} for c in ep['captions'] if c['start']>=end]
    ep['duration']+=delta
    (folder/'timeline.json').write_text(json.dumps(ep,indent=2),encoding='utf-8')
    (folder/'subtitles.srt').write_text('\n\n'.join(f"{i+1}\n{timestamp(c['start'])} --> {timestamp(c['end'])}\n{c['text']}" for i,c in enumerate(ep['captions'])),encoding='utf-8')
    print(json.dumps({'episode':'07','updatedScene':new['id'],'duration':ep['duration']}))

if __name__=='__main__':
    captures()
    asyncio.run(voice())
