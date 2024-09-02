#!/bin/env python3

from signal import SIGINT,SIG_DFL,signal
signal(SIGINT, SIG_DFL) 

from requests import get,ConnectionError,RequestException
from threading import Thread
from queue import Queue
from time import sleep
from argparse import ArgumentParser,RawDescriptionHelpFormatter,SUPPRESS
from textwrap import dedent
from sys import stdout
from tqdm import tqdm


wordlist_parsed = Queue()
thread = []
headers = {}
data = {}



def default():
    tqdm.write(f'''
    ___ _       __     __  
   /   | |     / /__  / /_ 
  / /| | | /| / / _ \/ __ \\
 / ___ | |/ |/ /  __/ /_/ /
/_/  |_|__/|__/\___/_.___/ 
                           
                         
Author: DamianoGubiani
''')




def wordlist_parser(wordlist):

    if parsed.extension is not None:
        with open(wordlist,'r') as f:
            for i in f:
                for a in parsed.extension:
                    wordlist_parsed.put(i.strip()+a) 

    with open(wordlist,'r') as f:
        for i in f:
                wordlist_parsed.put(i.strip())



def fuzzer(target,q):

    while not q.empty():

        try:
                
            value = q.get()
            url = target[0]+value+target[1]
                
            if parsed.header is not None or parsed.data is not None:
                result = get(url=url,headers=headers,data=data) 
            else:
                result = get(url=url)
                

            if str(len(result.text)) in parsed.filter_words or str(result.status_code) in parsed.filter_status:
                tqdm.write(f'{url} words [{len(result.text)}]  status [{result.status_code}]')
            elif str(len(result.text)) in parsed.hide_words or result.status_code in parsed.hide_status:
                pass
            else:
                tqdm.write(f'{url} words [{len(result.text)}]  status [{result.status_code}]')

        except ConnectionError:
            pass    
        except RequestException:
            pass
        except Exception:
            exit(1)
            
        pbar.update(1)
        q.task_done()
         




if __name__ == '__main__':

    parse = ArgumentParser(usage=SUPPRESS,formatter_class=RawDescriptionHelpFormatter,description=dedent('''\
                                                                                                                          
    ___ _       __     __  
   /   | |     / /__  / /_ 
  / /| | | /| / / _ \/ __ \\
 / ___ | |/ |/ /  __/ /_/ /
/_/  |_|__/|__/\___/_.___/ 
                           
                         
Author: DamianoGubiani
                       
aweb is a web fuzzing tool where u can change varius thing 
and filter by status or words of a request you need to change 
the word you want to fuzz with the word FUZZ
example:
                                                                                                                          
./aweb.py -u 'https://FUZZ.google.com' -w path/to/wordlist
                                                                                                                          
'''))

    parse.add_argument('-w',type=str,dest='wordlist_path',required=True,action='store',
                        help='')

    parse.add_argument('-u',type=str,dest='url',required=True,action='store',
                        help='')

    parse.add_argument('-H',type=str,dest='header',action='store',default=None,
                        help='')

    parse.add_argument('-D',type=str,dest='data',action='store',default=None,
                        help='')

    parse.add_argument('-t',type=int,dest='thread',default=100,action='store',
                        help='')

    parse.add_argument('-x',type=str,dest='extension',action='store',nargs='+',default=None,
                        help='')

    parse.add_argument('-fs',type=str,dest='filter_status',action='store',nargs='+',default=[],
                        help='')

    parse.add_argument('-fw',type=str,dest='filter_words',action='store',nargs='+',default=[],
                        help='')

    parse.add_argument('-hs',type=str,dest='hide_status',action='store',nargs='+',default=[404,400],
                        help='')

    parse.add_argument('-hw',type=str,dest='hide_words',action='store',nargs='+',default=[],
                                            help='')

    parsed = parse.parse_args()



    default()

    url = parsed.url.split('FUZZ')
    if len(url) != 2:
        parse.print_help()
        exit(1)    
    wordlist_parser(parsed.wordlist_path)


    if parsed.header is not None:
        header_split = parsed.header.split(':')
        headers = {header_split[0]:header_split[1]}
    elif parsed.data is not None:
        data_split = parsed.header.split(':')
        data = {data_split[0]:data_split[1]}


    with tqdm(total=wordlist_parsed.qsize(),file=stdout,desc='aweb',
              bar_format='[{l_bar}{bar:20}{n_fmt}/{total_fmt}] [{elapsed}] [{rate_fmt}]') \
                as pbar:

        for i in range(parsed.thread):
            t = Thread(target=fuzzer,args=(url,wordlist_parsed,))
            t.start()
            thread.append(t)
            sleep(0.2)

        for i in thread:
            i.join()
            
