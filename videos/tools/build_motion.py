"""Build the Hyperframes motion edition. Original recordings stay untouched."""
from pathlib import Path
import argparse, base64, html, json, shutil, subprocess, math
from prepare_motion import REPLACEMENTS

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'motion'
def esc(s): return html.escape(str(s), quote=True)
def english(s):
    for a,b in REPLACEMENTS.items(): s=s.replace(a,b)
    return s

CSS = '''
@font-face{font-family:Sans;src:url('assets/SourceSans3.ttf');font-weight:200 900}
@font-face{font-family:Mono;src:url('assets/JetBrainsMono.ttf');font-weight:100 900}
*{box-sizing:border-box}html,body{margin:0;width:1920px;height:1080px;background:#080F22;color:#EEF3FF;font-family:Sans}
#movie{position:relative;width:1920px;height:1080px}.scene{position:absolute;inset:0;overflow:hidden;background:radial-gradient(ellipse at 80% 15%,#1D3563 0%,#0E1933 45%,#080F22 85%)}
.grid{position:absolute;inset:0;background-image:linear-gradient(#52699518 1px,transparent 1px),linear-gradient(90deg,#52699518 1px,transparent 1px);background-size:70px 70px;transform:perspective(750px) rotateX(22deg) scale(1.4);opacity:.5}
.orb{position:absolute;width:650px;height:650px;right:-180px;top:-320px;border:1px solid #6386CE55;border-radius:50%;box-shadow:0 0 0 65px #2457E608,0 0 0 130px #6386CE15,0 0 0 195px #2457E608}
.brand{position:absolute;left:64px;top:38px;font-size:20px;font-weight:750;letter-spacing:4px;color:#9FBBF4}
.chapter{position:absolute;right:64px;top:32px;font:22px Mono;padding:10px 20px;border:1px solid #526995;border-radius:30px}
.heading{position:absolute;top:84px;left:64px;right:64px;font-size:49px;line-height:1.04;margin:0;font-weight:700;letter-spacing:-1px}
.rail{position:absolute;left:64px;top:173px;width:570px;height:712px;border:1px solid #526995;border-radius:20px;background:#0B1429;overflow:hidden;box-shadow:0 25px 80px #0007}
.bar{height:54px;background:#182A4A;border-bottom:1px solid #526995;padding:16px 22px;font-size:18px;color:#AFC6F2;letter-spacing:1px}
.bar::before{content:'● ● ●';color:#7995C8;letter-spacing:3px;margin-right:25px}
.code{padding:25px 20px;font:21px/1.38 Mono;white-space:pre-wrap;overflow-wrap:anywhere;color:#DCE8FF}
.line{position:relative;padding:4px 8px 4px 38px;border-left:3px solid transparent;min-height:30px;transform-origin:left}
.ln{position:absolute;left:5px;top:7px;width:26px;color:#728BB7;font-size:13px;user-select:none}
.comment{color:#91ACDB}.kw{color:#9AB9FF}.typing{display:inline}
.stage{position:absolute;left:670px;top:173px;width:1186px;height:712px;background:#111F3A;border:1px solid #526995;border-radius:20px;overflow:hidden;box-shadow:0 30px 90px #0007}
.stage .bar{background:#20365C}.browser-well{position:absolute;left:0;top:54px;width:1186px;height:658px;background:#F4F7FC}
.browser-caption{position:absolute;left:27px;top:19px;color:#14213D;font-size:24px;font-weight:700}
.browser-placeholder{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;font-size:40px;color:#2457E6}
.foot{position:absolute;left:64px;right:64px;top:908px;display:flex;align-items:center;gap:24px;font-size:22px;color:#AFC6F2}
.phase{padding:9px 18px;background:#20365C;border-radius:9px;font-size:18px;letter-spacing:2px;color:#DCE8FF}.track{flex:1;height:3px;background:#34496F}.fill{height:3px;background:#93B3FF;width:100%;transform-origin:left}
.caption{position:absolute;left:64px;right:64px;bottom:26px;min-height:73px;padding:14px 26px;background:#080F22EE;border-top:1px solid #526995;color:#EEF3FF;font-size:31px;line-height:1.16;text-align:center;display:flex;align-items:center;justify-content:center}
.node{position:absolute;width:245px;height:145px;border:1px solid #6288D4;border-radius:18px;background:#182D51;padding:24px;box-shadow:0 20px 30px #0003;font-size:28px;font-weight:650}
.node small{display:block;font:15px Mono;color:#AFC6F2;letter-spacing:1px;margin-bottom:17px}.wire{position:absolute;background:#537ABB;height:3px;transform-origin:left}
.packet{position:absolute;width:17px;height:17px;background:#C2D6FF;border:3px solid #2457E6;box-shadow:0 0 18px #90ADFF;border-radius:50%}
.insight{position:absolute;left:44px;right:44px;bottom:38px;padding:24px 28px;border-left:4px solid #8DADFF;font-size:31px;line-height:1.18;background:#142743}
.board{position:absolute;inset:85px 38px 125px;display:grid;grid-template-columns:1fr 1fr;gap:22px}.tile{padding:28px;background:#182D51;border:1px solid #526995;border-radius:18px;font-size:30px;line-height:1.2}.tile b{display:block;font:17px Mono;color:#AFC6F2;margin-bottom:23px}
.hero{position:absolute;left:62px;top:115px;font-size:155px;font-weight:760;line-height:.93;letter-spacing:-7px}.hero span{color:#9CBFFF}.hero-sub{position:absolute;left:64px;right:64px;top:435px;font-size:33px;line-height:1.25;color:#BCD0F6}
.terminal{position:absolute;left:32px;right:32px;top:85px;bottom:32px;padding:26px;background:#080F22;border-left:4px solid #6288D4;font:23px/1.55 Mono;white-space:pre-wrap;overflow-wrap:anywhere}
.focus{position:absolute;inset:6px;border:2px solid #C2D6FF;border-radius:14px;pointer-events:none}
.promptbox{position:absolute;left:46px;right:46px;top:112px;min-height:385px;background:#0B1429;border:1px solid #6C91D7;border-radius:24px;padding:36px;font:29px/1.45 Mono;box-shadow:0 20px 65px #0004}
.promptword{display:inline}.prompt-tag{position:absolute;left:46px;top:70px;color:#AFC6F2;letter-spacing:3px;font-size:19px}.prompt-send{position:absolute;right:48px;bottom:143px;padding:14px 25px;border-radius:12px;background:#2457E6;color:white;font-size:23px}.terminal-row{min-height:30px}
.workbench .rail{width:1000px}.workbench .stage{left:1100px;width:756px}.workbench .terminal{font-size:20px;line-height:1.35}.workbench .terminal-row{min-height:27px}.fullstage .rail{display:none}.fullstage .stage{left:64px;width:1792px}.fullstage .terminal{font-size:29px;line-height:1.35}.fullstage .hero{font-size:155px;left:90px}.fullstage .hero-sub{left:90px;right:90px}.workbench .code{font-size:23px!important;line-height:1.38}.fullstage .insight{font-size:26px}.activity{position:absolute;left:64px;right:64px;top:120px;display:flex;align-items:center;justify-content:space-between;gap:50px;visibility:hidden}.activity-node{flex:1;padding:40px 35px;border:1px solid #638CD2;border-radius:20px;background:#172E53;font-size:48px}.activity-arrow{font-size:55px;color:#AFC9FF}.activity-note{position:absolute;left:75px;right:75px;bottom:60px;visibility:hidden;font:26px Mono;color:#BCD3FF}
'''

