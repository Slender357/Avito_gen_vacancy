from partools import quickstart_sheet
from partools import CONFIG


def update_image_id():
    spreadsheet_id, service = quickstart_sheet(type_conection='drive',
                                               version_conection='v3')
    spisochek = service.files().list(pageSize=100,
                                     fields="nextPageToken, files(id, name, mimeType)").execute()
    spisok = {}
    while True:
        for k in CONFIG['sheet_name_image_id'].keys():
            spisok[k] = []
            for i in spisochek['files']:
                if i['mimeType'] == 'image/jpeg':
                    if i['name'][0] == k:
                        spisok[k].append([i['id']])
        try:
            nextPageToken = spisochek['nextPageToken']
            spisochek = service.files().list(pageSize=100,
                                             fields="nextPageToken, files(id, name, mimeType)",
                                             pageToken=nextPageToken).execute()
        except BaseException as r:
            break
    spreadsheet_id, service = quickstart_sheet()
    for i in spisok.keys():
        service.spreadsheets().values().clear(spreadsheetId=spreadsheet_id,
                                              range=CONFIG['sheet_name_image_id'][i] + '!A2:Z9999999').execute()
        service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=CONFIG['sheet_name_image_id'][i] + '!A2',
            valueInputOption='RAW',
            body={'values': spisok[i]
                  }).execute()


if __name__ == "__main__":
    update_image_id()
