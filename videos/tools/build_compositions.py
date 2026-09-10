from __future__ import annotations
import argparse, html, json, shutil
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
W,H=1920,1080

EVIDENCE_SCENES={'02-06','11-10'}
def esc(value):return html.escape(str(value),quote=True)

def scene_html(ep,sc,index,total):
    cid='s'+sc['id'].replace('-','');duration=sc['duration'];kind=sc.get('type','steps')
    bullets=sc.get('bullets',[])[:4]
    code=sc.get('code','')
    if sc['id'] in EVIDENCE_SCENES:
        code=''
        kind='evidence'
        if sc['id']=='11-10':
            raw=(ROOT/'lab/mainframe/evidence/hybrid-python-terminal.txt').read_text(encoding='utf-8')
            result=raw.split('STEP: lookup-result')[-1]
            wanted=('STATUS','REFERENCE','AMOUNT MINOR','CURRENCY','SOURCE','BALANCE MINOR')
            rows=[line.strip() for line in result.splitlines() if line.strip().startswith(wanted)]
            detail='<div class="evidence-label">ACTUAL TNZ SCREEN · TRAINING SIMULATOR</div><pre class="terminal-proof">'+esc('\n\n'.join(rows))+'</pre>'
        else:
            detail='<div class="evidence-label">ACTUAL LOCAL BROWSER CAPTURE</div><div class="evidence-points">'+''.join(f'<div>{esc(b)}</div>' for b in bullets)+'</div><p class="evidence-note">Pair the visible receipt with the authenticated API record and its exact transfer ID.</p>'
        content=f'<div class="evidence-grid"><img class="evidence-image" src="assets/evidence-{sc["id"]}.png" alt="Actual local Playwright browser evidence"><div class="evidence-detail">{detail}</div></div>'
    elif code:
        lines=code.splitlines();maxlen=max([len(x) for x in lines]+[1]);size=min(31,max(24,round(1480/(maxlen*.61),1)), round(390 / max(1,len(lines)) / 1.30,1))
        rendered=[]
        for i,line in enumerate(lines):
            style='comment' if line.strip().startswith(('#','//')) else ''
            rendered.append(f'<div id="{cid}-line-{i+1}" class="code-line {style}"><span class="line-no">{i+1:02}</span><span>{esc(line) or " "}</span></div>')
        content=f'<div class="code-label">{esc(sc.get("code_language","text"))} · {esc(sc.get("footer","Focused teaching excerpt"))}</div><div class="code-panel" style="font-size:{size}px">'+''.join(rendered)+'</div>'
        support=' '.join(bullets[:2])
        content+=f'<div class="support">{esc(support)}</div>'
    elif kind=='diagram' or sc.get('diagram'):
        nodes=sc.get('diagram') or bullets
        if isinstance(nodes,dict):nodes=list(nodes.values())
        nodes=[str(x) for x in nodes][:5]
        boxes=[]
        for i,label in enumerate(nodes):
            if i:boxes.append('<div class="arrow">→</div>')
            boxes.append(f'<div id="{cid}-node-{i}" class="node"><span class="node-number">{i+1:02}</span><div>{esc(label)}</div></div>')
        content='<div class="flow">'+''.join(boxes)+'</div><div class="takeaways">'+''.join(f'<div class="takeaway">{esc(x)}</div>' for x in bullets[:3])+'</div>'
    elif kind=='title':
        content=f'<div class="opener-number">{ep["id"]}</div><div class="opener-copy">'+''.join(f'<div class="opener-item">{esc(x)}</div>' for x in bullets)+'</div>'
    else:
        content='<div class="steps">'+''.join(f'<div id="{cid}-step-{i}" class="step"><div class="step-no">{i+1:02}</div><div>{esc(x)}</div></div>' for i,x in enumerate(bullets))+'</div>'
    title=sc['title'];title_size=64 if len(title)>62 else 72
    styles=f'''
@font-face{{font-family:CourseSans;src:url('assets/SourceSans3.ttf');font-weight:200 900}}@font-face{{font-family:CourseMono;src:url('assets/JetBrainsMono.ttf');font-weight:100 900}}
#{cid}{{position:relative;width:{W}px;height:{H}px;overflow:hidden;background:#F4F7FC;color:#14213D;font-family:CourseSans,sans-serif}}
#{cid}::before{{content:'';position:absolute;left:0;top:0;width:12px;height:930px;background:#2457E6}}
.chapter{{position:absolute;left:92px;top:51px;font-size:24px;letter-spacing:3px;font-weight:750;color:#14213D}}.chapter::before{{content:'';display:inline-block;width:15px;height:15px;margin-right:18px;border-radius:4px;background:#2457E6}}.episode-number{{position:absolute;right:92px;top:44px;font-size:23px;font-weight:700;letter-spacing:1px;padding:8px 18px;border:1px solid #D7DFED;border-radius:9px;background:#FFFFFF}}.rule{{position:absolute;left:92px;top:103px;width:1736px;height:2px;background:#D7DFED}}
.kicker{{position:absolute;left:92px;top:130px;font-size:23px;letter-spacing:1.8px;font-weight:700;color:#2457E6;background:#EAF0FF;border-radius:7px;padding:7px 16px}}.heading{{position:absolute;left:92px;top:193px;width:1732px;font-size:{title_size}px;line-height:1.09;letter-spacing:-1.5px;font-weight:730;margin:0}}
.content{{position:absolute;left:92px;top:340px;width:1736px;height:520px}}.code-label{{font-size:23px;letter-spacing:.8px;margin-bottom:15px;color:#56647A;font-weight:600}}.code-panel{{background:#111C34;color:#EEF3FF;padding:23px 24px;border:1px solid #283D67;border-left:6px solid #2457E6;border-radius:16px;font-family:CourseMono,monospace;font-variant-ligatures:none;line-height:1.3;white-space:pre;overflow:hidden;box-shadow:0 12px 28px #14213D12}}.code-line{{padding:0px 13px;border-radius:5px;display:flex;gap:24px}}.line-no{{color:#94A9D0;min-width:45px}}.comment{{color:#B7C7E8}}.support{{margin-top:20px;font-size:28px;color:#56647A;line-height:1.22;max-width:1660px}}
.flow{{display:flex;align-items:center;justify-content:center;gap:16px;margin-top:58px}}.node{{background:#FFFFFF;border:2px solid #D7DFED;border-radius:18px;flex:1;min-width:0;box-sizing:border-box;min-height:215px;padding:25px 20px;font-size:30px;line-height:1.12;display:flex;flex-direction:column;gap:22px;justify-content:center;box-shadow:0 10px 24px #14213D0A}}.node-number{{font-size:21px;font-weight:700;letter-spacing:1px;color:#2457E6;border-bottom:3px solid #2457E6;padding-bottom:9px;align-self:flex-start}}.arrow{{font-size:42px;color:#2457E6;flex:0 0 36px;text-align:center}}.takeaways{{display:flex;gap:35px;margin-top:65px}}.takeaway{{font-size:29px;line-height:1.25;flex:1;padding-top:18px;border-top:2px solid #D7DFED;color:#56647A}}
.steps{{display:grid;gap:16px;max-width:1710px}}.step{{display:flex;align-items:center;gap:30px;font-size:36px;line-height:1.2;padding:20px 26px;border:1px solid #D7DFED;border-radius:15px;min-height:112px;box-sizing:border-box;background:#FFFFFF;box-shadow:0 6px 18px #14213D06}}.step-no{{font-size:26px;font-weight:700;color:#2457E6;width:58px;height:58px;display:flex;align-items:center;justify-content:center;border-radius:12px;background:#EAF0FF;flex-shrink:0}}.opener-number{{position:absolute;left:0;top:12px;width:418px;height:386px;display:flex;align-items:center;justify-content:center;font-size:280px;font-weight:720;line-height:1;color:#FFFFFF;background:#2457E6;border-radius:28px;letter-spacing:-16px;box-shadow:0 18px 35px #2457E620}}.opener-copy{{position:absolute;left:500px;top:28px;right:0;display:grid;gap:27px}}.opener-item{{font-size:39px;line-height:1.18;padding:0 0 20px 22px;border-left:4px solid #2457E6;border-bottom:1px solid #D7DFED}}
.footer{{position:absolute;left:94px;top:882px;font-size:22px;color:#56647A;max-width:1490px;white-space:nowrap;overflow:hidden}}.counter{{position:absolute;right:92px;top:880px;font-size:23px;font-weight:650;color:#2457E6}}.progress{{position:absolute;left:0;top:922px;width:1920px;height:4px;background:#2457E6;transform-origin:left center}}'''
    styles+='''.evidence-grid{display:grid;grid-template-columns:700px 1fr;gap:48px;height:520px}.evidence-image{width:700px;height:520px;object-fit:contain;object-position:top;border-radius:16px;background:#111C34;box-shadow:0 10px 25px #14213D18}.evidence-label{font-size:22px;letter-spacing:1px;font-weight:700;color:#2457E6;margin-bottom:26px}.evidence-points{display:grid;gap:24px;font-size:35px;line-height:1.25}.evidence-points>div{padding-left:22px;border-left:4px solid #2457E6}.evidence-note{font-size:30px;line-height:1.3;color:#56647A;margin-top:42px}.terminal-proof{background:#111C34;color:#EEF3FF;font-family:CourseMono,monospace;font-variant-ligatures:none;font-size:23px;line-height:1.36;white-space:pre-wrap;padding:24px;border:1px solid #283D67;border-left:6px solid #2457E6;border-radius:16px;margin:0}'''
    animation=[f"tl.fromTo('#{cid} .heading',{{y:22,opacity:0}},{{y:0,opacity:1,duration:.45,ease:'power2.out'}},.1);",f"tl.fromTo('#{cid} .content',{{y:16,opacity:0}},{{y:0,opacity:1,duration:.4,ease:'power2.out'}},.25);",f"tl.fromTo('#{cid} .progress',{{scaleX:{index/total:.5f}}},{{scaleX:{(index+1)/total:.5f},duration:.6,ease:'power2.out'}},0);"]
    if code:
        selected=sc.get('highlight_lines') or list(range(1,min(len(code.splitlines()),4)+1))
        for i,ln in enumerate(selected):
            if not isinstance(ln,int) or ln<1 or ln>len(code.splitlines()):continue
            at=3+i*(duration-6)/max(1,len(selected));hold=max(2,(duration-6)/max(1,len(selected))-.3)
            animation.extend([f"tl.to('#{cid}-line-{ln}',{{backgroundColor:'#284679',duration:.25}}, {at:.5f});",f"tl.to('#{cid}-line-{ln}',{{backgroundColor:'#111C34',duration:.25}}, {min(duration-.5,at+hold):.5f});"])
    elif kind=='diagram' or sc.get('diagram'):
        for i in range(len(nodes)):
            at=2+i*(duration-5)/max(1,len(nodes));animation.append(f"tl.fromTo('#{cid}-node-{i}',{{y:0}},{{y:-12,backgroundColor:'#EAF0FF',duration:.4,ease:'power2.out'}}, {at:.5f});")
    elif kind not in ('title','evidence'):
        for i in range(len(bullets)):
            at=2+i*(duration-5)/max(1,len(bullets));animation.append(f"tl.to('#{cid}-step-{i}',{{color:'#2457E6',borderColor:'#9AB4F4',duration:.4,ease:'power2.out'}},{at:.5f});")
    return f'''<!doctype html><html lang="en"><body><template><style>{styles}</style><div id="{cid}" data-composition-id="{cid}" data-width="{W}" data-height="{H}" data-duration="{duration:.5f}"><div class="chapter">PLAYWRIGHT FIELD GUIDE</div><div class="episode-number">EPISODE {ep['id']} / 12</div><div class="rule"></div><div class="kicker">{esc(sc.get('kicker','STEP BY STEP').upper())}</div><h1 class="heading">{esc(title)}</h1><div class="content">{content}</div><div class="footer">{esc(sc.get('footer','Local training lab · Review the complete companion source'))}</div><div class="counter">{index+1:02} / {total:02}</div><div class="progress"></div></div><script>{{ const tl=gsap.timeline({{paused:true}});{''.join(animation)}window.__timelines['{cid}']=tl; }}</script></template></body></html>'''

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--episode');args=ap.parse_args()
    for timing in sorted((ROOT/'audio').glob('*/timeline.json')):
        ep=json.loads(timing.read_text(encoding='utf-8'));eid=ep['id']
        if args.episode and eid!=args.episode:continue
        project=ROOT/'compositions'/f'{eid}-{ep["slug"]}';frames=project/'compositions';assets=project/'assets';frames.mkdir(parents=True,exist_ok=True);assets.mkdir(exist_ok=True)
        for filename in ['gsap.min.js','SourceSans3.ttf','JetBrainsMono.ttf','SourceSans3-LICENSE.txt','JetBrainsMono-LICENSE.txt']:
            shutil.copy2(ROOT/'assets'/filename,assets/filename)
        for sc in ep['scenes']:
            if sc['id']=='02-06':
                origin=next((ROOT/'lab/distributed/evidence/test-results').glob('regression-TR-01-*/ui-success.png'))
                shutil.copy2(origin,assets/'evidence-02-06.png')
            if sc['id']=='11-10':
                shutil.copy2(ROOT/'lab/mainframe/evidence/hybrid-python-browser.png',assets/'evidence-11-10.png')
        shutil.copy2(timing.parent/'narration.wav',assets/'narration.wav')
        shutil.copy2(timing.parent/'subtitles.srt',project/'subtitles.srt')
        mounts=[];story=[]
        for index,scene in enumerate(ep['scenes']):
            cid='s'+scene['id'].replace('-','');(frames/f'{cid}.html').write_text(scene_html(ep,scene,index,len(ep['scenes'])),encoding='utf-8')
            mounts.append(f'<div id="{cid}" class="clip" data-composition-id="{cid}" data-composition-src="compositions/{cid}.html" data-start="{scene["start"]:.5f}" data-duration="{scene["duration"]:.5f}" data-track-index="0" data-width="1920" data-height="1080"></div>')
            story.append(f'## Frame {index+1}\n\nstatus: animated\nsrc: compositions/{cid}.html\nstart: {scene["start"]:.3f}\nduration: {scene["duration"]:.3f}\nmotion: dynamic-content-sequencing; stat-bars-and-fills; GSAP paint emphasis\n\n{scene["title"]}\n\n{scene["narration"]}\n')
        captions=[]
        for i,cue in enumerate(ep['captions']):
            captions.append(f'<div id="caption-{eid}-{i}" class="clip caption" data-start="{cue["start"]:.5f}" data-duration="{cue["end"]-cue["start"]:.5f}" data-track-index="20">{esc(cue["text"])}</div>')
        duration=ep['duration'];cid='episode'+eid
        index=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=1920,height=1080"><title>{esc(ep['title'])}</title><script src="assets/gsap.min.js"></script><style>@font-face{{font-family:CourseSans;src:url('assets/SourceSans3.ttf');font-weight:200 900}}@font-face{{font-family:CourseMono;src:url('assets/JetBrainsMono.ttf');font-weight:100 900}}html,body{{margin:0;width:1920px;height:1080px;background:#F4F7FC}}#{cid}{{position:relative;width:1920px;height:1080px;overflow:hidden;background:#F4F7FC}}.clip{{position:absolute;inset:0}}.caption{{inset:auto;left:0;top:930px;width:1920px;height:150px;box-sizing:border-box;padding:24px 100px;background:#111C34;color:#EEF3FF;display:flex;align-items:center;justify-content:center;text-align:center;font-family:CourseSans,sans-serif;font-size:34px;line-height:1.2;z-index:30}}.caption-bed{{position:absolute;left:0;top:930px;width:1920px;height:150px;background:#111C34;z-index:20}}</style></head><body><div id="{cid}" data-composition-id="{cid}" data-start="0" data-duration="{duration:.5f}" data-width="1920" data-height="1080">{''.join(mounts)}<div class="caption-bed"></div>{''.join(captions)}<audio id="narration-{eid}" class="clip" data-start="0" data-duration="{duration:.5f}" data-track-index="30" data-volume="1" src="assets/narration.wav"></audio></div><script>{{ const tl=gsap.timeline({{paused:true}});window.__timelines['{cid}']=tl; }}</script></body></html>'''
        (project/'index.html').write_text(index,encoding='utf-8')
        (project/'STORYBOARD.md').write_text(f'# Episode {eid}: {ep["title"]}\n\n'+ '\n'.join(story),encoding='utf-8')
        (project/'SCRIPT.md').write_text('\n\n'.join(s['narration'] for s in ep['scenes']),encoding='utf-8')
        (project/'hyperframes.json').write_text(json.dumps({'name':f'{eid}-{ep["slug"]}','entry':'index.html'},indent=2),encoding='utf-8')
        (project/'meta.json').write_text(json.dumps({'name':ep['title'],'description':ep.get('summary',''),'duration':duration,'width':1920,'height':1080},indent=2),encoding='utf-8')
        (project/'package.json').write_text(json.dumps({'name':f'playwright-episode-{eid}','private':True,'scripts':{'render':'npx hyperframes@0.8.33 render','check':'npx hyperframes@0.8.33 check'}},indent=2),encoding='utf-8')
        print(json.dumps({'episode':eid,'project':str(project),'duration':round(duration,2),'scenes':len(ep['scenes'])}),flush=True)

if __name__=='__main__':main()
