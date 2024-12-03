# import telegram module
import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackContext, Updater, CallbackQueryHandler

# API Token
updater = telegram.ext.Updater(token='6596343159:AAFhdU4trzTLcwNO6JmA_LX5tHprzpM8c0Q', use_context=True)
dispatcher = updater.dispatcher


# import selenium module
from selenium import webdriver
from selenium.webdriver.common.by import By

# import emoji module
import emoji

# global variable for each fortune
luck_types = [] # title name of each fortune type
main_fortune = [] # main fortune list

main_text = '' # main fortune content

# dictionary to save content of each fortune type
lucky_contents = {}
# type
# rating
# content

# set Chrome options
chrome_options = webdriver.ChromeOptions()

# set headers
chrome_options.add_argument('user-agent=Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36')

# accelerate web crawler
chrome_options.page_load_strategy = 'eager'

chrome_options.add_argument('--ignore-certificate-errors')
chrome_options.add_argument("--no-sandbox")

# not pop up the window of the target page
chrome_options.add_argument("--headless")

chrome_options.add_argument("--disable-gpu")
chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

browser = webdriver.Chrome(options=chrome_options)

# to scrape the fortune content
def fortune_crawler(zodiac_value, when_value):

    # browse target website: ELLE starsigns page
    browser.get('https://www.elle.com/tw/starsigns/')

    # get 'a' tag of target zodiac
    zodiac_links = browser.find_elements(By.XPATH, '//a[@data-vars-ga-call-to-action=' + '"' + zodiac_value[1:] + '"]')

    # to match the english version of when_value
    if when_value == '今日運勢':
        href_when_value = 'today'

    elif when_value == '明日運勢':
        href_when_value = 'tomorrow'

    elif when_value == '本週運勢':
        href_when_value = 'weekly'

    elif when_value == '本月運勢':
        href_when_value = 'monthly'

    # to get the url of target zodiac
    for zodiac_link in zodiac_links:
        
        # get the value of the attribute 'href' in a tag
        href = zodiac_link.get_attribute('href')
        if href_when_value in href:
            
            # browse the website through the href link directly
            browser.get(href)
            break # break the loop after browsing the website
    
    # get the date that corresponds to when_value
    the_date = browser.find_element(By.XPATH, '/html/body/div[1]/div/main/div[2]/div[1]/div[2]/p[1]').text.split('\n')[0]

    # add title for the scraped fortune content
    main_fortune.append(f'✨✨✨{zodiac_value}『{when_value}』✨✨✨\n時間🗓：{the_date}')

    # the main fortune content of the target zodiac (the very first block of the page)
    main_content = browser.find_element(By.XPATH, '/html/body/div[1]/div/main/div[2]/div[1]/div[2]/ul')

    # get each bullet point under the main fortune content
    for point in main_content.find_elements(By.TAG_NAME, 'li'):
        main_fortune.append(point.text) # add the bullet point content into main_fortune list
    
    # get the title of each type of fortune
    luckies = browser.find_elements(By.XPATH, '/html/body/div[1]/div/main/div[2]/div[1]/div[2]/h2')[0:4]
    
    # to scrape and save the the content of each type of fortune
    for luck_idx, each_luck in enumerate(luckies):
        
        # create multidimensional dictionary to save the content of each type of fortune
        lucky_contents[each_luck.text] = {}
        
        # fortune rating, represented in star sign emoji
        for ele in browser.find_elements(By.XPATH, '/html/body/div[1]/div/main/div[2]/div[1]/div[2]/div[' + str(luck_idx+1) + ']/div'):

            # to scraped and save the rating
            rating = ''
            for stars in ele.find_elements(By.TAG_NAME, 'img'):

                # use the svg image name inside src attribute to distinguish between solid and hollow star signs
                if '2523F3B032' in stars.get_attribute('src'):
                    rating += emoji.emojize(':glowing_star:')
            lucky_contents[each_luck.text]['rating'] = rating # save the rating value into matching dictionary

            # get all the following tags (instead of child tag) that come after the tag of each type of fortune name
            all_luck_content = ele.find_elements(By.XPATH, '/html/body/div[1]/div/main/div[2]/div[1]/div[2]/div[' + str(luck_idx+1) + ']/following-sibling::*')
            
            # get the luck content of each type of fortune
            luck_content = ''
            for each_block in all_luck_content:
                
                # there are no fixed number of following p tags
                if each_block.tag_name == 'p':

                    # if 'a' tag is the child tag of the p tag which means it contains link, and is not the target content
                    if each_block.find_elements(By.XPATH, './/a'):
                        break # break the for-loop
                    else:
                        luck_content += each_block.text + '\n\n'

                # if the div tag first occurred means it reaches the end of the content under this fortune type
                elif each_block.tag_name == 'div':
                    break # break the for-loop
                
            # save the content to the dictionary
            lucky_contents[each_luck.text]['content'] = each_luck.text + '：' + rating + '\n' + luck_content
  

