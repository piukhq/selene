# Selene

A webapp to upload MID files for processing and generating files for merchant on-boarding.


### MIDs Onboarding
The uploaded file is processed, generating files to be sent to each payment card provider (Visa, Amex, MasterCard) in 
their expected format.

Two files are generated for each provider after processing, one to send to the provider, and a cassandra input file
for importing the data into our cassandra database.

The produced files are stored in Azure Blob Storage stored in a folder identified by the timestamp of when they were 
uploaded in their respective provider folders e.g
merchants/amex/081018_043947721

The input file must be a csv format. Formatting details can be found on Bookstack.

### MasterCard handback files

For on-boarding merchants with MasterCard, they provide us with a pipe delimited csv file of MIDs. The Selene project
can also process these files to generate a cassandra input file. Formatting of this file can also be found on Bookstack.

## Not Implemented
The latest version of the app does not yet implement all features of the previous API version. The following 
features are not currently included:

- Option to ignore postcode validation (regex check).
- Automatically send export file via sftp for amex and send emails to visa and master card.
- Process cassandra input files to import data into cassandra.

Code for these features can be found in the previous version and may be helpful if the requirements to implement any
arise in the future.
