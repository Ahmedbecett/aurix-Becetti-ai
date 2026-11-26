#!/usr/bin/env python3
"""Read-only public HTTP/TLS/sitemap diagnostics. No credentials or deployment.
A spoofed Googlebot UA tests only UA-based responses, NOT actual Google IP access.
"""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import Request, build_opener, HTTPRedirectHandler
from urllib.error import HTTPError
from urllib.parse import urlsplit
from urllib.robotparser import RobotFileParser
import hashlib
import json
import socket
import ssl
import xml.etree.ElementTree as ET

HOST='aurix-ea09b.web.app'
BASE='https://'+HOST
UA={
    'ordinary':'Mozilla/5.0 AURIX-Public-Sitemap-Diagnostic/1.0',
    'googlebot-ua-only':'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'
}
HEADERS=['content-type','content-length','content-encoding','cache-control','etag','last-modified','location','server','x-robots-tag','content-security-policy','vary']
class Redirects(HTTPRedirectHandler):
    def __init__(self):super().__init__();self.chain=[]
    def redirect_request(self,request,fp,code,msg,headers,newurl):
        self.chain.append({'from':request.full_url,'status':code,'to':newurl})
        return super().redirect_request(request,fp,code,msg,headers,newurl)

class Meta(HTMLParser):
    def __init__(self):super().__init__();self.meta={};self.canonical=[];self.h1=0
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='meta':self.meta[a.get('name','').lower()]=a.get('content','')
        if tag=='link' and a.get('rel')=='canonical':self.canonical.append(a.get('href'))
        if tag=='h1':self.h1+=1

def fetch(path,kind='ordinary',origin=BASE):
    url=origin+path
    redirect=Redirects(); opener=build_opener(redirect)
    result={'url':url,'requestUserAgent':kind}
    try:
        request=Request(url,headers={'User-Agent':UA[kind],'Accept':'*/*','Cache-Control':'no-cache'})
        try:response=opener.open(request,timeout=20)
        except HTTPError as error:response=error
        with response:
            body=response.read(1_000_001)
            result.update({'status':response.status,'finalUrl':response.url,'redirects':redirect.chain,
              'headers':{key:response.headers.get(key) for key in HEADERS if response.headers.get(key) is not None},
              'bytes':len(body),'sha256':hashlib.sha256(body).hexdigest()})
            text=body.decode('utf-8-sig')
            if path.endswith('/sitemap.xml'):
                result['rawPrefix']=text[:150]
                try:
                    root=ET.fromstring(text)
                    result['xmlRoot']=root.tag
                    result['locations']=[e.text for e in root.findall('{http://www.sitemaps.org/schemas/sitemap/0.9}url/{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
                    result['validSitemapXML']=root.tag=='{http://www.sitemaps.org/schemas/sitemap/0.9}urlset' and bool(result['locations'])
                except ET.ParseError as error:result['validSitemapXML']=False;result['xmlError']=str(error)
            elif path.endswith('/sitemap.txt'):
                result['locations']=[line.strip() for line in text.splitlines() if line.strip()]
                result['allLinesAbsoluteHttps']=all(line.startswith('https://') for line in result['locations'])
            elif path.endswith('/robots.txt'):
                result['body']=text
            elif path.endswith('google16fac1570d0d10bd.html'):
                result['body']=text
            elif response.headers.get('content-type','').startswith('text/html'):
                page=Meta();page.feed(text)
                result['robotsMeta']=page.meta.get('robots')
                result['canonical']=page.canonical;result['h1']=page.h1
                result['titleDescriptionPresent']=bool(page.meta.get('description'))
    except Exception as error:result['error']=type(error).__name__+': '+str(error)
    return result

def connection():
    result={}
    try:
        addresses=socket.getaddrinfo(HOST,443,type=socket.SOCK_STREAM)
        result['dnsAddresses']=sorted({item[4][0] for item in addresses})
        context=ssl.create_default_context()
        with socket.create_connection((HOST,443),timeout=15) as sock:
            with context.wrap_socket(sock,server_hostname=HOST) as secured:
                cert=secured.getpeercert()
                result.update({'tlsVerified':True,'tlsProtocol':secured.version(),'certificateNotBefore':cert.get('notBefore'),'certificateNotAfter':cert.get('notAfter')})
    except Exception as error:result['error']=type(error).__name__+': '+str(error)
    return result

report={'observedAtUTC':datetime.now(timezone.utc).isoformat(),'vantagePoint':'GitHub-hosted Ubuntu runner, not Google Search Console','connection':connection()}
tasks=[('/sitemap.xml','ordinary',BASE),('/sitemap.xml','googlebot-ua-only',BASE),('/sitemap.txt','ordinary',BASE),('/sitemap.txt','googlebot-ua-only',BASE),('/robots.txt','ordinary',BASE),('/google16fac1570d0d10bd.html','ordinary',BASE),('/sitemap.xml','ordinary','https://aurix-ea09b.firebaseapp.com'),('/not-a-real-aurix-diagnostic-page','ordinary',BASE)]
with ThreadPoolExecutor(max_workers=4) as pool:report['responses']=list(pool.map(lambda args:fetch(*args),tasks))
xml=report['responses'][0];plain=report['responses'][2];robots=report['responses'][4]
urls=xml.get('locations',[])
with ThreadPoolExecutor(max_workers=4) as pool:
    report['sitemapPages']=list(pool.map(lambda url:fetch(urlsplit(url).path or '/'),[url for url in urls if urlsplit(url).netloc==HOST]))
rules=RobotFileParser();rules.parse(robots.get('body','').splitlines())
report['checks']={
    'primaryXMLHTTP200':xml.get('status')==200,
    'validSitemapNamespaceAndXML':xml.get('validSitemapXML',False),
    'xmlAndTextURLsMatch':urls==plain.get('locations'),
    'noDuplicateLocations':len(urls)==len(set(urls)),
    'allLocationsUseCorrectHttpsHost':bool(urls) and all(url.startswith(BASE+'/') for url in urls),
    'googlebotUAXMLHTTP200':report['responses'][1].get('status')==200,
    'googlebotUAXMLSameBody':xml.get('sha256')==report['responses'][1].get('sha256'),
    'robotsAllowsGooglebotSitemap':rules.can_fetch('Googlebot',BASE+'/sitemap.xml'),
    'allListedPagesHTTP200':bool(report['sitemapPages']) and all(p.get('status')==200 for p in report['sitemapPages']),
    'listedPagesNotNoindex':all('noindex' not in ((p.get('robotsMeta') or '')+' '+p.get('headers',{}).get('x-robots-tag','')).lower() for p in report['sitemapPages']),
    'listedPagesSelfCanonical':all(p.get('canonical')==[p['url']] for p in report['sitemapPages']),
    'googleVerificationExact':report['responses'][5].get('body','').strip()=='google-site-verification: google16fac1570d0d10bd.html',
    'notFoundReturns404':report['responses'][7].get('status')==404,
}
report['limitations']=['Googlebot User-Agent is not a request from a verified Google crawler IP.','This cannot read Search Console property ownership, its detailed error, historical fetches, indexing status, or Google internal connectivity.','A successful current request does not disprove an earlier transient outage.','No production site, robots file, hosting configuration, or sitemap was modified.']
report['allChecksPass']=all(report['checks'].values())
Path('sitemap-live-diagnostics.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
