# coding=utf-8
import socket
from os import system
from pyodbc import connect as conectar, Error as pyodbcError
from colorama import init, Fore
from gspread import authorize
import httplib2
from oauth2client.service_account import ServiceAccountCredentials
from time import sleep
from threading import Thread
from hashlib import sha1
from msvcrt import getch
from getpass import getpass
from sys import stdin, __stdin__, stdout
from consulta import sql_pos_stock

# inicia modulo de cores para a aplicação
init(autoreset=True)


def connect(local):
    """global connection factory"""
    con_string = 'Driver={SQL Server};Server='+local+';Database=xxx;uid=xxx;pwd=xxx'
    conn = conectar(con_string)
    # conn.setdecoding(pyodbc.SQL_CHAR, encoding='latin1', to=str)
    # conn.setencoding(str, encoding='latin1')
    return conn


def comunicacao(cmd):
    """Mensagem de comunicação do app"""
    if cmd == 'logo':
        msg = u'''
              ______           _ _                   _____                      _         
             |  ____|         | (_)                 |_   _|                    | |        
             | |__   _ __   __| |_  ___ ___  _ __     | |  _ ____   _____ _ __ | |_   ___ 
             |  __| | '_ \ / _` | |/ __/ _ \| '_ \    | | | '_ \ \ / / _ \ '_ \| __| / _ \ 
             | |____| | | | (_| | | (_| (_) | | | |  _| |_| | | \ V /  __/ | | | |_ |  __/
             |______|_| |_|\__,_|_|\___\___/|_| |_| |_____|_| |_|\_/ \___|_| |_|\__(_)___|
            
            Sistema de inventário rotativo Endicon Invent.e
            Logística Endicon - 2017 v1.0
            Suporte: suprimentos.corporativo@endicon.com.br | (91) 3202-4026
            
            '''
        print msg+'\n'
    elif cmd == 'continua':
        # pausa na execucao
        raw_input('Pressione Enter para continuar')
    elif cmd == 'sai':
        raw_input('Pressione Enter para sair')
        quit()


def is_connected(endereco, subject):
    """ Faz check de conexao com internet e servidores de dados"""
    print '\n--> Check de conexao...'
    try:
        if endereco == "db.endiconpa.com":
            conn = connect("db.endiconpa.com")
            if conn:
                pass
        else:
            # see if we can resolve the host name -- tells us if there is
            # a DNS listening
            remote_server = endereco
            host = socket.gethostbyname(remote_server)
            # connect to the host -- tells us if the host is actually
            # reachable
            s = socket.create_connection((host, 80), 2)
            if s:
                pass

        if subject == 'net':
            print(Fore.GREEN + 'Terminal com conexao a internet ativa')
        elif subject == 'bd':
            print(Fore.GREEN + 'Terminal com conexao ao servidor ativa')
        return True
    except (socket.timeout, socket.gaierror, pyodbcError):
        pass
        if subject == 'net':
            print(Fore.RED + 'Terminal sem conexao a internet\n')
        elif subject == 'bd':
            print(Fore.RED + 'Terminal sem conexao ao servidor\n')
        return False


def login(dados, logins):
    """Script simples [temporario] de login no sistema"""

    # limpa a tela da shell
    system('cls')
    print banner('Ambiente de Login ao Sistema')
    print u'\nPara acessar o programa é necessario fazer login na aplicação:\n'
    username = raw_input("Username:")
    password = pyssword()

    if username == '' or password == '':
        print Fore.RED + u'\nUsuário ou senha não podem ter valor vazio.'
        return False

    hash_object = sha1(password)
    password = hash_object.hexdigest()

    if username.lower() in logins:
        indice = logins.index(username)
        usuario = str(dados[indice][0])
        senha = str(dados[indice][1])
        ativo = str(dados[indice][2])

        if senha == '':
            senha = password_reset(usuario, logins, dados)

        if username.lower() == usuario and password == senha:
            if ativo == 's':
                return True
            else:
                print Fore.RED + u'\nUsuário não ativo. Entrar em contato com Endicon Suprimentos Corporativo.\n'
                print banner('Ambiente de Login ao Sistema') + '\n'
                comunicacao('sai')
    else:
        while True:
            print Fore.CYAN + u'\nUsuário não reconhecido na base de dados. Selecione as opções abaixo:\n' \
                  u'[C] NOVO CADASTRO;\n' \
                  u'[S] SAIR.\n' \
                  u'->',
            resposta = raw_input()
            if resposta.lower() not in ('c', 's'):
                print(Fore.RED + u"\nDesculpa, você deve usar uma das opções apresentadas.\nRecomeçando...\n")
                continue
            else:
                if resposta.lower() == 's':
                    print '\nSaindo...'
                    return False
                else:
                    new_user(logins, dados)
                    return False


