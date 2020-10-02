#!/usr/bin/env python
# coding: utf-8

# In[59]:


#importa as bibliotecas
from selenium import webdriver
from time import sleep
import pickle #https://www.semicolonworld.com/question/43757/how-to-save-and-load-cookies-using-python-selenium-webdriver
import random
from bs4 import BeautifulSoup
import pandas as pd
import re


# In[27]:


#acessa o driver do Chrome
driver = webdriver.Chrome("<FOLDER DO CHROMEDRIVE EM SEU EQUIPAMENTO>chromedriver.exe")    


# In[28]:


#acessa o link inicial dos prefeitos de SCS
driver.get('http://divulgacandcontas.tse.jus.br/divulga/#/municipios/2020/2030402020/70777/candidatos') #MUDE PARA O CAMINHO DE SUA CIDADE
driver.maximize_window()


# In[29]:


#pega a parte central
elemento = driver.find_element_by_xpath("/html/body/div[2]/div[1]/div/div/section[3]/div/div/table[2]")


# In[30]:


#pega o conteúdo do bloco
html_content = elemento.get_attribute('outerHTML')
#print(html_content)


# In[31]:


#aciona o soup para facilitar o tratamento
soup = BeautifulSoup(html_content, 'html.parser')
#soup


# In[38]:


candidatos = pd.DataFrame(columns=["nome", "coligacao", "situacao", "nome_urna", "cnpj", "total_bens", "dinheiro"])


# In[39]:


cadaUm = soup.find_all("td", class_=lambda x: x != "text-center")
conta = 0
for i in cadaUm:
    conta += 1
    pedacos = i.find_all("div")
    pedaco = 0
    for d in pedacos:
        pedaco += 1
        if pedaco == 1:
            nome = d.get_text()
        elif pedaco == 2:
            coligacao = d.get_text()
        elif pedaco == 3:
            situacao = d.get_text()

    nome_urna = i.strong.get_text()
    print(nome_urna)
    candidatos.loc[conta] = ({"nome": nome, "coligacao": coligacao, "situacao": situacao, 'nome_urna': nome_urna})

print(conta)


# In[40]:


candidatos.head(10)


# In[76]:


#busca dados da página individual
for i in range(1, conta + 1):
    ponto = '/html/body/div[2]/div[1]/div/div/section[3]/div/div/table[1]/tbody/tr[' + str(i) + ']/td[1]/a'
    driver.find_element_by_xpath(ponto).click()
    sleep(3)
    
    #pega o body
    paginaIndividual = driver.find_element_by_tag_name("body")
    htmlIndividual = paginaIndividual.get_attribute('outerHTML')
    soupIndividual = BeautifulSoup(htmlIndividual, 'html.parser')
    cnpj = soupIndividual.find("tr", {"data-ng-if" : "resultData.cnpjcampanha"}).get_text().replace("CNPJ - ", "")
    print(cnpj)
    candidatos.loc[i, 'cnpj'] = cnpj
    
    #vai para um nível mais abaixo para pegar o patrimônio
    ponto = '/html/body/div[2]/div[1]/div/div[1]/section[3]/div/div[1]/div[2]/button[1]'
    driver.find_element_by_xpath(ponto).click()
    sleep(3)
    paginaPatrimonio = driver.find_element_by_tag_name("body")
    #print(paginaPatrimonio)
    htmlPatromonio = paginaPatrimonio.get_attribute('outerHTML')
    #print(htmlPatromonio)
    soupPatrimonio = BeautifulSoup(htmlPatromonio, 'html.parser')
    #print(soupPatrimonio)
    patrimonio = soupPatrimonio.find("div", {"class" : "dvg-painel-azul"}).find("span").get_text()
    print(patrimonio)
    candidatos.loc[i, 'total_bens'] = patrimonio.replace("R$", "").replace(".", "")
    try:
        temDinheiro = soupPatrimonio.find("span",  text = re.compile("^Dinheiro em espécie - moeda nacional.*"), attrs = {"class" : "ng-binding"})
        dinheiro = temDinheiro.parent.findNext('td').find("span").get_text()
    except:
        dinheiro = "0"
    print(dinheiro)
    candidatos.loc[i, 'dinheiro'] = dinheiro.replace("R$", "").replace(".", "")
    
    driver.execute_script("window.history.go(-1)")
    sleep(3)
    
    driver.execute_script("window.history.go(-1)")
    sleep(3)
    


# In[74]:


candidatos.head(10)


# In[75]:


candidatos.to_excel("prefeitos.xls")


# In[ ]:




