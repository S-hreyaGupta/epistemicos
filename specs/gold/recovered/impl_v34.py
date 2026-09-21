#!/usr/bin/env python3
"""Citation extraction & bibliographic coherence — deterministic spec v3.3.

A faithful implementation of the spec, written to produce real output on a real
paper. Section numbers in comments refer to the spec.
"""
import sys, json, unicodedata, hashlib
import regex as re

# ---------------------------------------------------------------- §1 pinned
YEAR_RE      = r'(?:(?:1[5-9]|20)\d{2}[a-z]?|n\.d\.)'
PARTICLES    = ['della','delle','dos','del','der','den','van','von','ter','ten',
                'zur','zu','de','di','da','du','la','le']
PARTICLE     = '(?:' + '|'.join(PARTICLES) + ')'
NAMECHAR     = r"[\p{L}\p{M}'’-]"
CORE         = r"\p{Lu}" + NAMECHAR + r"+"
WS           = r'[ \t\n]+'
WSO          = r'(?:[ \t\n]+)?'   # the spec's WS? — optional, NOT a lazy +?
SURNAME      = r'(?:(?i:' + PARTICLE + r')' + WS + r')*' + CORE
INITIALS     = r'\p{Lu}\.(?:[- ]?\p{Lu}\.)*'

AUTHORS_PAREN = ('(?:' + SURNAME + WS + r'et' + WS + r'al\.'
                 '|' + SURNAME + r'(?:,' + WSO + SURNAME + r')*'
                       r'(?:,?' + WS + r'(?:&|and)' + WS + SURNAME + r')?'
                 ')')
AUTHORS_NARR  = ('(?:' + SURNAME + WS + r'et' + WS + r'al\.'
                 '|' + SURNAME + r'(?:,' + WS + SURNAME + r')*'
                       r',?' + WS + r'(?:&|and)' + WS + SURNAME +
                 '|' + SURNAME +
                 ')')
LOCATOR = r'(?:,' + WSO + r'(?:p\.|pp\.|para\.|chap\.)' + WSO + r'[^();]+)'
PREFIX  = r'(?:(?:e\.g\.|i\.e\.|cf\.|see also|see|but see)[, ]' + WSO + r')'
SEG     = (PREFIX + r'?' + AUTHORS_PAREN + r',' + WS + YEAR_RE +
           r'(?:,' + WS + YEAR_RE + r')*' + LOCATOR + r'?')
CITE_PAREN = (r'\(' + WSO + SEG + r'(?:;' + WSO + SEG + r')*' + WSO + r'\)')
CITE_NARR  = (AUTHORS_NARR + WS + r'\(' + WSO + YEAR_RE +
              r'(?:,' + WS + YEAR_RE + r')*' + LOCATOR + r'?' + WSO + r'\)')
ENTRY_START = r'^(?:(?i:' + PARTICLE + r')[ ])*' + CORE + r',[ ]' + INITIALS
NUMCITE = r'\[\d{1,3}(?:[ \t]*[,–—-][ \t]*\d{1,3})*\]'
SUPCITE = r'[¹²³⁰⁴-⁹]+'

STOP = set("""january february march april may june july august september october
november december jan. feb. mar. apr. jun. jul. aug. sep. sept. oct. nov. dec.
in the a an see since during early late as at on after before table figure
section chapter equation however moreover unlike although while whereas thus
therefore furthermore additionally finally similarly likewise consequently
meanwhile nevertheless nonetheless indeed overall importantly specifically
notably together here there this these those using given despite beyond under
over from with within without across toward towards per via following like
first second third next then also yet still both when where because if unless
until once""".split())

GUARD = ["et al.","e.g.","i.e.","cf.","vs.","Dr.","Prof.","Mr.","Mrs.","Ms.",
         "St.","Jr.","Sr.","no.","No.","p.","pp.","Vol.","vol.","Eq.","Fig.",
         "Figs.","Tab.","ca.","ed.","eds.","approx.","U.S.","U.K."]

ROLE_KEYWORDS = [("introduction", ["introduction"]),
                 ("literature_review", ["literature","related work","background"]),
                 ("methodology", ["method","methods","methodology"]),
                 ("results", ["result","results","finding","findings"]),
                 ("discussion", ["discussion"]),
                 ("conclusion", ["conclusion","conclusions"])]

def C(p, f=0): return re.compile(p, f)

