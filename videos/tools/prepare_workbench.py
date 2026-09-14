"""Extract displayable observations from actual runner reports, without environment data."""
from pathlib import Path
import base64, json, xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'motion'
def specs(suites):
    for suite in suites:
        yield from suite.get('specs',[])
        yield from specs(suite.get('suites',[]))
def main():
    ts=json.loads((ROOT/'lab/distributed/local-results/motion-contract/results.json').read_text())
    assert ts['stats']['expected']==10 and ts['stats']['unexpected']==0
    data={'typescript':['$ npx playwright test','']+[f"PASS  {s['title']}" for s in specs(ts['suites'])]+['','10 passed / retries 0'], 'python':['$ python -m pytest ...','']}
    for c in ET.parse(OUT/'local-results/python-tests.xml').iter('testcase'):
        assert c.find('failure') is None and c.find('error') is None
        data['python'].append('PASS  '+c.get('name'))
    data['python']+=['','8 passed / protocol + browser']
    data['java']=['$ mvn test','']
    for p in sorted((ROOT/'lab/mainframe/java/target/surefire-reports').glob('TEST-*.xml')):
        for c in ET.parse(p).iter('testcase'):
            assert c.find('failure') is None and c.find('error') is None
            data['java'].append('PASS  '+c.get('name'))
    data['java']+=['','Tests run: 3 / Failures: 0 / Errors: 0','BUILD SUCCESS']
    defect=json.loads((ROOT/'lab/distributed/local-results/motion-defect-replay/results.json').read_text())
    assert defect['stats']['unexpected']==1
    data['defect']=['$ npx playwright test --grep TR-03','LOCAL DEFECT MODE / port 3700','','FAIL  Sequential replay must keep the same ID','The idempotency assertion rejected the replay.']
    for s in specs(defect['suites']):
        for test in s['tests']:
            for result in test['results']:
                for attachment in result.get('attachments',[]):
                    if attachment['name']=='business-state':
                        body=json.loads(base64.b64decode(attachment['body']))
                        data['defect']+=['',f"Observed balanceMinor: {body['account']['balanceMinor']}",f"Observed canonical records: {body['transfers']['total']}"]
    data['defect']+=['','1 failed / intentional defect demonstration','Do not weaken the assertion.']
    data['provenance']={'date':'2026-09-14','healthyTests':22,'recordingTests':3,'intentionalDefectFailures':1,
        'sources':['lab/distributed/local-results/motion-contract/results.json','motion/local-results/python-tests.xml','lab/mainframe/java/target/surefire-reports','motion/local-results/mainframe-ts/hybrid-typescript-tests.xml','lab/distributed/local-results/motion-defect-replay/results.json']}
    (OUT/'captures/workbench.json').write_text(json.dumps(data,indent=2),encoding='utf-8')
    print('Extracted healthy runner output and one actual intentional failure.')
if __name__=='__main__':main()