def password_reset(usuario, logins, dados):
    while True:
        print Fore.RED + '\nO login:' + usuario + ' necessita de cadastro de uma nova senha.'
        nova_senha = pyssword()
        print 'Insira novamente o password:'
        confirma_senha = pyssword()

        if nova_senha != confirma_senha:
            print(Fore.RED + u"\nDesculpa, as senhas não conferem.\nRecomeçando...\n")
            continue
        elif nova_senha == '':
            print(Fore.RED + u"\nDesculpa, insira uma senha .\nRecomeçando...\n")
            continue
        else:
            print '\nRegistrando nova senha...'
            break

    while True:
        animacao = CursorAnimation()
        animacao.start()
        try:
            scope = ['https://spreadsheets.google.com/feeds']
            credentials = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
            client = authorize(credentials)
            sheet = client.open('data_inventario_rotativo').worksheet('logins')

            # referência de linha de atualização na tabela
            linha = logins.index(usuario) + 1

            hash_object = sha1(nova_senha)
            nova_senha = hash_object.hexdigest()

            # atualização de dados na tabela
            sheet.update_cell(linha, 2, nova_senha)

            animacao.stop()
            break
        except httplib2.ServerNotFoundError:
            animacao.stop()
            print Fore.RED + u"""\nATENÇÃO: O seu terminal aparenta estar sem conexão à internet ou resposta ao servidor. 
            Revise suas configurações e tente novamente.\n"""
            comunicacao('continua')
            continue

    # atualiza dados de login à lista temporária
    dados[linha][2] = nova_senha

    print Fore.GREEN + u'A senha do usuário: ' + usuario + ' foi cadastrada!\n'

    return nova_senha


def new_user(logins, dados):
    while True:
        print u'\nIniciando novo cadastro de usuário...'
        print u'\nDigite o novo usuário:',
        novo_usuario = raw_input()
        nova_senha = pyssword()
        print 'Insira novamente o password:'
        confirma_senha = pyssword()

        if nova_senha != confirma_senha:
            print(Fore.RED + u"\nDesculpa, as senhas não conferem.\nRecomeçando...\n")
            continue

        if novo_usuario.lower() in logins:
            print(Fore.RED + u"\nDesculpa, este nome de usuário não é válido.\nRecomeçando...\n")
            continue
        elif nova_senha == '':
            print(Fore.RED + u"\nDesculpa, insira uma senha .\nRecomeçando...\n")
            continue
        else:
            print u'O novo usuário será: ' + Fore.YELLOW + novo_usuario.lower() + '\n'

            comunicacao('continua')
            print '\n'
            while True:
                animacao = CursorAnimation()
                animacao.start()
                try:
                    scope = ['https://spreadsheets.google.com/feeds']
                    credentials = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
                    client = authorize(credentials)
                    sheet = client.open('data_inventario_rotativo').worksheet('logins')

                    # referência de linha de atualização na tabela
                    linha = len(logins) + 1

                    hash_object = sha1(nova_senha)
                    nova_senha = hash_object.hexdigest()

                    # atualização de dados na tabela
                    sheet.update_cell(linha, 1, novo_usuario.lower())
                    sheet.update_cell(linha, 2, nova_senha)

                    animacao.stop()
                    break
                except httplib2.ServerNotFoundError:
                    animacao.stop()
                    print Fore.RED + u"""\nATENÇÃO: O seu terminal aparenta estar sem conexão à internet ou resposta ao servidor. 
                    Revise suas configurações e tente novamente.\n"""
                    comunicacao('continua')
                    continue

            # atualiza dados de login à lista temporária
            logins.append(novo_usuario.lower())
            dados.append([novo_usuario.lower(), nova_senha, ''])

            print Fore.GREEN + u'Usuário: ' + novo_usuario.lower() + ' foi cadastrado!\n' + u'É necessário fazer login novamente.'
            break