# ---------------------------------------------------------------- §2 input
def normalize(raw: bytes):
    try: s = raw.decode('utf-8')
    except UnicodeDecodeError: return None
    s = s.replace('\r\n', '\n').replace('\r', '\n')
    return unicodedata.normalize('NFC', s)

# ---------------------------------------------------------------- §3 structure
HEAD_MD   = C(r'^(\#{1,6})[ \t]+(.*)$')
HEAD_HTML = C(r'^[ \t]*<h([1-6])(?:[ \t][^>]*)?>(.*?)</h\1>[ \t]*$', re.I)
CLEAN     = C(r'^\d+(\.\d+)*[.)]?[ \t]+')

def clean_name(n): return CLEAN.sub('', n)

def line_spans(text):
    out, pos = [], 0
    for ln in text.split('\n'):
        out.append((pos, pos + len(ln), ln)); pos += len(ln) + 1
    return out

def headings(text):
    hs = []
    for start, end, ln in line_spans(text):
        m = HEAD_MD.match(ln)
        if m:
            name = re.sub(r'(?:[ \t]+#+)?[ \t]*$', '', m.group(2))
            hs.append((start, end, len(m.group(1)), clean_name(name).strip())); continue
        m = HEAD_HTML.match(ln)
        if m:
            inner = re.sub(r'<[^>]*>', '', m.group(2))
            hs.append((start, end, int(m.group(1)),
                       clean_name(re.sub(r'\s+',' ',inner).strip()).strip()))
    return hs

def roles_of(name):
    low, hits = name.lower(), []
    for i,(role,kws) in enumerate(ROLE_KEYWORDS):
        best = None
        for kw in kws:
            m = re.search(r'(?<![\p{L}\p{N}_])' + re.escape(kw) + r'(?![\p{L}\p{N}_])', low)
            if m and (best is None or m.start() < best): best = m.start()
        if best is not None: hits.append((best, i, role))
    return [r for _,_,r in sorted(hits)]

# ---------------------------------------------------------------- §5 sentences
def sentences(text, lo, hi, hard_bounds):
    """Yield (start, end, content_end) for body region [lo,hi)."""
    out = []
    segs, cur = [], lo
    for b0, b1 in hard_bounds:
        if b0 >= lo and b1 <= hi:
            if b0 > cur: segs.append((cur, b0))
            cur = b1
    if cur < hi: segs.append((cur, hi))

    for s0, s1 in segs:
        para = text[s0:s1]
        i, start = 0, None
        while i < len(para):
            ch = para[i]
            if start is None:
                if not ch.isspace(): start = i
                i += 1; continue
            if ch in '.?!':
                j = i + 1
                while j < len(para) and para[j] in '”"’\')]': j += 1
                after = para[j:]
                terminates = (after.strip() == '') or bool(re.match(r'\s+\p{Lu}', after))
                if terminates and not guarded(para, i):
                    out.append((s0+start, s0+j, s0+i)); start = None; i = j; continue
            i += 1
        if start is not None:
            e = len(para)
            while e > start and para[e-1].isspace(): e -= 1
            if e > start: out.append((s0+start, s0+e, s0+e))
    return out

def guarded(para, t):
    ctx = para[:t+1]
    for g in GUARD:
        if ctx.endswith(g):
            k = len(ctx) - len(g)
            if k == 0 or para[k-1].isspace() or para[k-1] in '([\"“\'‘': return True
    m = re.search(r'\p{Lu}\.$', ctx)
    if m:
        k = m.start()
        if k == 0 or para[k-1].isspace() or para[k-1] in '([\"“\'‘': return True
    return False

# ---------------------------------------------------------------- §6 extraction
C1_RE   = C(r'\([^()]*\)')
YR_RE   = C(YEAR_RE)
TOK_ELIG= C(r"^(?:\p{Lu}[\p{L}\p{M}'’.-]*)$")
CP_RE   = C(r'^' + CITE_PAREN + r'$')
CN_RE   = C(r'^' + CITE_NARR + r'$')
SEG_RE  = C(SEG)
SEG_FULL_RE = C(r'^' + SEG + r'$')

