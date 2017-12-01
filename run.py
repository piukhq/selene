import settings
from app.controller import (onboard_mids, process_mastercard_handback_file,
                            handle_duplicate_mids_in_mastercard_handback_files)


decision1 = input('Selene asks that you choose your fate from our funky laser display board:\n'
                  '1) Onboard MIDs\n'
                  '2) Process Mastercard handback file(s)\n'
                  '3) Find duplicate MIDs in Mastercard handback file(s)\n')
if decision1 == '1':
    send_export_files = False
    if settings.ASK_TO_SEND_MAIL:
        decision2 = input('Do you want to send the export files now? Yes/No\n')
        if decision2.lower() == 'yes':
            send_export_files = True

    ignore_postcode_validation = True
    if settings.ASK_POSTCODE_VALIDATION:
        decision3 = input('Do you want to ignore post code validation? Yes/No\n')
        if decision3.lower() == 'no':
            ignore_postcode_validation = False

    onboard_mids(send_export_files, ignore_postcode_validation)
elif decision1 == '2':
    process_mastercard_handback_file()
elif decision1 == '3':
    handle_duplicate_mids_in_mastercard_handback_files()
else:
    print("Invalid choice, you must select 1, 2, or 3.  Exiting program.")
