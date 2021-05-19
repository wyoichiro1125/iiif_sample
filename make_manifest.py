#!/usr/bin/python3
import sys
import glob
import os
import csv
import datetime
import hashlib
import re
import json
from PIL import Image

#IIIF manifest の作成
base_url = 'https://wyoichiro1125.github.io/iiif_sample/'
#ここ↑はマニフェストが設置されるURLに応じて書き換える
base_image_url = "https://wyoichiro1125.github.io/iiif_sample/image/"
all_bib = {}
all_bib2 = {}
bib_title = []
mani_keys = ['dir','title','license','attribution','within','logo', 'description','viewingHint','viewingDirection']

df = pd.read_excel("sample_manifest.xlsx", header=0, index_col=None, dtype=str)
#rn = 0
for index, row in df.iterrows():
    link_name = row["Study ID"]#dir の名前と対応；このあたりをどうするかという問題、階層性とか
    all_bib[link_name] = row

for key in all_bib.keys():
    each_manifest = {}
    all_meta = []
    file_dir0 = "./image/" + key
    glob_name = "./image/" + key +"/*.jpg"
    if os.path.isdir(key):
        list_file_names = sorted(glob.glob(glob_name))
    if len(list_file_names) == 0:
        glob_name = key+"/*.jpg"
        list_file_names = sorted(glob.glob(glob_name))
    
    each_manifest["label"] = all_bib[key]["Title"]
    each_manifest["license"] = all_bib[key]["License"]
    each_manifest["attribution"] = all_bib[key]["Distributor"]

    each_manifest['@id'] = base_image_url+key+'/manifest.json'
    each_manifest['@type'] = 'sc:Manifest'
    each_manifest['@context'] = 'http://iiif.io/api/presentation/2/context.json'
    each_manifest['metadata'] = all_meta
    
    for mani_key in mani_keys:
        if mani_key == "dir" or mani_key == "title":
            pass
        elif not(mani_key in each_manifest.keys()):
            each_manifest[mani_key] = ""

    cn = 0
    canvases = []
    sequence = {}
    for file_path in list_file_names:
        mani_image = {}
        
        file_dir = os.path.split(file_path)[0]
        if os.path.isdir(file_dir):
            cn = cn + 1
            resource = {}
            canvas = {}
            canvas_number = 'p'+str(cn)+'.json'
            image_url_id = base_image_url+file_path
            img = Image.open(file_path)
            width, height = img.size
            
            mani_image["@type"]= 'oa:Annotation'
            mani_image["motivation"] = "sc:painting"
            resource["@id"] = image_url_id
            resource["@type"] = "dctypes:Image"
            resource["width"] = width
            resource["height"] = height            
            mani_image['resource']  = resource
            mani_image['on']  = str(cn)
            
            canvas['@id'] = mani_image["on"]
            canvas['@type'] = 'sc:Canvas'
            canvas['label'] = 'p. '+str(cn)
            canvas['width'] = width
            canvas['height'] = height
            
            canvas_image = []
            canvas_image.append(mani_image)
            canvas['images'] = canvas_image
            
            
            
            canvases.append(canvas)
    sequence['@type'] =  'sc:Sequence'
    sequence['canvases'] = canvases
    each_manifest['sequences'] = []
    each_manifest['sequences'].append(sequence)
    write_file_path = file_dir0+'/manifest.json'
    with open(write_file_path, mode='w') as f:
        json.dump(each_manifest, f, ensure_ascii=False)
        
        
# jpcoar の作成        
jpcoar_format = """<?xml version="1.0" encoding="UTF-8"?>
<jpcoar:jpcoar
    xmlns:jpcoar="https://github.com/JPCOAR/schema/blob/master/1.0/" 
    xmlns:dc="http://purl.org/dc/elements/1.1/" 
    xmlns:dcterms="http://purl.org/dc/terms/" 
    xmlns:rioxxterms="http://www.rioxx.net/schema/v2.0/rioxxterms/" 
    xmlns:datacite="https://schema.datacite.org/meta/kernel-4/" 
    xmlns:oaire="http://namespace.openaire.eu/schema/oaire/" 
    xmlns:dcndl="http://ndl.go.jp/dcndl/terms/" 
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" 
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
    xsi:schemaLocation="https://github.com/JPCOAR/schema/blob/master/1.0/jpcoar_scm.xsd">
    <dc:title xml:lang="ja">{Title}</dc:title>
    <jpcoar:creator>
        <jpcoar:creatorName xml:lang="ja">{Author}</jpcoar:creatorName>
    </jpcoar:creator>
    <dcterms:accessRights rdf:resource="http://purl.org/coar/access_right/c_abf2">open access</dcterms:accessRights>
    <jpcoar:rightsHolder>
        <jpcoar:rightsHolderName xml:lang="ja">{Publisher}</jpcoar:rightsHolderName>
    </jpcoar:rightsHolder>
    <jpcoar:relation relationType="references">
        <jpcoar:relatedIdentifier identifierType="Local">{label}</jpcoar:relatedIdentifier>
    </jpcoar:relation>
    <dc:language>{DataLanguage}</dc:language>
    <dc:type rdf:resource="http://purl.org/coar/resource_type/c_2f33">Book</dc:type>
    <jpcoar:sourceTitle xml:lang="ja">{Series}</jpcoar:sourceTitle>
    <jpcoar:URI objectType="other" label="{label}">{URI}</jpcoar:URI>
</jpcoar:jpcoar>"""


df = pd.read_excel("sample_manifest.xlsx", header=0, dtype=str)

for index, row in df.iterrows():
    output = jpcoar_format.format(Title=row["Title"], Author=row["Author"], Publisher=row["Publisher"], DataLanguage = row["Data Language"],  label=row["Study ID"], Series=row["Series"], URI=row["URI"])
    with open("./metadata/{}.xml".format(row["Study ID"]), mode="w", encoding="utf-8") as f:
        f.write(output)
        
        
def file_md5(file_path, size=4096):
    m = hashlib.md5()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(size * m.block_size), b''):
            m.update(chunk)
    return m.hexdigest()

now = str(datetime.datetime.utcnow())

now = re.sub(r"\.\d+", "Z", now)
now = now.replace(" ", "T")

pref = """<?xml version='1.0' encoding='UTF-8'?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:rs="http://www.openarchives.org/rs/terms/">
<rs:md at="{}" capability="resourcelist" completed="{} " />""".format(now, now)



directory = "./metadata/"
files = os.listdir(directory)

for f in files:
    path = directory + f
    filename = f
    hs = file_md5(path)
    lastmod = datetime.datetime.utcfromtimestamp(os.path.getmtime(path))
    length = os.path.getsize(path)
    template = """
    <url>
	    <loc>{}metadata/{}</loc>
	    <lastmod>{}</lastmod>
	    <rs:md hash="md5:{}" length="{}" type="application/xml" />
    </url>""".format(base_url, filename, lastmod, hs, length)

    pref = pref + template

pref = re.sub(r"""(<lastmod>.*?) (.*?</lastmod>)""", r"""\1T\2""", pref)
pref = re.sub(r"""(<lastmod>.*?)\.\d+(</lastmod>)""", r"\1Z\2", pref)

pref = pref + "\n</urlset>"
with open("./metadata/Resourcelist.xml", mode="w", encoding="utf-8") as g:
    g.write(pref)