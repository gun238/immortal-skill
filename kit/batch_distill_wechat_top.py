#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,json,os,re,subprocess,sys,tempfile
from pathlib import Path
from collections import Counter

SCRIPT_DIR=Path(__file__).resolve().parent
PROJECT_DIR=SCRIPT_DIR.parent
CLI_PATH=SCRIPT_DIR/"immortal_cli.py"
DEFAULT_TEMPLATE=PROJECT_DIR/"prompts"/"codex-wechat-distill.md"
FORBID="occupation, education, income, health, political stance, religion, sensitive identity"
TOK=re.compile(r"[\u4e00-\u9fffA-Za-z0-9_@#]{2,}")
FENCE=re.compile(r"```(?:json)?\s*(\{[\s\S]*?\})\s*```",re.I)
NOISE=("发起了群收款","请点击升级至最新版","如需收钱，请点击升级至最新版")

def run(cmd,cwd):
    p=subprocess.run(cmd,cwd=str(cwd),capture_output=True,text=True)
    if p.returncode!=0: raise RuntimeError(p.stderr or p.stdout)

def clean(t:str)->str:
    x=(t or "").strip()
    for n in NOISE:
        if n in x: return ""
    return x

def load_csv(p:Path):
    with p.open("r",encoding="utf-8-sig",newline="") as f: return list(csv.DictReader(f))

def resolve_inputs(args):
    if args.stats_csv and args.dataset_map: return Path(args.stats_csv),Path(args.dataset_map)
    if args.summary_dir:
        d=Path(args.summary_dir); return d/"sender_stats.csv",d/"sender_dataset_map.json"
    d=PROJECT_DIR.parent/"fork-WeChatMsg"/"exports"/"weixin4"/"trainset"/"summary"
    return d/"sender_stats.csv",d/"sender_dataset_map.json"

def confidence(n:int): return "high" if n>=400 else "medium" if n>=120 else "low" if n>=30 else "very_low"

def tokens(rows,k=12):
    c=Counter()
    for r in rows:
        for t in TOK.findall(r["text"]):
            if not t.isdigit() and len(t)>1: c[t]+=1
    return c.most_common(k)

def quotes(rows,k=10):
    out=[]; seen=set()
    for r in rows:
        t=r["text"].replace("\n"," ").strip()
        if len(t)<3 or len(t)>120 or t in seen: continue
        seen.add(t); out.append((r.get("datetime",""),(r.get("session_display_name") or r.get("session_username") or "").strip(),t))
        if len(out)>=k: break
    return out

def rules_dims(name,rows):
    cfd=confidence(len(rows)); tok="; ".join([f"{t}({n})" for t,n in tokens(rows)]) or "none"
    q=[f"- \"{t}\" ({dt} / {s}) `verbatim`" for dt,s,t in quotes(rows)] or ["- insufficient quote samples"]
    inter=f"# Interaction: {name}\n- sample_count: {len(rows)} (`artifact`)\n- top_tokens: {tok} (`artifact`)\n\n## Quotes\n"+"\n".join(q)+"\n"
    mem=f"# Memory: {name}\n- keep observable timeline/topics only\n- low sample allowed with confidence labels: {cfd}\n- forbidden inference: {FORBID}\n"
    per=f"# Personality: {name}\n- infer style/tone tendencies from chat behaviors only (confidence: {cfd})\n- forbidden inference: {FORBID}\n"
    pro=f"# Procedure: {name}\n- infer conversational workflow preference (ask-then-act or act-then-report)\n- forbidden inference: {FORBID}\n"
    con="# Conflicts\n- no stable conflict detected in current sample\n"
    return {"interaction_md":inter,"memory_md":mem,"personality_md":per,"procedure_md":pro,"conflicts_md":con}

def load_template(path:Path):
    if path.exists(): return path.read_text(encoding="utf-8")
    return "Return ONE JSON object with keys: interaction_md,memory_md,personality_md,procedure_md,conflicts_md,reasoning_notes. Role-free. Allow low-sample inference with confidence labels. Forbid sensitive identity inference."

