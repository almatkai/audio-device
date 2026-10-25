#!/usr/bin/env python3
"""Fetch verified helpers for a package build. Does not execute them."""
import argparse,hashlib,json,os,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class HTTPSRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl):
        if not newurl.startswith('https://'):raise ValueError('Helper redirect must use HTTPS')
        return super().redirect_request(req,fp,code,msg,headers,newurl)
def verify(data,descriptor):
    if len(data)>16*1024*1024 or hashlib.sha256(data).hexdigest()!=descriptor['expected_sha256']:raise ValueError('Helper size or SHA-256 mismatch: '+descriptor['filename'])
def prepare(target):
    if target not in ['aarch64-apple-darwin','x86_64-pc-windows-msvc']:raise ValueError('Unsupported helper target')
    destination=ROOT/'stage/helpers';destination.mkdir(parents=True,exist_ok=True)
    for d in json.loads((ROOT/'provenance/helpers.json').read_text()):
        if d['filename'].endswith('.exe')!=(target=='x86_64-pc-windows-msvc'):continue
        path=destination/d['filename']
        if path.exists():
            try:verify(path.read_bytes(),d);continue
            except ValueError:pass
        if not d['url'].startswith('https://'):raise ValueError('Helper URL must use HTTPS')
        with urllib.request.build_opener(HTTPSRedirect()).open(d['url'],timeout=30) as response:
            if not response.url.startswith('https://'):raise ValueError('Helper response must use HTTPS')
            data=response.read(16*1024*1024+1)
        verify(data,d);temporary=path.with_suffix('.download');temporary.write_bytes(data);temporary.chmod(0o755);os.replace(temporary,path)
        print(d['filename'],d['expected_sha256'])
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--target',required=True);a=p.parse_args();prepare(a.target)
