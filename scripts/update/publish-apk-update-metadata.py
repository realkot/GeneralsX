#!/usr/bin/env python3
"""Attach immutable update metadata to an already published, verified owner APK."""
import argparse,hashlib,json,os,urllib.request,urllib.parse

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--tag',required=True);parser.add_argument('--package',required=True);parser.add_argument('--code',required=True,type=int);parser.add_argument('--version',required=True);parser.add_argument('--apk',required=True);args=parser.parse_args()
    if args.package not in ('com.generalsx.zerohour','com.generalsx.zerohour.inputtest'):raise SystemExit('Unsupported package')
    token=os.environ.get('GH_TOKEN') or os.environ['GITHUB_TOKEN']
    headers={'Authorization':'Bearer '+token,'Accept':'application/vnd.github+json','User-Agent':'GeneralsX-realkot-release'}
    repo='/repos/realkot/GeneralsX'
    def get(path):
        with urllib.request.urlopen(urllib.request.Request('https://api.github.com'+path,headers=headers),timeout=30) as response:return json.load(response)
    release=get(repo+'/releases/tags/'+urllib.parse.quote(args.tag,safe=''))
    # GeneralsX @bugfix Codex 17/10/2026 Draft asset URLs change on publication.
    if release.get('draft'):raise SystemExit('Publish the release before attaching immutable update metadata')
    assets=get(repo+f'/releases/{release["id"]}/assets?per_page=100')
    apk=next(a for a in assets if a['name']==args.apk and a['state']=='uploaded')
    if not apk.get('digest','').startswith('sha256:'):raise SystemExit('Server APK digest unavailable')
    data=json.dumps({'schema':1,'package':args.package,'versionCode':args.code,'versionName':args.version,'bytes':apk['size'],'sha256':apk['digest'][7:],'url':apk['browser_download_url']},indent=2).encode()
    old=next((a for a in assets if a['name']=='update.json'),None)
    if old:
        if old.get('digest')!='sha256:'+hashlib.sha256(data).hexdigest():raise SystemExit('Different update.json already published; never overwrite a release identity')
        print('Metadata already matches');return
    url=release['upload_url'].split('{')[0]+'?name=update.json'
    if urllib.parse.urlsplit(url).hostname!='uploads.github.com':raise SystemExit('Unexpected upload host')
    req=urllib.request.Request(url,data=data,headers={**headers,'Content-Type':'application/json'},method='POST')
    with urllib.request.urlopen(req,timeout=60) as response:asset=json.load(response)
    assert asset['digest']=='sha256:'+hashlib.sha256(data).hexdigest()
    print('Published update.json for '+args.tag)

if __name__=='__main__':main()