def pyssword(prompt='Password: '):

    if stdin is not __stdin__:
        pwd = getpass(prompt)
        return pwd
    else:
        pwd = ""
        stdout.write(prompt)
        stdout.flush()
        while True:
            key = ord(getch())
            if key == 13:  # Return Key
                stdout.write('\n')
                return pwd
            if key == 8:  # Backspace key
                if len(pwd) > 0:
                    # Erases previous character.
                    stdout.write('\b' + ' ' + '\b')
                    stdout.flush()
                    pwd = pwd[:-1]
            else:
                # Masks user input.
                char = chr(key)
                stdout.write('*')
                stdout.flush()
                pwd = pwd + char


def banner(text, ch='=', length=103):
    """banner - comunicação visual"""
    spaced_text = ' %s ' % text
    bner = spaced_text.center(length, ch)
    return bner


def get_login():
    try:
        # use credentials to create a client to interact with the Google Drive API
        scope = ['https://spreadsheets.google.com/feeds']
        credentials = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
        client = authorize(credentials)

        # Find a workbook by name and open the first sheet
        # Make sure you use the right name here.
        sheet = client.open('data_inventario_rotativo').worksheet('logins')
        # Extract and print all of the values
        dados = sheet.get_all_values()

        sheet = client.open('data_inventario_rotativo').worksheet('version _data')
        versao = sheet.get_all_values()
    except httplib2.ServerNotFoundError:
        print Fore.RED + u"""ATENÇÃO: O seu terminal aparenta estar sem conexão à internet ou resposta ao servidor. 
        Revise suas configurações e tente novamente.\n"""
        dados = False
        versao = False
    return dados, versao


class Contagem:
    def __init__(self, cod_geral, cod_produto, local):
        self.cod_geral = cod_geral
        self.cod_produto = cod_produto

        # Create the connection
        conn = connect(local)
        cur = conn.cursor()

        # query db
        sql = sql_pos_stock.format(cod_geral, cod_produto)
        cur.execute(sql)

        result = cur.fetchone()

        # Fechando conexao com database
        conn.commit()
        conn.close()

        self.filial = result[1]
        self.armazem = result[2]
        self.descricao_armazem = result[3]
        self.situacao = result[4]
        self.tipo = result[5]
        self.inventariado = result[6]
        self.obriga_obra = result[7]
        self.descricao_produto = result[9]
        self.qtd = result[10]
        self.custo_sys = result[11]
        self.total_sys = result[12]
        self.custo_upc = result[13]
        self.total_upc = result[14]
        self.val_med_compra = result[15]
        self.qtde_prenota = result[16]
        self.total_prenota = result[17]
        self.dt_ult_saida = result[18]
        self.dt_invent = result[19]
        self.cod_grupo = result[20]
        self.desc_grupo = result[21]


# Animação para cursor de espera
# taken from: http://stackoverflow.com/questions/7039114/waiting-animation-in-command-prompt-python
class CursorAnimation(Thread):
    def __init__(self):
        self.flag = True
        self.animation_char = "|/-\\"
        self.idx = 0
        Thread.__init__(self)

    def run(self):
        while self.flag:
            print Fore.YELLOW + u'Aplicação: Processando... ',
            print Fore.YELLOW + self.animation_char[self.idx % len(self.animation_char)] + "\r",
            self.idx += 1
            sleep(0.1)

    def stop(self):
        self.flag = False
