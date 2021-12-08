import json
import urllib3, shutil

try:
    coverage = json.load(open('coverage.json'))
    coverage_percent = coverage['totals']['percent_covered_display'] + "%"
    try:
        url_to_dl = "https://img.shields.io/badge/Coverage-" + coverage_percent + "-green"
        
        c = urllib3.PoolManager()
        filename = "coverage_badge.svg"
        with c.request('GET',url_to_dl, preload_content=False) as resp, open(filename, 'wb') as out_file:
            shutil.copyfileobj(resp, out_file)
    except:
        print("Failed to fetch badge")
except:
    print("Failed to read json")