# to handle the time options of fortune chosen by the user
def fortune(update: telegram.Update, context: CallbackContext):

    # get the time of fortune the user chosed
    when_value = context.user_data.get('when')
    zodiac_value = update.message.text
    context.bot.send_message(chat_id=update.message.chat_id, text='請稍後...🔍')
            
    fortune_crawler(zodiac_value, when_value) # scrape the target page

    main_text = ''
    for main_txt in main_fortune:
        main_text += (main_txt + '\n')

    main_fortune.clear() # clear main_fortune
    context.bot.send_message(chat_id=update.message.chat_id, text=main_text)
    luck_type(update, context) # let user choose type of fortune


# to handle the fortune type options chosen by the user
def luck_content(update: telegram.Update, context: CallbackContext):
    which_type = update.message.text

    if '整體運勢' in which_type:
        context.bot.send_message(chat_id=update.message.chat_id, text='📊' + lucky_contents['整體運勢']['content'])

    elif '愛情運勢' in which_type:
        context.bot.send_message(chat_id=update.message.chat_id, text='💘' + lucky_contents['愛情運勢']['content'])

    elif '事業運勢' in which_type:
        context.bot.send_message(chat_id=update.message.chat_id, text='📈' + lucky_contents['事業運勢']['content'])

    elif '財運運勢' in which_type:
        context.bot.send_message(chat_id=update.message.chat_id, text='💰' + lucky_contents['財運運勢']['content'])

    luck_type(update, context)

# the start command to start the telegram bot
def start(update: telegram.Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.message.chat_id, text='歡迎使用星座大師Zodiac Master!🪄🔮')
    options_text = '請選擇：\n 1. /start    🔮重新開始\n 2. /when  🕰運勢時間'
    context.bot.send_message(chat_id=update.message.chat_id, text=options_text)


# the zodiac command to choose the desired zodiac
def zodiac(update: telegram.Update, context: CallbackContext):
    keyboard = [['♑摩羯座', '♒水瓶座', '♓雙魚座'],
                ['♈牡羊座', '♉金牛座', '♊雙子座'],
                ['♋巨蟹座', '♌獅子座', '♍處女座'],
                ['♎天秤座', '♏天蠍座', '♐射手座']]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    context.bot.send_message(chat_id=update.message.chat_id, text='請選擇星座：', reply_markup=reply_markup)


# the when command to choose the desired time of target zodiac fortune
def when_options (update: telegram.Update, context: CallbackContext):
    keyboard = [['今日運勢', '明日運勢'],
                ['本週運勢', '本月運勢']]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    context.bot.send_message(chat_id=update.message.chat_id, text='請選擇時間：', reply_markup=reply_markup)


# the fortune types options
def luck_type(update: telegram.Update, context: CallbackContext):
    keyboard = [['📊\n整體運勢', '💘\n愛情運勢', '📈\n事業運勢', '💰\n財運運勢']]
    options_text = '請選擇：\n 1. 📊💘📈💰運勢種類\n 2. /start      🔮重新開始\n 3. /zodiac   ⭐星座選項\n 4. /when     🕰運勢時間'
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    context.bot.send_message(chat_id=update.message.chat_id, text=options_text, reply_markup=reply_markup)


# To get the chosen time of target zodiac fortune
def when(update: telegram.Update, context: CallbackContext):

    when = update.message.text
    context.user_data['when'] = when
    context.bot.send_message(chat_id=update.message.chat_id, text=f'您選擇『{when}』')
    zodiac(update, context)
 

# main function to execute the telegram bot
def main():
    # API Token
    updater = telegram.ext.Updater(token='6596343159:AAFhdU4trzTLcwNO6JmA_LX5tHprzpM8c0Q', use_context=True)
    dispatcher = updater.dispatcher
    
    # all command handlers and process to execute the telegram bot
    start_handler = CommandHandler('start', start)
    zodiac_handler = CommandHandler('zodiac', zodiac)
    when_options_handler = CommandHandler('when', when_options)

    fortune_handler = MessageHandler(Filters.text & (~Filters.command), fortune)
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(when_options_handler)

    dispatcher.add_handler(MessageHandler(Filters.regex('^(今日運勢|明日運勢|本週運勢|本月運勢)$'), when))
    dispatcher.add_handler(zodiac_handler)
    luck_type_handler = MessageHandler(Filters.text & (~Filters.command), luck_type)
    dispatcher.add_handler(MessageHandler(Filters.regex('(整體運勢|愛情運勢|事業運勢|財運運勢)'), luck_content))
    dispatcher.add_handler(fortune_handler)

    dispatcher.add_handler(luck_type_handler)

    updater.start_polling()
    updater.idle()

# to execute main()
if __name__ == '__main__':
    main()