def candidates(text, lo, hi, sents):
    """§6.1 C1 + C2 token run."""
    sent_of = {}
    for s0,s1,ce in sents:
        for _ in (0,): sent_of[(s0,s1,ce)] = True
    out = []
    for m in C1_RE.finditer(text, lo, hi):
        if not YR_RE.search(m.group(0)): continue
        c0, c1 = m.start(), m.end()
        host = None
        for s0,s1,ce in sents:
            if s0 <= c0 < s1: host = (s0,s1,ce); break
        sstart = host[0] if host else lo
        # walk left collecting eligible tokens, max 6, not past sentence start
        run_start, count, k = c0, 0, c0
        while count < 6:
            j = k
            while j > sstart and text[j-1] in ' \t\n': j -= 1
            if j <= sstart: break
            t_end = j
            while j > sstart and text[j-1] not in ' \t\n': j -= 1
            t_start = j
            if t_start < sstart: break
            tok = text[t_start:t_end]
            probe = tok[:-1] if tok.endswith(',') else tok
            if TOK_ELIG.match(probe) or probe.lower() in ('et','al.','and','&') \
               or probe.lower() in PARTICLES:
                run_start, count, k = t_start, count+1, t_start
            else: break
        out.append((run_start, c0, c1, host))
    return out

def parse_candidates(text, cands):
    cites, unres = [], []
    for run_start, c0, c1, host in cands:
        c1span = text[c0:c1]
        # 1. parenthetical
        if CP_RE.match(c1span):
            segs = list(SEG_RE.finditer(c1span))
            first = segs[0].group(0) if segs else ''
            core = first_core(first)
            if core and core.isupper() and len(core) >= 2:
                unres.append((c0, c1, 'all_caps_surname', host)); continue
            cites.append(('parenthetical', c0, c1, c0, c1, host, c1span)); continue
        # 1b. B4 — group did not parse whole. Split on top-level ';' and parse
        # each segment independently, so one bad segment stops destroying its
        # neighbours. Offsets stay absolute into the canonical text.
        if c1span.startswith('(') and c1span.endswith(')') and ';' in c1span:
            inner_off = c0 + 1
            inner = c1span[1:-1]
            any_ok = False
            pos = 0
            for part in inner.split(';'):
                a = inner_off + pos
                b = a + len(part)
                pos += len(part) + 1
                stripped = part.strip()
                if not stripped: continue
                lead = part.index(stripped[0]) if stripped else 0
                sa, sb = a + lead, a + lead + len(stripped)
                if SEG_FULL_RE.match(stripped):
                    core = first_core(stripped)
                    if core and core.isupper() and len(core) >= 2:
                        unres.append((sa, sb, 'all_caps_surname', host)); continue
                    cites.append(('parenthetical', sa, sb, sa, sb, host,
                                  '(' + stripped + ')'))
                    any_ok = True
                else:
                    unres.append((sa, sb, 'no_grammar_match', host))
            if any_ok: continue
            continue
        # 2. narrative, longest admissible suffix
        toks = tokens_between(text, run_start, c0)
        best = None
        for L in range(len(toks), 0, -1):
            gstart = toks[len(toks)-L][0]
            if CN_RE.match(text[gstart:c1]): best = (L, gstart); break
        if best:
            L, gstart = best
            discarded = toks[:len(toks)-L]
            ok = all(discardable(text[a:b]) for a,b in discarded)
            if ok:
                core = first_core(text[gstart:c1])
                if core and core.isupper() and len(core) >= 2:
                    unres.append((gstart, c1, 'all_caps_surname', host)); continue
                if core and core.lower() in STOP:
                    unres.append((gstart, c1, 'stopword_surname', host)); continue
                cites.append(('narrative', gstart, c1, gstart, c1, host, text[gstart:c1])); continue
            unres.append((run_start, c1, 'no_grammar_match', host)); continue
        unres.append((run_start, c1, 'no_grammar_match', host))
    return cites, unres

def tokens_between(text, a, b):
    toks, i = [], a
    while i < b:
        while i < b and text[i] in ' \t\n': i += 1
        if i >= b: break
        j = i
        while j < b and text[j] not in ' \t\n': j += 1
        toks.append((i, j)); i = j
    return toks

def discardable(tok):
    t = tok.rstrip(',;:')
    return t.lower() in STOP or tok[-1:] in ',;:'

def first_core(s):
    m = re.search(CORE, s)
    return m.group(0) if m else None

def surname_of(seg_text):
    m = re.search(r'(?:(?i:' + PARTICLE + r')' + WS + r')*' + CORE, seg_text)
    if not m: return None
    return re.sub(r'\s+', ' ', m.group(0)).strip().lower()

def norm_year(y): return 'nd' if y == 'n.d.' else y

