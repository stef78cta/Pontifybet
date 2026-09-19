"""Harness independent pentru cele trei fixture-uri REPLAY din workbook-ul V14.

Nu este motor de producție și nu se integrează în PontifyBet. Folosește numai
biblioteca standard Python. Recalculează din rândurile native (fără cache intermediar)
statisticile, Poisson/NB și 42 de selecții, apoi compară cu cache-ul original.
Scope strict: fixture-urile livrate, fără prior/context și fără OOS aprobat.
Rulare: python verifica_replay.py
"""
from pathlib import Path
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
import json, math, collections

BASE=Path(__file__).resolve().parent
INPUT=json.loads((BASE/'fixture_input_original.json').read_text(encoding='utf-8'))
CONFIG=json.loads((BASE/'configuratie_exacta.json').read_text(encoding='utf-8'))
C={x['cell']:x['cached_value'] for x in CONFIG}
EXPECTED=json.loads((BASE/'expected_42_selectii_cache.json').read_text(encoding='utf-8'))
def date(v):return datetime.fromisoformat(v)
def avg(xs):return sum(xs)/len(xs)
def excel_round0(x):return int(Decimal(str(x)).quantize(Decimal('1'),rounding=ROUND_HALF_UP))
def native_rows():
    sources={s['Source_ID']:s for s in INPUT['Surse_Import']}
    seen=set();keys=collections.defaultdict(list)
    for h in INPUT['Istoric_Nativ']:
        key=(h['League'],h['Season'],date(h['Match_Date']).strftime('%Y%m%d'),h['Home'],h['Away'])
        keys[key].append((h['HC'],h['AC']))
    out=[]
    for h in INPUT['Istoric_Nativ']:
        s=sources[h['Source_ID']]
        assert h['Definition']=='FT90' and h['League']==s['League'] and h['Season']==s['Season']
        assert h['Retrieved_UTC']==s['Retrieved_UTC'] and h['Source_URL'] and h['Evidence']
        assert h['Home']!=h['Away'] and h['Event_ID']
        for field in ['HC','AC']:
            x=h[field];assert isinstance(x,(float,int)) and 0<=x<=100 and x%1==0
        key=(h['League'],h['Season'],date(h['Match_Date']).strftime('%Y%m%d'),h['Home'],h['Away'])
        assert len(set(keys[key]))==1,'Conflicte în fixture: în afara scope-ului acestui harness.'
        if key in seen:continue
        seen.add(key)
        out.append({**h,'date':date(h['Match_Date']),'total':h['HC']+h['AC']})
    return out

def recent(history,n):
    if not history:return []
    threshold=sorted((h['date'] for h in history),reverse=True)[min(n,len(history))-1]
    return [h for h in history if h['date']>=threshold]

