"""CLI: python -m quotation_engine.cli {profiles,new,validate,render,render-examples,verify-lock}."""
from __future__ import annotations
import argparse,hashlib,json,sys
from pathlib import Path
from .validation import ROOT,PROFILES,validate,ValidationError
from .renderer import render


def verify_lock():
    manifest=json.loads((Path(__file__).parent/'manifest.json').read_text())
    for name,expected in manifest['sha256'].items():
        p=ROOT/name
        if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=expected:
            raise ValidationError(f'Locked asset changed or missing: {name}')
    return manifest


def new_job(brand):
    # Deliberately no old client, dates, prices, tax or commercial defaults.
    return {'schema_version':2,'brand':brand,'template_id':PROFILES[brand]['template_id'],
        'title':'','quote_no':'','date':'','validity_days':None,'tax_treatment':'',
        'client':{k:'' for k in ('name','address','attention','role','location')},
        'prepared_by':{'name':'','role':''},'salutation':'','footer_label':'','amount_words':'',
        'expected_total':'0.00','introduction':[],
        'blocks':[{'type':'boq','title':'','items':[{'qty':'1','unit':'','description':'','unit_price':'0.00','amount':'0.00'}]}]}


def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__);sub=ap.add_subparsers(dest='cmd',required=True)
    sub.add_parser('profiles');sub.add_parser('verify-lock')
    new=sub.add_parser('new');new.add_argument('--brand',choices=PROFILES,required=True);new.add_argument('--output',required=True)
    for action in ('validate','render'):
        p=sub.add_parser(action);p.add_argument('job')
        if action=='render':p.add_argument('--output',required=True);p.add_argument('--overwrite',action='store_true')
    p=sub.add_parser('render-examples');p.add_argument('--output',required=True)
    args=ap.parse_args(argv)
    try:
        manifest=verify_lock()
        if args.cmd=='verify-lock':print('Verified '+manifest['release_id']);return 0
        if args.cmd=='profiles':print(json.dumps({k:{'id':v['template_id'],'status':v['status'],'page_points':v['page']} for k,v in PROFILES.items()},indent=2));return 0
        if args.cmd=='new':
            out=Path(args.output)
            if out.exists():raise ValidationError('Refusing to overwrite an existing job.')
            out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(new_job(args.brand),indent=2));print(out);return 0
        if args.cmd=='render-examples':
            for src in sorted((Path(__file__).parent/'examples').glob('cpsc-*.json')):
                j=json.loads(src.read_text());print(render(j,Path(args.output)/(src.stem+'.pdf')))
            return 0
        src=Path(args.job);job=json.loads(src.read_text());result=validate(job)
        if args.cmd=='validate':print(json.dumps(result,indent=2));return 0
        out=Path(args.output)
        if out.exists() and not args.overwrite:raise ValidationError('Use a new revision filename or --overwrite explicitly.')
        render(job,out)
        result.update({'job_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'pdf_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'pdf':str(out),'visual_review':'REQUIRED_BEFORE_DELIVERY'})
        out.with_suffix('.audit.json').write_text(json.dumps(result,indent=2));print(out);return 0
    except (ValueError,KeyError,OSError,RuntimeError) as exc:
        print(str(exc),file=sys.stderr);return 2

if __name__=='__main__':raise SystemExit(main())
