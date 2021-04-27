import random
import sys
sys.path.append("C:\Sneaks4Sure\Scrapper\my_env\Lib\site-packages")
from selenium import webdriver
from selenium.common.exceptions import UnexpectedAlertPresentException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC 
from selenium.webdriver.support.ui import WebDriverWait

import os
import numpy as np
import time
import zipfile

proxies = []


def get_random_hdr():
    random_hdr = ''
    header_file = 'header.txt'
    try:
        with open(header_file) as f:
            lines = f.readlines()
        if len(lines) > 0:
            prng = np.random.RandomState()
            index = prng.permutation(len(lines) - 1)
            idx = np.asarray(index, dtype=np.integer)[0]
            random_hdr = lines[int(idx)]
    except Exception as ex:
        print('Exception in random_ua')
        print(str(ex))
    finally:
        return random_hdr
def get_proxy_option(PROXY_HOST, PROXY_PORT, PROXY_USER, PROXY_PASS):
    manifest_json = """
    {
        "version": "1.0.0",
        "manifest_version": 2,
        "name": "Chrome Proxy",
        "permissions": [
            "proxy",
            "tabs",
            "unlimitedStorage",
            "storage",
            "<all_urls>",
            "webRequest",
            "webRequestBlocking"
        ],
        "background": {
            "scripts": ["background.js"]
        },
        "minimum_chrome_version":"22.0.0"
    }
    """

    background_js = """
    var config = {
            mode: "fixed_servers",
            rules: {
                singleProxy: {
                scheme: "http",
                host: "%s",
                port: parseInt(%s)
                },
                bypassList: ["localhost"]
            }
            };

    chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

    function callbackFn(details) {
        return {
            authCredentials: {
                username: "%s",
                password: "%s"
            }
        };
    }

    chrome.webRequest.onAuthRequired.addListener(
                callbackFn,
                {urls: ["<all_urls>"]},
                ['blocking']
    );
    """ % (PROXY_HOST, PROXY_PORT, PROXY_USER, PROXY_PASS)

    chrome_options = webdriver.ChromeOptions()
    pluginfile = 'proxy_auth_plugin.zip'
    # PROXY = PROXY_HOST + ":"+ PROXY_PORT
    with zipfile.ZipFile(pluginfile, 'w') as zp:
        zp.writestr("manifest.json", manifest_json)
        zp.writestr("background.js", background_js)
    # chrome_options.add_argument('--proxy-server=%s' % PROXY)
    chrome_options.add_extension(pluginfile)
    chrome_options.add_argument("--user-data-dir=WithProxy")
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--ignore-ssl-errors")
    chrome_options.add_argument("--system-developer-mode")
    chrome_options.add_argument("--no-first-run")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument("--disable-gpu")
    return chrome_options

def get_random_proxy():
    random_proxy = ''
    proxy_instance = {
        'http': "http://54.158.31.196:443",
        'https': "https://54.158.31.196:443"
    }
    proxy_file = 'proxy.txt'
    try:
        with open(proxy_file) as f:
            lines = f.readlines()
        if len(lines) > 0:
            # prng = np.random.RandomState()
            # index = prng.permutation(len(lines) - 1)
            idx = random.randint(0, len(lines) - 1)
            selected_proxy = lines[int(idx)]
            random_proxy = selected_proxy.strip()
            proxy = random_proxy.split(':')
            http_proxy = "http://" + proxy[2] + ":" + proxy[3] + "@" + proxy[0] + ":" + proxy[1] 
            https_proxy = "https://" + proxy[2] + ":" + proxy[3] + "@" + proxy[0] + ":" + proxy[1]
            # http_proxy = "http://" + random_proxy 
            # https_proxy = "https://" + random_proxy
            proxy_instance['http'] = http_proxy
            proxy_instance['https'] = https_proxy
            
            # proxy = ['161.97.101.134', '3691', 'zeboss', 'qMtO8OUs']
            # _options = get_proxy_option(proxy[0], proxy[1], proxy[2], proxy[3])
        pass
    except Exception as ex:
        print('Exception in random_proxy')
        print(str(ex))
    finally:
        return proxy_instance
        # return proxy[0], proxy[1], _options