# ---------------------------------------------------------------- §7 assembly
ENTRY_START_RE = C(ENTRY_START)
CAND_YEAR_A = C(r'\((?:(?:1[5-9]|20)\d{2}|n\.d\.)')
CAND_YEAR_B = C(r'^[^.\n]{2,60}\.[ \t]+\(?(?:(?:1[5-9]|20)\d{2}|n\.d\.)')
EMBEDDED    = C(r'\. (?:(?i:' + PARTICLE + r') )*\p{Lu}' + NAMECHAR + r'+, (?:\p{Lu}\. ?)+')
TERMINATOR  = C(r'(?:\.|\?|\d+[–—-]\d+\.?|(?:doi:|https?://)\S+)$')

def assemble(text, r0, r1):
    refs, unres = [], []
    open_lines = []
    def close():
        nonlocal open_lines
        if open_lines:
            start = open_lines[0][0]; end = open_lines[-1][1]
            joined = ' '.join(l[2] for l in open_lines)
            refs.append({'assembled': joined, 'start': start, 'end': end})
            open_lines = []
    for ls, le, raw in line_spans(text):
        if le <= r0 or ls >= r1: continue
        stripped = raw.strip(' \t')
        if not stripped:
            close(); continue
        off = ls + (len(raw) - len(raw.lstrip(' \t')))
        tend = off + len(stripped)
        if HEAD_MD.match(raw) or HEAD_HTML.match(raw):
            close(); continue
        if ENTRY_START_RE.match(stripped):
            close(); open_lines = [(off, tend, stripped)]; continue
        probe = stripped
        for p in PARTICLES:
            if probe.lower().startswith(p + ' '): probe = probe[len(p)+1:]; break
        if probe[:1] and re.match(r'\p{Lu}', probe[:1]) and (
                CAND_YEAR_A.search(stripped[:100]) or CAND_YEAR_B.match(stripped)):
            close(); unres.append({'text': stripped, 'start': off, 'end': tend,
                                   'reason': 'entry_start_grammar'}); continue
        if open_lines: open_lines.append((off, tend, stripped))
        else: unres.append({'text': stripped, 'start': off, 'end': tend,
                            'reason': 'orphan_line'})
    close()
    for r in refs:
        a = r['assembled']
        m = ENTRY_START_RE.match(a)
        sn = None
        if m:
            mm = re.match(r'(?:(?i:' + PARTICLE + r')[ ])*' + CORE, a)
            if mm: sn = re.sub(r'\s+',' ',mm.group(0)).strip().lower()
        r['surname'] = sn or ''
        ym = YR_RE.search(a)
        r['year'] = norm_year(ym.group(0)) if ym else None
        r['reference_key'] = (r['surname'] + '|' + r['year']) if (sn and r['year']) else None
        reasons = []
        if not ym: reasons.append('no_year')
        if not TERMINATOR.search(a): reasons.append('terminator')
        if len(a) > 1500: reasons.append('overlong')
        em = EMBEDDED.search(a)
        if em and em.start() > 10: reasons.append('embedded_entry_pattern')
        r['suspect_reasons'] = reasons
        r['validation_state'] = 'suspect' if reasons else 'ok'
    return refs, unres

# ---------------------------------------------------------------- §8 reconcile
def osa(a, b):
    la, lb = len(a), len(b)
    d = [[0]*(lb+1) for _ in range(la+1)]
    for i in range(la+1): d[i][0] = i
    for j in range(lb+1): d[0][j] = j
    for i in range(1, la+1):
        for j in range(1, lb+1):
            c = 0 if a[i-1]==b[j-1] else 1
            d[i][j] = min(d[i-1][j]+1, d[i][j-1]+1, d[i-1][j-1]+c)
            if i>1 and j>1 and a[i-1]==b[j-2] and a[i-2]==b[j-1]:
                d[i][j] = min(d[i][j], d[i-2][j-2]+c)
    return d[la][lb]

def transposed(y1, y2):
    if len(y1)!=len(y2) or y1==y2: return False
    for i in range(len(y1)-1):
        s = list(y1); s[i],s[i+1] = s[i+1],s[i]
        if ''.join(s)==y2: return True
    return False

