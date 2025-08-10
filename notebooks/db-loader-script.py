# CRS Database Metadata - Simplified Format

# Reference Table: Country Codes
crs_countrycode_metadata = {
    "table": "[Ref].[CRS_CountryCode]",
    "purpose": "Country code reference for CRS reporting",
    "columns": [
        {"name": "CountryShortCode", "type": "nvarchar(2)", "description": "ISO 2-letter country codes"},
        {"name": "Country", "type": "nvarchar(50)", "description": "Primary country name"},
        {"name": "Country2", "type": "nvarchar(50)", "description": "Alternative country name"},
        {"name": "Country3", "type": "nvarchar(50)", "description": "Additional country name variant"},
    ]
}

# Data Table: Ghana Account Reports
crs_gh_accountreport_metadata = {
    "table": "[DATA].[CRS_GH_AccountReport]",
    "purpose": "CRS account reporting data for Ghana",
    "key_fields": ["ParentID", "AccountNumber", "FirstName", "LastName", "AccountBalance"],
    "columns": [
        {"name": "ParentID", "type": "varchar(255)", "description": "Links to message specification"},
        {"name": "DocTypeIndic2", "type": "varchar(255)", "description": "Document type indicator"},
        {"name": "DocRefId3", "type": "varchar(255)", "description": "Document reference ID"},
        {"name": "AccountNumber", "type": "varchar(255)", "description": "Financial account number"},
        {"name": "AccNumberType", "type": "varchar(255)", "description": "Account number type"},
        {"name": "ClosedAccount", "type": "varchar(255)", "description": "Closed account indicator"},
        {"name": "DormantAccount", "type": "varchar(255)", "description": "Dormant account indicator"},
        {"name": "UndocumentedAccount", "type": "varchar(255)", "description": "Undocumented account indicator"},
        {"name": "ResCountryCode4", "type": "varchar(255)", "description": "Residence country code"},
        {"name": "AcctHolderType", "type": "varchar(255)", "description": "Account holder type"},
        {"name": "nameType", "type": "varchar(255)", "description": "Name type indicator"},
        {"name": "FirstName", "type": "varchar(255)", "description": "Account holder first name"},
        {"name": "LastName", "type": "varchar(255)", "description": "Account holder last name"},
        {"name": "MiddleName", "type": "varchar(255)", "description": "Account holder middle name"},
        {"name": "CountryCode5", "type": "varchar(255)", "description": "Address country code"},
        {"name": "Street", "type": "varchar(255)", "description": "Street address"},
        {"name": "PostCode", "type": "varchar(255)", "description": "Postal code"},
        {"name": "City", "type": "varchar(255)", "description": "City name"},
        {"name": "BirthDate", "type": "varchar(255)", "description": "Date of birth"},
        {"name": "TIN6", "type": "varchar(255)", "description": "Tax identification number"},
        {"name": "issuedBy7", "type": "varchar(255)", "description": "TIN issuing authority"},
        {"name": "AccountBalance", "type": "varchar(255)", "description": "Account balance amount"},
        {"name": "currCode", "type": "varchar(255)", "description": "Account balance currency"},
        {"name": "Type", "type": "varchar(255)", "description": "Payment type"},
        {"name": "PaymentAmnt", "type": "varchar(255)", "description": "Payment amount"},
        {"name": "currCode8", "type": "varchar(255)", "description": "Payment currency"},
        {"name": "Processed", "type": "bit", "description": "Processing status flag"},
    ]
}

# Data Table: Ghana Message Specifications
crs_gh_messagespec_metadata = {
    "table": "[DATA].[CRS_GH_MessageSpec]",
    "purpose": "CRS message header and reporting entity information",
    "key_fields": ["ParentID", "SendingCompanyIN", "MessageRefId", "ReportingPeriod"],
    "columns": [
        {"name": "ParentID", "type": "varchar(255)", "description": "Unique message identifier"},
        {"name": "version", "type": "varchar(255)", "description": "CRS schema version"},
        {"name": "SendingCompanyIN", "type": "varchar(255)", "description": "Sending company identifier"},
        {"name": "TransmittingCountry", "type": "varchar(255)", "description": "Transmitting country code"},
        {"name": "ReceivingCountry", "type": "varchar(255)", "description": "Receiving country code"},
        {"name": "MessageType", "type": "varchar(255)", "description": "Type of CRS message"},
        {"name": "MessageRefId", "type": "varchar(255)", "description": "Message reference identifier"},
        {"name": "MessageTypeIndic", "type": "varchar(255)", "description": "Message type indicator"},
        {"name": "ReportingPeriod", "type": "varchar(255)", "description": "Tax year/reporting period"},
        {"name": "Timestamp", "type": "varchar(255)", "description": "Message creation timestamp"},
        {"name": "ResCountryCode", "type": "varchar(255)", "description": "Reporting entity residence country"},
        {"name": "TIN", "type": "varchar(255)", "description": "Reporting entity tax ID"},
        {"name": "issuedBy", "type": "varchar(255)", "description": "TIN issuing jurisdiction"},
        {"name": "Name", "type": "varchar(255)", "description": "Reporting entity name"},
        {"name": "CountryCode", "type": "varchar(255)", "description": "Reporting entity country"},
        {"name": "AddressFree", "type": "varchar(255)", "description": "Reporting entity address"},
        {"name": "DocTypeIndic", "type": "varchar(255)", "description": "Document type indicator"},
        {"name": "DocRefId", "type": "varchar(255)", "description": "Document reference ID"},
        {"name": "Processed", "type": "bit", "description": "Processing status flag"},
    ]
}

# Relationships
crs_relationships = {
    "account_to_message": "ParentID in CRS_GH_AccountReport → ParentID in CRS_GH_MessageSpec",
    "country_lookups": "CountryCode fields → CRS_CountryCode.CountryShortCode"
}