def run():
    hist=native_rows();out=[];intermediate=[]
    assert not INPUT['OOS_Predictii']
    for idx,m in enumerate(INPUT['Input_Meci']):
        assert m['Mode']=='REPLAY' and m['Prior_Allowed']=='NO' and m['Sourcing_Decision']=='AUTO'
        assert all(m[k] is None for k in list(m)[list(m).index('Shots_H'):]),'Context nevid: în afara scope-ului.'
        assert date(m['Cutoff_UTC'])<date(m['Kickoff_UTC'])
        source=[s for s in INPUT['Surse_Import'] if s['League']==m['League'] and s['Season']==m['Season']]
        assert len(source)==1 and source[0]['Status'] in ['IMPORTED','PARTIAL','SOURCE CONFLICT']
        assert source[0]['Coverage']=='FULL SEASON EXPORT' and source[0]['URL'] and source[0]['SHA256']
        cutoff=date(m['Cutoff_UTC']).replace(hour=0,minute=0,second=0,microsecond=0)
        season=[h for h in hist if h['League']==m['League'] and h['Season']==m['Season'] and h['date']<cutoff]
        home=[h for h in season if m['Home'] in (h['Home'],h['Away'])]
        away=[h for h in season if m['Away'] in (h['Home'],h['Away'])]
        hh=[h for h in home if h['Home']==m['Home']]
        aa=[h for h in away if h['Away']==m['Away']]
        hr=recent(home,C['B54']);ar=recent(away,C['B54'])
        scopes=[home,hh,hr,away,aa,ar]
        targets=[C['B7'],C['B8'],C['B9']]*2
        assert all(len(h)>=n for h,n in zip(scopes,targets))
        core=[]
        for i,scope in enumerate(scopes):
            team=m['Home'] if i<3 else m['Away']
            cf=avg([h['HC'] if h['Home']==team else h['AC'] for h in scope])
            ca=avg([h['AC'] if h['Home']==team else h['HC'] for h in scope])
            core.append({'N':len(scope),'Corners_For':cf,'Corners_Against':ca})
        hf,hhf,hrf,af,aaf,arf=[v['Corners_For'] for v in core]
        ha,hha,hra,aaa,aaaa,ara=[v['Corners_Against'] for v in core]
        lamh=((hf+aaa)/2*C['B4']+(hhf+aaaa)/2*C['B5']+(hrf+ara)/2*C['B6'])*1*1
        lama=((af+ha)/2*C['B4']+(aaf+hha)/2*C['B5']+(arf+hra)/2*C['B6'])*1*1
        mu=lamh+lama
        union=[h for h in season if m['Home'] in (h['Home'],h['Away']) or m['Away'] in (h['Home'],h['Away'])]
        totals=[h['total'] for h in union];n=len(totals);mean=avg(totals)
        variance=max(0,(sum(x*x for x in totals)-n*mean**2)/(n-1));d=variance/mean
        size=9999 if d<=C['B10'] else mean/(d-1)
        sample=min(1,min(len(home),len(away))/C['B7'])*min(1,min(len(hh),len(aa))/C['B8'])*min(1,min(len(hr),len(ar))/C['B9'])
        stability=max(0,15-2*abs(hf-hrf)-2*abs(af-arf))
        dscore=15 if d<=C['B10'] else 13 if d<=C['B11'] else 10 if d<=C['B12'] else 6 if d<=C['B13'] else 0
        conf=max(0,min(100,excel_round0(40+25*sample+stability+dscore+5-C['B38'])))
        dfactor=1 if d<=C['B10'] else .95 if d<=C['B11'] else .88 if d<=C['B12'] else .78
        strength=min(1,C['B14']*(.7+.3*min(1,n/C['B15']))*dfactor*(.75+.25*conf/100))
        pmf=[math.exp(-mu) if d<=C['B10'] else (size/(size+mu))**size]
        for k in range(1,19):
            pmf.append(pmf[-1]*mu/k if d<=C['B10'] else pmf[-1]*(size+k-1)/k*mu/(size+mu))
        cdf=[min(1,sum(pmf[:k+1])) for k in range(19)]
        unionha=[h for h in season if h['Home']==m['Home'] or h['Away']==m['Away']]
        h10={h['Event_ID'] for h in recent(home,10)};a10={h['Event_ID'] for h in recent(away,10)}
        h20={h['Event_ID'] for h in recent(home,20)};a20={h['Event_ID'] for h in recent(away,20)}
        union10=[h for h in season if h['Event_ID'] in h10|a10]
        union20=[h for h in season if h['Event_ID'] in h20|a20]
        intermediate.append({'Match_ID':m['Match_ID'],'core':core,'N_Dispersion':n,'Mean_Total_History':mean,'Variance_Total_History':variance,'D':d,'NB_Size':size,'Lambda_H':lamh,'Lambda_A':lama,'Mu':mu,'Confidence_Base':conf,'Calibration_Strength':strength,'PMF':pmf,'CDF':cdf})
        matchrows=[]
        for lineidx,line in enumerate(INPUT['Calibrare_Linii']):
            k=line['k'];isover=line['Type']=='OVER'
            assert line['Review_Status'] in ['PILOT','PENDING'] and line['Calibration_Factor']==1
            raw=1-cdf[k] if isover else cdf[k]
            cal=max(.01,min(.99,.5+(raw-.5)*strength*line['Calibration_Factor']))
            failure_model=1-raw
            emp=[sum((h['total']<=k if isover else h['total']>k) for h in scope)/len(scope) if scope else None for scope in [unionha,union10,union20]]
            failure=max([failure_model]+[e for e in emp if e is not None])
            score=min(100,failure*100*C['B44']+min(100,d/C['B13']*100)*C['B45']+(100-conf)*C['B46']+0*C['B47'])
            rawlevel=1 if score<=20 else 2 if score<=40 else 3 if score<=60 else 4 if score<=80 else 5
            tail=('PASS' if failure<=C['B26'] else 'PENALTY' if failure<=C['C26'] else 'WATCH') if lineidx==0 else 'OOS PENDING'
            dispersion_penalty=C['B37'] if d>C['B12'] else C['B36'] if d>C['B11'] else 0
            cf=max(0,conf-(C['B35'] if tail=='OOS PENDING' else 0)-dispersion_penalty)
            candidate_conf=max(0,conf-dispersion_penalty)
            pfinal=min(cal,1-failure)
            candidate='CANDIDATE' if pfinal>=C['B50'] and candidate_conf>=C['B51'] and score<=C['B52'] and d<=C['B53'] and line['PASS_Max'] is not None and failure<=line['PASS_Max'] else 'NO'
            gate='OOS PENDING' if candidate=='CANDIDATE' else 'FAIL'
            level=5 if d>C['B13'] or tail=='WATCH' else min(5,max(C['B42'],rawlevel)+(1 if tail=='PENALTY' else 0))
            verdict='NO BET' if level==5 else 'WATCH' if pfinal<C['B16'] or cf<C['B18'] else {1:'DEFENSIV',2:'PRUDENT',3:'MODERAT',4:'RIDICAT'}[level]
            eligible=int(verdict in ['DEFENSIV','PRUDENT','MODERAT','RIDICAT'])
            builder='NO' if not eligible else 'YES' if tail=='PASS' else 'CONDITIONAL' if tail=='OOS PENDING' else 'NO'
            reason='Dispersie peste limita' if d>C['B13'] else 'Failure peste limita' if tail=='WATCH' else 'P finala sub prag' if pfinal<C['B16'] else 'Confidence sub prag' if cf<C['B18'] else 'Exemplu retrospectiv; exclus din Top LIVE'
            rec={'excel_row':6+14*idx+lineidx,'Match_ID':m['Match_ID'],'Line':line['Line'],'Release':'READY','G0':'PASS','Mu':mu,'D':d,'P_Raw':raw,'P_Calibrated':cal,'Failure_Model':failure_model,'Empirical_HA':emp[0],'Empirical_L10':emp[1],'Empirical_L20':emp[2],'Failure_Gate':failure,'Risk_Score':score,'Risk_Level_Raw':rawlevel,'Confidence_Final':cf,'Tail_Gate':tail,'Defensive_Candidate':candidate,'Defensive_Gate':gate,'Risk_Level_FINAL':level,'Verdict_FINAL':verdict,'P_FINAL':pfinal,'Eligible':eligible,'Builder':builder,'Live_Eligible_Best':0,'Rank_LIVE':None,'Reason':reason,'OOS_Status':'OOS PENDING','N_HA_Empirical':len(unionha),'N_L10_Empirical':len(union10),'N_L20_Empirical':len(union20),'Candidate_Confidence':candidate_conf,'Rank_In_Match':None}
            matchrows.append(rec)
        ranked=sorted((r for r in matchrows if r['Eligible']),key=lambda r:(r['Risk_Level_FINAL'],-r['P_FINAL'],-r['Confidence_Final'],r['excel_row']))
        for rank,r in enumerate(ranked,1):r['Rank_In_Match']=rank
        out.extend(matchrows)
    errors=[];compares=0;maxdiff=0
    for got,expected in zip(out,EXPECTED):
        for key,a in got.items():
            b=expected[key];compares+=1
            if isinstance(a,(float,int)) and isinstance(b,(float,int)):
                diff=abs(a-b);maxdiff=max(maxdiff,diff);ok=math.isclose(a,b,rel_tol=1e-12,abs_tol=1e-10)
            else:ok=a==b
            if not ok:errors.append({'row':got['excel_row'],'field':key,'recomputed':a,'cached':b})
    report={'selection_count':len(out),'comparisons':compares,'mismatches':errors,'max_abs_difference':maxdiff,'status':'PASS' if not errors else 'FAIL','scope':'3 exemple REPLAY existente; fără prior/context populat, fără OOS aprobat; nu certifică toate ramurile modelului.'}
    (BASE/'rezultate_replay_recalculate.json').write_text(json.dumps({'report':report,'intermediate':intermediate,'selections':out},ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))
    assert not errors
if __name__=='__main__':run()