def scene_markup(ep, sc, index):
    sid='m'+sc['id'].replace('-',''); duration=sc['duration']
    code=english(sc.get('code',''))
    bullets=[english(x) for x in sc.get('bullets',[])][:4]
    live_map={'02':{1:'success',5:'success',6:'insufficient'},'03':{5:'success'},'04':{5:'success'},'05':{3:'success'},'06':{3:'success'},'07':{4:'unavailable'},'11':{2:'success'},'12':{3:'success'}}
    live=live_map.get(ep['id'],{}).get(index)
    if live and ep['id'] in ('02','12'):
        code="await page.goto('/transfers');\nawait page.getByLabel('Source account')\n  .selectOption(lab.sourceAccountId);\nawait page.getByLabel('Amount (MXN)')\n  .fill('100.00');\nawait page.getByRole('button',\n  {name:'Transfer', exact:true}).click();\nawait expect(page.getByTestId(\n  'account-balance'))\n  .toHaveText('MXN 900.00');"
        if live=='insufficient':code=code.replace("fill('100.00')","fill('1100.00')").replace('MXN 900.00','MXN 1000.00')
    lines=code.splitlines() if code else ['// '+x for x in bullets]
    if not lines: lines=['// Observe the business outcome.']
    size=22
    while size>16 and sum(max(1,math.ceil(len(line)/((570-86)/(size*.61)))) for line in lines)*(size*1.38+8)>590:
        size-=1
    source=''.join(f'<div class="line" id="{sid}-l{i}"><span class="ln">{i+1:02}</span><span class="typing">{esc(line)}</span></div>' for i,line in enumerate(lines))
    diagram=sc.get('diagram') or []
    if not code and any(word in sc['title'].lower() for word in ('system map','architecture','ownership','boundaries','fixture graph','lifecycle','projection','processes')):
        diagram=['Browser / test context','Gateway / session','Accounts / canonical state','Ledger / projection']
    if isinstance(diagram,dict): diagram=list(diagram.values())
    nodes=[str(x) for x in diagram][:4] or ['Browser','Gateway','Accounts','Ledger']
    script=[]
    if live:
        right='<div class="bar">LOCAL CAPTURE / TRANSFERLAB</div><div class="browser-well"><div class="browser-placeholder">Recorded application run</div></div>'
    elif ep['id'] in ('09','10','11') and index in (6,7,8,9):
        raw=(OUT/'captures/terminal-success.txt').read_text(encoding='utf-8')
        wanted=('STATUS','REFERENCE','AMOUNT MINOR','CURRENCY','SOURCE','BALANCE MINOR')
        rows=[line.strip() for line in raw.split('STEP: lookup-result')[-1].splitlines() if line.strip().startswith(wanted)]
        right='<div class="bar">TNZ / RECORDED LOCAL SIMULATOR / SUCCESSFUL LOOKUP</div><div class="terminal">'
        for j,row in enumerate(['TRAINING LEDGER / TN3270','',*rows,'','Exact reference. Integer minor units.','Local simulator; no z/OS or CICS.']):
            right+=f'<div class="terminal-row" id="{sid}-tr{j}">{esc(row) or " "}</div>'
            script.append(f"tl.fromTo('#{sid}-tr{j}',{{clipPath:'inset(0 100% 0 0)'}},{{clipPath:'inset(0 0% 0 0)',duration:1.2,ease:'none'}},{2+j*1.8});")
        right+='</div>'
    elif (ep['id']=='12' and index in (1,2,5,6,7)) or ('AI' in sc['title']):
        prompt={1:'Inspect the real application contract. Map routes, roles and business invariants. Cite the source of every finding. Mark missing evidence as unconfirmed.',2:'Build a risk-based regression matrix. Link requirements to tests and observable outcomes. Separate designed, automated, executed and passed coverage.',5:'Extend the local transfer test through the TNZ adapter. Reconcile the exact reference, amount and balance. Bound the wait and clean up owned data.',6:'Review this test for weak assertions, hidden coupling and fabricated evidence. Propose the smallest correction. Do not remove the business oracle.',7:'Analyze this failure using its request, response and trace. Separate application defects, test defects and environment problems. Preserve the failing evidence.'}.get(index,'Inspect the complete case and its evidence. Preserve fixture ownership, exact transaction identity and the monetary oracle. Explain every proposed change before applying it.')
        words=prompt.split(' ')
        typed=''.join(f'<span class="promptword" id="{sid}-pw{j}">{esc(word)} </span>' for j,word in enumerate(words))
        right=f'<div class="bar">PROMPT WORKSHOP / COPYABLE TEACHING INPUT</div><div class="prompt-tag">CONTEXT → TASK → CONSTRAINTS → EVIDENCE</div><div class="promptbox">{typed}</div><div class="prompt-send">Review the proposed patch →</div><div class="insight">The assistant proposes. Execution provides evidence.</div>'
        for j in range(len(words)):
            script.append(f"tl.fromTo('#{sid}-pw{j}',{{opacity:0}},{{opacity:1,duration:.1}},{2+j*.24:.3f});")
        script.append(f"tl.fromTo('#{sid} .prompt-send',{{scale:.88,opacity:0}},{{scale:1,opacity:1,duration:.5,ease:'back.out(1.5)'}},{min(duration-3,3+len(words)*.24):.3f});")
    elif index==0:
        words={'01':('ONE ACTION.','THREE SERVICES.'),'02':('WRITE. RUN.','PROVE IT.'),'03':('ISOLATE.','THEN ASSERT.'),'04':('LIFECYCLE.','UNDER CONTROL.'),'05':('YOUR TEST.','YOUR DATA.'),'06':('FOLLOW','THE EXACT ID.'),'07':('CONTROL','THE FAILURE.'),'08':('REWIND.','FIND THE CAUSE.'),'09':('BROWSER','MEETS TERMINAL.'),'10':('FIELDS.','WAITS. CLEANUP.'),'11':('ONE ID.','TWO PROTOCOLS.'),'12':('FROM PROMPT','TO EVIDENCE.')}
        a,b=words[ep['id']]
        hero_size=min(155,1750/max(len(a),len(b)))
        right=f'<div class="bar">MISSION {ep["id"]} / ENGINEERING THE OUTCOME</div><div class="hero" style="font-size:{hero_size}px">{esc(a)}<br><span>{esc(b)}</span></div><div class="hero-sub">{esc(ep.get("summary",""))}</div>'
        script += [f"tl.fromTo('#{sid} .hero',{{x:80,opacity:0,scale:.9}},{{x:0,opacity:1,scale:1,duration:1.2,ease:'power4.out'}},1);",f"tl.fromTo('#{sid} .hero-sub',{{y:35,opacity:0}},{{y:0,opacity:1,duration:.7}},3);"]
        right+='<div class="activity"><div class="activity-node">Browser<br>Observe</div><div class="activity-arrow">→</div><div class="activity-node">API<br>Verify</div><div class="activity-arrow">→</div><div class="activity-node">Terminal<br>Reconcile</div></div><div class="activity-note">ONE WORKFLOW / EXPLICIT BOUNDARIES / OBSERVABLE OUTCOMES</div>'
        script.extend([f"tl.to('#{sid} .hero, #{sid} .hero-sub',{{y:-50,opacity:0,duration:.5}},7);",f"tl.set('#{sid} .activity',{{visibility:'visible'}},7.6);",f"tl.fromTo('#{sid} .activity-node',{{x:60,opacity:0}},{{x:0,opacity:1,stagger:1.2,duration:.7,ease:'power3.out'}},7.6);",f"tl.fromTo('#{sid} .activity-arrow',{{opacity:0,scaleX:0}},{{opacity:1,scaleX:1,stagger:1.2,duration:.7}},9);",f"tl.set('#{sid} .activity-note',{{visibility:'visible'}},14);",f"tl.fromTo('#{sid} .activity-note',{{y:35,opacity:0}},{{y:0,opacity:1,duration:.6}},14);"])
    elif diagram or sc.get('type')=='diagram':
        coords=[(60,130),(635,130),(635,330),(60,330)]
        right='<div class="bar">REQUEST PATH / CONCEPTUAL ANIMATION</div>'
        for i,n in enumerate(nodes):
            x,y=coords[i]
            right+=f'<div id="{sid}-n{i}" class="node" style="left:{x}px;top:{y}px;width:420px"><small>BOUNDARY {i+1:02}</small>{esc(n)}</div>'
            at=1+i*max(2,(duration-8)/len(nodes))
            script.append(f"tl.fromTo('#{sid}-n{i}',{{y:30,opacity:.2}},{{y:0,opacity:1,borderColor:'#B8CFFF',duration:.6}}, {at:.3f});")
        right+='<div class="wire" style="left:480px;top:201px;width:155px"></div><div class="wire" style="left:845px;top:275px;width:55px;transform:rotate(90deg)"></div><div class="wire" style="left:480px;top:403px;width:155px"></div>'
        right+=f'<div id="{sid}-packet" class="packet" style="left:475px;top:194px"></div><div class="insight">{esc(bullets[0] if bullets else "Follow the same identity across every boundary.")}</div>'
        script+=[f"tl.to('#{sid}-packet',{{x:160,duration:2,ease:'none'}},3);",f"tl.to('#{sid}-packet',{{x:362,y:135,duration:2}},7);",f"tl.to('#{sid}-packet',{{x:0,y:203,duration:2}},12);"]
    else:
        title=sc['title'].lower()
        if ep['id']=='08' and index<7:
            rows=json.loads((OUT/'captures/workbench.json').read_text())['defect'];label='RECORDED TEST OUTPUT / INTENTIONAL DEFECT'
        elif any(w in title for w in ('run','report','result','trace','prepare','environment','readiness','project','execute','preparation')):
            lang='java' if ep['id']=='04' or 'java' in title or 'mvn ' in code.lower() else 'python' if ep['id']=='03' or 'python' in title or 'python' in code.lower() or 'pytest' in code.lower() or ep['id'] in ('09','10') else 'typescript'
            rows=json.loads((OUT/'captures/workbench.json').read_text())[lang];label=f'RECORDED {lang.upper()} RUN / HEALTHY LAB'
            rows=[row if len(row)<45 else row[:42]+'…' for row in rows]
        else:
            scenario='unavailable' if ep['id']=='07' else 'insufficient' if any(w in title for w in ('insufficient','reject')) else 'success'
            record=json.loads((OUT/'captures'/f'events-{scenario}.json').read_text())
            observation={'response':record['result'],'balanceMinor':record['balanceMinor'],'canonicalRecords':record['transferCount']}
            rows=json.dumps(observation,indent=2).splitlines();label='INSPECTOR / CAPTURED BUSINESS OBSERVATIONS'
        right=f'<div class="bar">{label}</div><div class="terminal">'
        for j,row in enumerate(rows):
            right+=f'<div class="terminal-row" id="{sid}-obs{j}">{esc(row) or " "}</div>'
            at=1+j*min(1.25,(duration*.55)/max(1,len(rows)))
            script.append(f"tl.fromTo('#{sid}-obs{j}',{{clipPath:'inset(0 100% 0 0)'}},{{clipPath:'inset(0 0% 0 0)',duration:.65,ease:'none'}},{at:.3f});")
        right+='</div>'
    for i,line in enumerate(lines):
        at=1+i*min(1.5,(duration*.45)/max(1,len(lines)))
        script += [f"tl.fromTo('#{sid}-l{i}',{{clipPath:'inset(0 100% 0 0)'}},{{clipPath:'inset(0 0% 0 0)',duration:{min(1.3,max(.3,len(line)/50)):.3f},ease:'none'}},{at:.3f});"]
    selected=sc.get('highlight_lines') or [1,min(len(lines),3),len(lines)]
    if live and ep['id'] in ('02','12'):
        selected=[]
        events=json.loads((OUT/'captures'/f'events-{live}.json').read_text())['events']
        for event_index,line_numbers in [(0,[0]),(1,[1,2]),(3,[3,4]),(4,[5,6]),(5,[7,8,9])]:
            at=1.5+events[event_index]['time']
            for ln in line_numbers:
                script.append(f"tl.to('#{sid}-l{ln}',{{backgroundColor:'#203C68',borderColor:'#AFC9FF',duration:.2}},{at:.3f});")
                script.append(f"tl.to('#{sid}-l{ln}',{{backgroundColor:'#0B1429',borderColor:'transparent',duration:.2}},{min(duration-.5,at+2):.3f});")
    for j,ln in enumerate(selected):
        if not isinstance(ln,int) or not 1<=ln<=len(lines): continue
        at=duration*.52+j*max(1,(duration*.4)/max(1,len(selected)))
        script += [f"tl.to('#{sid}-l{ln-1}',{{backgroundColor:'#203C68',borderColor:'#AFC9FF',duration:.3}},{at:.3f});"]
    script += [f"tl.fromTo('#{sid} .heading',{{y:25,opacity:0}},{{y:0,opacity:1,duration:.65,ease:'power3.out'}},.15);",f"tl.fromTo('#{sid} .rail',{{x:-60,opacity:0}},{{x:0,opacity:1,duration:.7,ease:'power3.out'}},.35);",f"tl.fromTo('#{sid} .stage',{{x:90,opacity:0}},{{x:0,opacity:1,duration:.8,ease:'power3.out'}},.45);",f"tl.fromTo('#{sid} .fill',{{scaleX:0}},{{scaleX:1,duration:.5,ease:'power2.out'}},{duration-1});",f"tl.to('#{sid} .orb',{{rotation:30,x:-35,duration:4,ease:'power2.out'}},0);"]
    special=('PROMPT WORKSHOP' in right or 'RECORDED LOCAL SIMULATOR' in right or bool(diagram))
    layout='fullstage' if not code and not live and not diagram else 'workbench' if code and not live and not special else ''
    markup=f'<section class="scene {layout}" id="{sid}"><div class="grid"></div><div class="orb"></div><div class="brand">PLAYWRIGHT / FIELD OPERATIONS</div><div class="chapter">{ep["id"]} · {index+1:02}/12</div><h1 class="heading">{esc(english(sc["title"]))}</h1><div class="rail"><div class="bar">{esc(sc.get("code_language","text").upper())} / WALKTHROUGH</div><div class="code" style="font-size:{size}px">{source}</div></div><div class="stage">{right}</div><div class="foot"><span class="phase">OBSERVE → EXECUTE → VERIFY</span><div class="track"><div class="fill"></div></div><span>{esc(ep["id"])} / MOTION EDITION</span></div></section>'
    return sid,markup,script,live