def reconcile(cites, refs):
    out = {}
    cite_keys, seen = [], set()
    for c in cites:
        if c['citation_key'] not in seen:
            seen.add(c['citation_key']); cite_keys.append(c['citation_key'])
    keyed = [(i,r) for i,r in enumerate(refs) if r['reference_key']]
    bykey = {}
    for i,r in keyed: bykey.setdefault(r['reference_key'], []).append(i)
    dup = {k:v for k,v in bykey.items() if len(v)>=2}
    out['duplicate_reference_key'] = [
        {'reference_key':k, 'reference_indices':sorted(v),
         'cited': k in seen} for k,v in sorted(dup.items(), key=lambda kv: min(kv[1]))]
    unique = {k:v[0] for k,v in bykey.items() if len(v)==1}
    matched = [k for k in cite_keys if k in unique]
    out['matched_works'] = len(matched)
    out['matched_occurrences'] = sum(1 for c in cites if c['citation_key'] in matched)
    out['ambiguous_citation'] = [k for k in cite_keys if k in dup]
    missing = [k for k in cite_keys if k not in unique and k not in dup]
    uncited = [ (i, refs[i]['reference_key']) for k,i in sorted(unique.items(), key=lambda kv: kv[1])
                if k not in seen ]
    pairs = []
    miss_left, unc_left = list(missing), list(uncited)
    for mk in list(miss_left):
        msn, myr = mk.rsplit('|',1)
        for (ri, rk) in list(unc_left):
            rsn, ryr = rk.rsplit('|',1)
            ev = None
            if myr==ryr and osa(msn,rsn)<=1 and len(msn)>=4: ev='surname_edit_distance_1'
            elif msn==rsn and myr.isdigit() and ryr.isdigit() and abs(int(myr)-int(ryr))==1: ev='year_adjacent'
            elif msn==rsn and myr.isdigit() and ryr.isdigit() and transposed(myr,ryr): ev='year_transposition'
            if ev:
                pairs.append({'citation_key':mk,'reference_index':ri,
                              'reference_key':rk,'evidence':ev})
                miss_left.remove(mk); unc_left.remove((ri,rk)); break
    out['possible_mismatch'] = pairs
    out['missing_reference'] = miss_left
    out['uncited_reference'] = unc_left
    return out

# ---------------------------------------------------------------- driver
def jline(o): return json.dumps(o, ensure_ascii=False, separators=(',', ':'))

def run(path):
    raw = open(path,'rb').read()
    text = normalize(raw)
    if text is None:
        print(jline({"type":"meta","spec_version":"3.3"}))
        print(jline({"type":"error","code":5,"reason":"invalid utf-8"})); return 5

    hs = headings(text)
    h1 = [h for h in hs if h[2]==1]; h2 = [h for h in hs if h[2]==2]
    if len(h1) >= 2 and len(h2) == 0:
        print(jline({"type":"meta","spec_version":"3.3"}))
        print(jline({"type":"error","code":4,"reason":"heading contract violated"})); return 4

    refhead = None
    for i,h in enumerate(hs):
        if h[2] in (2,3,4) and h[3].lower() in ('references','bibliography','works cited'):
            refhead = (i,h); break
    if refhead is None:
        print(jline({"type":"meta","spec_version":"3.3"}))
        print(jline({"type":"error","code":3,"reason":"references section not found"})); return 3

    i, h = refhead
    r0 = h[1] + 1
    r1 = len(text)
    for h2_ in hs[i+1:]:
        if h2_[2] <= h[2]: r1 = h2_[0]; break

    body_lo, body_hi = 0, h[0]
    hard = [(a, b+1) for a,b,_,_ in hs]
    for a,b,ln in line_spans(text):
        if ln.strip()=='' : hard.append((a, b+1))
    hard.sort()
    sents = sentences(text, body_lo, body_hi, hard)

    cands = candidates(text, body_lo, body_hi, sents)
    cparses, unres_c = parse_candidates(text, cands)

    # §6.3 occurrences: one per SEG per YEAR
    cites = []
    for style, gs, ge, ss, se, host, span in cparses:
        gtext = text[gs:ge]
        if style=='parenthetical':
            for sm in SEG_RE.finditer(gtext):
                seg = sm.group(0)
                sn = surname_of(seg)
                for ym in YR_RE.finditer(seg):
                    cites.append(mk_cite(text,'parenthetical',gs,ge,
                                         gs+sm.start(),gs+sm.end(),sn,ym.group(0),host,hs))
        else:
            sn = surname_of(gtext)
            paren = gtext[gtext.rindex('('):]
            for ym in YR_RE.finditer(paren):
                cites.append(mk_cite(text,'narrative',gs,ge,gs,ge,sn,ym.group(0),host,hs))

    cites.sort(key=lambda c:(c['group_start'], c['segment_start']))
    refs, unres_r = assemble(text, r0, r1)
    rec = reconcile(cites, refs)

    lines = [{"type":"meta","spec_version":"3.3"}]
    for i,c in enumerate(cites):
        lines.append({"type":"citation","index":i,**{k:c[k] for k in
            ('citation_group','citation_segment','citation_key','surname','year','style',
             'group_start','group_end','segment_start','segment_end','sentence',
             'sentence_start','sentence_position','section_level','section_name',
             'section_type','section_roles')}})
    unres_c.sort(key=lambda u:u[0])
    for i,(a,b,reason,host) in enumerate(unres_c):
        lvl,name,_,_ = section_at(hs, a)
        lines.append({"type":"unresolved_citation","index":i,"text":text[a:b],
                      "start":a,"end":b,"reason":reason,
                      "sentence": text[host[0]:host[1]] if host else "",
                      "sentence_start": host[0] if host else 0,
                      "section_level":lvl,"section_name":name})
    for i,r in enumerate(refs):
        lines.append({"type":"reference","index":i,"assembled":r['assembled'],
                      "reference_key":r['reference_key'],"surname":r['surname'],
                      "year":r['year'],"start":r['start'],"end":r['end'],
                      "validation_state":r['validation_state'],
                      "suspect_reasons":r['suspect_reasons']})
    for i,u in enumerate(unres_r):
        lines.append({"type":"unresolved_reference","index":i,**u})
    for k in rec['missing_reference']:
        ex = next((c['citation_segment'] for c in cites if c['citation_key']==k), "")
        n = sum(1 for c in cites if c['citation_key']==k)
        lines.append({"type":"missing_reference","citation_key":k,"example":ex,"occurrences":n})
    for ri,rk in rec['uncited_reference']:
        lines.append({"type":"uncited_reference","reference_index":ri,"reference_key":rk})
    for d in rec['duplicate_reference_key']:
        lines.append({"type":"duplicate_reference_key",**d})
    for k in rec['ambiguous_citation']:
        ex = next((c['citation_segment'] for c in cites if c['citation_key']==k), "")
        idx = [i for i,r in enumerate(refs) if r['reference_key']==k]
        lines.append({"type":"ambiguous_citation","citation_key":k,"example":ex,
                      "reference_indices":idx})
    for p in rec['possible_mismatch']:
        lines.append({"type":"possible_mismatch",**p})

    fail = (rec['missing_reference'] or rec['uncited_reference'] or rec['possible_mismatch']
            or rec['duplicate_reference_key'] or rec['ambiguous_citation']
            or unres_c or unres_r or any(r['validation_state']!='ok' for r in refs))
    code = 1 if fail else 0
    lines.append({"type":"summary","matched_occurrences":rec['matched_occurrences'],
                  "matched_works":rec['matched_works'],"exit":code})
    for l in lines: print(jline(l))
    return code

def section_at(hs, off):
    stack = []
    for a,b,lvl,name in hs:
        if a > off: break
        if lvl in (2,3,4):
            while stack and stack[-1][0] >= lvl: stack.pop()
            stack.append((lvl,name))
    if not stack: return "none","front matter","other",[]
    for lvl,name in reversed(stack):
        rs = roles_of(name)
        if rs: return f"h{stack[-1][0]}", stack[-1][1], rs[0], rs
    return f"h{stack[-1][0]}", stack[-1][1], "other", []

def mk_cite(text, style, gs, ge, ss, se, sn, yr, host, hs):
    lvl,name,st,rs = section_at(hs, gs)
    if host: s0,s1,ce = host
    else: s0,s1,ce = gs,ge,ge
    pos = 'start' if gs==s0 else ('end' if ge==ce else 'middle')
    return {'citation_group':text[gs:ge],'citation_segment':text[ss:se],
            'citation_key': f"{sn}|{norm_year(yr)}", 'surname':sn,'year':norm_year(yr),
            'style':style,'group_start':gs,'group_end':ge,
            'segment_start':ss,'segment_end':se,
            'sentence':text[s0:s1],'sentence_start':s0,'sentence_position':pos,
            'section_level':lvl,'section_name':name,'section_type':st,'section_roles':rs}

if __name__ == '__main__':
    sys.exit(run(sys.argv[1]))
