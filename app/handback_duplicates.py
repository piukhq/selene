import os

from app.utils import get_agent


def collect_mids(file, agent_instance):
    mids = []

    for count, row in enumerate(file):

        if row[0] == '30':
            break

        elif agent_instance.has_mid(row[23]):
            mids.append([row[23], count])

    return mids


def find_duplicates(file, agent_instance):

    mids = collect_mids(file, agent_instance)

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
            msg = "Duplicate MID: {} found on line number {}".format(mids[i][0], mids[i][1])
            duplicates.add(msg)
            dup_mids.add(mids[i][0])

    return dup_mids, duplicates


def find_duplicate_mids_in_mastercard_handback_file(file):
    agent_instance = get_agent('mastercard')
    agent_instance.write_path = os.path.join(agent_instance.write_path, 'duplicates')
    os.makedirs(agent_instance.write_path, exist_ok=True)

    file = file[1:-1]

    dup_mids, duplicates = find_duplicates(file, agent_instance)

    if len(dup_mids):
        print(dup_mids)

        agent_instance.write_duplicates_file(duplicates)
    else:
        print("No duplicates found.")
