from fastapi import FastAPI
from model import  Info, conect_banco
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from hashlib import sha256
import re
import email.message
import random
import smtplib


app = FastAPI()
session = conect_banco()

# CORS 
app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://127.0.0.1:5005', # INFO: PAG DO CADASTRO
                  'http://127.0.0.1:5006',  # INFO: PAG DO LOGIN
                  'http://127.0.0.1:5007',  # INFO: PAG DO LOGIN SUCESS
                  'http://127.0.0.1:5008',  # INFO: ESQUECEU A SENHA
                  'http://127.0.0.1:5009'], # INFO: PAG DO EMAIL ENVIADO
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#VERIFCA SE O USER JA É CADASTRADO
def verificar_email_cel(name:str,email:str, cel:str, senha:str):

    x = session.query(Info).filter_by(email=email).all() # INFO: VERIFICAR SE O EMAIL JÁ EXISE NO BD
    z = session.query(Info).filter_by(celular=cel).all() # INFO: VERIFICAR SE O CELULAR JÁ EXISTE NO BD
    
    regex_email = re.compile('[a-zA-Z0-9]+@[a-zA-z]+\.com')     # INFO: REGEX PARA VALIDAR O EMAIL
    regex_nome = re.compile('[a-zA-Z]+')                        # INFO: REGEX PARA VALIDAR O NOME
    regex_cel = re.compile('[0-9]{2}[\s]?[0-9]{5}[-]?[0-9]{4}') # INFO: REGEX PARA VALIDAR O CELULAR

#VERIFICANDO SE OS CAMPOS ESTÃO VAZIOS 
    if (name == '' and email == '' or (name == '' or email == '')): # INFO : VERIFICANDO OS CAMPOS
        return '3' # ---> ERRO = CAMPOS VAZIOS

    elif len(x) == 0 and len(z) == 0:
        if re.fullmatch(regex_nome, name) != None: #INFO: PROCURANDO O PADRAO NO 'NAME'
            
            if re.fullmatch(regex_email, email) != None: #INFO: PROCURANDO O PADRAO NO 'EMAIL'
                    
                    if re.fullmatch(regex_cel , cel) != None: #INFO: PROCURANDO O PADRAO NO 'CELULAR'
                        y = Info(nome=name,email=email,celular=cel, senha=senha)
                        session.add(y)
                        session.commit()
                        return '0' #---> SUCESSO = CADASTRADO
                    
                    else:
                        return '1.3' #---> ERRO = CELULAR INVALIDO
            
            else:
                return '1.2' #---> ERRO = EMAIL INVALIDO

        else:
            return '1.1' #---> ERRO = NOME INVALIDO

    
    
    elif len(x) > 0 :
        if x[0].email == email:
            return '1' #---> ERRO = EMAIL JÁ CADASTRADO
    elif len(z) > 0:
        if z[0].celular == cel:
            return '2' #---> ERRO = CELULAR JÁ CADASTRADO
    
def verificar_login(email:str, senha:str):
    email = email.lower() #--> Tranformando em lower case
    senha_cp = sha256(senha.encode()).hexdigest()#--> Cripto
    
    if (email == '' or senha == ''): # INFO : VERIFICANDO OS CAMPOS
        return '1' # ---> ERRO = CAMPOS VAZIOS
    
    else:
        regex_email = re.compile('[a-zA-Z0-9]+@[a-zA-z]+\.com')     # INFO: REGEX PARA VALIDAR O EMAIL
        
        if re.fullmatch(regex_email, email) != None: #INFO: PROCURANDO O PADRAO NO 'EMAIL'
       
            verif_email = session.query(Info).filter_by(email=email).all()#-->Puxando os dados do BD

            if len(verif_email) == 0:
                return '1.2' #--> ERRO: USUÁRIO NÃO CADASTRADO
            
            elif len(verif_email) > 0:
                verif_email = session.query(Info).filter_by(email= email,senha=senha_cp).all()#-->Puxando os dados do BD
                
                if len(verif_email) == 0:
                    return '1.3' #--> ERRO: EMAIL/SENHA INCORRETAS
                
                elif len(verif_email) > 0:
                    return '1.4' #--> SUCESS: LOGADO
        
        else:
            return '1.1' #--> ERRO: EMAIL INVÁLIDO