def codex_run(command,prompt,timeout):
    with tempfile.TemporaryDirectory(prefix="immortal_codex_") as td:
        pfile=Path(td)/"prompt.txt"; pfile.write_text(prompt,encoding="utf-8")
        c=command.replace("{prompt_file}",str(pfile)); use_file="{prompt_file}" in command
        p=subprocess.run(c,input=None if use_file else prompt,text=True,encoding="utf-8",errors="replace",capture_output=True,timeout=timeout,shell=True)
        if p.returncode!=0: raise RuntimeError(p.stderr or p.stdout or "codex command failed")
        return (p.stdout or p.stderr or "").strip()

def parse_obj(text):
    m=FENCE.search(text)
    if m: return json.loads(m.group(1))
    t=text.strip()
    if t.startswith("{") and t.endswith("}"): return json.loads(t)
    i,j=t.find("{"),t.rfind("}")
    if i>=0 and j>i: return json.loads(t[i:j+1])
    raise ValueError("no json object found")

def codex_dims(name,sender,rows,template,command,timeout,max_quotes):
    payload={"subject":{"name":name,"sender_username":sender,"message_count":len(rows),"confidence":confidence(len(rows))},"top_tokens":tokens(rows,20),"quotes":[{"datetime":d,"session":s,"text":t} for d,s,t in quotes(rows,max_quotes)],"forbidden_infer_fields":FORBID}
    prompt=template+"\n\nINPUT:\n```json\n"+json.dumps(payload,ensure_ascii=False,indent=2)+"\n```"
    obj=parse_obj(codex_run(command,prompt,timeout))
    need=["interaction_md","memory_md","personality_md","procedure_md","conflicts_md"]
    out={}
    for k in need:
        v=obj.get(k,"")
        if not isinstance(v,str) or not v.strip(): raise ValueError(f"missing field: {k}")
        out[k]=v if v.endswith("\n") else v+"\n"
    return out,str(obj.get("reasoning_notes",""))

