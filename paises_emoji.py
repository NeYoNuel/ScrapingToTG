#pip install emoji-country-flag

import flag
emoji = 'https://flagpedia.net/emoji'
soup = BeautifulSoup(requests.get(emoji).content, 'html.parser')
dic_paises = {}
trs = soup.find_all('tr')
for td in trs:
        td_flag = td.find_all('td', class_='td-flag')
        for td1 in td_flag:
            a_flag = td1.find_all('a')
            for a in a_flag:
                a.text.strip()
        td_code = td.find_all('code')
        for code in td_code:
            if code.text.strip():
               dic_paises[a.text.strip()] = code.text.strip()
               continue

f = open('paises_emoji.txt', 'w')
for key, value in dic_paises.items():
   # print(emoji.emojize(str(key), use_aliases=True))
    #code = emoji.emoji_country_code(value)
    sigla = flag.dflagize(key)
    f.write(f'{sigla[1:-1]}: {key}\n')
f.close()

