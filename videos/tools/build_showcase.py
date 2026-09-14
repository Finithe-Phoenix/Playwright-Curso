"""Narrated cinematic walkthrough assembled from verified local captures."""
from pathlib import Path
import asyncio, html, json, shutil
import numpy as np
import soundfile as sf
from synthesize_edge import synthesize_scene, timestamp

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'motion';P=OUT/'compositions/showcase'
WORDS=[
('One transfer. Three services.', 'One transfer. Three services. One question: can you prove that the money moved exactly once?'),
('Write the contract', 'Start with a precise prompt. Ask for an isolated fixture, stable locators, and assertions against real business state. Review the proposed code before you execute it.'),
('Build the executable case', 'The code opens our local application. Every test owns a fresh source account and beneficiary. The test expresses a business promise, with an exact balance assertion.'),
('Watch the browser', 'Watch the browser select the account, enter one hundred pesos, and submit the transfer. This is a recorded run against the local application. The form responds with a reference, and the balance changes from one thousand to nine hundred pesos.'),
('Follow the request', 'Now follow the identity. The gateway accepts the command. The accounts service commits the debit and publishes an event. The independent ledger projection catches up afterward.'),
('Prove the business state', 'The balance is nine hundred pesos. One canonical record carries this exact reference. A visible success message alone is not enough. Verify both the identity and the effect.'),
('Cross the terminal boundary', 'Use the same reference at the terminal boundary. TNZ enters it into the local simulator, waits for the result, and verifies the amount and balance. Playwright controls the browser. TNZ controls the terminal.'),
('Keep each language native', 'Python and Java use the same business contract. Keep their fixture and lifecycle rules native to each runner. The same balance assertion must protect the same customer outcome.'),
('Control the failure', 'Now control a failure. This browser interception returns service unavailable. The form recovers and the account remains unchanged. That is a user interface experiment, not proof of a real backend outage.'),
('Read the actual evidence', 'Run the suites and inspect the evidence. Twenty-two checks passed in this local run, across TypeScript, Python, Java, and the terminal protocol. Keep reports connected to the cases they actually executed.'),
('From intention to evidence', 'From prompt, to code, to browser, to terminal. Keep one identity, clear boundaries, and assertions that can catch a real defect. That is the workflow you will build in this course.'),
]
def esc(x):return html.escape(str(x))