def mk_skill(skill_id,name,sender,engine,dataset_csv):
    meta={"profile_mode":"wechat-adaptive","role_free":True,"distill_engine":engine,"forbidden_infer_fields":FORBID,"sender_username":sender,"dataset":str(dataset_csv),"platforms":["wechat"]}
    return "---\n"+f'name: "{skill_id}"\n'+f'description: "wechat 4-dim profile for {name}"\n'+"license: MIT\n"+f"metadata: {json.dumps(meta,ensure_ascii=False,separators=(',',':'))}\n"+"---\n\n"+f"# {name}\n\nTarget: `{sender}`\n\nRules:\n1. Always use 4 dimensions.\n2. Low sample allowed, must include confidence markers.\n3. Forbidden inference: "+FORBID+"\n"

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--stats-csv"); ap.add_argument("--dataset-map"); ap.add_argument("--summary-dir")
    ap.add_argument("--top-n",type=int,default=35); ap.add_argument("--min-messages",type=int,default=1)
    ap.add_argument("--out-base",default=str(PROJECT_DIR/"skills"/"immortals")); ap.add_argument("--report-base",default=str(PROJECT_DIR/"distill_outputs"))
    ap.add_argument("--dir-name-mode",default="nickname",choices=["slug","nickname"]); ap.add_argument("--force",action="store_true")
    ap.add_argument("--engine",default="codex",choices=["rules","codex","hybrid"]); ap.add_argument("--codex-command",default=os.environ.get("IMMORTAL_CODEX_COMMAND","codex"))
    ap.add_argument("--codex-timeout-sec",type=int,default=180); ap.add_argument("--codex-template",default=str(DEFAULT_TEMPLATE)); ap.add_argument("--codex-max-quotes",type=int,default=80)
    ap.add_argument("--codex-strict",action="store_true"); ap.add_argument("--note",default="wechat_adaptive_codex")
    args=ap.parse_args()
    stats_csv,map_path=resolve_inputs(args); out_base=Path(args.out_base); out_base.mkdir(parents=True,exist_ok=True)
    stats=load_csv(stats_csv)[:args.top_n]; ds_map=json.loads(Path(map_path).read_text(encoding="utf-8")); template=load_template(Path(args.codex_template))
    used=set(); used_dirs={p.name for p in out_base.iterdir() if p.is_dir()}; results=[]
    for rank,row in enumerate(stats,start=1):
        sender=(row.get("sender_username") or "").strip(); name=(row.get("sender_display_name") or "").strip() or sender; dsv=ds_map.get(sender)
        if not sender or not dsv: continue
        csv_path=Path(dsv); csv_path=csv_path if csv_path.is_absolute() else (Path(map_path).parent/csv_path).resolve()
        if not csv_path.exists(): continue
        rr=[]; [rr.append({**x,"text":t}) for x in load_csv(csv_path) if (t:=clean(x.get("text","")))]
        if len(rr)<args.min_messages: continue
        base=re.sub(r"[^a-z0-9]+","-",sender.lower()).strip("-") or "unknown"; sid=f"wx-{base}"; i=2
        while sid in used: sid=f"wx-{base}-{i}"; i+=1
        used.add(sid); dname=sid if args.dir_name_mode=="slug" else (name or "unnamed"); j=2
        while dname in used_dirs: dname=f"{name}_{j}"; j+=1
        used_dirs.add(dname)
        run([sys.executable,str(CLI_PATH),"init","--slug",sid,"--base",str(out_base)]+(["--force"] if args.force else []),PROJECT_DIR)
        note=""; engine_used="rules"
        if args.engine=="rules": dims=rules_dims(name,rr)
        else:
            try: dims,note=codex_dims(name,sender,rr,template,args.codex_command,args.codex_timeout_sec,args.codex_max_quotes); engine_used="codex"
            except Exception as e:
                if args.engine=="codex" and args.codex_strict: raise
                dims=rules_dims(name,rr); engine_used="rules-fallback"; note=f"codex_failed={e}"
        skill_dir=out_base/sid
        for fn,k in [("interaction.md","interaction_md"),("memory.md","memory_md"),("personality.md","personality_md"),("procedure.md","procedure_md"),("conflicts.md","conflicts_md")]:
            (skill_dir/fn).write_text(dims[k],encoding="utf-8")
        (skill_dir/"SKILL.md").write_text(mk_skill(sid,name,sender,engine_used,csv_path),encoding="utf-8")
        run([sys.executable,str(CLI_PATH),"stamp","--slug",sid,"--base",str(out_base),"--sources",f"wechat:{csv_path.name}","--note",args.note],PROJECT_DIR)
        final=out_base/dname
        if dname!=sid:
            if final.exists(): raise RuntimeError(f"target exists: {final}")
            skill_dir.rename(final)
        results.append({"rank":rank,"skill_id":sid,"dir_name":dname,"sender_username":sender,"sender_display_name":name,"message_count":len(rr),"confidence":confidence(len(rr)),"dataset_csv":str(csv_path),"skill_dir":str(final if dname!=sid else skill_dir),"requested_engine":args.engine,"engine_used":engine_used,"engine_note":note})
    ts=__import__("datetime").datetime.now().strftime("%Y%m%d_%H%M%S"); rdir=Path(args.report_base)/f"wechat_top{args.top_n}_{ts}"; rdir.mkdir(parents=True,exist_ok=True)
    (rdir/"distill_manifest.json").write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding="utf-8")
    with (rdir/"distill_manifest.csv").open("w",encoding="utf-8-sig",newline="") as f:
        w=csv.writer(f); w.writerow(["rank","skill_id","dir_name","sender_username","sender_display_name","message_count","confidence","dataset_csv","skill_dir","requested_engine","engine_used","engine_note"])
        [w.writerow([x[k] for k in ["rank","skill_id","dir_name","sender_username","sender_display_name","message_count","confidence","dataset_csv","skill_dir","requested_engine","engine_used","engine_note"]]) for x in results]
    print(f"distilled_count={len(results)}"); print(f"requested_engine={args.engine}"); print(f"codex_command={args.codex_command}"); print(f"report_json={rdir/'distill_manifest.json'}"); print(f"report_csv={rdir/'distill_manifest.csv'}")

if __name__=="__main__": main()