def build(eid, preview=False):
    timeline=OUT/'audio'/eid/'timeline.json'
    if not timeline.exists(): timeline=ROOT/'audio'/eid/'timeline.json'
    ep=json.loads(timeline.read_text(encoding='utf-8-sig'))
    project=OUT/'compositions'/eid
    if preview: project=OUT/'compositions'/'preview'
    assets=project/'assets'; assets.mkdir(parents=True,exist_ok=True)
    for name in ('gsap.min.js','SourceSans3.ttf','JetBrainsMono.ttf','SourceSans3-LICENSE.txt','JetBrainsMono-LICENSE.txt'):
        shutil.copy2(ROOT/'assets'/name,assets/name)
    duration=ep['duration'] if not preview else ep['scenes'][0]['duration']+ep['scenes'][1]['duration']
    scenes=ep['scenes'] if not preview else ep['scenes'][:2]
    mounts=[]; animations=[]; overlays=[]
    for i,sc in enumerate(scenes):
        sid,markup,scripts,live=scene_markup(ep,sc,i)
        mounts.append(markup)
        animations.append(f"tl.set('#{sid}',{{display:'none'}},0);tl.set('#{sid}',{{display:'block'}},{sc['start']});tl.set('#{sid}',{{display:'none'}},{sc['start']+sc['duration']});")
        animations.append('{ const tl=gsap.timeline();'+''.join(scripts)+f"master.add(tl,{sc['start']});"+'}')
        if live: overlays.append({'scene':sc['id'],'start':sc['start']+1.5,'duration':sc['duration']-1.5,'capture':live,'x':671,'y':228,'width':1184,'height':656})
    caption_html=[]
    for i,cue in enumerate(ep['captions']):
        if cue['start']>=duration:break
        caption_html.append(f'<div class="caption" id="cue{i}" style="visibility:hidden">{esc(cue["text"])}</div>')
        animations.append(f"tl.set('#cue{i}',{{visibility:'visible'}},{cue['start']});tl.set('#cue{i}',{{visibility:'hidden'}},{min(duration,cue['end'])});")
    shutil.copy2(timeline.parent/'narration.wav',assets/'narration.wav')
    page=f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>{esc(ep["title"])}</title><script src="assets/gsap.min.js"></script><style>{CSS}</style></head><body><div id="movie" data-composition-id="movie" data-width="1920" data-height="1080" data-duration="{duration}">{"".join(mounts)}{"".join(caption_html)}<audio id="narration" src="assets/narration.wav" data-start="0" data-duration="{duration}" data-track-index="30"></audio></div><script>const master=gsap.timeline({{paused:true}});const tl=master;{"".join(animations)}window.__timelines.movie=master;</script></body></html>'
    (project/'index.html').write_text(page,encoding='utf-8')
    (project/'hyperframes.json').write_text(json.dumps({'name':f'motion-{eid}','entry':'index.html'}),encoding='utf-8')
    (project/'meta.json').write_text(json.dumps({'name':ep['title'],'duration':duration,'width':1920,'height':1080}),encoding='utf-8')
    (project/'edit.json').write_text(json.dumps({'episode':eid,'duration':duration,'overlays':overlays,'sourceNarration':str(timeline.relative_to(ROOT))},indent=2),encoding='utf-8')
    print(json.dumps({'project':str(project),'duration':duration,'overlays':len(overlays)}))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--episode');ap.add_argument('--preview',action='store_true');args=ap.parse_args()
    for eid in ([args.episode] if args.episode else [f'{i:02}' for i in range(1,13)]):build(eid,args.preview)
