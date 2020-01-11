from bs4 import BeautifulSoup
import urllib.request
from tqdm import tqdm
import time
import pandas as pd


def position(personal,doc_value):
    inner_html = urllib.request.urlopen(
        f'http://opac.nlc.cn/F/{personal}?func=item-global&doc_library=NLC01&doc_number={doc_value}&year=&volume=&sub_library=')
    inner_soup = BeautifulSoup(inner_html, 'html.parser')
    string = ""
    for code, repo, shelf in zip(inner_soup.select("td[align='center']")[2::10], inner_soup.select("td[align='center']")[5::10],inner_soup.select("td[align='center']")[6::10]):
        code = code.text.strip()
        repo = repo.text.strip()
        shelf = shelf.text.strip()
        string += "-".join([code,repo,shelf])+";"

    return string


def scrape(personal,isbn):
    html = urllib.request.urlopen(f'http://opac.nlc.cn/F/{personal}?func=find-b&find_code=ISB&request={isbn}&local_base=NLC01&filter_code_1=WLN&filter_request_1=&filter_code_2=WYR&filter_request_2=&filter_code_3=WYR&filter_request_3=&filter_code_4=WFM&filter_request_4=&filter_code_5=WSL&filter_request_5=')
    soup = BeautifulSoup(html,'html.parser')

    result = {}
    if len(soup.select('#feedbackbar')[0].contents) > 1:
        # print(f"{isbn} no record")
        return None
    else:
        # print(f"{isbn} exists")
        for key,value in zip(soup.select("td .td1")[0::2],soup.select("td .td1")[1::2]):
            key = key.text.strip()
            value = value.text.strip()
            result[key] = value
            if key != 'ID 号':
                pass
            else:
                time.sleep(2)
                result['position']=position(personal,value)


        return result

if __name__ == '__main__':
    personel = '3BSG4R3D7C7E17U2MU53AYSBQK48PA9PUIX5A66YIBRTTFEI8K-05381'

    with open('test','r') as test_file:
        with open('result','w',encoding='utf-8') as output_file:
            lines = test_file.readlines()
            lines = list(map(lambda x: x.strip(),lines))
            count = 0
            isbn_not_hit = []
            for _ in tqdm(lines):
                result = scrape(personel,_)
                if result == None:
                    isbn_not_hit.append(_)
                    count += 1
                else:
                    s = _ + '##'+'##'.join(list(map(lambda x: x.replace("\t","").replace(r'\xa0',"").replace('',""), result.values())))+'\n'
                    output_file.write(s)
                time.sleep(2)
            print(f'{count} books not found in library\n isbn:')
            for _ in isbn_not_hit:
                print(f'{_}')
