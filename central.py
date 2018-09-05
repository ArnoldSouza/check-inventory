# coding=utf-8
from funcoes import *
from timeit import default_timer

# inicia modulo de cores para a aplicação
init(autoreset=True)

# chama mensagem de abertura
comunicacao('logo')

# pergunta onde a aplicação está localizada
while True:
    print u'Qual Endicon você está?\n' \
          u'[M] MATRIZ;\n' \
          u'[F] FILIAL.\n' \
          u'->',
    local = raw_input()
    if local.lower() not in ('m', 'f'):
        print(Fore.RED + u"Desculpa, você deve alocar Matriz ou Filial\nRecomeçando...\n")
        continue
    else:
        # analisa o valor inserido
        if local.lower() == 'm':
            local = "db.endiconpa.com"
        elif local.lower() == 'f':
            local = "sistema.endiconpa.com"

        if is_connected("www.google.com", 'net') and is_connected(local, 'bd'):
            print Fore.GREEN + u'\n-> Fim de teste: as conexões estão ativas.\n'
            break
        else:
            while True:
                print Fore.YELLOW + u'ATENCAO: O teste de conexão apresentou falha. Use as opções: \n' \
                      u'[T] Tentar Novamente;\n' \
                      u'[S] Sair.\n' \
                      u'->',
                resposta = raw_input()
                if resposta.lower() not in ('t', 's'):
                    print(Fore.RED + u"Opção inválida.\n")
                    continue
                elif resposta.lower() == 's':
                    comunicacao('sai')
                elif resposta.lower() == 't':
                    print '\nTentando novamente...\n'
                    break
            else:
                break

# pausa na execucao
comunicacao('continua')

while True:
    print u'\niniciando aplicação de login:\n'

    start_time = default_timer()

    # Carrega objeto cursor de animação
    animacao = CursorAnimation()
    # Start Animation
    animacao.start()

    dados, versao = get_login()

    animacao.stop()

    if not dados or not versao:
        comunicacao('continua')
        continue
    else:
        break

elapsed = default_timer() - start_time

logins = [dados[nomes][0] for nomes in range(len(dados))]
sys_versao = versao[1][0]
sys_situacao = versao[1][1]

print Fore.GREEN + u'Aplicação: Processando... Feito!\n' \
      'Tempo processando: {:.1f} segundos \n'.format(elapsed)

print u'Versão aplicação: v1.0\n'

if sys_versao != 'v1.0' or sys_situacao != 'ativo':
    print u'sys versão atual: ' + sys_versao + u' | sys situação: ' + sys_situacao + '\n'
    print u'A versão da aplicação está desatualizada ou o sistema está off-line. ' \
          'Entre em contato com Endicon Suprimentos Corporativo.\n'
    comunicacao('sai')

# pausa na execucao
comunicacao('continua')

# check de login
i = 1
while True:
    if login(dados, logins):
        print Fore.GREEN + u"\nVocê está logado!\n"
        print banner('Ambiente de Login ao Sistema') + '\n'
        comunicacao('continua')
        # limpa a tela da shell
        system('cls')
        break
    else:
        print Fore.YELLOW + "\nLogin incorreto. Tentativa: {} de 3.\n".format(i)
        print banner('Ambiente de Login ao Sistema') + '\n'
        comunicacao('continua')
        i += 1
        if i > 3:
            print Fore.RED + u'\nLimite de tentativa ultrapassado. A aplicação foi terminada.\n'
            comunicacao('sai')

comunicacao('logo')
print banner('Consulta de saldo em estoque') + '\n'

cod_local = raw_input('\nDigite o armazem a ser inventariado:')

while True:
    cod_produto = raw_input('\ninsira o codigo do produto ou pressione S para sair:')
    if cod_produto.strip() == 'S' or cod_produto.strip() == 's':
        print Fore.YELLOW + u'\n\t--> ATENÇÃO: A aplicação foi finalizada à pedido do operador.\n'
        comunicacao('sai')
    try:
        # leitura de dados
        print "-"*100
        consulta = Contagem(cod_local, cod_produto, local)
        attrs = vars(consulta)
        print ', \n'.join("%s: %s" % item for item in attrs.items())
        print "-" * 100
    except TypeError:
        print Fore.YELLOW + u'\n\t--> ATENÇÃO: Não foi encontrado posição de estoque para o produto especificado'
        pass
    except pyodbcError:
        print Fore.RED + u'ATENÇÃO: Aparentemente você está sem conexão à internet. Verifique suas configurações e tente novamente'
