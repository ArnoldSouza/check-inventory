# coding=utf-8
import timeit
import gspread
import httplib2
from oauth2client.service_account import ServiceAccountCredentials


class DbGoogleSheets:
    def __init__(self):
        pass

    start_time = timeit.default_timer()
    try:
        # use creds to create a client to interact with the Google Drive API
        scope = ['https://spreadsheets.google.com/feeds']
        creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
        client = gspread.authorize(creds)

        # Find a workbook by name and open the first sheet
        # Make sure you use the right name here.
        sheet = client.open('data_inventario_rotativo').sheet1

        # Extract and print all of the values
        dados = sheet.get_all_values()

        print dados
        login = [dados[y + 1][0] for y in range(len(dados) - 1)]

        print login

        elapsed = timeit.default_timer() - start_time

        print elapsed
    except httplib2.ServerNotFoundError:
        print u'O seu terminal aparenta estar sem conexão à internet ou resposta ao servidor. Revise suas configurações e tente novamente'


