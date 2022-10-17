from partools import quickstart_sheet

spreadsheet_id, service = quickstart_sheet(type_conection='drive',
                                           version_conection='v3')
spisochek = service.files().list(pageSize=100,
                                 fields="nextPageToken, files(id, name, mimeType)").execute()
k = 0
print(spisochek)
for i in spisochek['files']:
    if i['mimeType'] == 'image/jpeg':
        print(i['id'])
        k += 1
print(k)