def enviar_email(email_user):
    lista_num = [1,2,3,4,5,6,7,8,9]
    cod_gerado = random.choices(lista_num,k=4)
    cod_formato = ''
    for x in cod_gerado:
        cod_formato += f'{x}'


    corpo_email = f"""
    <p> CLIQUE NO LINK PARA REDEFINIR  </p>
    <a style="padding: 1
    0px; background:rgb(17, 236, 46); text-decoration: none;border: 2px solid rgb(0, 0, 0); border-radius: 10px; font-weight: bold; color: black;"  href='http://127.0.0.1:5009'>REDEFINIR SENHA</a>
    <p></p>
    """

    msg = email.message.Message()
    msg['Subject'] = "TROCAR SENHA"
    msg['From'] = 'testeparaprojetos321@gmail.com'
    msg['To'] = email_user
    password = 'rnpbvfudamjpbjft' 
    msg.add_header('Content-Type', 'text/html')
    msg.set_payload(corpo_email )

    s = smtplib.SMTP('smtp.gmail.com: 587')
    s.starttls()
    s.login(msg['From'], password)
    s.sendmail(msg['From'], [msg['To']], msg.as_string().encode('utf-8'))
    return 'ok'




@app.post('/cadastrar')
def info_cadastrar(nome: str,email:str,cel:str ,senha: str):
    nome = nome.capitalize() #--> 1° Letra Maiúscula
    celular = cel
    email = email.lower() #--> LOWER CASE
    senha = sha256(senha.encode()).hexdigest() #--> CRIPTO A SENHA PARA COLOCAR NO BANCO DE DADOS
    
    #RETORNO 0 ---> TUDO OK = CADASTRADO COM SUCESSO
    #RETORNO 1 ---> ERRO = EMAIL JÁ CADASTRADO
    #RETORNO 1.1 -> ERRO = NOME INVÁLIDO
    #RETORNO 1.2 -> ERRO = EMAIL INVÁLIDO
    #RETORNO 1.3 -> ERRO = CELULAR INVÁLIDO
    #RETORNO 2 ---> ERRO = CELULAR JÁ CADASTRADO
    #RETORNO 3 ---> ERRO = CAMPOS VAZIOS
    
    teste = verificar_email_cel(nome, email, celular, senha)
    match(teste):
        case '0':
            return '0' #---> TUDO OK = CADASTRADO COM SUCESSO
        
        case '1':
            return '1' #---> ERRO = EMAIL JÁ CADASTRADO
        
        case '1.1':
            return '1.1' #-> ERRO = NOME INVÁLIDO
        
        case '1.2':
            return '1.2' #-> ERRO = EMAIL INVÁLIDO
        
        case '1.3':
            return '1.3' #-> ERRO = CELULAR INVÁLIDO
        
        case '2':
            return '2' #---> ERRO = CELULAR JÁ CADASTRADO
        
        case '3':
            return '3' #---> ERRO = CAMPOS VAZIOS

    
@app.post('/logar')
def logar(email:str, senha:str):
    return verificar_login(email, senha)

@app.post('/recup')
def recup_pass(email:str):
    email = email.lower() #--> Tranformando em lower case
    
    if (email == ''): # INFO : VERIFICANDO OS CAMPOS
        return '1' # ---> ERRO = CAMPOS VAZIOS
    
    else:
        regex_email = re.compile('[a-zA-Z0-9]+@[a-zA-z]+\.com')     # INFO: REGEX PARA VALIDAR O EMAIL
        
        if re.fullmatch(regex_email, email) != None: #INFO: PROCURANDO O PADRAO NO 'EMAIL'
            verif_email = session.query(Info).filter_by(email=email).all()#-->Puxando os dados do BD
            if len(verif_email) == 0:
                return '1.2' #--> ERRO: USUÁRIO NÃO CADASTRADO
            
            elif len(verif_email) > 0:
                return enviar_email(email) #--> INFO: EMAIL ENVIADO

        else:
            return '1.1'

@app.post('/redef')
def redef_pass(email: str, senha:str, senhacf:str):
    
    v_01 = session.query(Info).filter_by(email=email).all()
    regex_email = re.compile('[a-zA-Z0-9]+@[a-zA-z]+\.com')     # INFO: REGEX PARA VALIDAR O EMAIL
    if re.fullmatch(regex_email, email) != None: #INFO: PROCURANDO O PADRAO NO 'EMAIL'
        
        if len(v_01) > 0:
                new_senha_cp = sha256(senha.encode()).hexdigest()
                new_senha_cp_01 = sha256(senhacf.encode()).hexdigest()

                if new_senha_cp == new_senha_cp_01: # FAZENDO A COMPARAÇÃO ENTRE AS SENHAS
                    v_01[0].senha = new_senha_cp_01 
                    session.commit() # SALVANDO A ALTERAÇÃO NO BD
                    return 'ok'
                
                else:
                    return '1.3'# --> ERRO: SENHAS NÃO SE COINCIDEM

        else:
            return '1.2' #--> ERRO: EMAIL NÃO CADASTRADO
    else:
        return '1.1' # ---> ERRO: EMAIL INVALIDO




   

if __name__ == '__main__':
    uvicorn.run('controller:app', port=5000, reload=True, access_log=False) 
