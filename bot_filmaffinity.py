import requests, os, re
import unidecode
from telegram import InputFile
import flag
from bs4 import BeautifulSoup
from telegram.ext import Updater, CommandHandler, ConversationHandler, MessageHandler, Filters
from telegram import ChatAction, InlineKeyboardMarkup, InlineKeyboardButton
import logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
INPUT_TEXT_1 = 0
INPUT_TEXT_2 = 1
INPUT_TEXT_3 = 3
newlink = ''


dic_paises = {} # crear un diccionario vacío
with open("paises_emoji.txt", "r") as archivo: # abrir el archivo en modo lectura
    for linea in archivo: # iterar por cada línea del archivo 
        clave, valor = linea.split(":") # separar la línea por el delimitador “:” 
        clave = clave.strip() # eliminar los espacios en blanco alrededor de la clave 
        valor = valor.strip() # eliminar los espacios en blanco alrededor del valor 

        dic_paises[clave] = valor # asignar el valor a la clave en el diccionario
    #for key, value in diccionario.items():
        #print(f'clave->{key}: valor->{value}\n')
    
def filmaffinity(update, context):
    link = 'https://www.filmaffinity.com/es/main.html'
    soup = BeautifulSoup(requests.get(link).content, 'html.parser')
    tittle = update.message.text
    print('!!!' + tittle + '!!!')
    chat = update.message.chat
    chat.send_action(
        action=ChatAction.TYPING,
        timeout=None
    )
    
    calendario = {}
    divs = soup.find_all('div', class_='movie-poster')

    for div in divs:
        links = div.find_all('a')
        for a in links:
            if a['title']:
                calendario[a['title']] = a['href']
                print(a['title'])
    
    for elem in calendario:
        if unidecode.unidecode(tittle.lower()) in unidecode.unidecode(elem.lower()):  # saber si cadena introducida esta incluida dentro del title
            nameFull = elem
            newlink = calendario[elem]
            #serieTv = False
            print(newlink)
            context.bot.send_message(
                chat_id=952639916, text=f'Encontre lo que buscas como: {nameFull} {newlink}')
            if 'TV' in nameFull:
                serieTv = True
            return filmaffinityPlantilla(serieTv, newlink, update, context)
    update.message.reply_text('No encontre lo que buscas')
    return ConversationHandler.END
def filmaffinityPlantilla(serieTv, newlink, update, context):
    context.bot.send_message(chat_id=952639916, text=f'Comienza function filmaffinityPelicula')
    soup = BeautifulSoup(requests.get(newlink).content, 'html.parser')
    div_pic =  soup.find_all('div', id="movie-main-image-container")
    for a in div_pic:
        link = a.find_all('a')
        for a in link:
            link_pic = a['href']
    img_response = requests.get(link_pic)
    with open('image_temp.jpg', 'wb') as f:
        f.write(img_response.content)

    dts = [i.text.strip().replace(':', '') for i in soup.find_all(class_='movie-info')[0].find_all('dt')]
    dds = [i.text.strip().replace('\n', '') for i in soup.find_all(class_='movie-info')[0].find_all('dd')]
    ddcountry = soup.find_all(class_='movie-info')[0].find_all('span')
    for span in ddcountry:
        img = span.find_all('img')
        for src in img:
            siglas_pais = src['src'][-6:-4]
            break
    details = dict()
    for dt, dd in zip(dts, dds):
        if (dt == "Género"):
            gen_data = dd.lower()
            gens = re.split(r'[|./& ]+|de|tv|serie', gen_data)
            all_gen = " "
            for item in gens:
                if len(item) > 1:
                    all_gen += "#" + item + ", "
            details[dt] = all_gen[:-2]
        elif (len(dd) > 400):
            details[dt] = dd.split('(FILMAFFINITY)')[0][:400].rsplit(' ', 1)[0] + "..."
        else:
            details[dt] = dd
    if serieTv == True:
        with open('image_temp.jpg', 'rb') as f:
            context.bot.send_photo(chat_id=952639916, photo=f, caption=f'\U0001F451 {details.get("Título original")}\n\n'
                                                         f'\U0000203C ESTRENO \U0000203C\n\n'
                                                         f'\U0001F3AC #Serie {details.get("País")}, {dic_paises.get(siglas_pais)}\n'
                                                         f'\U0001F4C6 Año: {details.get("Año")}\n'
                                                         f'\U0001F551 Duracción: {details.get("Duración")}\n'
                                                         f'\U0001F3C6 Calificación: \U00002B50 - IMDB, -% Google, -% \U0001F345 Rotten Tomatoes\n'
                                                         f'\U0001F50A Audio: \n'
                                                         f'\U0001F4AC Subtítulos: \n'
                                                         f'\U0001F465 Actúan: {details.get("Reparto")}\n'
                                                         f'\U0001F3B2 Sinópsis: {details.get("Sinopsis")}\n'
                                                         f'\U0001F3AD Género(s): {details.get("Género")}\n')
        os.remove('image_temp.jpg')
    else:
        context.bot.send_message(chat_id=952639916, text=f'\U0001F451 {details.get("Título original")}\n\n'
                                                         f'\U0000203C ESTRENO \U0000203C\n\n'
                                                         f'\U0001F3AC #Película {details.get("País")}, {dic_paises.get(siglas_pais)}\n'
                                                         f'\U0001F4C6 Año: {details.get("Año")}\n'
                                                         f'\U0001F551 Duracción: {details.get("Duración")}\n'
                                                         f'\U0001F3C6 Calificación: \U00002B50 - IMDB, -% Google, -% \U0001F345 Rotten Tomatoes\n'
                                                         f'\U0001F50A Audio: \n'
                                                         f'\U0001F4AC Subtítulos: \n'
                                                         f'\U0001F465 Dirección: {details.get("Dirección:")}, Actúan: {details.get("Reparto")}\n'
                                                         f'\U0001F3B2 Sinópsis: {details.get("Sinopsis")}\n'
                                                         f'\U0001F3AD Género(s): {details.get("Género")}\n')
    
    return ConversationHandler.END
def start(update, context):
    button1 = InlineKeyboardButton(
        text='Filmaffinity',
        url='https://www.filmaffinity.com/es/main.html'
    )
    update.message.reply_text(
        text='Hola, bienvenidos con nuestro bot puedes obtenet información del contenido publicado en la siguiente página:',
        reply_markup=InlineKeyboardMarkup([[button1]])
    )
def titulo_command_handler(update, context):
    update.message.reply_text(
        'Enviame el titulo del contenido que desee encontrar')
    return INPUT_TEXT_1

def series_command_handler(update, context):
    chat = update.message.chat
    chat.send_action(
        action=ChatAction.TYPING,
        timeout=None
    )
    link = 'https://www.filmaffinity.com/es/main.html'
    soup = BeautifulSoup(requests.get(link).content, 'html.parser')
    divs = soup.find_all('div', class_='movie-poster')
    last_series = ''
    for div in divs:
        links = div.find_all('a')
        for a in links:
            if a['title']:
                last_series = last_series + '\U0001F3AC ' + a['title'].split('(')[0][:-1] + '\n'
    update.message.reply_text(
        'Últimos Estrenos (Serie de TV):\n\n' + last_series)
    return ConversationHandler.END
def plantilla_command_handler(update, context):
    update.message.reply_text(
        'Generando Plntilla')
    return INPUT_TEXT_2
def init(context):
    context.bot.send_message(
        chat_id=952639916, text=f'Plantillas | Top Estreno ha sido iniciado')
updater = Updater(
    token='6151945025:AAE0MeNtxdzmAjRdIBN8sXmTDgUlH0V5Zvs', use_context=True)
updater.job_queue.run_once(init, when=0)
dp = updater.dispatcher
dp.add_handler(ConversationHandler(
               entry_points=[
                   CommandHandler('title', titulo_command_handler),
                   CommandHandler('plant', plantilla_command_handler),
                   CommandHandler('last_tv', series_command_handler)
               ],
               states={
                   INPUT_TEXT_1: [MessageHandler(Filters.text, filmaffinity)],
                   INPUT_TEXT_2: [MessageHandler(Filters.text, filmaffinityPlantilla)]
               },
               fallbacks=[]
               ))
# dp.add_handler(CommandHandler('titulo', titulo_command_handler))
dp.add_handler(CommandHandler('start', start))
# updater.job_queue.run_repeating(filmaffinity, interval=30, first=0)
updater.start_polling()
updater.idle()