async def main():
    assets=P/'assets';assets.mkdir(parents=True,exist_ok=True)
    for name in ('gsap.min.js','SourceSans3.ttf','JetBrainsMono.ttf','SourceSans3-LICENSE.txt','JetBrainsMono-LICENSE.txt'):shutil.copy2(ROOT/'assets'/name,assets/name)
    audio_dir=OUT/'audio/showcase';audio_dir.mkdir(parents=True,exist_ok=True)
    scenes=[];cues=[];cursor=0.;audio=[]
    for i,(title,narration) in enumerate(WORDS):
        scene={'id':f'showcase-{i+1:02}','title':title,'narration':narration}
        meta=await synthesize_scene(scene,audio_dir,'en-US-JennyNeural','+0%')
        scene.update(start=cursor,duration=meta['duration']);scenes.append(scene)
        cues.extend({**c,'start':c['start']+cursor,'end':c['end']+cursor} for c in meta['cues'])
        segment,rate=sf.read(audio_dir/(scene['id']+'.wav'),dtype='float32');assert rate==24000;audio.append(segment);cursor+=meta['duration']
    sf.write(assets/'narration.wav',np.concatenate(audio),24000,subtype='PCM_16')
    proof=json.loads((OUT/'captures/terminal-result.json').read_text())
    ident=proof['reference']
    css='''@font-face{font-family:S;src:url('assets/SourceSans3.ttf');font-weight:200 900}@font-face{font-family:M;src:url('assets/JetBrainsMono.ttf')}*{box-sizing:border-box}html,body,#movie{margin:0;width:1920px;height:1080px;background:#070D1C;color:#F1F5FF;font-family:S;overflow:hidden}.shot{position:absolute;inset:0;background:radial-gradient(ellipse at 70% 20%,#234D8B,#0F1D38 45%,#070D1C 80%);overflow:hidden}.brand{position:absolute;left:72px;top:42px;font-size:22px;letter-spacing:4px;color:#B4CDFB}.idx{position:absolute;right:72px;top:35px;font:25px M;color:#AAC9FF}.title{position:absolute;left:72px;top:105px;margin:0;font-size:50px;letter-spacing:-1px}.word{position:absolute;left:65px;right:65px;top:315px;text-align:center;font-size:185px;font-weight:800;line-height:1;letter-spacing:-8px}.caption{position:absolute;left:65px;right:65px;bottom:20px;min-height:95px;display:flex;align-items:center;justify-content:center;text-align:center;font-size:32px;line-height:1.18;border-top:1px solid #6587C555;background:#070D1CEB;padding:20px 35px}.slash{position:absolute;width:2400px;height:160px;left:-2400px;top:450px;background:#2457E6;transform:rotate(-12deg)}.window{position:absolute;left:180px;right:180px;top:220px;height:635px;background:#0B152B;border:1px solid #7499DA;border-radius:22px;overflow:hidden;box-shadow:0 30px 90px #0008}.chrome{height:55px;padding:15px 26px;background:#233E68;color:#C2D7FF;font-size:20px;letter-spacing:2px}.prompt{padding:40px 55px;font:39px/1.45 M;color:#EDF4FF}.inputword{display:inline}.code{font:32px/1.52 M;white-space:pre-wrap;padding:35px 45px;margin:0}.codeline{padding:3px 12px;border-left:3px solid #638CD2;min-height:40px}.node{position:absolute;top:320px;width:460px;height:260px;border:1px solid #80A7EC;border-radius:24px;padding:42px;background:#172E53;font-size:58px;box-shadow:0 30px 70px #0007}.node small{display:block;font-size:25px;color:#AEC9F8;margin-top:15px}.packet{position:absolute;top:435px;left:548px;width:25px;height:25px;border-radius:50%;background:#D7E5FF;box-shadow:0 0 35px #8CAFFF}.path{position:absolute;top:447px;left:545px;height:3px;width:740px;background:#7499DA}.ref{position:absolute;left:80px;right:80px;top:730px;padding:25px;font:32px M;color:#BDD3FB;text-align:center;border-top:1px solid #638CD2}.balance{position:absolute;left:90px;top:265px;font-size:175px;line-height:1;font-weight:750;letter-spacing:-6px}.balance small{display:block;font-size:28px;letter-spacing:2px;color:#B4CDFB;margin-bottom:35px}.count{position:absolute;right:120px;top:280px;text-align:center;font-size:175px;font-weight:750;line-height:1}.count small{display:block;font-size:30px;color:#B4CDFB;margin-top:22px}.terminal{font:32px/1.6 M;white-space:pre-wrap;padding:25px 38px}.cols{position:absolute;left:70px;right:70px;top:230px;display:grid;grid-template-columns:1fr 1fr;gap:30px}.col{border:1px solid #7499DA;border-radius:18px;overflow:hidden;background:#0B152B;min-height:575px}.col pre{font:27px/1.7 M;white-space:pre-wrap;margin:0;padding:30px}.metric{position:absolute;left:80px;top:220px;font-size:310px;letter-spacing:-20px;font-weight:800;color:#A6C6FF;line-height:1}.metric small{display:block;font-size:36px;letter-spacing:0;color:#EAF2FF}.results{position:absolute;left:780px;right:85px;top:275px;font-size:43px}.result{border-bottom:1px solid #587BB8;padding:20px 10px}.result b{float:right;color:#BBD3FF}.underline{position:absolute;left:260px;right:260px;top:620px;height:8px;background:#8BB1FF;transform-origin:left}'''
    markup=[];js=[];overlays=[]
    for i,sc in enumerate(scenes):
        sid=f'shot{i}';d=sc['duration'];inner='';anim=[]
        if i in (0,10):
            words=['ONE TRANSFER.','THREE SERVICES.','PROVE IT.'] if i==0 else ['PROMPT.','CODE.','BROWSER.','TERMINAL.','EVIDENCE.']
            for j,word in enumerate(words):
                at=j*(d-.8)/len(words)
                inner+=f'<div class="word" id="{sid}-w{j}" style="visibility:hidden">{word}</div>'
                anim.extend([f"t.set('#{sid}-w{j}',{{visibility:'visible'}},{at});",f"t.fromTo('#{sid}-w{j}',{{y:100,scale:.75,opacity:0}},{{y:0,scale:1,opacity:1,duration:.65,ease:'power4.out'}},{at});",f"t.to('#{sid}-w{j}',{{y:-90,opacity:0,duration:.35}},{at+(d-.8)/len(words)-.4});"])
            inner+='<div class="underline"></div>';anim.append(f"t.fromTo('#{sid} .underline',{{scaleX:0}},{{scaleX:1,duration:1.5}},.4);")
        elif i==1:
            prompt='Create one complete transfer test. Use a unique fixture, accessible locators, and authenticated API checks. Assert one debit, one canonical record, the exact reference, and cleanup. Do not invent a passing result.'
            inner='<div class="window"><div class="chrome">PROMPT / TEACHING INPUT</div><div class="prompt">'
            for j,word in enumerate(prompt.split()):
                inner+=f'<span class="inputword" id="{sid}-p{j}">{esc(word)} </span>';anim.append(f"t.fromTo('#{sid}-p{j}',{{opacity:0}},{{opacity:1,duration:.08}},{1+j*.24});")
            inner+='</div></div>'
        elif i==2:
            code=["await page.goto('/transfers');","await page.getByLabel('Source account')","  .selectOption(lab.sourceAccountId);","await page.getByLabel('Amount (MXN)').fill('100.00');","await page.getByRole('button',","  { name: 'Transfer', exact: true }).click();","await expect(page.getByTestId('account-balance'))","  .toHaveText('MXN 900.00');"]
            inner='<div class="window"><div class="chrome">TYPESCRIPT / THE BROWSER CONTRACT</div><div class="code">'
            for j,line in enumerate(code):
                inner+=f'<div class="codeline" id="{sid}-l{j}">{esc(line)}</div>';anim.append(f"t.fromTo('#{sid}-l{j}',{{clipPath:'inset(0 100% 0 0)'}},{{clipPath:'inset(0 0% 0 0)',duration:.85,ease:'none'}},{1+j*.8});")
            inner+='</div></div>'
        elif i in (3,8):
            inner='<div class="window" style="left:350px;right:350px;top:160px;height:740px"><div class="chrome">RECORDED LOCAL BROWSER RUN'+(' / INTERCEPTED 503' if i==8 else '')+'</div></div>'
            overlays.append({'scene':sc['id'],'start':sc['start']+.8,'duration':d-.8,'capture':'success' if i==3 else 'unavailable','x':351,'y':216,'width':1218,'height':684})
        elif i==4:
            inner='<div class="path"></div>'
            for j,(label,desc) in enumerate([('Gateway','Accept the command'),('Accounts','Commit + outbox'),('Ledger','Project the event')]):
                inner+=f'<div class="node" id="{sid}-n{j}" style="left:{90+j*640}px">{label}<small>{desc}</small></div>'
                anim.append(f"t.fromTo('#{sid}-n{j}',{{y:65,opacity:0}},{{y:0,opacity:1,duration:.6,ease:'power3.out'}},{1+j*1.1});")
            inner+='<div class="packet"></div><div class="ref">CONCEPTUAL REQUEST PATH / EXACT IDENTITY</div>'
            anim.append(f"t.to('#{sid} .packet',{{x:745,duration:4.5,ease:'none'}},4);")
        elif i==5:
            inner=f'<div class="balance"><small>VERIFIED ACCOUNT BALANCE</small>MXN 900.00</div><div class="count">1<small>CANONICAL RECORD</small></div><div class="ref">{ident}</div>'
            anim.extend([f"t.fromTo('#{sid} .balance',{{x:-150,opacity:0}},{{x:0,opacity:1,duration:.8,ease:'power4.out'}},.7);",f"t.fromTo('#{sid} .count',{{scale:2,opacity:0}},{{scale:1,opacity:1,duration:.8,ease:'power3.out'}},3);",f"t.fromTo('#{sid} .ref',{{y:30,opacity:0}},{{y:0,opacity:1,duration:.6}},5);"])
        elif i==6:
            lines=['TRAINING LEDGER / LOCAL TN3270','',f'REFERENCE     {ident}','STATUS        COMPLETED','AMOUNT MINOR  10000','CURRENCY      MXN','BALANCE MINOR 90000','','TNZ client → local simulator']
            inner='<div class="window"><div class="chrome">ACTUAL CAPTURED TERMINAL RESULT</div><div class="terminal">'
            for j,line in enumerate(lines):
                inner+=f'<div id="{sid}-t{j}">{esc(line) or " "}</div>';anim.append(f"t.fromTo('#{sid}-t{j}',{{clipPath:'inset(0 100% 0 0)'}},{{clipPath:'inset(0 0% 0 0)',duration:.8,ease:'none'}},{1+j*1.1});")
            inner+='</div></div>'
        elif i==7:
            inner='<div class="cols"><div class="col"><div class="chrome">PYTHON / PYTEST</div><pre>expect(\n  page.get_by_test_id(\n    "account-balance"\n  )\n).to_have_text(\n  "MXN 900.00"\n)</pre></div><div class="col"><div class="chrome">JAVA / JUNIT</div><pre>assertThat(\n  page.getByTestId(\n    "account-balance"\n  )\n).hasText(\n  "MXN 900.00"\n);</pre></div></div>'
            anim.append(f"t.fromTo('#{sid} .col',{{y:70,opacity:0}},{{y:0,opacity:1,stagger:.65,duration:.8,ease:'power3.out'}},1);")
        elif i==9:
            inner='<div class="metric">22<small>CHECKS PASSED</small></div><div class="results">'+''.join(f'<div class="result" id="{sid}-r{j}">{name}<b>{count}</b></div>' for j,(name,count) in enumerate([('TypeScript / distributed',10),('Python / browser + protocol',8),('Java / core + hybrid',3),('TypeScript / hybrid',1)]))+'</div><div class="ref">VERIFIED LOCAL RUN / 14 SEPTEMBER 2026</div>'
            for j in range(4):anim.append(f"t.fromTo('#{sid}-r{j}',{{x:100,opacity:0}},{{x:0,opacity:1,duration:.6}}, {2+j*1.5});")
            anim.append(f"t.fromTo('#{sid} .metric',{{scale:.5,opacity:0}},{{scale:1,opacity:1,duration:1,ease:'power4.out'}},.5);")
        markup.append(f'<section class="shot" id="{sid}" style="visibility:hidden"><div class="brand">PLAYWRIGHT / IN MOTION</div><div class="idx">{i+1:02} / 11</div><h1 class="title">{esc(sc["title"])}</h1>{inner}</section>')
        js.append(f"master.set('#{sid}',{{visibility:'visible'}},{sc['start']});master.set('#{sid}',{{visibility:'hidden'}},{sc['start']+d});")
        js.append('{const t=gsap.timeline();'+''.join(anim)+f"master.add(t,{sc['start']});"+'}')
    for i,cue in enumerate(cues):
        markup.append(f'<div class="caption" id="cap{i}" style="visibility:hidden">{esc(cue["text"])}</div>')
        js.append(f"master.set('#cap{i}',{{visibility:'visible'}},{cue['start']});master.set('#cap{i}',{{visibility:'hidden'}},{cue['end']});")
    page=f'<!doctype html><html lang="en"><head><meta charset="utf-8"><script src="assets/gsap.min.js"></script><style>{css}</style></head><body><div id="movie" data-composition-id="movie" data-width="1920" data-height="1080" data-duration="{cursor}">{"".join(markup)}<audio id="voice" src="assets/narration.wav" data-start="0" data-duration="{cursor}" data-track-index="30"></audio></div><script>const master=gsap.timeline({{paused:true}});{"".join(js)}window.__timelines.movie=master;</script></body></html>'
    (P/'index.html').write_text(page,encoding='utf-8');(P/'hyperframes.json').write_text(json.dumps({'name':'showcase','entry':'index.html'}))
    (P/'edit.json').write_text(json.dumps({'episode':'showcase','duration':cursor,'overlays':overlays,'scenes':scenes},indent=2))
    (audio_dir/'subtitles.srt').write_text('\n\n'.join(f"{i+1}\n{timestamp(c['start'])} --> {timestamp(c['end'])}\n{c['text']}" for i,c in enumerate(cues)),encoding='utf-8')
    print(json.dumps({'showcaseDuration':cursor,'scenes':len(scenes)}),flush=True)

if __name__=='__main__':asyncio.run(main())