def get_proxy_option_forGoat(PROXY_HOST, PROXY_PORT, PROXY_USER, PROXY_PASS):
    manifest_json = """
    {
        "version": "1.0.0",
        "manifest_version": 2,
        "name": "Chrome Proxy",
        "permissions": [
            "proxy",
            "tabs",
            "unlimitedStorage",
            "storage",
            "<all_urls>",
            "webRequest",
            "webRequestBlocking"
        ],
        "background": {
            "scripts": ["background.js"]
        },
        "minimum_chrome_version":"22.0.0"
    }
    """

    background_js = """
    var config = {
        "mode": "pac_script",
        "pacScript": {
            "data": "function FindProxyForURL(url, host) 
            {
                var rules = [\"*.*\"];
                var proxyServers = '%s:%s';                
                for (var i = 0, l = rules.length; i < l; i++) 
                {
                    if (host === rules[i] || host.substr(-rules[i].length - 1) === ('.'+rules[i]))                           return 'DIRECT';\n                    }\n                    return proxyServers;\n                }\n            "
                }
            };

        chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});
        function callbackFn(details) {
            return {
                authCredentials: {
                    username: "%s",
                    password: "%s"
                }
            };
        }

    chrome.webRequest.onAuthRequired.addListener(
                callbackFn,
                {urls: ["<all_urls>"]},
                ['blocking']
    );""" % (PROXY_HOST, PROXY_PORT, PROXY_USER, PROXY_PASS)

    chrome_options = webdriver.ChromeOptions()
    pluginfile = 'proxy_auth_plugin.zip'
    # PROXY = PROXY_HOST + ":"+ PROXY_PORT
    with zipfile.ZipFile(pluginfile, 'w') as zp:
        zp.writestr("manifest.json", manifest_json)
        zp.writestr("background.js", background_js)
    # chrome_options.add_argument('--proxy-server=%s' % PROXY)
    chrome_options.add_extension(pluginfile)
    chrome_options.add_argument("--user-data-dir=WithProxy")
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--ignore-ssl-errors")
    chrome_options.add_argument("--system-developer-mode")
    chrome_options.add_argument("--no-first-run")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument("--disable-gpu")
    return chrome_options

def get_random_proxy_forGoat():
    random_proxy = ''
    proxy_instance = ''
    proxy_file = 'realProxy.txt'
    try:
        with open(proxy_file) as f:
            lines = f.readlines()
        if len(lines) > 0:
            # prng = np.random.RandomState()
            # index = prng.permutation(len(lines) - 1)
            idx = random.randint(0, len(lines) - 1)
            selected_proxy = lines[int(idx)]
            random_proxy = selected_proxy.strip()
            proxy = random_proxy.split(':')
            proxy_instance = random_proxy
            # _options = get_proxy_option_forGoat(proxy[0], proxy[1], proxy[2], proxy[3])
        pass
    except Exception as ex:
        print('Exception in random_proxy')
        print(str(ex))
    finally:
        return proxy_instance
        # return proxy[0], proxy[1], _options

def proxy_setting():
    proxy_file = 'proxy-2.txt'
    proxy_signFile = 'Sign-Proxy.txt'
    try:
        with open(proxy_file) as f:
            lines = f.readlines()
        proxy_list = list(dict.fromkeys(lines))
        with open(proxy_signFile) as ff:
            sign_lines = ff.readlines()
        signproxy_list = list(dict.fromkeys(sign_lines))

        real_proxyList = list(set(proxy_list) - set(signproxy_list))
        with open('realProxy.txt', 'w') as f:
            for item in real_proxyList:
                f.write("%s" % item)
        length = len(real_proxyList)
    except Exception as ex:
        print(ex)
# proxy_setting()

# get_random_proxy_forGoat()