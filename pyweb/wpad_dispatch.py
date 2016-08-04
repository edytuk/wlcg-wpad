# Dispatch a wpad.dat request
# If the URL ends with ?ip=ADDR then use ADDR instead of $REMOTE_ADDR

import sys, urlparse
import wlcg_wpad
from wpad_utils import *
import geosort

geosortconffile = '/var/lib/wlcg-wpad/geosort.conf'

def error_request(start_response, response_code, response_body):
    response_body = response_body + '\n'
    start_response(response_code,
                   [('Cache-control', 'max-age=0'),
                    ('Content-Length', str(len(response_body)))])
    return [response_body]

def bad_request(start_response, host, ip, reason):
    response_body = 'Bad Request: ' + reason
    logmsg(host, ip, 'bad request: ' + reason)
    return error_request(start_response, '400 Bad Request', response_body)

def good_request(start_response, response_body):
    response_code = '200 OK'
    start_response(response_code,
                  [('Content-Type', 'text/plain'),
                   ('Cache-control', 'max-age=0'),
                   ('Content-Length', str(len(response_body)))])
    return [response_body]

def parse_geosort_conf():
    hostproxies = []
    try:
	for line in open(geosortconffile, 'r').read().split('\n'):
	    words = line.split()
	    if words:
		if words[0] == 'hostproxies':
		    parts = words[1].split('=')
		    proxies = parts[1].split(',')
		    hostproxies.append([parts[0], proxies])
    except Exception, e:
	logmsg('-', '-', 'error reading ' + geosortconffile + ', continuing: ' + str(e))
    return hostproxies

hostproxies = parse_geosort_conf()

def dispatch(environ, start_response):
    if 'SERVER_NAME' not in environ:
	return bad_request(start_response, 'wpad-dispatch', '-', 'SERVER_NAME not set')
    if 'REMOTE_ADDR' not in environ:
	return bad_request(start_response, 'wpad-dispatch', '-', 'REMOTE_ADDR not set')
    proxies = []
    host = environ['SERVER_NAME']
    remoteip = environ['REMOTE_ADDR']
    if 'QUERY_STRING' in environ:
	parameters = urlparse.parse_qs(environ['QUERY_STRING'])
	if 'ip' in parameters:
	    # for testing
	    remoteip = parameters['ip'][0]
    if host == 'wlcg-wpad.cern.ch':
	proxies, errmsg = wlcg_wpad.get_proxies(host, remoteip)
	if errmsg != None:
	    return bad_request(start_response, host, remoteip, errmsg)
    else:
        gotone = False
        for hostproxy in hostproxies:
            if host == hostproxy[0]:
                gotone = True
                proxies, errmsg = geosort.sort_proxies(remoteip, hostproxy[1])
                if errmsg != None:
                    return bad_request(start_response, host, remoteip, errmsg)
		break
        if not gotone:
            return bad_request(start_response, host, remoteip, 'Unrecognized host name')
	logmsg(host, remoteip, 'squids are ' + ';'.join(proxies))
    if proxies == []:
	return bad_request(start_response, host, remoteip, 'No proxy found for ' + remoteip)
    proxystr = ""
    for proxy in proxies:
	if proxystr != "":
	    proxystr += "; "
	proxystr += "PROXY http://" + str(proxy)
	if proxy.find(':') == -1:
	    proxystr += ":3128"
    body = 'function FindProxyForURL(url, host) {\n' + \
    	   '    return "' + proxystr + '"\n' + \
	   '}\n'
    return good_request(start_response, body)
