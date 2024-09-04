from botcity.web import WebBot, Browser, By
from botcity.web.parsers import table_to_dict
from botcity.maestro import *
import pandas as pd
from time import sleep
import requests

API_KEY = '57428462782c3df7b88e53018233f31d'

BotMaestroSDK.RAISE_NOT_CONNECTED = False

tabela = pd.read_csv('cep_pag.csv')

def solve_captcha(image_path):
    with open(image_path, "rb") as captcha_file:
        response = requests.post("http://2captcha.com/in.php", data={
            'key': API_KEY,
            'method': 'post',
            'json': 1
        }, files={'file': captcha_file})

    request_id = response.json().get('request')

    captcha_response = None
    while True:
        result = requests.get(f"http://2captcha.com/res.php?key={API_KEY}&action=get&id={request_id}&json=1")
        if result.json().get('status') == 1:
            captcha_response = result.json().get('request')
            break
        print("Aguardando solução do CAPTCHA...")
        sleep(5)
    
    return captcha_response

def main():

    maestro = BotMaestroSDK.from_sys_args()
    execution = maestro.get_execution()

    print(f"Task ID is: {execution.task_id}")
    print(f"Task Parameters are: {execution.parameters}")

    bot = WebBot()

    bot.headless = False

    bot.browser = Browser.CHROME

    bot.driver_path = "resources\chromedriver.exe"

    bot.browse("https://buscacepinter.correios.com.br/app/endereco/index.php")

    bot.maximize_window()

    dados_coletados = []

    for index, row in tabela.iterrows():
        cep = row['CEP']

        sleep(5)
        cepP =bot.find_element("endereco",By.ID)
        cepP.send_keys(cep)
        
        bot.find_element("captcha", By.ID).click()
        captcha_image= bot.find_element("captcha_image", By.ID)
        captcha_image.screenshot("captcha.png")
        
        captcha_solution = solve_captcha("captcha.png")
        bot.paste(captcha_solution)
        
        bt_buscar= bot.find_element("btn_pesquisar", By.ID)
        bt_buscar.click()
        bot.sleep(10)

        sleep(5)  

        try:
            tabela_resultados = bot.find_element("resultado-DNEC", By.ID)
            resultados_dict = table_to_dict(table=tabela_resultados)
            if resultados_dict:
                dados_coletados.extend(resultados_dict)
            else:
                print(f"Não foram encontrados dados para o CEP {cep}.")
        except Exception as e:
            print(f"Erro ao coletar dados: {e}")

        nova_busca = bot.find_element("btn_nbusca", By.ID).click()

    df_dados = pd.DataFrame(dados_coletados)
    df_dados.to_csv('dados_coletados.csv', index=False, encoding='utf-8')

    maestro.finish_task(
        task_id=execution.task_id,
        status=AutomationTaskFinishStatus.SUCCESS,
        message="Task Finished OK."
    )

def not_found(label):
    print(f"Element not found: {label}")


if __name__ == '__main__':
    main()
