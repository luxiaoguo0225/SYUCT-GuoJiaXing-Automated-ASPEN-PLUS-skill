"""Conservative history parser shared by output checks; no COM invocation."""
import re

def decode_history(data):
    if data.startswith((b'\xff\xfe', b'\xfe\xff')):
        return data.decode('utf-16'), 'utf-16'
    if data and data.count(b'\x00')/len(data) > .1:
        for enc in ('utf-16-le','utf-16-be'):
            try:
                text=data.decode(enc)
                if re.search(r'ERROR|WARNING|SIMULATION',text,re.I): return text,enc
            except UnicodeError: pass
    for enc in ('utf-8-sig','gb18030'):
        try: return data.decode(enc),enc
        except UnicodeError: pass
    return data.decode('latin1'),'latin1'

def his_verdict(data):
    text,encoding=decode_history(data)
    keys=('severe','errors','warnings'); summaries=[]
    for chunk in re.split(r'SUMMARY\s+OF\s+SIMULATION\s+ERRORS',text,flags=re.I)[1:]:
        table=re.search(r'SEVERE\s+ERRORS\s+ERRORS\s+WARNINGS[^\r\n]*[\r\n]+(?:[^\w\d\r\n]*[\r\n]+)*\s*(\d+)\s+(\d+)\s+(\d+)',chunk[:1600],re.I)
        if table:
            summaries.append(dict(zip(keys,map(int,table.groups()))));continue
        counts={}
        for line in chunk[:1600].splitlines():
            for key,label in (('severe',r'SEVERE\s+ERRORS?'),('errors',r'ERRORS?'),('warnings',r'WARNINGS?')):
                m=re.match(rf'^\s*(?:\*\s*)?(?:{label}\s*[:=]?\s*(\d+)|(\d+)\s+{label})\s*[.!]?\s*$',line,re.I)
                if m: counts[key]=int(next(x for x in m.groups() if x is not None))
        if len(counts)==3: summaries.append(counts)
    counts={k:max((x[k] for x in summaries),default=0) for k in keys}
    messages=dict.fromkeys(keys,0)
    for line in text.splitlines():
        if re.search(r'^\s*\*+\s*SEVERE\s+ERROR\b|\bSEVERE\s+ERROR\s+(?:WHILE|IN|AT)\b|^\s*SEVERE ERROR\s*$',line,re.I): messages['severe']+=1
        elif re.search(r'^\s*\*+\s*(?:TERMINAL\s+)?ERROR\b|\b(?:TERMINAL\s+ERROR|ERROR\s+WHILE\s+EXECUTING)\b',line,re.I): messages['errors']+=1
        if re.search(r'^\s*\*+\s*WARNING\b|\bWARNING\s+WHILE\s+EXECUTING\b|TEMPERATURE\s+CROSSOVER\s+DETECTED',line,re.I): messages['warnings']+=1
    counts={k:max(counts[k],messages[k]) for k in keys}
    clean=bool(re.search(r'NO\s+ERRORS\s+OR\s+WARNINGS\s+(?:WERE\s+)?GENERATED',text,re.I))
    status='FAIL' if any(counts.values()) else ('PASS' if summaries or clean else 'UNVERIFIED')
    unclassified=[]
    for line in text.splitlines():
        if not re.search(r'\bERRORS?\b|\bWARNINGS?\b',line,re.I): continue
        if re.search(r'SUMMARY\s+OF\s+SIMULATION\s+ERRORS|NO\s+ERRORS\s+OR\s+WARNINGS\s+(?:WERE\s+)?GENERATED',line,re.I): continue
        if re.match(r'^\s*(?:SEVERE\s+ERRORS?\s+ERRORS?\s+WARNINGS?|(?:SEVERE\s+ERRORS?|ERRORS?|WARNINGS?)\s*[:=]?\s*\d+|\d+\s+(?:SEVERE\s+ERRORS?|ERRORS?|WARNINGS?))\s*$',line,re.I): continue
        if re.search(r'^\s*\*+\s*(?:SEVERE\s+|TERMINAL\s+)?(?:ERROR|WARNING)\b|\b(?:ERROR|WARNING)\s+WHILE\s+EXECUTING\b|^\s*SEVERE ERROR\s*$',line,re.I): continue
        unclassified.append(line.strip())
    if status=='PASS' and unclassified: status='UNVERIFIED'
    trace=bool(re.search(r'SIMULATION CALCULATIONS BEGIN',text,re.I) and re.search(r'GENERATING RESULTS FOR UOS BLOCK',text,re.I))
    return {'status':status,**counts,'encoding':encoding,'summary_count':len(summaries),'clean_marker':clean,'message_counts':messages,'unclassified_message_lines':unclassified,'calculation_trace':trace}
