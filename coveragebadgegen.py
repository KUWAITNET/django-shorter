import json
import urllib3, shutil
try:
    coverage = json.load(open("coverage.json"))
    coverage_percent = coverage['totals']['percent_covered_display'] + " \% only"
    try:
        url = "https://img.shields.io/badge/Coverage-" + str(coverage_percent) + "-green"
        http = urllib3.PoolManager()
        filename = "coverage_badge.svg"
        with open(filename, 'wb') as out:
            r = http.request('GET', url, preload_content=False)
            shutil.copyfileobj(r, out)
        
    except:
        print("Failed to retrieve badge.")

except:
    print("Failed to find coverage")