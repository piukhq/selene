import os
import csv
import settings
from app.utils import validate_uk_postcode, get_agent


# todo implement mastercard handback files
def export_mastercard(files):
    agent_instance = get_agent('mastercard')
    merchants = set()
    footer_id = 30

    errors = []
    for txt_file in files:
        with open(txt_file, newline='') as csvfile:
            mcardreader = csv.reader(csvfile, delimiter='|')

            for count, row in enumerate(mcardreader):
                if count == 0:
                    continue
                elif footer_id == int(row[0]):
                    # EOF
                    break
                elif agent_instance.has_mid(row[23]):
                    if not validate_uk_postcode(row[17].strip('"')):
                        error = "Invalid post code, post code='{}', row: {}, file: {}".format(row[17].strip('"'),
                                                                                              count, txt_file)
                        print(error)
                        errors.append(error)
                    merchant = (row[23], row[7], row[13], row[45], row[17],)
                    merchants.add(merchant)
                else:
                    error = "Invalid MID, MID='{}', row: {}, file: {}".format(row[23], count, txt_file)
                    print(error)
                    errors.append(error)

    if len(merchants):
        prepped_merchants = []
        for merc in merchants:
            merc_dict = dict()
            merc_dict['MasterCard MIDs'] = merc[0]
            merc_dict['Partner Name'] = merc[1]
            merc_dict['Town/City'] = merc[2]
            merc_dict['Scheme'] = merc[3]
            merc_dict['Postcode'] = merc[4]
            prepped_merchants.append(merc_dict)
        agent_instance.write_transaction_matched_csv(prepped_merchants)

    err_filename = 'mastercard_errors.txt'
    path = os.path.join(settings.APP_DIR, 'merchants/mastercard', err_filename)
    with open(path, 'w') as error_output_file:
        for err in errors:
            error_output_file.write(err + '\n')


def process_mastercard_handback_file(files):
    export_mastercard(files)


# todo implement mastercard duplicate
def handle_duplicate_mids_in_mastercard_handback_files(files):
    agent_instance = get_agent('mastercard')
    footer_id = 30
    mids = []

    for txt_file in files:
        with open(txt_file, newline='') as csvfile:
            mcardreader = csv.reader(csvfile, delimiter='|')

            for count, row in enumerate(mcardreader):
                if count == 0:
                    continue
                elif footer_id == int(row[0]):
                    # EOF
                    break
                else:
                    if agent_instance.has_mid(row[23]):
                        mids.append([row[23], count, txt_file])
                    else:
                        print("Invalid MID, row: {}, file: {}".format(count, txt_file))

    duplicates = set()
    dup_mids = set()
    for i in range(0, len(mids)):
        found = False

        for j in range(0, len(mids)):
            if i != j:
                if found:
                    break
                if mids[i][0] == mids[j][0]:
                    found = True

        if found:
            msg = "Duplicate MID: {} found on line number {} in file {}".format(mids[i][0], mids[i][1], mids[i][2])
            duplicates.add(msg)
            dup_mids.add(mids[i][0])

    if len(dup_mids):
        print(dup_mids)

        agent_instance.write_duplicates_file(duplicates)
    else:
        print("No duplicates found.")
