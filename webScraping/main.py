
import requests
from bs4 import BeautifulSoup
import sys, re, csv

def normalizaNome(nome):
    
    nome = nome.split()
    nome = ' '.join(nome)    
    
    return nome

def processaDado(precoCartao):    
    
    precoCartao = ' '.join(precoCartao.split())
    
    padrao = re.search(r"(\d+)X de R\$ (\d+,\d+) no Cartão", precoCartao)
    
    if padrao:
        num_parcelas = padrao.group(1)
        valor_parcela = padrao.group(2)
        
        valorTotal = round(int(num_parcelas) * float(valor_parcela.replace(',','.')), 2)
        valorTotal = ('R$ ' + f'{valorTotal}').replace('.',',')
        
    return valorTotal

def getPageContent(URL):
    
    resposta = requests.get(URL).text
    soup = BeautifulSoup(resposta, 'html.parser')
    
    return soup

def verificaQtdProdutosEncontrados(resposta):
    if resposta == '0 produtos encontrados para essa busca':
        print('Nenhum produto com esse nome encontrado')
        sys.exit()        
    
    return 

def getProductInfo(page):
    
    produtos = []
    rows = page.find_all('a', attrs={'class':'in_stock'})
    
    verificaQtdProdutosEncontrados(page.find('span', attrs={'class':'registros-numero'}).get_text(strip=True))    
     
    for row in rows:
    
        nomeProduto = normalizaNome(row.find('h3', attrs={'class':'product-name'}).get_text(strip=True))
        
        if row.find('span', attrs={'class':'old-price'}):            
            precoAntigo = row.find('span', attrs={'class':'old-price'}).get_text(strip=True)
        else:
            precoAntigo = row.find('span', attrs={'class':'price-boleto'}).get_text(strip=True)
            
        precoPIX = row.find('span', attrs={'class':'price-boleto'}).get_text(strip=True)
        precoCartao = row.find('span', attrs={'class':'type-payment-condiction'}).get_text()
        imagemProduto = row.find('img')
        imagemProdutoSrc = imagemProduto.get('data-imagem-principal')    
        
        precoCartao = processaDado(precoCartao)
        
        produto = {'nome' : nomeProduto,
                'preco antigo' : precoAntigo,
                'preco PIX': precoPIX,
                'preco cartao' : precoCartao,
                'imagem' : imagemProdutoSrc}
        
        produtos.append(produto)        
              
    return produtos
    
def stringToURL(buscaProduto):
    
    nomeBusca = buscaProduto.replace(' ', '+') 
    nomeBusca = re.sub(r'\++', '+', nomeBusca) # Remove '+' repetidos caso o input tenha varios espaços   
    
    return nomeBusca

def argToString(args):
            
    busca = ' '.join(args)        
    busca = stringToURL(busca)

    return busca

def geraCsv(produtos):    
    
    with open(f'produtos.csv', 'w') as f:
        wr = csv.writer(f, quoting=csv.QUOTE_ALL)
        wr.writerow(produtos)
       
def main():    
    
    dominio = 'https://www.lojamaeto.com/'
    URL = f'{dominio}busca?q='
    busca = ''
    
    if len(sys.argv) == 1:     
        busca = input("Insira o nome do produto a pesquisar: ")
        busca = stringToURL(busca)
    else:        
        busca = argToString(sys.argv[1:])        
        
    URL = URL + busca 
       
    page = getPageContent(URL)    
    produtos = getProductInfo(page)
    geraCsv(produtos) 
    
if __name__ == '__main__':
    main()    
