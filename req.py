import requests
#import cloudscraper
url="https://agoranoticiasbrasil.com.br/agencia-brasil-explica-como-calcular-distribuicao-do-lucro-do-fgts/"
#headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'}
headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

#r = reqs_old.get(url, headers=headers, timeout=100, verify=True)
#print(r)
#requests = cloudscraper.create_scraper()
#r = requests.get(url, headers=headers, timeout=100, verify=True)
#print(r)
proxy = {
    'http': 'http://20.33.5.27:8888',
    'https': 'http://20.33.5.27:8888'
}
try:
    # Fazendo a solicitação usando o proxy
    response = requests.get(url, proxies=proxy)

    # Verificando se a solicitação foi bem sucedida
    if response.status_code == 200:
        # Imprime o conteúdo HTML da página
        print(response.text)
    else:
        print("Não foi possível acessar a página. Código de status:", response.status_code)

except requests.exceptions.RequestException as e:
    print("Erro ao fazer a solicitação:", e)
