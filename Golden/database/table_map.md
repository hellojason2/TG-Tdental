# TDental Imported DB Table Map

Generated: 2026-03-01 07:20:44 UTC
Database: `tdental` in container `tdental-postgres`

## Summary

- Total tables imported: **398**
- Core-plan tables found: **22** / 26 expected
- Bonus tables: **376**

### Missing Expected Core Tables

- `dashboard_reports`
- `app_users`
- `app_sessions`
- `app_settings`

### Bonus Tables

| Table | Row Count |
|---|---:|
| `dbo.__efmigrationshistory` | 52 |
| `dbo.accountaccounts` | 123 |
| `dbo.accountaccounttypes` | 11 |
| `dbo.accountfinancialreportaccountaccounttyperels` | 4 |
| `dbo.accountfinancialreports` | 3 |
| `dbo.accountfinancialrevenuereportaccountaccountrels` | 0 |
| `dbo.accountfinancialrevenuereportaccountaccounttyperels` | 0 |
| `dbo.accountfinancialrevenuereports` | 0 |
| `dbo.accountfullreconciles` | 48237 |
| `dbo.accountinvoiceaccountmovelinerel` | 0 |
| `dbo.accountinvoicelines` | 0 |
| `dbo.accountinvoicelinetoothrel` | 0 |
| `dbo.accountinvoicepaymentrel` | 0 |
| `dbo.accountinvoices` | 0 |
| `dbo.accountjournals` | 89 |
| `dbo.accountmovelines` | 228721 |
| `dbo.accountmovepaymentrels` | 53713 |
| `dbo.accountmoves` | 113622 |
| `dbo.accountpartialreconciles` | 51427 |
| `dbo.accountregisterpaymentinvoicerel` | 0 |
| `dbo.accountregisterpayments` | 0 |
| `dbo.accounttaxes` | 0 |
| `dbo.accounttaxrepartitionlines` | 0 |
| `dbo.advisory` | 52 |
| `dbo.advisoryproductrels` | 45 |
| `dbo.advisorytoothdiagnosisrels` | 255 |
| `dbo.advisorytoothrels` | 0 |
| `dbo.agents` | 31 |
| `dbo.applicationrolefunctions` | 10317 |
| `dbo.applicationroleirrulerels` | 0 |
| `dbo.applicationrolemessagesubtyperels` | 0 |
| `dbo.applicationrolenotificationconfigs` | 8 |
| `dbo.appointmentalarmlines` | 72 |
| `dbo.appointmentconfirmeds` | 0 |
| `dbo.appointmentmailmessagerels` | 0 |
| `dbo.appointmentpartnerrels` | 64916 |
| `dbo.appttodayreminders` | 0 |
| `dbo.aspnetroleclaims` | 0 |
| `dbo.aspnetroles` | 10 |
| `dbo.aspnetuserclaims` | 0 |
| `dbo.aspnetuserlogins` | 0 |
| `dbo.aspnetuserroles` | 200 |
| `dbo.aspnetusertokens` | 0 |
| `dbo.authtotpdevices` | 0 |
| `dbo.authtotpwizards` | 0 |
| `dbo.automationactionstates` | 0 |
| `dbo.automationactiontargets` | 0 |
| `dbo.automationruns` | 0 |
| `dbo.baseautomations` | 0 |
| `dbo.baseautomationv2s` | 0 |
| `dbo.buspresences` | 128 |
| `dbo.callcalls` | 0 |
| `dbo.callcomposers` | 0 |
| `dbo.cardcards` | 0 |
| `dbo.cardhistories` | 0 |
| `dbo.chamcongs` | 780 |
| `dbo.changeloglines` | 18487045 |
| `dbo.changelogs` | 1818429 |
| `dbo.commissionhistories` | 12919 |
| `dbo.commissionhistorylines` | 12919 |
| `dbo.commissionparticipantroles` | 102072 |
| `dbo.commissionproductrules` | 1460 |
| `dbo.commissionsettlements` | 7526 |
| `dbo.companyproductpricerels` | 0 |
| `dbo.configmedicalprescriptions` | 0 |
| `dbo.configprints` | 0 |
| `dbo.conversationassignmentlogs` | 0 |
| `dbo.countries` | 195 |
| `dbo.couponprogramruleproductcategoryrels` | 0 |
| `dbo.crmcallcenteragent` | 0 |
| `dbo.crmcallcenterhistories` | 0 |
| `dbo.crmcallcenterlines` | 0 |
| `dbo.crmcallcenters` | 0 |
| `dbo.crmcallchannels` | 0 |
| `dbo.crmcalluserchannels` | 0 |
| `dbo.crmleadassignmenthistories` | 0 |
| `dbo.crmleadpartnercategoryrels` | 0 |
| `dbo.crmleads` | 0 |
| `dbo.crmstages` | 0 |
| `dbo.crmtaskactionlogs` | 0 |
| `dbo.crmtaskapplicationuserrels` | 0 |
| `dbo.crmtaskcategorydataincludeirmodelfieldrels` | 0 |
| `dbo.crmtaskcategorydataincludes` | 0 |
| `dbo.crmtaskcategorydataresults` | 0 |
| `dbo.crmtaskdataincludeirmodelfieldrels` | 0 |
| `dbo.crmtaskdataincludes` | 0 |
| `dbo.crmtaskdataresults` | 0 |
| `dbo.crmtaskrelations` | 0 |
| `dbo.crmtasktypes` | 4 |
| `dbo.crmteammembers` | 0 |
| `dbo.crmteams` | 7 |
| `dbo.currencies` | 1 |
| `dbo.currencyrates` | 0 |
| `dbo.customerreceiptproductrels` | 9823 |
| `dbo.devicelogs` | 145138 |
| `dbo.discusscontacthistories` | 0 |
| `dbo.dotkhamcompanyrels` | 0 |
| `dbo.dotkhamlineoperations` | 0 |
| `dbo.dotkhamlines` | 4 |
| `dbo.dotkhamlinetoothrels` | 0 |
| `dbo.dotkhamproductlineaccountmovelinerels` | 0 |
| `dbo.dotkhamproductlines` | 39465 |
| `dbo.dotkhamsteps` | 63896 |
| `dbo.dotkhamstepv2s` | 0 |
| `dbo.einvoiceaccountcompanyrels` | 0 |
| `dbo.einvoiceaccounts` | 0 |
| `dbo.einvoicetemplates` | 0 |
| `dbo.employeecategories` | 0 |
| `dbo.eventoutbox` | 0 |
| `dbo.facebookconnectpages` | 0 |
| `dbo.facebookconnects` | 0 |
| `dbo.facebookmassmessagings` | 0 |
| `dbo.facebookmessagingtraces` | 0 |
| `dbo.facebookpages` | 0 |
| `dbo.facebookscheduleappointmentconfigs` | 0 |
| `dbo.facebooktags` | 0 |
| `dbo.facebookuserprofiles` | 0 |
| `dbo.facebookuserprofiletagrels` | 0 |
| `dbo.giftcardcompanyrels` | 0 |
| `dbo.giftcardpartnerrels` | 0 |
| `dbo.giftcards` | 0 |
| `dbo.histories` | 0 |
| `dbo.historycategories` | 0 |
| `dbo.householdbusinesses` | 0 |
| `dbo.householdcompanyrels` | 0 |
| `dbo.hrjobs` | 40 |
| `dbo.hrpayrollstructures` | 0 |
| `dbo.hrpayrollstructuretypes` | 0 |
| `dbo.hrpaysliplines` | 0 |
| `dbo.hrpaysliprun2s` | 0 |
| `dbo.hrpayslipruns` | 5 |
| `dbo.hrpayslips` | 193 |
| `dbo.hrpayslipworkeddays` | 0 |
| `dbo.hrsalaryconfigs` | 0 |
| `dbo.hrsalaryrulecategories` | 0 |
| `dbo.hrsalaryrules` | 0 |
| `dbo.imbus` | 0 |
| `dbo.iractionservers` | 0 |
| `dbo.iractionserverv2s` | 0 |
| `dbo.irattachments` | 7984 |
| `dbo.irconfigparameters` | 7 |
| `dbo.irmodelaccesses` | 0 |
| `dbo.irmodeldatas` | 481 |
| `dbo.irmodelfields` | 49 |
| `dbo.irmodelfieldselections` | 22 |
| `dbo.irmodelfieldvalues` | 0 |
| `dbo.irmodels` | 100 |
| `dbo.irmodulecategories` | 5 |
| `dbo.irproperties` | 265 |
| `dbo.irrulecategories` | 0 |
| `dbo.irrules` | 73 |
| `dbo.irsequencedateranges` | 0 |
| `dbo.irsequences` | 165 |
| `dbo.labobitejoints` | 0 |
| `dbo.labobridges` | 0 |
| `dbo.labofinishlines` | 0 |
| `dbo.laboorderlines` | 0 |
| `dbo.laboorderlinetoothrels` | 0 |
| `dbo.laboorderproductrels` | 0 |
| `dbo.laboorders` | 0 |
| `dbo.laboordertoothrels` | 0 |
| `dbo.labowarranty` | 0 |
| `dbo.labowarrantytoothrels` | 0 |
| `dbo.lead2opportunitypartners` | 0 |
| `dbo.leadrecallrules` | 0 |
| `dbo.loaithuchis` | 0 |
| `dbo.mailactivities` | 0 |
| `dbo.mailactivitytypes` | 0 |
| `dbo.mailfollowermailmessagesubtyperels` | 0 |
| `dbo.mailfollowers` | 386518 |
| `dbo.mailmessagerespartnerrels` | 0 |
| `dbo.mailmessages` | 640707 |
| `dbo.mailmessagesubtypes` | 7 |
| `dbo.mailnotifications` | 0 |
| `dbo.mailpush` | 0 |
| `dbo.mailpushdevices` | 0 |
| `dbo.mailtrackingvalues` | 0 |
| `dbo.marketingcampaignactivities` | 0 |
| `dbo.marketingcampaignactivityfacebooktagrels` | 0 |
| `dbo.marketingcampaigns` | 0 |
| `dbo.marketingmessagebuttons` | 0 |
| `dbo.marketingmessages` | 0 |
| `dbo.marketingtraces` | 0 |
| `dbo.medicineorderlines` | 0 |
| `dbo.medicineorders` | 0 |
| `dbo.memberlevels` | 0 |
| `dbo.notifyconfigs` | 0 |
| `dbo.onlinesurveyquestionanswers` | 0 |
| `dbo.onlinesurveyquestions` | 0 |
| `dbo.onlinesurveysurveys` | 0 |
| `dbo.onlinesurveyuserinputemployeerels` | 0 |
| `dbo.onlinesurveyuserinputlines` | 0 |
| `dbo.onlinesurveyuserinputproductrels` | 0 |
| `dbo.onlinesurveyuserinputs` | 0 |
| `dbo.outboxstates` | 0 |
| `dbo.partneradvances` | 13591 |
| `dbo.partnerallowcompanyrels` | 22041 |
| `dbo.partnercontactstatuses` | 0 |
| `dbo.partnercustomerstatuschangelogs` | 0 |
| `dbo.partnerdebtadjustments` | 0 |
| `dbo.partnerhistoryrels` | 0 |
| `dbo.partnerimages` | 0 |
| `dbo.partnerlinkcompanies` | 0 |
| `dbo.partnermappsidfacebookpages` | 0 |
| `dbo.partnerpartnercategoryrel` | 4364 |
| `dbo.partnerprofilesummaries` | 11942 |
| `dbo.partnerreturnmarketinglogs` | 0 |
| `dbo.partnerserviceinterestrels` | 0 |
| `dbo.partnersubscriptions` | 3776 |
| `dbo.partnertitles` | 5 |
| `dbo.paymentquotations` | 0 |
| `dbo.paymentrequests` | 0 |
| `dbo.phieuthuchis` | 0 |
| `dbo.printpapersizes` | 2 |
| `dbo.printtemplateconfigs` | 9 |
| `dbo.printtemplateconfigv2s` | 0 |
| `dbo.printtemplates` | 49 |
| `dbo.productappointmentrels` | 18844 |
| `dbo.productboms` | 0 |
| `dbo.productcompanyrels` | 0 |
| `dbo.productpricehistories` | 554 |
| `dbo.productpricelistitems` | 0 |
| `dbo.productpricelists` | 1 |
| `dbo.productrequestlines` | 0 |
| `dbo.productrequests` | 0 |
| `dbo.productsteps` | 14 |
| `dbo.productstockinventorycriteriarels` | 0 |
| `dbo.productuomlines` | 3 |
| `dbo.productuomrels` | 216 |
| `dbo.promotionprogramcompanyrels` | 0 |
| `dbo.promotionprograms` | 0 |
| `dbo.promotionruleproductcategoryrels` | 0 |
| `dbo.promotionruleproductrels` | 0 |
| `dbo.promotionrules` | 0 |
| `dbo.purchaseorderlines` | 0 |
| `dbo.purchaseorders` | 0 |
| `dbo.quotationlines` | 649 |
| `dbo.quotationlinetoothrels` | 0 |
| `dbo.quotationpromotionlines` | 0 |
| `dbo.quotationpromotions` | 0 |
| `dbo.ratingratings` | 0 |
| `dbo.reportviewingconfigs` | 0 |
| `dbo.resbanks` | 53 |
| `dbo.rescompanyusersrels` | 384 |
| `dbo.resconfigsettings` | 5 |
| `dbo.resgroupimpliedrels` | 16 |
| `dbo.resgroups` | 35 |
| `dbo.resgroupsusersrels` | 1032 |
| `dbo.resinsurancepaymentlines` | 0 |
| `dbo.resinsurancepayments` | 0 |
| `dbo.resinsurances` | 0 |
| `dbo.resourcecalendarattendances` | 0 |
| `dbo.resourcecalendarleaves` | 0 |
| `dbo.resourcecalendars` | 0 |
| `dbo.respartnerbanks` | 0 |
| `dbo.rewardproductrels` | 0 |
| `dbo.routinglines` | 0 |
| `dbo.routings` | 0 |
| `dbo.rulegrouprels` | 0 |
| `dbo.salarypayments` | 0 |
| `dbo.salecouponhistories` | 0 |
| `dbo.salecouponprogramcardtyperels` | 0 |
| `dbo.salecouponprogramcompanyapplieds` | 0 |
| `dbo.salecouponprogrammemberlevelrels` | 0 |
| `dbo.salecouponprogrampartnerrels` | 0 |
| `dbo.salecouponprogramproductcategoryrels` | 0 |
| `dbo.salecouponprogramproductrels` | 0 |
| `dbo.salecouponprogramrewardproductcategoryrels` | 0 |
| `dbo.salecouponprogramrewardproductrels` | 0 |
| `dbo.salecouponprogramrewards` | 0 |
| `dbo.salecouponprogramrulecardtyperels` | 0 |
| `dbo.salecouponprogramrulepartnerrels` | 0 |
| `dbo.salecouponprogramruleproductrels` | 0 |
| `dbo.salecouponprogramrules` | 0 |
| `dbo.salecouponprograms` | 0 |
| `dbo.salecoupons` | 0 |
| `dbo.saleorderlinecommissionhistories` | 10214 |
| `dbo.saleorderlineinvoice2rels` | 52941 |
| `dbo.saleorderlineinvoicerels` | 0 |
| `dbo.saleorderlinepartnercommissions` | 0 |
| `dbo.saleorderlinepaymentrels` | 0 |
| `dbo.saleorderlineproductrequesteds` | 0 |
| `dbo.saleorderlinesaleproductionrels` | 0 |
| `dbo.saleorderlinetoothrels` | 64 |
| `dbo.saleordernocodepromoprograms` | 0 |
| `dbo.saleorderpaymentaccountmoverels` | 49536 |
| `dbo.saleorderpaymentaccountpaymentrels` | 54144 |
| `dbo.saleorderpaymenthistorylinedotkhamproductlinerels` | 0 |
| `dbo.saleorderpaymenthistorylines` | 52108 |
| `dbo.saleorderpaymentjournallineallocations` | 0 |
| `dbo.saleorderpaymentjournallines` | 54144 |
| `dbo.saleorderpaymentoutstandings` | 0 |
| `dbo.saleorderpaymentrels` | 0 |
| `dbo.saleorderpromotionlines` | 40 |
| `dbo.saleorderpromotions` | 49 |
| `dbo.saleorderservicecardcardrels` | 0 |
| `dbo.saleordertransfercompanies` | 0 |
| `dbo.saleproductionlineproductrequestlinerels` | 0 |
| `dbo.saleproductionlines` | 0 |
| `dbo.saleproductions` | 0 |
| `dbo.salesettings` | 1 |
| `dbo.sampleprescriptionlines` | 0 |
| `dbo.sampleprescriptions` | 0 |
| `dbo.scheduledjobs` | 0 |
| `dbo.servicecardcards` | 0 |
| `dbo.servicecardorderlineinvoicerels` | 0 |
| `dbo.servicecardorderlines` | 0 |
| `dbo.servicecardorderpaymentrels` | 0 |
| `dbo.servicecardorderpayments` | 0 |
| `dbo.servicecardorders` | 0 |
| `dbo.servicecardtypes` | 0 |
| `dbo.setupchamcongs` | 0 |
| `dbo.smsaccounts` | 0 |
| `dbo.smsappointmentautomationconfigs` | 0 |
| `dbo.smsbirthdayautomationconfigs` | 0 |
| `dbo.smscampaign` | 0 |
| `dbo.smscareafterorderautomationconfigs` | 0 |
| `dbo.smscomposers` | 0 |
| `dbo.smsconfigproductcategoryrels` | 0 |
| `dbo.smsconfigproductrels` | 0 |
| `dbo.smsmessageappointmentrels` | 0 |
| `dbo.smsmessagedetails` | 0 |
| `dbo.smsmessagepartnerrels` | 0 |
| `dbo.smsmessages` | 0 |
| `dbo.smsmessagesaleorderlinerels` | 0 |
| `dbo.smsmessagesaleorderrels` | 0 |
| `dbo.smstemplates` | 0 |
| `dbo.smsthankscustomerautomationconfigs` | 0 |
| `dbo.socialaccountmembers` | 0 |
| `dbo.socialaccounts` | 0 |
| `dbo.states` | 3654 |
| `dbo.stockinventory` | 18 |
| `dbo.stockinventorycriterias` | 1 |
| `dbo.stockinventoryline` | 1430 |
| `dbo.stocklocations` | 23 |
| `dbo.stockmovemoverels` | 0 |
| `dbo.stockpickingtypes` | 16 |
| `dbo.stockquantmoverel` | 1267 |
| `dbo.stockquants` | 815 |
| `dbo.stockvaluationlayers` | 907 |
| `dbo.stockwarehouses` | 8 |
| `dbo.surveyanswers` | 0 |
| `dbo.surveyassignments` | 0 |
| `dbo.surveycallcontents` | 0 |
| `dbo.surveyquestions` | 0 |
| `dbo.surveytags` | 0 |
| `dbo.surveyuserinputlines` | 0 |
| `dbo.surveyuserinputs` | 0 |
| `dbo.surveyuserinputsurveytagrels` | 0 |
| `dbo.tcarecampaigns` | 0 |
| `dbo.tcareconfigs` | 0 |
| `dbo.tcaremessages` | 0 |
| `dbo.tcaremessagetemplates` | 0 |
| `dbo.tcaremessagingpartnerrels` | 0 |
| `dbo.tcaremessagings` | 0 |
| `dbo.tcareproperties` | 0 |
| `dbo.tcarerules` | 0 |
| `dbo.tcarescenarios` | 0 |
| `dbo.teeth` | 52 |
| `dbo.toathuoclines` | 0 |
| `dbo.toathuocs` | 0 |
| `dbo.toothcategories` | 2 |
| `dbo.toothdiagnosis` | 300 |
| `dbo.toothdiagnosisproductrels` | 0 |
| `dbo.toothinitials` | 0 |
| `dbo.toothprocedures` | 536 |
| `dbo.uomcategories` | 5 |
| `dbo.uoms` | 418 |
| `dbo.userbackupcodes` | 0 |
| `dbo.userdevices` | 1689 |
| `dbo.userrefreshtokens` | 20873 |
| `dbo.workentrytypes` | 0 |
| `dbo.zalooaconfigs` | 0 |
| `dbo.zalotemplates` | 0 |
| `dbo.znscomposers` | 0 |
| `dbo.znsmessages` | 0 |

## Full Table Details

### `dbo.__efmigrationshistory`

- Row count: **52**
- Primary key: `migrationid`
- Columns (2): migrationid (text NOT NULL), productversion (text NOT NULL)
- Key foreign keys:
  - (none)

### `dbo.accountaccounts`

- Row count: **123**
- Primary key: `id`
- Columns (14): id (uuid NOT NULL), name (text NOT NULL), code (text NOT NULL), usertypeid (uuid NOT NULL), active (boolean NOT NULL), note (text), companyid (uuid NOT NULL), internaltype (text), reconcile (boolean NOT NULL), isexcludedprofitandlossreport (boolean NOT NULL), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_accountaccounts_accountaccounttypes_usertypeid`: (usertypeid) -> `dbo.accountaccounttypes` (id)
  - `fk_accountaccounts_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_accountaccounts_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_accountaccounts_companies_companyid`: (companyid) -> `dbo.companies` (id)

### `dbo.accountaccounttypes`

- Row count: **11**
- Primary key: `id`
- Columns (9): id (uuid NOT NULL), name (text NOT NULL), type (text NOT NULL), note (text), includeinitialbalance (boolean NOT NULL), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_accountaccounttypes_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_accountaccounttypes_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)

### `dbo.accountfinancialreportaccountaccounttyperels`

- Row count: **4**
- Primary key: `accounttypeid, financialreportid`
- Columns (2): accounttypeid (uuid NOT NULL), financialreportid (uuid NOT NULL)
- Key foreign keys:
  - `fk_accountfinancialreportaccountaccounttyperels_accountaccountt`: (accounttypeid) -> `dbo.accountaccounttypes` (id)
  - `fk_accountfinancialreportaccountaccounttyperels_accountfinancia`: (financialreportid) -> `dbo.accountfinancialreports` (id)

### `dbo.accountfinancialreports`

- Row count: **3**
- Primary key: `id`
- Columns (12): id (uuid NOT NULL), name (text NOT NULL), parentid (uuid), level (integer), sequence (integer), type (text), sign (integer NOT NULL), displaydetail (text), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_accountfinancialreports_accountfinancialreports_parentid`: (parentid) -> `dbo.accountfinancialreports` (id)
  - `fk_accountfinancialreports_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_accountfinancialreports_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)

### `dbo.accountfinancialrevenuereportaccountaccountrels`

- Row count: **0**
- Primary key: `id`
- Columns (9): id (uuid NOT NULL), accountcode (text), financialrevenuereportid (uuid NOT NULL), column (integer NOT NULL), journaltypes (text), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_accountfinancialrevenuereportaccountaccountrels_accountfinan`: (financialrevenuereportid) -> `dbo.accountfinancialrevenuereports` (id)
  - `fk_accountfinancialrevenuereportaccountaccountrels_aspnetusers_`: (createdbyid) -> `dbo.aspnetusers` (id)

### `dbo.accountfinancialrevenuereportaccountaccounttyperels`

- Row count: **0**
- Primary key: `accounttypeid, financialrevenuereportid`
- Columns (4): accounttypeid (uuid NOT NULL), financialrevenuereportid (uuid NOT NULL), column (integer NOT NULL), journaltypes (text)
- Key foreign keys:
  - `fk_accountfinancialrevenuereportaccountaccounttyperels_accounta`: (accounttypeid) -> `dbo.accountaccounttypes` (id)
  - `fk_accountfinancialrevenuereportaccountaccounttyperels_accountf`: (financialrevenuereportid) -> `dbo.accountfinancialrevenuereports` (id)

### `dbo.accountfinancialrevenuereports`

- Row count: **0**
- Primary key: `id`
- Columns (12): id (uuid NOT NULL), name (text NOT NULL), parentid (uuid), level (integer), sequence (integer), type (text), sign (integer NOT NULL), displaydetail (text), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_accountfinancialrevenuereports_accountfinancialrevenuereport`: (parentid) -> `dbo.accountfinancialrevenuereports` (id)
  - `fk_accountfinancialrevenuereports_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_accountfinancialrevenuereports_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)

### `dbo.accountfullreconciles`

- Row count: **48237**
- Primary key: `id`
- Columns (7): id (uuid NOT NULL), name (text NOT NULL), exchangemoveid (uuid), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_accountfullreconciles_accountmoves_exchangemoveid`: (exchangemoveid) -> `dbo.accountmoves` (id)
  - `fk_accountfullreconciles_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_accountfullreconciles_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)

### `dbo.accountinvoiceaccountmovelinerel`

- Row count: **0**
- Primary key: `accountinvoiceid, movelineid`
- Columns (2): accountinvoiceid (uuid NOT NULL), movelineid (uuid NOT NULL)
- Key foreign keys:
  - `fk_accountinvoiceaccountmovelinerel_accountinvoices_accountinvo`: (accountinvoiceid) -> `dbo.accountinvoices` (id)
  - `fk_accountinvoiceaccountmovelinerel_accountmovelines_movelineid`: (movelineid) -> `dbo.accountmovelines` (id)

### `dbo.accountinvoicelines`

- Row count: **0**
- Primary key: `id`
- Columns (26): id (uuid NOT NULL), name (text NOT NULL), origin (text), sequence (integer NOT NULL), invoiceid (uuid), uomid (uuid), productid (uuid), accountid (uuid NOT NULL), priceunit (numeric(18,2) NOT NULL), pricesubtotal (numeric(18,2) NOT NULL), pricesubtotalsigned (numeric(18,2) NOT NULL), discount (numeric(18,2) NOT NULL), quantity (numeric(18,2) NOT NULL), partnerid (uuid), companyid (uuid), employeeid (uuid), toothcategoryid (uuid), note (text), diagnostic (text), toothid (uuid), labolineid (uuid), purchaselineid (uuid), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_accountinvoicelines_accountaccounts_accountid`: (accountid) -> `dbo.accountaccounts` (id)
  - `fk_accountinvoicelines_accountinvoices_invoiceid`: (invoiceid) -> `dbo.accountinvoices` (id)
  - `fk_accountinvoicelines_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_accountinvoicelines_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_accountinvoicelines_companies_companyid`: (companyid) -> `dbo.companies` (id)
  - `fk_accountinvoicelines_laboorderlines_labolineid`: (labolineid) -> `dbo.laboorderlines` (id)
  - `fk_accountinvoicelines_partners_employeeid`: (employeeid) -> `dbo.partners` (id)
  - `fk_accountinvoicelines_partners_partnerid`: (partnerid) -> `dbo.partners` (id)
  - ... and 5 more

### `dbo.accountinvoicelinetoothrel`

- Row count: **0**
- Primary key: `invoicelineid, toothid`
- Columns (2): invoicelineid (uuid NOT NULL), toothid (uuid NOT NULL)
- Key foreign keys:
  - `fk_accountinvoicelinetoothrel_accountinvoicelines_invoicelineid`: (invoicelineid) -> `dbo.accountinvoicelines` (id)
  - `fk_accountinvoicelinetoothrel_teeth_toothid`: (toothid) -> `dbo.teeth` (id)

### `dbo.accountinvoicepaymentrel`

- Row count: **0**
- Primary key: `paymentid, invoiceid`
- Columns (2): paymentid (uuid NOT NULL), invoiceid (uuid NOT NULL)
- Key foreign keys:
  - `fk_accountinvoicepaymentrel_accountinvoices_invoiceid`: (invoiceid) -> `dbo.accountinvoices` (id)
  - `fk_accountinvoicepaymentrel_accountpayments_paymentid`: (paymentid) -> `dbo.accountpayments` (id)

### `dbo.accountinvoices`

- Row count: **0**
- Primary key: `id`
- Columns (37): id (uuid NOT NULL), name (text), origin (text), type (text), refundinvoiceid (uuid), number (text), movename (text), reference (text), comment (text), state (text), sent (boolean NOT NULL), dateinvoice (timestamp without time zone), datedue (timestamp without time zone), partnerid (uuid NOT NULL), moveid (uuid), amounttotal (numeric(18,2) NOT NULL), journalid (uuid NOT NULL), reconciled (boolean NOT NULL), residual (numeric(18,2) NOT NULL), accountid (uuid), userid (text), amounttotalsigned (numeric(18,2) NOT NULL), residualsigned (numeric(18,2) NOT NULL), companyid (uuid NOT NULL), date (timestamp without time zone), amounttax (numeric(18,2) NOT NULL), amountuntaxed (numeric(18,2) NOT NULL), dateorder (timestamp without time zone), note (text), discounttype (text), discountpercent (numeric(18,2) NOT NULL), discountfixed (numeric(18,2) NOT NULL), discountamount (numeric(18,2) NOT NULL), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_accountinvoices_accountaccounts_accountid`: (accountid) -> `dbo.accountaccounts` (id)
  - `fk_accountinvoices_accountinvoices_refundinvoiceid`: (refundinvoiceid) -> `dbo.accountinvoices` (id)
  - `fk_accountinvoices_accountjournals_journalid`: (journalid) -> `dbo.accountjournals` (id)
  - `fk_accountinvoices_accountmoves_moveid`: (moveid) -> `dbo.accountmoves` (id)
  - `fk_accountinvoices_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_accountinvoices_aspnetusers_userid`: (userid) -> `dbo.aspnetusers` (id)
  - `fk_accountinvoices_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_accountinvoices_companies_companyid`: (companyid) -> `dbo.companies` (id)
  - ... and 1 more

### `dbo.accountjournals`

- Row count: **89**
- Primary key: `id`
- Columns (18): id (uuid NOT NULL), name (text NOT NULL), code (text NOT NULL), active (boolean NOT NULL), type (text NOT NULL), defaultdebitaccountid (uuid), defaultcreditaccountid (uuid), updateposted (boolean NOT NULL), sequenceid (uuid NOT NULL), refundsequenceid (uuid), companyid (uuid NOT NULL), dedicatedrefund (boolean NOT NULL), bankaccountid (uuid), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone), issecondary (boolean NOT NULL)
- Key foreign keys:
  - `fk_accountjournals_accountaccounts_defaultcreditaccountid`: (defaultcreditaccountid) -> `dbo.accountaccounts` (id)
  - `fk_accountjournals_accountaccounts_defaultdebitaccountid`: (defaultdebitaccountid) -> `dbo.accountaccounts` (id)
  - `fk_accountjournals_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_accountjournals_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_accountjournals_companies_companyid`: (companyid) -> `dbo.companies` (id)
  - `fk_accountjournals_irsequences_refundsequenceid`: (refundsequenceid) -> `dbo.irsequences` (id)
  - `fk_accountjournals_irsequences_sequenceid`: (sequenceid) -> `dbo.irsequences` (id)
  - `fk_accountjournals_respartnerbanks_bankaccountid`: (bankaccountid) -> `dbo.respartnerbanks` (id)

### `dbo.accountmovelines`

- Row count: **228721**
- Primary key: `id`
- Columns (57): id (uuid NOT NULL), name (text NOT NULL), quantity (numeric(18,2)), productuomid (uuid), productid (uuid), debit (numeric(18,2) NOT NULL), credit (numeric(18,2) NOT NULL), balance (numeric(18,2) NOT NULL), ref (text), journalid (uuid), datematurity (timestamp without time zone), partnerid (uuid), date (timestamp without time zone), moveid (uuid NOT NULL), accountid (uuid NOT NULL), amountresidual (numeric(18,2) NOT NULL), companyid (uuid), reconciled (boolean NOT NULL), paymentid (uuid), fullreconcileid (uuid), invoiceid (uuid), discount (numeric(18,2)), priceunit (numeric(18,2)), excludefrominvoicetab (boolean), movename (text), parentstate (text), accountinternaltype (text), pricesubtotal (numeric(18,2)), pricetotal (numeric(18,2)), purchaselineid (uuid), labolineid (uuid), discounttype (text), discountfixed (numeric(18,2)), phieuthuchiid (uuid), salesmanid (text), employeeid (uuid), assistantid (uuid), insuranceid (uuid), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone), counselorid (uuid), amountcurrency (numeric(18,2)), amountresidualcurrency (numeric(18,2)), companycurrencyid (uuid), currencyid (uuid), currencyrate (double precision), dotkhamlineid (uuid), taxid (uuid), taxrepartitionlineid (uuid), amountdiscount (numeric(18,2)), loaithuchiid (uuid), tax2id (uuid), assistantsecondaryid (uuid), agentid (uuid), isoldflow (boolean NOT NULL)
- Key foreign keys:
  - `fk_accountmovelines_accountaccounts_accountid`: (accountid) -> `dbo.accountaccounts` (id)
  - `fk_accountmovelines_accountfullreconciles_fullreconcileid`: (fullreconcileid) -> `dbo.accountfullreconciles` (id)
  - `fk_accountmovelines_accountinvoices_invoiceid`: (invoiceid) -> `dbo.accountinvoices` (id)
  - `fk_accountmovelines_accountjournals_journalid`: (journalid) -> `dbo.accountjournals` (id)
  - `fk_accountmovelines_accountmoves_moveid`: (moveid) -> `dbo.accountmoves` (id)
  - `fk_accountmovelines_accountpayments_paymentid`: (paymentid) -> `dbo.accountpayments` (id)
  - `fk_accountmovelines_accounttaxes_tax2id`: (tax2id) -> `dbo.accounttaxes` (id)
  - `fk_accountmovelines_accounttaxes_taxid`: (taxid) -> `dbo.accounttaxes` (id)
  - ... and 21 more

### `dbo.accountmovepaymentrels`

- Row count: **53713**
- Primary key: `paymentid, moveid`
- Columns (2): moveid (uuid NOT NULL), paymentid (uuid NOT NULL)
- Key foreign keys:
  - `fk_accountmovepaymentrels_accountmoves_moveid`: (moveid) -> `dbo.accountmoves` (id)
  - `fk_accountmovepaymentrels_accountpayments_paymentid`: (paymentid) -> `dbo.accountpayments` (id)

### `dbo.accountmoves`

- Row count: **113622**
- Primary key: `id`
- Columns (64): id (uuid NOT NULL), name (text NOT NULL), ref (text), date (timestamp without time zone NOT NULL), journalid (uuid NOT NULL), state (text NOT NULL), narration (text), partnerid (uuid), companyid (uuid), amount (numeric(18,2) NOT NULL), type (text), invoiceorigin (text), amountuntaxed (numeric(18,2)), amounttax (numeric(18,2)), amounttotal (numeric(18,2)), amountresidual (numeric(18,2)), amountuntaxedsigned (numeric(18,2)), amounttaxsigned (numeric(18,2)), amounttotalsigned (numeric(18,2)), amountresidualsigned (numeric(18,2)), invoicepaymentstate (text), invoicedate (timestamp without time zone), invoicepaymentref (text), invoiceuserid (text), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone), amounttotalincurrencysigned (numeric(18,2)), currencyid (uuid), invoiceorigin2 (text), selleraddress (text), sellername (text), sellertaxcode (text), buyeraddress (text), buyername (text), buyertaxcode (text), buyerlegalname (text), iscompany (boolean NOT NULL), iselecinvoicerequested (boolean NOT NULL), amountdiscount (numeric(18,2)), einvoicetemplateid (uuid), externaleinvoiceid (text), einvoicestate (text), einvoicestatuscode (text), einvoicestatusmessage (text), buyerlegaladdress (text), buyerlegalsubname (text), sendinvoiceby (text), sendinvoiceemail (text), sendinvoicezalo (text), securitycode (text), einvoicecqtstate (text), einvoicenaturestate (text), reversedentryid (uuid), invoicenumber (text), paymentjournalid (uuid), saleorderid (uuid), paymentmethodname (text), buyerpersonalidentitycard (text), buyerpersonaltaxcode (text), householdbusinessid (uuid), sequencenumber (integer), sequenceprefix (text)
- Key foreign keys:
  - `fk_accountmoves_accountjournals_journalid`: (journalid) -> `dbo.accountjournals` (id)
  - `fk_accountmoves_accountjournals_paymentjournalid`: (paymentjournalid) -> `dbo.accountjournals` (id)
  - `fk_accountmoves_accountmoves_reversedentryid`: (reversedentryid) -> `dbo.accountmoves` (id)
  - `fk_accountmoves_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_accountmoves_aspnetusers_invoiceuserid`: (invoiceuserid) -> `dbo.aspnetusers` (id)
  - `fk_accountmoves_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_accountmoves_companies_companyid`: (companyid) -> `dbo.companies` (id)
  - `fk_accountmoves_currencies_currencyid`: (currencyid) -> `dbo.currencies` (id)
  - ... and 4 more

### `dbo.accountpartialreconciles`

- Row count: **51427**
- Primary key: `id`
- Columns (14): id (uuid NOT NULL), debitmoveid (uuid NOT NULL), creditmoveid (uuid NOT NULL), amount (numeric(18,2) NOT NULL), companyid (uuid), fullreconcileid (uuid), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone), creditamountcurrency (numeric(18,2)), creditcurrencyid (uuid), debitamountcurrency (numeric(18,2)), debitcurrencyid (uuid)
- Key foreign keys:
  - `fk_accountpartialreconciles_accountfullreconciles_fullreconcile`: (fullreconcileid) -> `dbo.accountfullreconciles` (id)
  - `fk_accountpartialreconciles_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_accountpartialreconciles_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_accountpartialreconciles_companies_companyid`: (companyid) -> `dbo.companies` (id)
  - `fk_accountpartialreconciles_currencies_creditcurrencyid`: (creditcurrencyid) -> `dbo.currencies` (id)
  - `fk_accountpartialreconciles_currencies_debitcurrencyid`: (debitcurrencyid) -> `dbo.currencies` (id)

### `dbo.accountpayments`

- Row count: **54322**
- Primary key: `id`
- Columns (35): id (uuid NOT NULL), companyid (uuid), partnerid (uuid), partnertype (text), paymentdate (timestamp without time zone NOT NULL), journalid (uuid NOT NULL), insuranceid (uuid), state (text), name (text), paymenttype (text NOT NULL), amount (numeric(18,2) NOT NULL), communication (text), paymentdifferencehandling (text), writeoffaccountid (uuid), destinationaccountid (uuid), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone), destinationjournalid (uuid), isinternaltransfer (boolean), pairedinternaltransferpaymentid (uuid), destinationcompanyid (uuid), isintercompany (boolean NOT NULL), pairedintercompanypaymentid (uuid), paymentrequestid (uuid), partnerbankid (uuid), partnerjournaltype (text), requester (text), currencyid (uuid), householdbusinessid (uuid), isprepayment (boolean NOT NULL), moveid (uuid), sequencenumber (integer), sequenceprefix (text)
- Key foreign keys:
  - `fk_accountpayments_accountaccounts_destinationaccountid`: (destinationaccountid) -> `dbo.accountaccounts` (id)
  - `fk_accountpayments_accountaccounts_writeoffaccountid`: (writeoffaccountid) -> `dbo.accountaccounts` (id)
  - `fk_accountpayments_accountjournals_destinationjournalid`: (destinationjournalid) -> `dbo.accountjournals` (id)
  - `fk_accountpayments_accountjournals_journalid`: (journalid) -> `dbo.accountjournals` (id)
  - `fk_accountpayments_accountmoves_moveid`: (moveid) -> `dbo.accountmoves` (id)
  - `fk_accountpayments_accountpayments_pairedintercompanypaymentid`: (pairedintercompanypaymentid) -> `dbo.accountpayments` (id)
  - `fk_accountpayments_accountpayments_pairedinternaltransferpaymen`: (pairedinternaltransferpaymentid) -> `dbo.accountpayments` (id)
  - `fk_accountpayments_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - ... and 9 more

### `dbo.accountregisterpaymentinvoicerel`

- Row count: **0**
- Primary key: `paymentid, invoiceid`
- Columns (2): paymentid (uuid NOT NULL), invoiceid (uuid NOT NULL)
- Key foreign keys:
  - `fk_accountregisterpaymentinvoicerel_accountinvoices_invoiceid`: (invoiceid) -> `dbo.accountinvoices` (id)
  - `fk_accountregisterpaymentinvoicerel_accountregisterpayments_pay`: (paymentid) -> `dbo.accountregisterpayments` (id)

### `dbo.accountregisterpayments`

- Row count: **0**
- Primary key: `id`
- Columns (12): id (uuid NOT NULL), paymentdate (timestamp without time zone NOT NULL), communication (text), journalid (uuid NOT NULL), partnertype (text), amount (numeric(18,2) NOT NULL), paymenttype (text NOT NULL), partnerid (uuid), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_accountregisterpayments_accountjournals_journalid`: (journalid) -> `dbo.accountjournals` (id)
  - `fk_accountregisterpayments_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_accountregisterpayments_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_accountregisterpayments_partners_partnerid`: (partnerid) -> `dbo.partners` (id)

### `dbo.accounttaxes`

- Row count: **0**
- Primary key: `id`
- Columns (13): id (uuid NOT NULL), name (text), active (boolean NOT NULL), amount (numeric(18,2) NOT NULL), invoicelabel (text), amounttype (text), datecreated (timestamp without time zone), createdbyid (text), lastupdated (timestamp without time zone), writebyid (text), priceinclude (boolean NOT NULL), istaxablerate (boolean NOT NULL), isdeleted (boolean NOT NULL)
- Key foreign keys:
  - `fk_accounttaxes_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_accounttaxes_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)

### `dbo.accounttaxrepartitionlines`

- Row count: **0**
- Primary key: `id`
- Columns (13): id (uuid NOT NULL), factorpercent (double precision NOT NULL), repartitiontype (text NOT NULL), accountid (uuid), invoicetaxid (uuid), refundtaxid (uuid), companyid (uuid), sequence (integer), useintaxclosing (boolean), datecreated (timestamp without time zone), createdbyid (text), lastupdated (timestamp without time zone), writebyid (text)
- Key foreign keys:
  - `fk_accounttaxrepartitionlines_accountaccounts_accountid`: (accountid) -> `dbo.accountaccounts` (id)
  - `fk_accounttaxrepartitionlines_accounttaxes_invoicetaxid`: (invoicetaxid) -> `dbo.accounttaxes` (id)
  - `fk_accounttaxrepartitionlines_accounttaxes_refundtaxid`: (refundtaxid) -> `dbo.accounttaxes` (id)
  - `fk_accounttaxrepartitionlines_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_accounttaxrepartitionlines_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_accounttaxrepartitionlines_companies_companyid`: (companyid) -> `dbo.companies` (id)

### `dbo.advisory`

- Row count: **52**
- Primary key: `id`
- Columns (12): id (uuid NOT NULL), date (timestamp without time zone NOT NULL), employeeid (uuid), customerid (uuid), toothcategoryid (uuid), toothtype (text), note (text), companyid (uuid NOT NULL), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_advisory_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_advisory_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_advisory_companies_companyid`: (companyid) -> `dbo.companies` (id)
  - `fk_advisory_employees_employeeid`: (employeeid) -> `dbo.employees` (id)
  - `fk_advisory_partners_customerid`: (customerid) -> `dbo.partners` (id)
  - `fk_advisory_toothcategories_toothcategoryid`: (toothcategoryid) -> `dbo.toothcategories` (id)

### `dbo.advisoryproductrels`

- Row count: **45**
- Primary key: `advisoryid, productid`
- Columns (2): advisoryid (uuid NOT NULL), productid (uuid NOT NULL)
- Key foreign keys:
  - `fk_advisoryproductrels_advisory_advisoryid`: (advisoryid) -> `dbo.advisory` (id)
  - `fk_advisoryproductrels_products_productid`: (productid) -> `dbo.products` (id)

### `dbo.advisorytoothdiagnosisrels`

- Row count: **255**
- Primary key: `advisoryid, toothdiagnosisid`
- Columns (2): advisoryid (uuid NOT NULL), toothdiagnosisid (uuid NOT NULL)
- Key foreign keys:
  - `fk_advisorytoothdiagnosisrels_advisory_advisoryid`: (advisoryid) -> `dbo.advisory` (id)
  - `fk_advisorytoothdiagnosisrels_toothdiagnosis_toothdiagnosisid`: (toothdiagnosisid) -> `dbo.toothdiagnosis` (id)

### `dbo.advisorytoothrels`

- Row count: **0**
- Primary key: `advisoryid, toothid`
- Columns (2): advisoryid (uuid NOT NULL), toothid (uuid NOT NULL)
- Key foreign keys:
  - `fk_advisorytoothrels_advisory_advisoryid`: (advisoryid) -> `dbo.advisory` (id)
  - `fk_advisorytoothrels_teeth_toothid`: (toothid) -> `dbo.teeth` (id)

### `dbo.agents`

- Row count: **31**
- Primary key: `id`
- Columns (24): id (uuid NOT NULL), name (text), classify (text), customerid (uuid), employeeid (uuid), gender (text), birthyear (integer), birthmonth (integer), birthday (integer), jobtitle (text), phone (text), email (text), address (text), bankid (uuid), bankbranch (text), accountnumber (text), accountholder (text), companyid (uuid), partnerid (uuid), commissionid (uuid), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_agents_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_agents_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_agents_commissions_commissionid`: (commissionid) -> `dbo.commissions` (id)
  - `fk_agents_companies_companyid`: (companyid) -> `dbo.companies` (id)
  - `fk_agents_employees_employeeid`: (employeeid) -> `dbo.employees` (id)
  - `fk_agents_partners_customerid`: (customerid) -> `dbo.partners` (id)
  - `fk_agents_partners_partnerid`: (partnerid) -> `dbo.partners` (id)
  - `fk_agents_resbanks_bankid`: (bankid) -> `dbo.resbanks` (id)

### `dbo.applicationrolefunctions`

- Row count: **10317**
- Primary key: `id`
- Columns (7): id (uuid NOT NULL), func (text NOT NULL), roleid (text), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_applicationrolefunctions_aspnetroles_roleid`: (roleid) -> `dbo.aspnetroles` (id)
  - `fk_applicationrolefunctions_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_applicationrolefunctions_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)

### `dbo.applicationroleirrulerels`

- Row count: **0**
- Primary key: `roleid, irruleid`
- Columns (2): roleid (text NOT NULL), irruleid (uuid NOT NULL)
- Key foreign keys:
  - `fk_applicationroleirrulerels_aspnetroles_roleid`: (roleid) -> `dbo.aspnetroles` (id)
  - `fk_applicationroleirrulerels_irrules_irruleid`: (irruleid) -> `dbo.irrules` (id)

### `dbo.applicationrolemessagesubtyperels`

- Row count: **0**
- Primary key: `roleid, subtypeid`
- Columns (2): roleid (text NOT NULL), subtypeid (uuid NOT NULL)
- Key foreign keys:
  - `fk_applicationrolemessagesubtyperels_aspnetroles_roleid`: (roleid) -> `dbo.aspnetroles` (id)
  - `fk_applicationrolemessagesubtyperels_mailmessagesubtypes_subtyp`: (subtypeid) -> `dbo.mailmessagesubtypes` (id)

### `dbo.applicationrolenotificationconfigs`

- Row count: **8**
- Primary key: `id`
- Columns (9): id (uuid NOT NULL), appttodaynotify (boolean NOT NULL), appttodayfilter (text), roleid (text), datecreated (timestamp without time zone), createdbyid (text), lastupdated (timestamp without time zone), writebyid (text), apptfromhead (boolean NOT NULL)
- Key foreign keys:
  - `fk_applicationrolenotificationconfigs_aspnetroles_roleid`: (roleid) -> `dbo.aspnetroles` (id)
  - `fk_applicationrolenotificationconfigs_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_applicationrolenotificationconfigs_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)

### `dbo.appointmentalarmlines`

- Row count: **72**
- Primary key: `id`
- Columns (10): id (uuid NOT NULL), appointmentid (uuid NOT NULL), alarmtype (integer NOT NULL), duration (integer NOT NULL), interval (integer NOT NULL), durationminutes (integer), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_appointmentalarmlines_appointments_appointmentid`: (appointmentid) -> `dbo.appointments` (id)
  - `fk_appointmentalarmlines_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_appointmentalarmlines_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)

### `dbo.appointmentconfirmeds`

- Row count: **0**
- Primary key: `id`
- Columns (8): id (uuid NOT NULL), name (text NOT NULL), sequence (integer), color (integer), datecreated (timestamp without time zone), createdbyid (text), lastupdated (timestamp without time zone), writebyid (text)
- Key foreign keys:
  - `fk_appointmentconfirmeds_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_appointmentconfirmeds_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)

### `dbo.appointmentmailmessagerels`

- Row count: **0**
- Primary key: `appointmentid, mailmessageid`
- Columns (2): appointmentid (uuid NOT NULL), mailmessageid (uuid NOT NULL)
- Key foreign keys:
  - `fk_appointmentmailmessagerels_appointments_appointmentid`: (appointmentid) -> `dbo.appointments` (id)
  - `fk_appointmentmailmessagerels_mailmessages_mailmessageid`: (mailmessageid) -> `dbo.mailmessages` (id)

### `dbo.appointmentpartnerrels`

- Row count: **64916**
- Primary key: `appointmentid, partnerid`
- Columns (2): appointmentid (uuid NOT NULL), partnerid (uuid NOT NULL)
- Key foreign keys:
  - `fk_appointmentpartnerrels_appointments_appointmentid`: (appointmentid) -> `dbo.appointments` (id)
  - `fk_appointmentpartnerrels_partners_partnerid`: (partnerid) -> `dbo.partners` (id)

### `dbo.appointments`

- Row count: **214900**
- Primary key: `id`
- Columns (36): id (uuid NOT NULL), name (text NOT NULL), date (timestamp without time zone NOT NULL), time (text), datetimeappointment (timestamp without time zone), dateappointmentreminder (timestamp without time zone), timeexpected (integer NOT NULL), note (text), userid (text), partnerid (uuid NOT NULL), companyid (uuid NOT NULL), dotkhamid (uuid), doctorid (uuid), state (text), reason (text), saleorderid (uuid), isrepeatcustomer (boolean NOT NULL), color (text), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone), leadid (uuid), callid (uuid), teamid (uuid), lastdatereminder (timestamp without time zone), confirmedid (uuid), datetimearrived (timestamp without time zone), datetimedismissed (timestamp without time zone), datetimeseated (timestamp without time zone), aptstate (text), customerreceiptid (uuid), customercarestatus (integer), datedone (timestamp without time zone), isnotreatment (boolean NOT NULL), crmtaskid (uuid)
- Key foreign keys:
  - `fk_appointments_appointmentconfirmeds_confirmedid`: (confirmedid) -> `dbo.appointmentconfirmeds` (id)
  - `fk_appointments_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_appointments_aspnetusers_userid`: (userid) -> `dbo.aspnetusers` (id)
  - `fk_appointments_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_appointments_callcalls_callid`: (callid) -> `dbo.callcalls` (id)
  - `fk_appointments_companies_companyid`: (companyid) -> `dbo.companies` (id)
  - `fk_appointments_crmleads_leadid`: (leadid) -> `dbo.crmleads` (id)
  - `fk_appointments_crmtasks_crmtaskid`: (crmtaskid) -> `dbo.crmtasks` (id)
  - ... and 6 more

### `dbo.appttodayreminders`

- Row count: **0**
- Primary key: `id`
- Columns (9): id (uuid NOT NULL), companyid (uuid NOT NULL), roleid (text), filter (text), userid (text), datecreated (timestamp without time zone), createdbyid (text), lastupdated (timestamp without time zone), writebyid (text)
- Key foreign keys:
  - `fk_appttodayreminders_aspnetroles_roleid`: (roleid) -> `dbo.aspnetroles` (id)
  - `fk_appttodayreminders_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_appttodayreminders_aspnetusers_userid`: (userid) -> `dbo.aspnetusers` (id)
  - `fk_appttodayreminders_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_appttodayreminders_companies_companyid`: (companyid) -> `dbo.companies` (id)

### `dbo.aspnetroleclaims`

- Row count: **0**
- Primary key: `id`
- Columns (4): id (integer NOT NULL), roleid (text NOT NULL), claimtype (text), claimvalue (text)
- Key foreign keys:
  - `fk_aspnetroleclaims_aspnetroles_roleid`: (roleid) -> `dbo.aspnetroles` (id)

### `dbo.aspnetroles`

- Row count: **10**
- Primary key: `id`
- Columns (7): id (text NOT NULL), hidden (boolean NOT NULL), name (text), normalizedname (text), concurrencystamp (text), module (text), groupid (uuid)
- Key foreign keys:
  - `fk_aspnetroles_resgroups_groupid`: (groupid) -> `dbo.resgroups` (id)

### `dbo.aspnetuserclaims`

- Row count: **0**
- Primary key: `id`
- Columns (4): id (integer NOT NULL), userid (text NOT NULL), claimtype (text), claimvalue (text)
- Key foreign keys:
  - `fk_aspnetuserclaims_aspnetusers_userid`: (userid) -> `dbo.aspnetusers` (id)

### `dbo.aspnetuserlogins`

- Row count: **0**
- Primary key: `loginprovider, providerkey`
- Columns (4): loginprovider (text NOT NULL), providerkey (text NOT NULL), providerdisplayname (text), userid (text NOT NULL)
- Key foreign keys:
  - `fk_aspnetuserlogins_aspnetusers_userid`: (userid) -> `dbo.aspnetusers` (id)

### `dbo.aspnetuserroles`

- Row count: **200**
- Primary key: `userid, roleid`
- Columns (2): userid (text NOT NULL), roleid (text NOT NULL)
- Key foreign keys:
  - `fk_aspnetuserroles_aspnetroles_roleid`: (roleid) -> `dbo.aspnetroles` (id)
  - `fk_aspnetuserroles_aspnetusers_userid`: (userid) -> `dbo.aspnetusers` (id)

### `dbo.aspnetusers`

- Row count: **221**
- Primary key: `id`
- Columns (24): id (text NOT NULL), name (text NOT NULL), partnerid (uuid NOT NULL), companyid (uuid NOT NULL), active (boolean NOT NULL), isuserroot (boolean NOT NULL), facebookpageid (uuid), username (text), normalizedusername (text), email (text), normalizedemail (text), emailconfirmed (boolean NOT NULL), passwordhash (text), securitystamp (text), concurrencystamp (text), phonenumber (text), phonenumberconfirmed (boolean NOT NULL), twofactorenabled (boolean NOT NULL), lockoutend (timestamp with time zone), lockoutenabled (boolean NOT NULL), accessfailedcount (integer NOT NULL), tenantid (text), companyisunrestricted (boolean NOT NULL), totpsecret (text)
- Key foreign keys:
  - `fk_aspnetusers_companies_companyid`: (companyid) -> `dbo.companies` (id)
  - `fk_aspnetusers_facebookpages_facebookpageid`: (facebookpageid) -> `dbo.facebookpages` (id)
  - `fk_aspnetusers_partners_partnerid`: (partnerid) -> `dbo.partners` (id)

### `dbo.aspnetusertokens`

- Row count: **0**
- Primary key: `userid, loginprovider, name`
- Columns (4): userid (text NOT NULL), loginprovider (text NOT NULL), name (text NOT NULL), value (text)
- Key foreign keys:
  - `fk_aspnetusertokens_aspnetusers_userid`: (userid) -> `dbo.aspnetusers` (id)

### `dbo.authtotpdevices`

- Row count: **0**
- Primary key: `id`
- Columns (9): id (uuid NOT NULL), name (text NOT NULL), userid (text NOT NULL), scope (text), expirationdate (timestamp without time zone), datecreated (timestamp without time zone), createdbyid (text), lastupdated (timestamp without time zone), writebyid (text)
- Key foreign keys:
  - `fk_authtotpdevices_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_authtotpdevices_aspnetusers_userid`: (userid) -> `dbo.aspnetusers` (id)
  - `fk_authtotpdevices_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)

### `dbo.authtotpwizards`

- Row count: **0**
- Primary key: `id`
- Columns (10): id (uuid NOT NULL), code (text), userid (text NOT NULL), secret (text NOT NULL), url (text), qrcode (bytea), datecreated (timestamp without time zone), createdbyid (text), lastupdated (timestamp without time zone), writebyid (text)
- Key foreign keys:
  - `fk_authtotpwizards_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_authtotpwizards_aspnetusers_userid`: (userid) -> `dbo.aspnetusers` (id)
  - `fk_authtotpwizards_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)

### `dbo.automationactionstates`

- Row count: **0**
- Primary key: `id`
- Columns (10): id (uuid NOT NULL), datedone (timestamp without time zone), lastid (uuid), actionid (uuid NOT NULL), rowversion (bytea), datecreated (timestamp without time zone), createdbyid (text), lastupdated (timestamp without time zone), writebyid (text), runid (uuid)
- Key foreign keys:
  - `fk_automationactionstates_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_automationactionstates_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_automationactionstates_automationruns_runid`: (runid) -> `dbo.automationruns` (id)
  - `fk_automationactionstates_iractionserverv2s_actionid`: (actionid) -> `dbo.iractionserverv2s` (id)

### `dbo.automationactiontargets`

- Row count: **0**
- Primary key: `id`
- Columns (8): id (uuid NOT NULL), resmodel (text), resid (uuid NOT NULL), actionstateid (uuid NOT NULL), datecreated (timestamp without time zone), createdbyid (text), lastupdated (timestamp without time zone), writebyid (text)
- Key foreign keys:
  - `fk_automationactiontargets_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_automationactiontargets_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_automationactiontargets_automationactionstates_actionstateid`: (actionstateid) -> `dbo.automationactionstates` (id)

### `dbo.automationruns`

- Row count: **0**
- Primary key: `id`
- Columns (6): id (uuid NOT NULL), automationid (uuid NOT NULL), datecreated (timestamp without time zone), createdbyid (text), lastupdated (timestamp without time zone), writebyid (text)
- Key foreign keys:
  - `fk_automationruns_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_automationruns_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_automationruns_baseautomationv2s_automationid`: (automationid) -> `dbo.baseautomationv2s` (id)

### `dbo.baseautomations`

- Row count: **0**
- Primary key: `id`
- Columns (18): id (uuid NOT NULL), name (text), description (text), active (boolean NOT NULL), model (text), trigger (text), triggerdatefield (text), triggerdaterange (integer), triggerdaterangetype (text), filterdomain (text), lastrun (timestamp without time zone), datecreated (timestamp without time zone), createdbyid (text), lastupdated (timestamp without time zone), writebyid (text), scheduletime (timestamp without time zone), scheduletype (text), onchangefields (text)
- Key foreign keys:
  - `fk_baseautomations_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_baseautomations_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)

### `dbo.baseautomationv2s`

- Row count: **0**
- Primary key: `id`
- Columns (28): id (uuid NOT NULL), name (text), description (text), active (boolean NOT NULL), isdeleted (boolean NOT NULL), triggertype (text), filterdomain (text), scheduletype (text), scheduletime (timestamp without time zone), lastrun (timestamp without time zone), isalwayrun (boolean NOT NULL), dateexpire (timestamp without time zone), timerepeat (integer NOT NULL), repeattype (text), repeatrule (text), datecreated (timestamp without time zone), createdbyid (text), lastupdated (timestamp without time zone), writebyid (text), nextrun (timestamp without time zone), state (text), istemplate (boolean), scheduledjobid (text), actiontrigger (text), conditiontrigger (text), modeltrigger (text), fieldchangetrigger (text), valuechangetrigger (text)
- Key foreign keys:
  - `fk_baseautomationv2s_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_baseautomationv2s_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)

### `dbo.buspresences`

- Row count: **128**
- Primary key: `id`
- Columns (9): id (uuid NOT NULL), userid (text), lastpoll (timestamp without time zone NOT NULL), lastpresence (timestamp without time zone NOT NULL), datecreated (timestamp without time zone), createdbyid (text), lastupdated (timestamp without time zone), writebyid (text), status (text)
- Key foreign keys:
  - `fk_buspresences_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_buspresences_aspnetusers_userid`: (userid) -> `dbo.aspnetusers` (id)
  - `fk_buspresences_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)

### `dbo.callcalls`

- Row count: **0**
- Primary key: `id`
- Columns (34): id (uuid NOT NULL), receiptnumber (text), state (text), partnerid (uuid), numberext (text), callcenterid (uuid), mailmessageid (uuid), datecreated (timestamp without time zone), createdbyid (text), lastupdated (timestamp without time zone), writebyid (text), direction (text), linkfile (text), uniqueid (text), phonename (text), disposition (integer NOT NULL), timeanswer (timestamp without time zone), timecall (timestamp without time zone), answereduserid (text), note (text), resid (uuid), resmodel (text), timedial (timestamp without time zone), timeend (timestamp without time zone), active (boolean NOT NULL), callednumber (text), callingname (text), callingnumber (text), callinguserid (text), started (timestamp without time zone), callcenteragentid (uuid), callid (text), hotline (text), content (text)
- Key foreign keys:
  - `fk_callcalls_aspnetusers_answereduserid`: (answereduserid) -> `dbo.aspnetusers` (id)
  - `fk_callcalls_aspnetusers_callinguserid`: (callinguserid) -> `dbo.aspnetusers` (id)
  - `fk_callcalls_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_callcalls_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_callcalls_crmcallcenteragent_callcenteragentid`: (callcenteragentid) -> `dbo.crmcallcenteragent` (id)
  - `fk_callcalls_crmcallcenters_callcenterid`: (callcenterid) -> `dbo.crmcallcenters` (id)
  - `fk_callcalls_mailmessages_mailmessageid`: (mailmessageid) -> `dbo.mailmessages` (id)
  - `fk_callcalls_partners_partnerid`: (partnerid) -> `dbo.partners` (id)

### `dbo.callcomposers`

- Row count: **0**
- Primary key: `id`
- Columns (10): id (uuid NOT NULL), resmodel (text), resid (uuid), number (text), agentid (uuid), datecreated (timestamp without time zone), createdbyid (text), lastupdated (timestamp without time zone), writebyid (text), callname (text)
- Key foreign keys:
  - `fk_callcomposers_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_callcomposers_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_callcomposers_crmcallcenteragent_agentid`: (agentid) -> `dbo.crmcallcenteragent` (id)

### `dbo.cardcards`

- Row count: **0**
- Primary key: `id`
- Columns (16): id (uuid NOT NULL), name (text NOT NULL), typeid (uuid NOT NULL), state (text), activateddate (timestamp without time zone), barcode (text), partnerid (uuid), totalpoint (numeric(18,2)), pointinperiod (numeric(18,2)), expireddate (timestamp without time zone), upgradetypeid (uuid), companyid (uuid), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_cardcards_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_cardcards_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_cardcards_cardtypes_typeid`: (typeid) -> `dbo.cardtypes` (id)
  - `fk_cardcards_cardtypes_upgradetypeid`: (upgradetypeid) -> `dbo.cardtypes` (id)
  - `fk_cardcards_companies_companyid`: (companyid) -> `dbo.companies` (id)
  - `fk_cardcards_partners_partnerid`: (partnerid) -> `dbo.partners` (id)

### `dbo.cardhistories`

- Row count: **0**
- Primary key: `id`
- Columns (11): id (uuid NOT NULL), cardid (uuid NOT NULL), startdate (timestamp without time zone), enddate (timestamp without time zone), pointinperiod (numeric(18,2)), totalpoint (numeric(18,2)), typeid (uuid NOT NULL), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_cardhistories_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_cardhistories_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_cardhistories_cardcards_cardid`: (cardid) -> `dbo.cardcards` (id)
  - `fk_cardhistories_cardtypes_typeid`: (typeid) -> `dbo.cardtypes` (id)

### `dbo.cardtypes`

- Row count: **0**
- Primary key: `id`
- Columns (15): id (uuid NOT NULL), name (text NOT NULL), basicpoint (numeric(18,2)), discount (numeric(18,2) NOT NULL), pricelistid (uuid), nbperiod (integer NOT NULL), period (text), sequence (integer), note (text), color (text), companyid (uuid), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_cardtypes_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_cardtypes_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_cardtypes_companies_companyid`: (companyid) -> `dbo.companies` (id)
  - `fk_cardtypes_productpricelists_pricelistid`: (pricelistid) -> `dbo.productpricelists` (id)

### `dbo.chamcongs`

- Row count: **780**
- Primary key: `id`
- Columns (16): id (uuid NOT NULL), employeeid (uuid NOT NULL), timein (timestamp without time zone), date (timestamp without time zone), timeout (timestamp without time zone), hourworked (numeric(18,2)), companyid (uuid NOT NULL), status (text), workentrytypeid (uuid), type (text), overtime (boolean NOT NULL), overtimehour (numeric(18,2)), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_chamcongs_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_chamcongs_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_chamcongs_companies_companyid`: (companyid) -> `dbo.companies` (id)
  - `fk_chamcongs_employees_employeeid`: (employeeid) -> `dbo.employees` (id)
  - `fk_chamcongs_workentrytypes_workentrytypeid`: (workentrytypeid) -> `dbo.workentrytypes` (id)

### `dbo.changeloglines`

- Row count: **18487045**
- Primary key: `id`
- Columns (22): id (uuid NOT NULL), changelogid (uuid NOT NULL), trackingsequence (integer), fielddesc (text), fieldtype (text), oldvalueguid (uuid), newvalueguid (uuid), oldvalueinteger (integer), newvalueinteger (integer), oldvaluestring (text), newvaluestring (text), oldvaluedatetime (timestamp without time zone), newvaluedatetime (timestamp without time zone), oldvaluedecimal (numeric(18,2)), newvaluedecimal (numeric(18,2)), oldvaluedouble (double precision), newvaluedouble (double precision), irmodelfieldid (uuid), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_changeloglines_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_changeloglines_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_changeloglines_changelogs_changelogid`: (changelogid) -> `dbo.changelogs` (id)
  - `fk_changeloglines_irmodelfields_irmodelfieldid`: (irmodelfieldid) -> `dbo.irmodelfields` (id)

### `dbo.changelogs`

- Row count: **1818429**
- Primary key: `id`
- Columns (17): id (uuid NOT NULL), name (text), date (timestamp without time zone NOT NULL), model (text), recordname (text), parentname (text), resid (uuid NOT NULL), partnerid (uuid), companyid (uuid), userid (text), parentid (uuid), irmodelid (uuid), state (text), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_changelogs_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_changelogs_aspnetusers_userid`: (userid) -> `dbo.aspnetusers` (id)
  - `fk_changelogs_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_changelogs_changelogs_parentid`: (parentid) -> `dbo.changelogs` (id)
  - `fk_changelogs_companies_companyid`: (companyid) -> `dbo.companies` (id)
  - `fk_changelogs_irmodels_irmodelid`: (irmodelid) -> `dbo.irmodels` (id)
  - `fk_changelogs_partners_partnerid`: (partnerid) -> `dbo.partners` (id)

### `dbo.commissionhistories`

- Row count: **12919**
- Primary key: `id`
- Columns (13): id (uuid NOT NULL), date (timestamp without time zone), partnerid (uuid), employeeid (uuid), agentid (uuid), commissionid (uuid), companyid (uuid), state (text), saleorderpaymentid (uuid), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_commissionhistories_agents_agentid`: (agentid) -> `dbo.agents` (id)
  - `fk_commissionhistories_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_commissionhistories_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_commissionhistories_commissions_commissionid`: (commissionid) -> `dbo.commissions` (id)
  - `fk_commissionhistories_companies_companyid`: (companyid) -> `dbo.companies` (id)
  - `fk_commissionhistories_employees_employeeid`: (employeeid) -> `dbo.employees` (id)
  - `fk_commissionhistories_partners_partnerid`: (partnerid) -> `dbo.partners` (id)
  - `fk_commissionhistories_saleorderpayments_saleorderpaymentid`: (saleorderpaymentid) -> `dbo.saleorderpayments` (id)

### `dbo.commissionhistorylines`

- Row count: **12919**
- Primary key: `id`
- Columns (14): id (uuid NOT NULL), productid (uuid), productqty (numeric(18,2) NOT NULL), productpricewithdiscount (numeric(18,2)), productstandardprice (numeric(18,2)), profitamount (numeric(18,2)), paymentamount (numeric(18,2)), profitamounttotal (numeric(18,2)), saleorderlineid (uuid), commissionhistoryid (uuid NOT NULL), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_commissionhistorylines_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_commissionhistorylines_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_commissionhistorylines_commissionhistories_commissionhistory`: (commissionhistoryid) -> `dbo.commissionhistories` (id)
  - `fk_commissionhistorylines_products_productid`: (productid) -> `dbo.products` (id)
  - `fk_commissionhistorylines_saleorderlines_saleorderlineid`: (saleorderlineid) -> `dbo.saleorderlines` (id)

### `dbo.commissionparticipantroles`

- Row count: **102072**
- Primary key: `id`
- Columns (9): id (uuid NOT NULL), employeeid (uuid), role (text), accountmovelineid (uuid), datecreated (timestamp without time zone), createdbyid (text), lastupdated (timestamp without time zone), writebyid (text), userid (text)
- Key foreign keys:
  - `fk_commissionparticipantroles_accountmovelines_accountmovelinei`: (accountmovelineid) -> `dbo.accountmovelines` (id)
  - `fk_commissionparticipantroles_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_commissionparticipantroles_aspnetusers_userid`: (userid) -> `dbo.aspnetusers` (id)
  - `fk_commissionparticipantroles_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_commissionparticipantroles_employees_employeeid`: (employeeid) -> `dbo.employees` (id)

### `dbo.commissionproductrules`

- Row count: **1460**
- Primary key: `id`
- Columns (13): id (uuid NOT NULL), appliedon (text), productid (uuid), categid (uuid), commissiontype (text), percent (numeric(18,2)), fixedamount (numeric(18,2)), commissionid (uuid NOT NULL), companyid (uuid), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_commissionproductrules_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_commissionproductrules_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_commissionproductrules_commissions_commissionid`: (commissionid) -> `dbo.commissions` (id)
  - `fk_commissionproductrules_companies_companyid`: (companyid) -> `dbo.companies` (id)
  - `fk_commissionproductrules_productcategories_categid`: (categid) -> `dbo.productcategories` (id)
  - `fk_commissionproductrules_products_productid`: (productid) -> `dbo.products` (id)

### `dbo.commissions`

- Row count: **17**
- Primary key: `id`
- Columns (9): id (uuid NOT NULL), name (text NOT NULL), active (boolean NOT NULL), type (text), companyid (uuid), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_commissions_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_commissions_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_commissions_companies_companyid`: (companyid) -> `dbo.companies` (id)

### `dbo.commissionsettlements`

- Row count: **7526**
- Primary key: `id`
- Columns (26): id (uuid NOT NULL), partnerid (uuid), employeeid (uuid), agentid (uuid), totalamount (numeric(18,2)), baseamount (numeric(18,2)), commissiontype (text), productqty (numeric(18,2)), percentage (numeric(18,2)), fixedamount (numeric(18,2)), amount (numeric(18,2)), profitamount (numeric(18,2)), factor (numeric(18,2)), movelineid (uuid), commissionid (uuid), date (timestamp without time zone), productid (uuid), saleorderlineid (uuid), historylineid (uuid), commissionhistoryid (uuid), commissionproductruleid (uuid), companyid (uuid), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_commissionsettlements_accountmovelines_movelineid`: (movelineid) -> `dbo.accountmovelines` (id)
  - `fk_commissionsettlements_agents_agentid`: (agentid) -> `dbo.agents` (id)
  - `fk_commissionsettlements_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_commissionsettlements_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_commissionsettlements_commissionhistories_commissionhistoryi`: (commissionhistoryid) -> `dbo.commissionhistories` (id)
  - `fk_commissionsettlements_commissionproductrules_commissionprodu`: (commissionproductruleid) -> `dbo.commissionproductrules` (id)
  - `fk_commissionsettlements_commissions_commissionid`: (commissionid) -> `dbo.commissions` (id)
  - `fk_commissionsettlements_companies_companyid`: (companyid) -> `dbo.companies` (id)
  - ... and 5 more

### `dbo.companies`

- Row count: **7**
- Primary key: `id`
- Columns (36): id (uuid NOT NULL), name (text NOT NULL), partnerid (uuid NOT NULL), email (text), phone (text), periodlockdate (timestamp without time zone), accountincomeid (uuid), accountexpenseid (uuid), logo (text), active (boolean NOT NULL), reportheader (text), reportfooter (text), notallowexportinventorynegative (boolean NOT NULL), medicalfacilitycode (text), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone), isuppercasepartnername (boolean NOT NULL), ishead (boolean NOT NULL), paymentsmsvalidation (boolean NOT NULL), paymentsmsvalidationtemplateid (uuid), currencyid (uuid), isconnectconfigmedicalprescription (boolean NOT NULL), taxbankaccount (text), taxbankname (text), taxcode (text), taxphone (text), taxunitaddress (text), taxunitname (text), einvoiceaccountid (uuid), einvoicetemplateid (uuid), defaulthouseholdid (uuid), revenueinvisibledate (timestamp without time zone), parentid (uuid), parentpath (text)
- Key foreign keys:
  - `fk_companies_accountaccounts_accountexpenseid`: (accountexpenseid) -> `dbo.accountaccounts` (id)
  - `fk_companies_accountaccounts_accountincomeid`: (accountincomeid) -> `dbo.accountaccounts` (id)
  - `fk_companies_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_companies_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_companies_companies_parentid`: (parentid) -> `dbo.companies` (id)
  - `fk_companies_currencies_currencyid`: (currencyid) -> `dbo.currencies` (id)
  - `fk_companies_einvoiceaccounts_einvoiceaccountid`: (einvoiceaccountid) -> `dbo.einvoiceaccounts` (id)
  - `fk_companies_einvoicetemplates_einvoicetemplateid`: (einvoicetemplateid) -> `dbo.einvoicetemplates` (id)
  - ... and 3 more

### `dbo.companyproductpricerels`

- Row count: **0**
- Primary key: `companyid, productpricelistid`
- Columns (2): companyid (uuid NOT NULL), productpricelistid (uuid NOT NULL)
- Key foreign keys:
  - `fk_companyproductpricerels_companies_companyid`: (companyid) -> `dbo.companies` (id)
  - `fk_companyproductpricerels_productpricelists_productpricelistid`: (productpricelistid) -> `dbo.productpricelists` (id)

### `dbo.configmedicalprescriptions`

- Row count: **0**
- Primary key: `id`
- Columns (11): id (uuid NOT NULL), companyid (uuid NOT NULL), name (text), active (boolean NOT NULL), username (text), password (text), datecreated (timestamp without time zone), createdbyid (text), lastupdated (timestamp without time zone), writebyid (text), token (text)
- Key foreign keys:
  - `fk_configmedicalprescriptions_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_configmedicalprescriptions_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_configmedicalprescriptions_companies_companyid`: (companyid) -> `dbo.companies` (id)

### `dbo.configprints`

- Row count: **0**
- Primary key: `id`
- Columns (9): id (uuid NOT NULL), papersizeid (uuid), name (text), isinfocompany (boolean NOT NULL), companyid (uuid NOT NULL), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_configprints_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_configprints_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_configprints_companies_companyid`: (companyid) -> `dbo.companies` (id)
  - `fk_configprints_printpapersizes_papersizeid`: (papersizeid) -> `dbo.printpapersizes` (id)

### `dbo.conversationassignmentlogs`

- Row count: **0**
- Primary key: `id`
- Columns (9): id (uuid NOT NULL), userid (text), lastassign (timestamp without time zone), socialaccountid (uuid), datecreated (timestamp without time zone), createdbyid (text), lastupdated (timestamp without time zone), writebyid (text), teamid (uuid)
- Key foreign keys:
  - `fk_conversationassignmentlogs_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_conversationassignmentlogs_aspnetusers_userid`: (userid) -> `dbo.aspnetusers` (id)
  - `fk_conversationassignmentlogs_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_conversationassignmentlogs_crmteams_teamid`: (teamid) -> `dbo.crmteams` (id)
  - `fk_conversationassignmentlogs_socialaccounts_socialaccountid`: (socialaccountid) -> `dbo.socialaccounts` (id)

### `dbo.countries`

- Row count: **195**
- Primary key: `id`
- Columns (8): id (uuid NOT NULL), code (text), name (text), value (integer NOT NULL), datecreated (timestamp without time zone), createdbyid (text), lastupdated (timestamp without time zone), writebyid (text)
- Key foreign keys:
  - `fk_countries_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_countries_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)

### `dbo.couponprogramruleproductcategoryrels`

- Row count: **0**
- Primary key: `programruleid, productcategoryid`
- Columns (2): programruleid (uuid NOT NULL), productcategoryid (uuid NOT NULL)
- Key foreign keys:
  - `fk_couponprogramruleproductcategoryrels_productcategories_produ`: (productcategoryid) -> `dbo.productcategories` (id)
  - `fk_couponprogramruleproductcategoryrels_salecouponprogramrules_`: (programruleid) -> `dbo.salecouponprogramrules` (id)

### `dbo.crmcallcenteragent`

- Row count: **0**
- Primary key: `id`
- Columns (13): id (uuid NOT NULL), userid (text), serverid (uuid NOT NULL), callcenterlineid (uuid), datecreated (timestamp without time zone), createdbyid (text), lastupdated (timestamp without time zone), writebyid (text), numberext (text), hotline (text), isblocked (boolean NOT NULL), prefix (text), active (boolean NOT NULL)
- Key foreign keys:
  - `fk_crmcallcenteragent_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_crmcallcenteragent_aspnetusers_userid`: (userid) -> `dbo.aspnetusers` (id)
  - `fk_crmcallcenteragent_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_crmcallcenteragent_crmcallcenterlines_callcenterlineid`: (callcenterlineid) -> `dbo.crmcallcenterlines` (id)
  - `fk_crmcallcenteragent_crmcallcenters_serverid`: (serverid) -> `dbo.crmcallcenters` (id)

### `dbo.crmcallcenterhistories`

- Row count: **0**
- Primary key: `id`
- Columns (21): id (uuid NOT NULL), date (timestamp without time zone NOT NULL), key (text), callcenterid (uuid NOT NULL), callname (text), callnumber (text), queuenumber (text), receiptnumber (text), direction (text), numberpbx (text), totaltimecall (text), realtimecall (text), linkfile (text), message (text), status (text), datecreated (timestamp without time zone), createdbyid (text), lastupdated (timestamp without time zone), writebyid (text), companyid (uuid), agentid (uuid)
- Key foreign keys:
  - `fk_crmcallcenterhistories_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_crmcallcenterhistories_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_crmcallcenterhistories_companies_companyid`: (companyid) -> `dbo.companies` (id)
  - `fk_crmcallcenterhistories_crmcallcenteragent_agentid`: (agentid) -> `dbo.crmcallcenteragent` (id)
  - `fk_crmcallcenterhistories_crmcallcenters_callcenterid`: (callcenterid) -> `dbo.crmcallcenters` (id)

### `dbo.crmcallcenterlines`

- Row count: **0**
- Primary key: `id`
- Columns (8): id (uuid NOT NULL), callcenterid (uuid NOT NULL), name (text NOT NULL), datecreated (timestamp without time zone), createdbyid (text), lastupdated (timestamp without time zone), writebyid (text), numberpbx (text)
- Key foreign keys:
  - `fk_crmcallcenterlines_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_crmcallcenterlines_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_crmcallcenterlines_crmcallcenters_callcenterid`: (callcenterid) -> `dbo.crmcallcenters` (id)

### `dbo.crmcallcenters`

- Row count: **0**
- Primary key: `id`
- Columns (16): id (uuid NOT NULL), servicename (text), authkey (text), authuser (text), datecreated (timestamp without time zone), createdbyid (text), lastupdated (timestamp without time zone), writebyid (text), active (boolean NOT NULL), companyid (uuid), name (text), type (text), apikey (text), apisecert (text), token (text), tokenexpiry (timestamp without time zone)
- Key foreign keys:
  - `fk_crmcallcenters_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_crmcallcenters_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_crmcallcenters_companies_companyid`: (companyid) -> `dbo.companies` (id)

### `dbo.crmcallchannels`

- Row count: **0**
- Primary key: `id`
- Columns (26): id (uuid NOT NULL), eventtime (timestamp without time zone), callid (uuid), serverid (uuid), userid (text), channel (text), uniqueid (text), linkedid (text), context (text), connectedlinenum (text), connectedlinename (text), state (text), statedesc (text), exten (text), calleridnum (text), calleridname (text), cause (text), causetxt (text), hangupdate (timestamp without time zone), event (text), recordingfilepath (text), active (boolean NOT NULL), datecreated (timestamp without time zone), createdbyid (text), lastupdated (timestamp without time zone), writebyid (text)
- Key foreign keys:
  - `fk_crmcallchannels_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_crmcallchannels_aspnetusers_userid`: (userid) -> `dbo.aspnetusers` (id)
  - `fk_crmcallchannels_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_crmcallchannels_callcalls_callid`: (callid) -> `dbo.callcalls` (id)
  - `fk_crmcallchannels_crmcallcenters_serverid`: (serverid) -> `dbo.crmcallcenters` (id)

### `dbo.crmcalluserchannels`

- Row count: **0**
- Primary key: `id`
- Columns (9): id (uuid NOT NULL), name (text NOT NULL), pbxuserid (uuid NOT NULL), serverid (uuid), sequence (integer), datecreated (timestamp without time zone), createdbyid (text), lastupdated (timestamp without time zone), writebyid (text)
- Key foreign keys:
  - `fk_crmcalluserchannels_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_crmcalluserchannels_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_crmcalluserchannels_crmcallcenteragent_pbxuserid`: (pbxuserid) -> `dbo.crmcallcenteragent` (id)
  - `fk_crmcalluserchannels_crmcallcenters_serverid`: (serverid) -> `dbo.crmcallcenters` (id)

### `dbo.crmleadassignmenthistories`

- Row count: **0**
- Primary key: `id`
- Columns (9): id (uuid NOT NULL), leadid (uuid NOT NULL), assigneduserid (text), assigneddate (timestamp without time zone NOT NULL), datecreated (timestamp without time zone), createdbyid (text), lastupdated (timestamp without time zone), writebyid (text), teamid (uuid)
- Key foreign keys:
  - `fk_crmleadassignmenthistories_aspnetusers_assigneduserid`: (assigneduserid) -> `dbo.aspnetusers` (id)
  - `fk_crmleadassignmenthistories_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_crmleadassignmenthistories_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_crmleadassignmenthistories_crmleads_leadid`: (leadid) -> `dbo.crmleads` (id)
  - `fk_crmleadassignmenthistories_crmteams_teamid`: (teamid) -> `dbo.crmteams` (id)

### `dbo.crmleadpartnercategoryrels`

- Row count: **0**
- Primary key: `categoryid, leadid`
- Columns (2): categoryid (uuid NOT NULL), leadid (uuid NOT NULL)
- Key foreign keys:
  - `fk_crmleadpartnercategoryrels_crmleads_leadid`: (leadid) -> `dbo.crmleads` (id)
  - `fk_crmleadpartnercategoryrels_partnercategories_categoryid`: (categoryid) -> `dbo.partnercategories` (id)

### `dbo.crmleads`

- Row count: **0**
- Primary key: `id`
- Columns (51): id (uuid NOT NULL), name (text NOT NULL), phone (text), email (text), userid (text), description (text), companyid (uuid), active (boolean NOT NULL), function (text), titleid (uuid), street (text), countryid (uuid), citycode (text), cityname (text), districtcode (text), districtname (text), wardcode (text), wardname (text), stateid (uuid), sourceid (uuid), birthyear (integer), birthmonth (integer), birthday (integer), datecreated (timestamp without time zone), createdbyid (text), lastupdated (timestamp without time zone), writebyid (text), gender (text), partnerid (uuid), stageid (uuid), channelid (text), channeltype (integer), socialid (text), teamid (uuid), conversationid (text), customerticketexpireddate (timestamp without time zone), iscustomerticket (boolean NOT NULL), deactivereason (text), ref (text), dateassign (timestamp without time zone), dateconversion (timestamp without time zone), datelastaction (timestamp without time zone), datelaststageupdate (timestamp without time zone), lastcrmtaskdone (timestamp without time zone), nextcrmtaskdate (timestamp without time zone), citycodev2 (text), citynamev2 (text), usedaddressv2 (boolean), wardcodev2 (text), wardnamev2 (text), extraproperties (text)
- Key foreign keys:
  - `fk_crmleads_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_crmleads_aspnetusers_userid`: (userid) -> `dbo.aspnetusers` (id)
  - `fk_crmleads_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_crmleads_companies_companyid`: (companyid) -> `dbo.companies` (id)
  - `fk_crmleads_countries_countryid`: (countryid) -> `dbo.countries` (id)
  - `fk_crmleads_crmstages_stageid`: (stageid) -> `dbo.crmstages` (id)
  - `fk_crmleads_crmteams_teamid`: (teamid) -> `dbo.crmteams` (id)
  - `fk_crmleads_partners_partnerid`: (partnerid) -> `dbo.partners` (id)
  - ... and 3 more

### `dbo.crmstages`

- Row count: **0**
- Primary key: `id`
- Columns (9): id (uuid NOT NULL), name (text NOT NULL), color (integer), sequence (integer), datecreated (timestamp without time zone), createdbyid (text), lastupdated (timestamp without time zone), writebyid (text), iswon (boolean)
- Key foreign keys:
  - `fk_crmstages_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_crmstages_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)

### `dbo.crmtaskactionlogs`

- Row count: **0**
- Primary key: `id`
- Columns (11): id (uuid NOT NULL), actiontype (text), targetmodel (text), targetfield (text), targetid (uuid), newvalue (text), crmtaskid (uuid), datecreated (timestamp without time zone), createdbyid (text), lastupdated (timestamp without time zone), writebyid (text)
- Key foreign keys:
  - `fk_crmtaskactionlogs_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_crmtaskactionlogs_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_crmtaskactionlogs_crmtasks_crmtaskid`: (crmtaskid) -> `dbo.crmtasks` (id)

### `dbo.crmtaskapplicationuserrels`

- Row count: **0**
- Primary key: `crmtaskid, applicationuserid`
- Columns (2): crmtaskid (uuid NOT NULL), applicationuserid (text NOT NULL)
- Key foreign keys:
  - `fk_crmtaskapplicationuserrels_aspnetusers_applicationuserid`: (applicationuserid) -> `dbo.aspnetusers` (id)
  - `fk_crmtaskapplicationuserrels_crmtasks_crmtaskid`: (crmtaskid) -> `dbo.crmtasks` (id)

### `dbo.crmtaskcategories`

- Row count: **0**
- Primary key: `id`
- Columns (10): id (uuid NOT NULL), name (text NOT NULL), description (text), active (boolean NOT NULL), datecreated (timestamp without time zone), createdbyid (text), lastupdated (timestamp without time zone), writebyid (text), isdeleted (boolean NOT NULL), istemplate (boolean)
- Key foreign keys:
  - `fk_crmtaskcategories_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_crmtaskcategories_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)

### `dbo.crmtaskcategorydataincludeirmodelfieldrels`

- Row count: **0**
- Primary key: `crmtaskcategorydataincludeid, irmodelfieldid`
- Columns (2): crmtaskcategorydataincludeid (uuid NOT NULL), irmodelfieldid (uuid NOT NULL)
- Key foreign keys:
  - `fk_crmtaskcategorydataincludeirmodelfieldrels_crmtaskcategoryda`: (crmtaskcategorydataincludeid) -> `dbo.crmtaskcategorydataincludes` (id)
  - `fk_crmtaskcategorydataincludeirmodelfieldrels_irmodelfields_irm`: (irmodelfieldid) -> `dbo.irmodelfields` (id)

### `dbo.crmtaskcategorydataincludes`

- Row count: **0**
- Primary key: `id`
- Columns (8): id (uuid NOT NULL), crmtaskcategoryid (uuid), irmodelid (uuid NOT NULL), datecreated (timestamp without time zone), createdbyid (text), lastupdated (timestamp without time zone), writebyid (text), sequence (integer NOT NULL)
- Key foreign keys:
  - `fk_crmtaskcategorydataincludes_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_crmtaskcategorydataincludes_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_crmtaskcategorydataincludes_crmtaskcategories_crmtaskcategor`: (crmtaskcategoryid) -> `dbo.crmtaskcategories` (id)
  - `fk_crmtaskcategorydataincludes_irmodels_irmodelid`: (irmodelid) -> `dbo.irmodels` (id)

### `dbo.crmtaskcategorydataresults`

- Row count: **0**
- Primary key: `id`
- Columns (9): id (uuid NOT NULL), isrequired (boolean NOT NULL), crmtaskcategoryid (uuid), irmodelfieldid (uuid), datecreated (timestamp without time zone), createdbyid (text), lastupdated (timestamp without time zone), writebyid (text), sequence (integer NOT NULL)
- Key foreign keys:
  - `fk_crmtaskcategorydataresults_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_crmtaskcategorydataresults_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_crmtaskcategorydataresults_crmtaskcategories_crmtaskcategory`: (crmtaskcategoryid) -> `dbo.crmtaskcategories` (id)
  - `fk_crmtaskcategorydataresults_irmodelfields_irmodelfieldid`: (irmodelfieldid) -> `dbo.irmodelfields` (id)

### `dbo.crmtaskdataincludeirmodelfieldrels`

- Row count: **0**
- Primary key: `crmtaskdataincludeid, irmodelfieldid`
- Columns (2): crmtaskdataincludeid (uuid NOT NULL), irmodelfieldid (uuid NOT NULL)
- Key foreign keys:
  - `fk_crmtaskdataincludeirmodelfieldrels_crmtaskdataincludes_crmta`: (crmtaskdataincludeid) -> `dbo.crmtaskdataincludes` (id)
  - `fk_crmtaskdataincludeirmodelfieldrels_irmodelfields_irmodelfiel`: (irmodelfieldid) -> `dbo.irmodelfields` (id)

### `dbo.crmtaskdataincludes`

- Row count: **0**
- Primary key: `id`
- Columns (8): id (uuid NOT NULL), sequence (integer NOT NULL), crmtaskid (uuid NOT NULL), irmodelid (uuid), datecreated (timestamp without time zone), createdbyid (text), lastupdated (timestamp without time zone), writebyid (text)
- Key foreign keys:
  - `fk_crmtaskdataincludes_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_crmtaskdataincludes_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_crmtaskdataincludes_crmtasks_crmtaskid`: (crmtaskid) -> `dbo.crmtasks` (id)
  - `fk_crmtaskdataincludes_irmodels_irmodelid`: (irmodelid) -> `dbo.irmodels` (id)

### `dbo.crmtaskdataresults`

- Row count: **0**
- Primary key: `id`
- Columns (9): id (uuid NOT NULL), isrequired (boolean NOT NULL), sequence (integer NOT NULL), crmtaskid (uuid), irmodelfieldid (uuid), datecreated (timestamp without time zone), createdbyid (text), lastupdated (timestamp without time zone), writebyid (text)
- Key foreign keys:
  - `fk_crmtaskdataresults_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_crmtaskdataresults_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_crmtaskdataresults_crmtasks_crmtaskid`: (crmtaskid) -> `dbo.crmtasks` (id)
  - `fk_crmtaskdataresults_irmodelfields_irmodelfieldid`: (irmodelfieldid) -> `dbo.irmodelfields` (id)

### `dbo.crmtaskrelations`

- Row count: **0**
- Primary key: `id`
- Columns (15): id (uuid NOT NULL), resid (uuid NOT NULL), resmodel (text), crmtaskid (uuid NOT NULL), datecreated (timestamp without time zone), createdbyid (text), lastupdated (timestamp without time zone), writebyid (text), type (text), appointmentid (uuid), crmtaskrelid (uuid), dotkhamid (uuid), laboorderid (uuid), quotationid (uuid), saleorderid (uuid)
- Key foreign keys:
  - `fk_crmtaskrelations_appointments_appointmentid`: (appointmentid) -> `dbo.appointments` (id)
  - `fk_crmtaskrelations_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_crmtaskrelations_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_crmtaskrelations_crmtasks_crmtaskid`: (crmtaskid) -> `dbo.crmtasks` (id)
  - `fk_crmtaskrelations_crmtasks_crmtaskrelid`: (crmtaskrelid) -> `dbo.crmtasks` (id)
  - `fk_crmtaskrelations_dotkhams_dotkhamid`: (dotkhamid) -> `dbo.dotkhams` (id)
  - `fk_crmtaskrelations_laboorders_laboorderid`: (laboorderid) -> `dbo.laboorders` (id)
  - `fk_crmtaskrelations_quotations_quotationid`: (quotationid) -> `dbo.quotations` (id)
  - ... and 1 more

### `dbo.crmtasks`

- Row count: **0**
- Primary key: `id`
- Columns (40): id (uuid NOT NULL), title (text), description (text), stage (integer NOT NULL), dateassign (timestamp without time zone), datestart (timestamp without time zone), datedone (timestamp without time zone), dateexpire (timestamp without time zone), priority (boolean NOT NULL), assigneduserid (text), partnerid (uuid), resid (uuid), resmodel (text), datecreated (timestamp without time zone), createdbyid (text), lastupdated (timestamp without time zone), writebyid (text), leadid (uuid), crmtasktypeid (uuid), active (boolean NOT NULL), cancelreason (text), result (text), refcode (bigint NOT NULL), teamid (uuid), laststatuschange (timestamp without time zone), notifycount (integer NOT NULL), warningtime (timestamp without time zone), resname (text), dotkhamid (uuid), iractionserverid (uuid), baseautomationv2id (uuid), iractionserverv2id (uuid), crmtaskcategoryid (uuid), notifyconfigid (uuid), datenotify (timestamp without time zone), crmtaskparentid (uuid), datecancel (timestamp without time zone), reminderjobid (text), expiredreminderjobid (text), note (text)
- Key foreign keys:
  - `fk_crmtasks_aspnetusers_assigneduserid`: (assigneduserid) -> `dbo.aspnetusers` (id)
  - `fk_crmtasks_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_crmtasks_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_crmtasks_baseautomationv2s_baseautomationv2id`: (baseautomationv2id) -> `dbo.baseautomationv2s` (id)
  - `fk_crmtasks_crmleads_leadid`: (leadid) -> `dbo.crmleads` (id)
  - `fk_crmtasks_crmtaskcategories_crmtaskcategoryid`: (crmtaskcategoryid) -> `dbo.crmtaskcategories` (id)
  - `fk_crmtasks_crmtasks_crmtaskparentid`: (crmtaskparentid) -> `dbo.crmtasks` (id)
  - `fk_crmtasks_crmtasktypes_crmtasktypeid`: (crmtasktypeid) -> `dbo.crmtasktypes` (id)
  - ... and 6 more

### `dbo.crmtasktypes`

- Row count: **4**
- Primary key: `id`
- Columns (14): id (uuid NOT NULL), name (text), description (text), priority (integer NOT NULL), limittime (integer), datecreated (timestamp without time zone), createdbyid (text), lastupdated (timestamp without time zone), writebyid (text), code (text), recallinterval (text), recallnumber (integer NOT NULL), warningminutes (integer NOT NULL), isdeleted (boolean NOT NULL)
- Key foreign keys:
  - `fk_crmtasktypes_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_crmtasktypes_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)

### `dbo.crmteammembers`

- Row count: **0**
- Primary key: `id`
- Columns (8): id (uuid NOT NULL), crmteamid (uuid NOT NULL), userid (text NOT NULL), active (boolean NOT NULL), datecreated (timestamp without time zone), createdbyid (text), lastupdated (timestamp without time zone), writebyid (text)
- Key foreign keys:
  - `fk_crmteammembers_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_crmteammembers_aspnetusers_userid`: (userid) -> `dbo.aspnetusers` (id)
  - `fk_crmteammembers_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_crmteammembers_crmteams_crmteamid`: (crmteamid) -> `dbo.crmteams` (id)

### `dbo.crmteams`

- Row count: **7**
- Primary key: `id`
- Columns (15): id (uuid NOT NULL), name (text NOT NULL), sequence (integer), active (boolean NOT NULL), companyid (uuid), userid (text), color (integer), datecreated (timestamp without time zone), createdbyid (text), lastupdated (timestamp without time zone), writebyid (text), isho (boolean NOT NULL), useleads (boolean), useopportunities (boolean), leadpropertiesdefinition (text)
- Key foreign keys:
  - `fk_crmteams_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_crmteams_aspnetusers_userid`: (userid) -> `dbo.aspnetusers` (id)
  - `fk_crmteams_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_crmteams_companies_companyid`: (companyid) -> `dbo.companies` (id)

### `dbo.currencies`

- Row count: **1**
- Primary key: `id`
- Columns (11): id (uuid NOT NULL), name (text NOT NULL), fullname (text), rounding (double precision NOT NULL), active (boolean NOT NULL), datecreated (timestamp without time zone), createdbyid (text), lastupdated (timestamp without time zone), writebyid (text), exchangerate (double precision NOT NULL), decimalplaces (integer NOT NULL)
- Key foreign keys:
  - `fk_currencies_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_currencies_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)

### `dbo.currencyrates`

- Row count: **0**
- Primary key: `id`
- Columns (8): id (uuid NOT NULL), currencyid (uuid NOT NULL), exchangerate (double precision NOT NULL), date (timestamp without time zone NOT NULL), datecreated (timestamp without time zone), createdbyid (text), lastupdated (timestamp without time zone), writebyid (text)
- Key foreign keys:
  - `fk_currencyrates_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_currencyrates_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_currencyrates_currencies_currencyid`: (currencyid) -> `dbo.currencies` (id)

### `dbo.customerreceiptproductrels`

- Row count: **9823**
- Primary key: `customerreceiptid, productid`
- Columns (2): customerreceiptid (uuid NOT NULL), productid (uuid NOT NULL)
- Key foreign keys:
  - `fk_customerreceiptproductrels_customerreceipts_customerreceipti`: (customerreceiptid) -> `dbo.customerreceipts` (id)
  - `fk_customerreceiptproductrels_products_productid`: (productid) -> `dbo.products` (id)

### `dbo.customerreceipts`

- Row count: **164469**
- Primary key: `id`
- Columns (18): id (uuid NOT NULL), datewaiting (timestamp without time zone), dateexamination (timestamp without time zone), datedone (timestamp without time zone), timeexpected (integer NOT NULL), note (text), userid (text), partnerid (uuid NOT NULL), companyid (uuid NOT NULL), doctorid (uuid), state (text), reason (text), isrepeatcustomer (boolean NOT NULL), isnotreatment (boolean NOT NULL), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_customerreceipts_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_customerreceipts_aspnetusers_userid`: (userid) -> `dbo.aspnetusers` (id)
  - `fk_customerreceipts_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_customerreceipts_companies_companyid`: (companyid) -> `dbo.companies` (id)
  - `fk_customerreceipts_employees_doctorid`: (doctorid) -> `dbo.employees` (id)
  - `fk_customerreceipts_partners_partnerid`: (partnerid) -> `dbo.partners` (id)

### `dbo.devicelogs`

- Row count: **145138**
- Primary key: `id`
- Columns (18): id (uuid NOT NULL), sessionidentifier (text NOT NULL), platform (text), browser (text), ipaddress (text), country (text), city (text), devicetype (text), userid (text), firstactivity (timestamp without time zone), lastactivity (timestamp without time zone), revoked (boolean), datecreated (timestamp without time zone), createdbyid (text), lastupdated (timestamp without time zone), writebyid (text), id2 (integer NOT NULL), deviceid (text)
- Key foreign keys:
  - `fk_devicelogs_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_devicelogs_aspnetusers_userid`: (userid) -> `dbo.aspnetusers` (id)
  - `fk_devicelogs_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)

### `dbo.discusscontacthistories`

- Row count: **0**
- Primary key: `id`
- Columns (15): id (uuid NOT NULL), type (text), messageid (uuid), callid (uuid), callcenterid (uuid), partnerid (uuid), datecreated (timestamp without time zone), createdbyid (text), lastupdated (timestamp without time zone), writebyid (text), channel (text), content (text), tposchannelid (text), tposchanneltype (integer), tposuserid (text)
- Key foreign keys:
  - `fk_discusscontacthistories_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_discusscontacthistories_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_discusscontacthistories_callcalls_callid`: (callid) -> `dbo.callcalls` (id)
  - `fk_discusscontacthistories_crmcallcenters_callcenterid`: (callcenterid) -> `dbo.crmcallcenters` (id)
  - `fk_discusscontacthistories_mailmessages_messageid`: (messageid) -> `dbo.mailmessages` (id)
  - `fk_discusscontacthistories_partners_partnerid`: (partnerid) -> `dbo.partners` (id)

### `dbo.dotkhamcompanyrels`

- Row count: **0**
- Primary key: `dotkhamid, companyid`
- Columns (2): dotkhamid (uuid NOT NULL), companyid (uuid NOT NULL)
- Key foreign keys:
  - `fk_dotkhamcompanyrels_companies_companyid`: (companyid) -> `dbo.companies` (id)
  - `fk_dotkhamcompanyrels_dotkhams_dotkhamid`: (dotkhamid) -> `dbo.dotkhams` (id)

### `dbo.dotkhamlineoperations`

- Row count: **0**
- Primary key: `id`
- Columns (11): id (uuid NOT NULL), lineid (uuid), productid (uuid), sequence (integer), state (text), datestart (timestamp without time zone), datefinished (timestamp without time zone), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_dotkhamlineoperations_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_dotkhamlineoperations_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_dotkhamlineoperations_dotkhamlines_lineid`: (lineid) -> `dbo.dotkhamlines` (id)
  - `fk_dotkhamlineoperations_products_productid`: (productid) -> `dbo.products` (id)

### `dbo.dotkhamlines`

- Row count: **4**
- Primary key: `id`
- Columns (24): id (uuid NOT NULL), dotkhamid (uuid NOT NULL), sequence (integer), namestep (text), productid (uuid), saleorderlineid (uuid), note (text), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone), dotkhamstepid (uuid), numberoftimes (integer NOT NULL), isdone (boolean NOT NULL), toothrange (text), toothtypefilter (integer NOT NULL), productlineid (uuid), toothtype (text), percentage (numeric(18,2)), quantity (numeric(18,2)), dotkhamstepv2id (uuid), recognizedrevenuepercentperexecution (double precision NOT NULL), solinepricetotal (numeric(18,6) NOT NULL), pricetotal (numeric(18,2) NOT NULL)
- Key foreign keys:
  - `fk_dotkhamlines_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_dotkhamlines_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_dotkhamlines_dotkhamproductlines_productlineid`: (productlineid) -> `dbo.dotkhamproductlines` (id)
  - `fk_dotkhamlines_dotkhams_dotkhamid`: (dotkhamid) -> `dbo.dotkhams` (id)
  - `fk_dotkhamlines_dotkhamsteps_dotkhamstepid`: (dotkhamstepid) -> `dbo.dotkhamsteps` (id)
  - `fk_dotkhamlines_dotkhamstepv2s_dotkhamstepv2id`: (dotkhamstepv2id) -> `dbo.dotkhamstepv2s` (id)
  - `fk_dotkhamlines_products_productid`: (productid) -> `dbo.products` (id)
  - `fk_dotkhamlines_saleorderlines_saleorderlineid`: (saleorderlineid) -> `dbo.saleorderlines` (id)

### `dbo.dotkhamlinetoothrels`

- Row count: **0**
- Primary key: `lineid, toothid`
- Columns (2): lineid (uuid NOT NULL), toothid (uuid NOT NULL)
- Key foreign keys:
  - `fk_dotkhamlinetoothrels_dotkhamlines_lineid`: (lineid) -> `dbo.dotkhamlines` (id)
  - `fk_dotkhamlinetoothrels_teeth_toothid`: (toothid) -> `dbo.teeth` (id)

### `dbo.dotkhamproductlineaccountmovelinerels`

- Row count: **0**
- Primary key: `dotkhamproductlineid, accountmovelineid`
- Columns (2): dotkhamproductlineid (uuid NOT NULL), accountmovelineid (uuid NOT NULL)
- Key foreign keys:
  - `fk_dotkhamproductlineaccountmovelinerels_accountmovelines_accou`: (accountmovelineid) -> `dbo.accountmovelines` (id)
  - `fk_dotkhamproductlineaccountmovelinerels_dotkhamproductlines_do`: (dotkhamproductlineid) -> `dbo.dotkhamproductlines` (id)

### `dbo.dotkhamproductlines`

- Row count: **39465**
- Primary key: `id`
- Columns (11): id (uuid NOT NULL), dotkhamid (uuid NOT NULL), productid (uuid NOT NULL), saleorderlineid (uuid), name (text), date (timestamp without time zone NOT NULL), datecreated (timestamp without time zone), createdbyid (text), lastupdated (timestamp without time zone), writebyid (text), isglobaldiscount (boolean NOT NULL)
- Key foreign keys:
  - `fk_dotkhamproductlines_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_dotkhamproductlines_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_dotkhamproductlines_dotkhams_dotkhamid`: (dotkhamid) -> `dbo.dotkhams` (id)
  - `fk_dotkhamproductlines_products_productid`: (productid) -> `dbo.products` (id)
  - `fk_dotkhamproductlines_saleorderlines_saleorderlineid`: (saleorderlineid) -> `dbo.saleorderlines` (id)

### `dbo.dotkhams`

- Row count: **84309**
- Primary key: `id`
- Columns (26): id (uuid NOT NULL), sequence (integer), name (text), saleorderid (uuid), partnerid (uuid), date (timestamp without time zone NOT NULL), reason (text), state (text), companyid (uuid NOT NULL), doctorid (uuid), appointmentid (uuid), assistantid (uuid), accountinvoiceid (uuid), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone), note (text), userid (text), activitystatus (text), assistantsecondaryid (uuid), invoicestate (text), paymentstate (text), totalamount (numeric(18,2)), amountresidual (numeric(18,2)), isdeleted (boolean NOT NULL)
- Key foreign keys:
  - `fk_dotkhams_accountinvoices_accountinvoiceid`: (accountinvoiceid) -> `dbo.accountinvoices` (id)
  - `fk_dotkhams_appointments_appointmentid`: (appointmentid) -> `dbo.appointments` (id)
  - `fk_dotkhams_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_dotkhams_aspnetusers_userid`: (userid) -> `dbo.aspnetusers` (id)
  - `fk_dotkhams_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_dotkhams_companies_companyid`: (companyid) -> `dbo.companies` (id)
  - `fk_dotkhams_employees_assistantid`: (assistantid) -> `dbo.employees` (id)
  - `fk_dotkhams_employees_assistantsecondaryid`: (assistantsecondaryid) -> `dbo.employees` (id)
  - ... and 3 more

### `dbo.dotkhamsteps`

- Row count: **63896**
- Primary key: `id`
- Columns (12): id (uuid NOT NULL), name (text NOT NULL), productid (uuid), salelineid (uuid), saleorderid (uuid), isdone (boolean NOT NULL), order (integer), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone), numberoftimes (integer NOT NULL)
- Key foreign keys:
  - `fk_dotkhamsteps_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_dotkhamsteps_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_dotkhamsteps_products_productid`: (productid) -> `dbo.products` (id)
  - `fk_dotkhamsteps_saleorderlines_salelineid`: (salelineid) -> `dbo.saleorderlines` (id)
  - `fk_dotkhamsteps_saleorders_saleorderid`: (saleorderid) -> `dbo.saleorders` (id)

### `dbo.dotkhamstepv2s`

- Row count: **0**
- Primary key: `id`
- Columns (19): id (uuid NOT NULL), name (text NOT NULL), productid (uuid), salelineid (uuid), saleorderid (uuid), isdone (boolean NOT NULL), numberoftimes (integer NOT NULL), order (integer), defaultrevenuepercentconfig (double precision), requiredexecutioncount (integer NOT NULL), isnewgenerate (boolean), datecreated (timestamp without time zone), createdbyid (text), lastupdated (timestamp without time zone), writebyid (text), defaultrequiredexecutioncount (integer NOT NULL), remainingrevenuepercent (double precision), recognizedrevenuepercent (double precision), totalstepexecutedcount (integer NOT NULL)
- Key foreign keys:
  - `fk_dotkhamstepv2s_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_dotkhamstepv2s_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_dotkhamstepv2s_products_productid`: (productid) -> `dbo.products` (id)
  - `fk_dotkhamstepv2s_saleorderlines_salelineid`: (salelineid) -> `dbo.saleorderlines` (id)
  - `fk_dotkhamstepv2s_saleorders_saleorderid`: (saleorderid) -> `dbo.saleorders` (id)

### `dbo.einvoiceaccountcompanyrels`

- Row count: **0**
- Primary key: `einvoiceaccountid, companyid`
- Columns (2): einvoiceaccountid (uuid NOT NULL), companyid (uuid NOT NULL)
- Key foreign keys:
  - `fk_einvoiceaccountcompanyrels_companies_companyid`: (companyid) -> `dbo.companies` (id)
  - `fk_einvoiceaccountcompanyrels_einvoiceaccounts_einvoiceaccounti`: (einvoiceaccountid) -> `dbo.einvoiceaccounts` (id)

### `dbo.einvoiceaccounts`

- Row count: **0**
- Primary key: `id`
- Columns (13): id (uuid NOT NULL), name (text NOT NULL), code (text NOT NULL), taxcode (text), username (text), password (text), datecreated (timestamp without time zone), createdbyid (text), lastupdated (timestamp without time zone), writebyid (text), active (boolean NOT NULL), defaulteinvoicetemplateid (uuid), codedvcs (text)
- Key foreign keys:
  - `fk_einvoiceaccounts_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_einvoiceaccounts_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_einvoiceaccounts_einvoicetemplates_defaulteinvoicetemplateid`: (defaulteinvoicetemplateid) -> `dbo.einvoicetemplates` (id)

### `dbo.einvoicetemplates`

- Row count: **0**
- Primary key: `id`
- Columns (8): id (uuid NOT NULL), name (text NOT NULL), accountid (uuid), invoiceseries (text), datecreated (timestamp without time zone), createdbyid (text), lastupdated (timestamp without time zone), writebyid (text)
- Key foreign keys:
  - `fk_einvoicetemplates_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_einvoicetemplates_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_einvoicetemplates_einvoiceaccounts_accountid`: (accountid) -> `dbo.einvoiceaccounts` (id)

### `dbo.employeecategories`

- Row count: **0**
- Primary key: `id`
- Columns (7): id (uuid NOT NULL), name (text NOT NULL), type (text), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_employeecategories_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_employeecategories_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)

### `dbo.employees`

- Row count: **373**
- Primary key: `id`
- Columns (39): id (uuid NOT NULL), name (text NOT NULL), active (boolean NOT NULL), ref (text), address (text), phone (text), identitycard (text), email (text), birthday (timestamp without time zone), categoryid (uuid), companyid (uuid), partnerid (uuid), isdoctor (boolean NOT NULL), isassistant (boolean NOT NULL), commissionid (uuid), assistantcommissionid (uuid), counselorcommissionid (uuid), userid (text), structuretypeid (uuid), wage (numeric(18,2)), hourlywage (numeric(18,2)), startworkdate (timestamp without time zone), enrollnumber (text), leavepermonth (numeric(18,2)), regularhour (numeric(18,2)), overtimerate (numeric(18,2)), restdayrate (numeric(18,2)), allowance (numeric(18,2)), avatar (text), isallowsurvey (boolean NOT NULL), groupid (uuid), hrjobid (uuid), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone), medicalprescriptioncode (text), tokenmedicalprescription (text), isreceptionist (boolean NOT NULL)
- Key foreign keys:
  - `fk_employees_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_employees_aspnetusers_userid`: (userid) -> `dbo.aspnetusers` (id)
  - `fk_employees_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_employees_commissions_assistantcommissionid`: (assistantcommissionid) -> `dbo.commissions` (id)
  - `fk_employees_commissions_commissionid`: (commissionid) -> `dbo.commissions` (id)
  - `fk_employees_commissions_counselorcommissionid`: (counselorcommissionid) -> `dbo.commissions` (id)
  - `fk_employees_companies_companyid`: (companyid) -> `dbo.companies` (id)
  - `fk_employees_employeecategories_categoryid`: (categoryid) -> `dbo.employeecategories` (id)
  - ... and 4 more

### `dbo.eventoutbox`

- Row count: **0**
- Primary key: `id`
- Columns (6): id (uuid NOT NULL), eventname (text NOT NULL), eventdata (bytea NOT NULL), creationtime (timestamp without time zone NOT NULL), tenant (text), outboxid (uuid)
- Key foreign keys:
  - `fk_eventoutbox_outboxstates_outboxid`: (outboxid) -> `dbo.outboxstates` (id)

### `dbo.facebookconnectpages`

- Row count: **0**
- Primary key: `id`
- Columns (10): id (uuid NOT NULL), pageid (text), pagename (text), pageaccesstoken (text), picture (text), connectid (uuid NOT NULL), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_facebookconnectpages_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_facebookconnectpages_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_facebookconnectpages_facebookconnects_connectid`: (connectid) -> `dbo.facebookconnects` (id)

### `dbo.facebookconnects`

- Row count: **0**
- Primary key: `id`
- Columns (8): id (uuid NOT NULL), fbuserid (text), fbusername (text), fbuseraccesstoken (text), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_facebookconnects_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_facebookconnects_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)

### `dbo.facebookmassmessagings`

- Row count: **0**
- Primary key: `id`
- Columns (13): id (uuid NOT NULL), name (text NOT NULL), content (text), sentdate (timestamp without time zone), scheduledate (timestamp without time zone), state (text), facebookpageid (uuid), jobid (text), audiencefilter (text), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_facebookmassmessagings_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_facebookmassmessagings_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_facebookmassmessagings_facebookpages_facebookpageid`: (facebookpageid) -> `dbo.facebookpages` (id)

### `dbo.facebookmessagingtraces`

- Row count: **0**
- Primary key: `id`
- Columns (13): id (uuid NOT NULL), massmessagingid (uuid), sent (timestamp without time zone), exception (timestamp without time zone), delivered (timestamp without time zone), opened (timestamp without time zone), messageid (text), state (text), userprofileid (uuid), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_facebookmessagingtraces_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_facebookmessagingtraces_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_facebookmessagingtraces_facebookmassmessagings_massmessaging`: (massmessagingid) -> `dbo.facebookmassmessagings` (id)
  - `fk_facebookmessagingtraces_facebookuserprofiles_userprofileid`: (userprofileid) -> `dbo.facebookuserprofiles` (id)

### `dbo.facebookpages`

- Row count: **0**
- Primary key: `id`
- Columns (14): id (uuid NOT NULL), type (text), userid (text), username (text), useraccesstoken (text), pageid (text), pagename (text), pageaccesstoken (text), avatar (text), autoconfigid (uuid), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_facebookpages_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_facebookpages_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_facebookpages_facebookscheduleappointmentconfigs_autoconfigi`: (autoconfigid) -> `dbo.facebookscheduleappointmentconfigs` (id)

### `dbo.facebookscheduleappointmentconfigs`

- Row count: **0**
- Primary key: `id`
- Columns (10): id (uuid NOT NULL), scheduletype (text), schedulenumber (integer), autoscheduleappoint (boolean NOT NULL), contentmessage (text), recurringjobid (text), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_facebookscheduleappointmentconfigs_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_facebookscheduleappointmentconfigs_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)

### `dbo.facebooktags`

- Row count: **0**
- Primary key: `id`
- Columns (6): id (uuid NOT NULL), name (text NOT NULL), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_facebooktags_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_facebooktags_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)

### `dbo.facebookuserprofiles`

- Row count: **0**
- Primary key: `id`
- Columns (14): id (uuid NOT NULL), name (text), firstname (text), lastname (text), gender (text), avatar (text), phone (text), psid (text), fbpageid (uuid NOT NULL), partnerid (uuid), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_facebookuserprofiles_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_facebookuserprofiles_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_facebookuserprofiles_facebookpages_fbpageid`: (fbpageid) -> `dbo.facebookpages` (id)
  - `fk_facebookuserprofiles_partners_partnerid`: (partnerid) -> `dbo.partners` (id)

### `dbo.facebookuserprofiletagrels`

- Row count: **0**
- Primary key: `userprofileid, tagid`
- Columns (2): userprofileid (uuid NOT NULL), tagid (uuid NOT NULL)
- Key foreign keys:
  - `fk_facebookuserprofiletagrels_facebooktags_tagid`: (tagid) -> `dbo.facebooktags` (id)
  - `fk_facebookuserprofiletagrels_facebookuserprofiles_userprofilei`: (userprofileid) -> `dbo.facebookuserprofiles` (id)

### `dbo.giftcardcompanyrels`

- Row count: **0**
- Primary key: `giftcardid, companyid`
- Columns (2): giftcardid (uuid NOT NULL), companyid (uuid NOT NULL)
- Key foreign keys:
  - `fk_giftcardcompanyrels_companies_companyid`: (companyid) -> `dbo.companies` (id)
  - `fk_giftcardcompanyrels_giftcards_giftcardid`: (giftcardid) -> `dbo.giftcards` (id)

### `dbo.giftcardpartnerrels`

- Row count: **0**
- Primary key: `giftcardid, partnerid`
- Columns (2): giftcardid (uuid NOT NULL), partnerid (uuid NOT NULL)
- Key foreign keys:
  - `fk_giftcardpartnerrels_giftcards_giftcardid`: (giftcardid) -> `dbo.giftcards` (id)
  - `fk_giftcardpartnerrels_partners_partnerid`: (partnerid) -> `dbo.partners` (id)

### `dbo.giftcards`

- Row count: **0**
- Primary key: `id`
- Columns (14): id (uuid NOT NULL), name (text NOT NULL), date (timestamp without time zone NOT NULL), code (text), desription (text), initialamount (numeric(18,2)), balance (numeric(18,2)), expireddate (timestamp without time zone), companyid (uuid), state (text), datecreated (timestamp without time zone), createdbyid (text), lastupdated (timestamp without time zone), writebyid (text)
- Key foreign keys:
  - `fk_giftcards_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_giftcards_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_giftcards_companies_companyid`: (companyid) -> `dbo.companies` (id)

### `dbo.histories`

- Row count: **0**
- Primary key: `id`
- Columns (8): id (uuid NOT NULL), name (text NOT NULL), active (boolean NOT NULL), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone), categoryid (uuid)
- Key foreign keys:
  - `fk_histories_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_histories_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_histories_historycategories_categoryid`: (categoryid) -> `dbo.historycategories` (id)

### `dbo.historycategories`

- Row count: **0**
- Primary key: `id`
- Columns (7): id (uuid NOT NULL), name (text), active (boolean NOT NULL), datecreated (timestamp without time zone), createdbyid (text), lastupdated (timestamp without time zone), writebyid (text)
- Key foreign keys:
  - `fk_historycategories_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_historycategories_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)

### `dbo.householdbusinesses`

- Row count: **0**
- Primary key: `id`
- Columns (13): id (uuid NOT NULL), name (text NOT NULL), taxcode (text), address (text), active (boolean NOT NULL), einvoiceaccountid (uuid), datecreated (timestamp without time zone), createdbyid (text), lastupdated (timestamp without time zone), writebyid (text), accounttaxid (uuid), iscompany (boolean NOT NULL), taxamount (numeric(18,2))
- Key foreign keys:
  - `fk_householdbusinesses_accounttaxes_accounttaxid`: (accounttaxid) -> `dbo.accounttaxes` (id)
  - `fk_householdbusinesses_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_householdbusinesses_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_householdbusinesses_einvoiceaccounts_einvoiceaccountid`: (einvoiceaccountid) -> `dbo.einvoiceaccounts` (id)

### `dbo.householdcompanyrels`

- Row count: **0**
- Primary key: `companyid, householdbusinessid`
- Columns (2): householdbusinessid (uuid NOT NULL), companyid (uuid NOT NULL)
- Key foreign keys:
  - `fk_householdcompanyrels_companies_companyid`: (companyid) -> `dbo.companies` (id)
  - `fk_householdcompanyrels_householdbusinesses_householdbusinessid`: (householdbusinessid) -> `dbo.householdbusinesses` (id)

### `dbo.hrjobs`

- Row count: **40**
- Primary key: `id`
- Columns (7): id (uuid NOT NULL), name (text), companyid (uuid), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_hrjobs_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_hrjobs_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_hrjobs_companies_companyid`: (companyid) -> `dbo.companies` (id)

### `dbo.hrpayrollstructures`

- Row count: **0**
- Primary key: `id`
- Columns (13): id (uuid NOT NULL), name (text NOT NULL), active (boolean NOT NULL), note (text), regularpay (boolean NOT NULL), typeid (uuid NOT NULL), useworkeddaylines (boolean NOT NULL), schedulepay (text), companyid (uuid), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_hrpayrollstructures_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_hrpayrollstructures_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_hrpayrollstructures_companies_companyid`: (companyid) -> `dbo.companies` (id)
  - `fk_hrpayrollstructures_hrpayrollstructuretypes_typeid`: (typeid) -> `dbo.hrpayrollstructuretypes` (id)

### `dbo.hrpayrollstructuretypes`

- Row count: **0**
- Primary key: `id`
- Columns (12): id (uuid NOT NULL), defaultresourcecalendarid (uuid), defaultschedulepay (text), defaultstructid (uuid), defaultworkentrytypeid (uuid), name (text NOT NULL), wagetype (text NOT NULL), companyid (uuid), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_hrpayrollstructuretypes_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_hrpayrollstructuretypes_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_hrpayrollstructuretypes_companies_companyid`: (companyid) -> `dbo.companies` (id)
  - `fk_hrpayrollstructuretypes_hrpayrollstructures_defaultstructid`: (defaultstructid) -> `dbo.hrpayrollstructures` (id)
  - `fk_hrpayrollstructuretypes_resourcecalendars_defaultresourcecal`: (defaultresourcecalendarid) -> `dbo.resourcecalendars` (id)
  - `fk_hrpayrollstructuretypes_workentrytypes_defaultworkentrytypei`: (defaultworkentrytypeid) -> `dbo.workentrytypes` (id)

### `dbo.hrpaysliplines`

- Row count: **0**
- Primary key: `id`
- Columns (15): id (uuid NOT NULL), name (text NOT NULL), code (text), quantity (numeric(18,2)), amount (numeric(18,2)), total (numeric(18,2)), slipid (uuid NOT NULL), salaryruleid (uuid NOT NULL), rate (numeric(18,2)), categoryid (uuid), sequence (integer), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_hrpaysliplines_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_hrpaysliplines_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_hrpaysliplines_hrpayslips_slipid`: (slipid) -> `dbo.hrpayslips` (id)
  - `fk_hrpaysliplines_hrsalaryrulecategories_categoryid`: (categoryid) -> `dbo.hrsalaryrulecategories` (id)
  - `fk_hrpaysliplines_hrsalaryrules_salaryruleid`: (salaryruleid) -> `dbo.hrsalaryrules` (id)

### `dbo.hrpaysliprun2s`

- Row count: **0**
- Primary key: `id`
- Columns (17): id (uuid NOT NULL), name (text NOT NULL), state (text), datestart (timestamp without time zone NOT NULL), dateend (timestamp without time zone NOT NULL), companyid (uuid NOT NULL), moveid (uuid), householdbusinessid (uuid), salary (numeric(18,2) NOT NULL), datecreated (timestamp without time zone), createdbyid (text), lastupdated (timestamp without time zone), writebyid (text), healthinsurance (numeric(18,2) NOT NULL), socialinsurance (numeric(18,2) NOT NULL), unemploymentinsurance (numeric(18,2) NOT NULL), accountingdate (timestamp without time zone)
- Key foreign keys:
  - `fk_hrpaysliprun2s_accountmoves_moveid`: (moveid) -> `dbo.accountmoves` (id)
  - `fk_hrpaysliprun2s_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_hrpaysliprun2s_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_hrpaysliprun2s_companies_companyid`: (companyid) -> `dbo.companies` (id)
  - `fk_hrpaysliprun2s_householdbusinesses_householdbusinessid`: (householdbusinessid) -> `dbo.householdbusinesses` (id)

### `dbo.hrpayslipruns`

- Row count: **5**
- Primary key: `id`
- Columns (12): id (uuid NOT NULL), name (text NOT NULL), state (text), datestart (timestamp without time zone NOT NULL), dateend (timestamp without time zone NOT NULL), companyid (uuid NOT NULL), date (timestamp without time zone), moveid (uuid), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_hrpayslipruns_accountmoves_moveid`: (moveid) -> `dbo.accountmoves` (id)
  - `fk_hrpayslipruns_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_hrpayslipruns_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_hrpayslipruns_companies_companyid`: (companyid) -> `dbo.companies` (id)

### `dbo.hrpayslips`

- Row count: **193**
- Primary key: `id`
- Columns (38): id (uuid NOT NULL), structid (uuid), name (text NOT NULL), number (text), employeeid (uuid NOT NULL), datefrom (timestamp without time zone NOT NULL), dateto (timestamp without time zone NOT NULL), state (text), companyid (uuid NOT NULL), accountmoveid (uuid), paysliprunid (uuid), totalamount (numeric(18,2)), structuretypeid (uuid), daysalary (numeric(18,2)), workedday (numeric(18,2)), totalbasicsalary (numeric(18,2)), overtimehour (numeric(18,2)), overtimehoursalary (numeric(18,2)), overtimeday (numeric(18,2)), overtimedaysalary (numeric(18,2)), allowance (numeric(18,2)), otherallowance (numeric(18,2)), rewardsalary (numeric(18,2)), holidayallowance (numeric(18,2)), totalsalary (numeric(18,2)), commissionsalary (numeric(18,2)), tax (numeric(18,2)), socialinsurance (numeric(18,2)), advancepayment (numeric(18,2)), amercementmoney (numeric(18,2)), netsalary (numeric(18,2)), actualleavepermonth (numeric(18,2)), leavepermonthunpaid (numeric(18,2)), salarypaymentid (uuid), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_hrpayslips_accountmoves_accountmoveid`: (accountmoveid) -> `dbo.accountmoves` (id)
  - `fk_hrpayslips_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_hrpayslips_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_hrpayslips_companies_companyid`: (companyid) -> `dbo.companies` (id)
  - `fk_hrpayslips_employees_employeeid`: (employeeid) -> `dbo.employees` (id)
  - `fk_hrpayslips_hrpayrollstructures_structid`: (structid) -> `dbo.hrpayrollstructures` (id)
  - `fk_hrpayslips_hrpayrollstructuretypes_structuretypeid`: (structuretypeid) -> `dbo.hrpayrollstructuretypes` (id)
  - `fk_hrpayslips_hrpayslipruns_paysliprunid`: (paysliprunid) -> `dbo.hrpayslipruns` (id)
  - ... and 1 more

### `dbo.hrpayslipworkeddays`

- Row count: **0**
- Primary key: `id`
- Columns (13): id (uuid NOT NULL), name (text NOT NULL), payslipid (uuid NOT NULL), sequence (integer), code (text), numberofdays (numeric(18,2)), numberofhours (numeric(18,2)), workentrytypeid (uuid NOT NULL), amount (numeric(18,2)), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_hrpayslipworkeddays_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_hrpayslipworkeddays_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_hrpayslipworkeddays_hrpayslips_payslipid`: (payslipid) -> `dbo.hrpayslips` (id)
  - `fk_hrpayslipworkeddays_workentrytypes_workentrytypeid`: (workentrytypeid) -> `dbo.workentrytypes` (id)

### `dbo.hrsalaryconfigs`

- Row count: **0**
- Primary key: `id`
- Columns (7): id (uuid NOT NULL), companyid (uuid), defaultgloballeavetypeid (uuid NOT NULL), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_hrsalaryconfigs_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_hrsalaryconfigs_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_hrsalaryconfigs_companies_companyid`: (companyid) -> `dbo.companies` (id)
  - `fk_hrsalaryconfigs_workentrytypes_defaultgloballeavetypeid`: (defaultgloballeavetypeid) -> `dbo.workentrytypes` (id)

### `dbo.hrsalaryrulecategories`

- Row count: **0**
- Primary key: `id`
- Columns (9): id (uuid NOT NULL), name (text NOT NULL), code (text), note (text), parentid (uuid), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_hrsalaryrulecategories_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_hrsalaryrulecategories_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_hrsalaryrulecategories_hrsalaryrulecategories_parentid`: (parentid) -> `dbo.hrsalaryrulecategories` (id)

### `dbo.hrsalaryrules`

- Row count: **0**
- Primary key: `id`
- Columns (19): id (uuid NOT NULL), name (text NOT NULL), code (text), categoryid (uuid), sequence (integer), active (boolean NOT NULL), companyid (uuid), amountselect (text), amountfix (numeric(18,2)), amountpercentage (numeric(18,2)), appearsonpayslip (boolean NOT NULL), note (text), amountcodecompute (text), amountpercentagebase (text), structid (uuid NOT NULL), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_hrsalaryrules_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_hrsalaryrules_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_hrsalaryrules_companies_companyid`: (companyid) -> `dbo.companies` (id)
  - `fk_hrsalaryrules_hrpayrollstructures_structid`: (structid) -> `dbo.hrpayrollstructures` (id)
  - `fk_hrsalaryrules_hrsalaryrulecategories_categoryid`: (categoryid) -> `dbo.hrsalaryrulecategories` (id)

### `dbo.imbus`

- Row count: **0**
- Primary key: `id`
- Columns (7): id (uuid NOT NULL), channel (text), message (text), datecreated (timestamp without time zone), createdbyid (text), lastupdated (timestamp without time zone), writebyid (text)
- Key foreign keys:
  - `fk_imbus_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_imbus_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)

### `dbo.iractionservers`

- Row count: **0**
- Primary key: `id`
- Columns (23): id (uuid NOT NULL), name (text), usage (text), baseautomationid (uuid), state (text), sequence (integer NOT NULL), model (text), tasktypeid (uuid), tasksummary (text), tasknote (text), taskusertype (text), taskuserid (text), taskuserfieldname (text), datecreated (timestamp without time zone), createdbyid (text), lastupdated (timestamp without time zone), writebyid (text), smsaccountid (uuid), smstemplateid (uuid), zalotemplateid (uuid), taskduedatein (integer), taskuseridsconfig (text), teamid (uuid)
- Key foreign keys:
  - `fk_iractionservers_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_iractionservers_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_iractionservers_baseautomations_baseautomationid`: (baseautomationid) -> `dbo.baseautomations` (id)
  - `fk_iractionservers_crmtasktypes_tasktypeid`: (tasktypeid) -> `dbo.crmtasktypes` (id)
  - `fk_iractionservers_crmteams_teamid`: (teamid) -> `dbo.crmteams` (id)
  - `fk_iractionservers_smsaccounts_smsaccountid`: (smsaccountid) -> `dbo.smsaccounts` (id)
  - `fk_iractionservers_smstemplates_smstemplateid`: (smstemplateid) -> `dbo.smstemplates` (id)
  - `fk_iractionservers_zalotemplates_zalotemplateid`: (zalotemplateid) -> `dbo.zalotemplates` (id)

### `dbo.iractionserverv2s`

- Row count: **0**
- Primary key: `id`
- Columns (40): id (uuid NOT NULL), baseautomationv2id (uuid), tasktype (text), actiontype (text), name (text), taskdescription (text), taskexpiredtype (text), taskexpiredvalue (integer NOT NULL), taskexpiredunit (text), taskexpirefixeddate (timestamp without time zone), taskusertype (text), taskuserids (text), taskuserpriority (text), distributionprioritytype (text), distributionteamids (text), distributionuserids (text), taskdistributiontype (boolean NOT NULL), notifytouserasign (boolean NOT NULL), isrevokeexpiredtask (boolean NOT NULL), smstemplateid (uuid), smsaccountid (uuid), zalotemplateid (uuid), datecreated (timestamp without time zone), createdbyid (text), lastupdated (timestamp without time zone), writebyid (text), companyids (text), hrjobids (text), teamids (text), crmtasktypeid (uuid), tasktitle (text), smstemplatetitle (text), smstype (text), znstemplatetitle (text), mailmessagesubtypeid (uuid), crmtaskcategoryid (uuid), sequense (integer), enablecaretimeexceededrule (boolean), caretimeexceededthresholdindays (integer), caretimeexceededaction (text)
- Key foreign keys:
  - `fk_iractionserverv2s_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_iractionserverv2s_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_iractionserverv2s_baseautomationv2s_baseautomationv2id`: (baseautomationv2id) -> `dbo.baseautomationv2s` (id)
  - `fk_iractionserverv2s_crmtaskcategories_crmtaskcategoryid`: (crmtaskcategoryid) -> `dbo.crmtaskcategories` (id)
  - `fk_iractionserverv2s_crmtasktypes_crmtasktypeid`: (crmtasktypeid) -> `dbo.crmtasktypes` (id)
  - `fk_iractionserverv2s_mailmessagesubtypes_mailmessagesubtypeid`: (mailmessagesubtypeid) -> `dbo.mailmessagesubtypes` (id)
  - `fk_iractionserverv2s_smsaccounts_smsaccountid`: (smsaccountid) -> `dbo.smsaccounts` (id)
  - `fk_iractionserverv2s_smstemplates_smstemplateid`: (smstemplateid) -> `dbo.smstemplates` (id)
  - ... and 1 more

### `dbo.irattachments`

- Row count: **7984**
- Primary key: `id`
- Columns (20): id (uuid NOT NULL), name (text NOT NULL), datasfname (text), description (text), resname (text), resfield (text), resmodel (text), resid (uuid), companyid (uuid), type (text NOT NULL), url (text), dbdatas (bytea), minetype (text), active (boolean NOT NULL), filesize (integer), uploadid (text), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_irattachments_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_irattachments_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_irattachments_companies_companyid`: (companyid) -> `dbo.companies` (id)

### `dbo.irconfigparameters`

- Row count: **7**
- Primary key: `id`
- Columns (7): id (uuid NOT NULL), key (text NOT NULL), value (text NOT NULL), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_irconfigparameters_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_irconfigparameters_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)

### `dbo.irmodelaccesses`

- Row count: **0**
- Primary key: `id`
- Columns (13): id (uuid NOT NULL), name (text NOT NULL), active (boolean NOT NULL), permread (boolean NOT NULL), permwrite (boolean NOT NULL), permcreate (boolean NOT NULL), permunlink (boolean NOT NULL), modelid (uuid NOT NULL), groupid (uuid), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_irmodelaccesses_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_irmodelaccesses_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_irmodelaccesses_irmodels_modelid`: (modelid) -> `dbo.irmodels` (id)
  - `fk_irmodelaccesses_resgroups_groupid`: (groupid) -> `dbo.resgroups` (id)

### `dbo.irmodeldatas`

- Row count: **481**
- Primary key: `id`
- Columns (9): id (uuid NOT NULL), name (text NOT NULL), resid (text), model (text NOT NULL), module (text), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_irmodeldatas_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_irmodeldatas_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)

### `dbo.irmodelfields`

- Row count: **49**
- Primary key: `id`
- Columns (20): id (uuid NOT NULL), model (text NOT NULL), irmodelid (uuid), name (text NOT NULL), ttype (text NOT NULL), relation (text), fielddesc (text), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone), manual (boolean NOT NULL), readonly (boolean NOT NULL), store (boolean NOT NULL), string (text), type (text), isdeleted (boolean NOT NULL), note (text), iscustomfield (boolean NOT NULL), irmodelfieldupdateid (uuid)
- Key foreign keys:
  - `fk_irmodelfields_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_irmodelfields_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_irmodelfields_irmodelfields_irmodelfieldupdateid`: (irmodelfieldupdateid) -> `dbo.irmodelfields` (id)
  - `fk_irmodelfields_irmodels_irmodelid`: (irmodelid) -> `dbo.irmodels` (id)

### `dbo.irmodelfieldselections`

- Row count: **22**
- Primary key: `id`
- Columns (9): id (uuid NOT NULL), fieldid (uuid NOT NULL), value (text), name (text NOT NULL), sequence (integer), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_irmodelfieldselections_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_irmodelfieldselections_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_irmodelfieldselections_irmodelfields_fieldid`: (fieldid) -> `dbo.irmodelfields` (id)

### `dbo.irmodelfieldvalues`

- Row count: **0**
- Primary key: `id`
- Columns (16): id (uuid NOT NULL), resid (uuid NOT NULL), resmodel (text NOT NULL), irmodelfieldid (uuid), stringvalue (text), guidvalue (uuid), datetimevalue (timestamp without time zone), intvalue (integer), datecreated (timestamp without time zone), createdbyid (text), lastupdated (timestamp without time zone), writebyid (text), parentresid (uuid), parentresmodel (text), guidnote (text), boolvalue (boolean)
- Key foreign keys:
  - `fk_irmodelfieldvalues_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_irmodelfieldvalues_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_irmodelfieldvalues_irmodelfields_irmodelfieldid`: (irmodelfieldid) -> `dbo.irmodelfields` (id)

### `dbo.irmodels`

- Row count: **100**
- Primary key: `id`
- Columns (8): id (uuid NOT NULL), name (text NOT NULL), model (text NOT NULL), transient (boolean NOT NULL), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_irmodels_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_irmodels_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)

### `dbo.irmodulecategories`

- Row count: **5**
- Primary key: `id`
- Columns (11): id (uuid NOT NULL), name (text NOT NULL), description (text), parentid (uuid), sequence (integer), visible (boolean), exclusive (boolean), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_irmodulecategories_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_irmodulecategories_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_irmodulecategories_irmodulecategories_parentid`: (parentid) -> `dbo.irmodulecategories` (id)

### `dbo.irproperties`

- Row count: **265**
- Primary key: `id`
- Columns (17): id (uuid NOT NULL), name (text), valuefloat (double precision), valueinteger (integer), valuetext (text), valuebinary (bytea), valuereference (text), valuedatetime (timestamp without time zone), type (text NOT NULL), companyid (uuid), fieldid (uuid NOT NULL), resid (text), valuedecimal (numeric(18,2)), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_irproperties_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_irproperties_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_irproperties_companies_companyid`: (companyid) -> `dbo.companies` (id)
  - `fk_irproperties_irmodelfields_fieldid`: (fieldid) -> `dbo.irmodelfields` (id)

### `dbo.irrulecategories`

- Row count: **0**
- Primary key: `id`
- Columns (6): id (uuid NOT NULL), name (text NOT NULL), datecreated (timestamp without time zone), createdbyid (text), lastupdated (timestamp without time zone), writebyid (text)
- Key foreign keys:
  - `fk_irrulecategories_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_irrulecategories_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)

### `dbo.irrules`

- Row count: **73**
- Primary key: `id`
- Columns (17): id (uuid NOT NULL), name (text NOT NULL), global (boolean NOT NULL), active (boolean NOT NULL), permunlink (boolean NOT NULL), permwrite (boolean NOT NULL), permread (boolean NOT NULL), permcreate (boolean NOT NULL), modelid (uuid NOT NULL), code (text), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone), categid (uuid), isdisplay (boolean), domain (text)
- Key foreign keys:
  - `fk_irrules_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_irrules_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_irrules_irmodels_modelid`: (modelid) -> `dbo.irmodels` (id)
  - `fk_irrules_irrulecategories_categid`: (categid) -> `dbo.irrulecategories` (id)

### `dbo.irsequencedateranges`

- Row count: **0**
- Primary key: `id`
- Columns (9): id (uuid NOT NULL), datefrom (timestamp without time zone NOT NULL), dateto (timestamp without time zone NOT NULL), sequenceid (uuid NOT NULL), numbernext (integer NOT NULL), datecreated (timestamp without time zone), createdbyid (text), lastupdated (timestamp without time zone), writebyid (text)
- Key foreign keys:
  - `fk_irsequencedateranges_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_irsequencedateranges_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_irsequencedateranges_irsequences_sequenceid`: (sequenceid) -> `dbo.irsequences` (id)

### `dbo.irsequences`

- Row count: **165**
- Primary key: `id`
- Columns (16): id (uuid NOT NULL), code (text), name (text NOT NULL), numbernext (integer NOT NULL), implementation (text), padding (integer NOT NULL), numberincrement (integer NOT NULL), prefix (text), active (boolean NOT NULL), suffix (text), companyid (uuid), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone), usedaterange (boolean NOT NULL)
- Key foreign keys:
  - `fk_irsequences_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_irsequences_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_irsequences_companies_companyid`: (companyid) -> `dbo.companies` (id)

### `dbo.labobitejoints`

- Row count: **0**
- Primary key: `id`
- Columns (6): id (uuid NOT NULL), name (text NOT NULL), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_labobitejoints_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_labobitejoints_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)

### `dbo.labobridges`

- Row count: **0**
- Primary key: `id`
- Columns (6): id (uuid NOT NULL), name (text NOT NULL), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_labobridges_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_labobridges_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)

### `dbo.labofinishlines`

- Row count: **0**
- Primary key: `id`
- Columns (6): id (uuid NOT NULL), name (text NOT NULL), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_labofinishlines_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_labofinishlines_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)

### `dbo.laboorderlines`

- Row count: **0**
- Primary key: `id`
- Columns (26): id (uuid NOT NULL), name (text), sequence (integer), productqty (numeric(18,2) NOT NULL), productid (uuid), partnerid (uuid), customerid (uuid), color (text), priceunit (numeric(18,2) NOT NULL), pricesubtotal (numeric(18,2) NOT NULL), pricetotal (numeric(18,2) NOT NULL), orderid (uuid NOT NULL), warrantycode (text), warrantyperiod (timestamp without time zone), companyid (uuid), note (text), toothcategoryid (uuid), qtyinvoiced (numeric(18,2) NOT NULL), state (text), saleorderlineid (uuid), isreceived (boolean NOT NULL), receiveddate (timestamp without time zone), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_laboorderlines_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_laboorderlines_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_laboorderlines_companies_companyid`: (companyid) -> `dbo.companies` (id)
  - `fk_laboorderlines_laboorders_orderid`: (orderid) -> `dbo.laboorders` (id)
  - `fk_laboorderlines_partners_customerid`: (customerid) -> `dbo.partners` (id)
  - `fk_laboorderlines_partners_partnerid`: (partnerid) -> `dbo.partners` (id)
  - `fk_laboorderlines_products_productid`: (productid) -> `dbo.products` (id)
  - `fk_laboorderlines_saleorderlines_saleorderlineid`: (saleorderlineid) -> `dbo.saleorderlines` (id)
  - ... and 1 more

### `dbo.laboorderlinetoothrels`

- Row count: **0**
- Primary key: `labolineid, toothid`
- Columns (2): labolineid (uuid NOT NULL), toothid (uuid NOT NULL)
- Key foreign keys:
  - `fk_laboorderlinetoothrels_laboorderlines_labolineid`: (labolineid) -> `dbo.laboorderlines` (id)
  - `fk_laboorderlinetoothrels_teeth_toothid`: (toothid) -> `dbo.teeth` (id)

### `dbo.laboorderproductrels`

- Row count: **0**
- Primary key: `laboorderid, productid`
- Columns (2): laboorderid (uuid NOT NULL), productid (uuid NOT NULL)
- Key foreign keys:
  - `fk_laboorderproductrels_laboorders_laboorderid`: (laboorderid) -> `dbo.laboorders` (id)
  - `fk_laboorderproductrels_products_productid`: (productid) -> `dbo.products` (id)

### `dbo.laboorders`

- Row count: **0**
- Primary key: `id`
- Columns (34): id (uuid NOT NULL), name (text NOT NULL), partnerid (uuid NOT NULL), customerid (uuid), dateorder (timestamp without time zone NOT NULL), dateplanned (timestamp without time zone), datereceipt (timestamp without time zone), dateexport (timestamp without time zone), companyid (uuid NOT NULL), productid (uuid), color (text), note (text), quantity (numeric(18,2) NOT NULL), priceunit (numeric(18,2) NOT NULL), amounttotal (numeric(18,2) NOT NULL), saleorderlineid (uuid), type (text), parentid (uuid), warrantycode (text), reason (text), warrantyperiod (timestamp without time zone), state (text), accountmoveid (uuid), indicated (text), technicalnote (text), labofinishlineid (uuid), labobitejointid (uuid), labobridgeid (uuid), doctorid (uuid), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone), toothrange (text)
- Key foreign keys:
  - `fk_laboorders_accountmoves_accountmoveid`: (accountmoveid) -> `dbo.accountmoves` (id)
  - `fk_laboorders_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_laboorders_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_laboorders_companies_companyid`: (companyid) -> `dbo.companies` (id)
  - `fk_laboorders_employees_doctorid`: (doctorid) -> `dbo.employees` (id)
  - `fk_laboorders_labobitejoints_labobitejointid`: (labobitejointid) -> `dbo.labobitejoints` (id)
  - `fk_laboorders_labobridges_labobridgeid`: (labobridgeid) -> `dbo.labobridges` (id)
  - `fk_laboorders_labofinishlines_labofinishlineid`: (labofinishlineid) -> `dbo.labofinishlines` (id)
  - ... and 5 more

### `dbo.laboordertoothrels`

- Row count: **0**
- Primary key: `toothid, laboorderid`
- Columns (2): laboorderid (uuid NOT NULL), toothid (uuid NOT NULL)
- Key foreign keys:
  - `fk_laboordertoothrels_laboorders_laboorderid`: (laboorderid) -> `dbo.laboorders` (id)
  - `fk_laboordertoothrels_teeth_toothid`: (toothid) -> `dbo.teeth` (id)

### `dbo.labowarranty`

- Row count: **0**
- Primary key: `id`
- Columns (17): id (uuid NOT NULL), name (text), laboorderid (uuid), companyid (uuid NOT NULL), employeeid (uuid), datereceiptwarranty (timestamp without time zone), datesendwarranty (timestamp without time zone), datereceiptinspection (timestamp without time zone), dateassemblywarranty (timestamp without time zone), reason (text), content (text), note (text), state (text), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_labowarranty_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_labowarranty_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_labowarranty_companies_companyid`: (companyid) -> `dbo.companies` (id)
  - `fk_labowarranty_employees_employeeid`: (employeeid) -> `dbo.employees` (id)
  - `fk_labowarranty_laboorders_laboorderid`: (laboorderid) -> `dbo.laboorders` (id)

### `dbo.labowarrantytoothrels`

- Row count: **0**
- Primary key: `labowarrantyid, toothid`
- Columns (2): labowarrantyid (uuid NOT NULL), toothid (uuid NOT NULL)
- Key foreign keys:
  - `fk_labowarrantytoothrels_labowarranty_labowarrantyid`: (labowarrantyid) -> `dbo.labowarranty` (id)
  - `fk_labowarrantytoothrels_teeth_toothid`: (toothid) -> `dbo.teeth` (id)

### `dbo.lead2opportunitypartners`

- Row count: **0**
- Primary key: `id`
- Columns (11): id (uuid NOT NULL), name (text), action (text), leadid (uuid NOT NULL), userid (text), partnerid (uuid), datecreated (timestamp without time zone), createdbyid (text), lastupdated (timestamp without time zone), writebyid (text), companyid (uuid)
- Key foreign keys:
  - `fk_lead2opportunitypartners_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_lead2opportunitypartners_aspnetusers_userid`: (userid) -> `dbo.aspnetusers` (id)
  - `fk_lead2opportunitypartners_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_lead2opportunitypartners_companies_companyid`: (companyid) -> `dbo.companies` (id)
  - `fk_lead2opportunitypartners_crmleads_leadid`: (leadid) -> `dbo.crmleads` (id)
  - `fk_lead2opportunitypartners_partners_partnerid`: (partnerid) -> `dbo.partners` (id)

### `dbo.leadrecallrules`

- Row count: **0**
- Primary key: `id`
- Columns (14): id (uuid NOT NULL), name (text), active (boolean NOT NULL), stageid (uuid), daystorecall (integer NOT NULL), dailyruntime (timestamp without time zone), datecreated (timestamp without time zone), createdbyid (text), lastupdated (timestamp without time zone), writebyid (text), taskdescription (text), taskduedatein (integer NOT NULL), tasktitle (text), tasktypeid (uuid)
- Key foreign keys:
  - `fk_leadrecallrules_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_leadrecallrules_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_leadrecallrules_crmstages_stageid`: (stageid) -> `dbo.crmstages` (id)
  - `fk_leadrecallrules_crmtasktypes_tasktypeid`: (tasktypeid) -> `dbo.crmtasktypes` (id)

### `dbo.loaithuchis`

- Row count: **0**
- Primary key: `id`
- Columns (15): id (uuid NOT NULL), name (text), code (text), note (text), type (text), isinclude (boolean NOT NULL), accountid (uuid), isaccounting (boolean NOT NULL), companyid (uuid), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone), active (boolean NOT NULL), issecondary (boolean NOT NULL)
- Key foreign keys:
  - `fk_loaithuchis_accountaccounts_accountid`: (accountid) -> `dbo.accountaccounts` (id)
  - `fk_loaithuchis_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_loaithuchis_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_loaithuchis_companies_companyid`: (companyid) -> `dbo.companies` (id)

### `dbo.mailactivities`

- Row count: **0**
- Primary key: `id`
- Columns (14): id (uuid NOT NULL), resmodel (text), resid (uuid), activitytypeid (uuid), summary (text), note (text), datedeadline (timestamp without time zone), automated (boolean), userid (text), datecreated (timestamp without time zone), createdbyid (text), lastupdated (timestamp without time zone), writebyid (text), resname (text)
- Key foreign keys:
  - `fk_mailactivities_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_mailactivities_aspnetusers_userid`: (userid) -> `dbo.aspnetusers` (id)
  - `fk_mailactivities_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_mailactivities_mailactivitytypes_activitytypeid`: (activitytypeid) -> `dbo.mailactivitytypes` (id)

### `dbo.mailactivitytypes`

- Row count: **0**
- Primary key: `id`
- Columns (15): id (uuid NOT NULL), name (text NOT NULL), summary (text), defaultnote (text), defaultuserid (text), sequence (integer), active (boolean NOT NULL), resmodel (text), category (text), datecreated (timestamp without time zone), createdbyid (text), lastupdated (timestamp without time zone), writebyid (text), delaycount (integer), delayunit (text)
- Key foreign keys:
  - `fk_mailactivitytypes_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_mailactivitytypes_aspnetusers_defaultuserid`: (defaultuserid) -> `dbo.aspnetusers` (id)
  - `fk_mailactivitytypes_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)

### `dbo.mailfollowermailmessagesubtyperels`

- Row count: **0**
- Primary key: `mailfollowerid, mailmessagesubtypeid`
- Columns (2): mailfollowerid (uuid NOT NULL), mailmessagesubtypeid (uuid NOT NULL)
- Key foreign keys:
  - `fk_mailfollowermailmessagesubtyperels_mailfollowers_mailfollowe`: (mailfollowerid) -> `dbo.mailfollowers` (id)
  - `fk_mailfollowermailmessagesubtyperels_mailmessagesubtypes_mailm`: (mailmessagesubtypeid) -> `dbo.mailmessagesubtypes` (id)

### `dbo.mailfollowers`

- Row count: **386518**
- Primary key: `id`
- Columns (8): id (uuid NOT NULL), resmodel (text NOT NULL), resid (uuid), partnerid (uuid NOT NULL), datecreated (timestamp without time zone), createdbyid (text), lastupdated (timestamp without time zone), writebyid (text)
- Key foreign keys:
  - `fk_mailfollowers_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_mailfollowers_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_mailfollowers_partners_partnerid`: (partnerid) -> `dbo.partners` (id)

### `dbo.mailmessagerespartnerrels`

- Row count: **0**
- Primary key: `mailmessageid, partnerid`
- Columns (2): mailmessageid (uuid NOT NULL), partnerid (uuid NOT NULL)
- Key foreign keys:
  - `fk_mailmessagerespartnerrels_mailmessages_mailmessageid`: (mailmessageid) -> `dbo.mailmessages` (id)
  - `fk_mailmessagerespartnerrels_partners_partnerid`: (partnerid) -> `dbo.partners` (id)

### `dbo.mailmessages`

- Row count: **640707**
- Primary key: `id`
- Columns (27): id (uuid NOT NULL), subject (text), date (timestamp without time zone), body (text), model (text), resid (uuid), recordname (text), subtypeid (uuid), messagetype (text NOT NULL), emailfrom (text), authorid (uuid), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone), callcenterhistoryid (uuid), znstemplatedata (text), znstemplateid (uuid), smsaccountid (uuid), smscampaignid (uuid), mailactivitytypeid (uuid), activitystatus (integer), partnerid (uuid), taskid (uuid), tasktypeid (uuid), baseautomationv2id (uuid), residstr (text)
- Key foreign keys:
  - `fk_mailmessages_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_mailmessages_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_mailmessages_baseautomationv2s_baseautomationv2id`: (baseautomationv2id) -> `dbo.baseautomationv2s` (id)
  - `fk_mailmessages_crmcallcenterhistories_callcenterhistoryid`: (callcenterhistoryid) -> `dbo.crmcallcenterhistories` (id)
  - `fk_mailmessages_crmtasks_taskid`: (taskid) -> `dbo.crmtasks` (id)
  - `fk_mailmessages_crmtasktypes_tasktypeid`: (tasktypeid) -> `dbo.crmtasktypes` (id)
  - `fk_mailmessages_mailactivitytypes_mailactivitytypeid`: (mailactivitytypeid) -> `dbo.mailactivitytypes` (id)
  - `fk_mailmessages_mailmessagesubtypes_subtypeid`: (subtypeid) -> `dbo.mailmessagesubtypes` (id)
  - ... and 5 more

### `dbo.mailmessagesubtypes`

- Row count: **7**
- Primary key: `id`
- Columns (15): id (uuid NOT NULL), name (text NOT NULL), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone), default (boolean NOT NULL), description (text), hidden (boolean NOT NULL), internal (boolean NOT NULL), resmodel (text), sequence (integer NOT NULL), parentid (uuid), relationfield (text), type (text)
- Key foreign keys:
  - `fk_mailmessagesubtypes_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_mailmessagesubtypes_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_mailmessagesubtypes_mailmessagesubtypes_parentid`: (parentid) -> `dbo.mailmessagesubtypes` (id)

### `dbo.mailnotifications`

- Row count: **0**
- Primary key: `id`
- Columns (17): id (uuid NOT NULL), mailmessageid (uuid NOT NULL), respartnerid (uuid), isread (boolean NOT NULL), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone), authorid (uuid), notificationstatus (text), notificationtype (text), znsfailuretype (text), znsmessageid (uuid), znsnumber (text), smsfailuretype (text), smsid (uuid), smsnumber (text)
- Key foreign keys:
  - `fk_mailnotifications_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_mailnotifications_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_mailnotifications_mailmessages_mailmessageid`: (mailmessageid) -> `dbo.mailmessages` (id)
  - `fk_mailnotifications_partners_authorid`: (authorid) -> `dbo.partners` (id)
  - `fk_mailnotifications_partners_respartnerid`: (respartnerid) -> `dbo.partners` (id)
  - `fk_mailnotifications_smsmessagedetails_smsid`: (smsid) -> `dbo.smsmessagedetails` (id)
  - `fk_mailnotifications_znsmessages_znsmessageid`: (znsmessageid) -> `dbo.znsmessages` (id)

### `dbo.mailpush`

- Row count: **0**
- Primary key: `id`
- Columns (7): id (uuid NOT NULL), devicetoken (text), payload (text), datecreated (timestamp without time zone), createdbyid (text), lastupdated (timestamp without time zone), writebyid (text)
- Key foreign keys:
  - `fk_mailpush_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_mailpush_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)

### `dbo.mailpushdevices`

- Row count: **0**
- Primary key: `id`
- Columns (9): id (uuid NOT NULL), partnerid (uuid NOT NULL), endpoint (text NOT NULL), keys (text NOT NULL), expirationtime (timestamp without time zone), datecreated (timestamp without time zone), createdbyid (text), lastupdated (timestamp without time zone), writebyid (text)
- Key foreign keys:
  - `fk_mailpushdevices_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_mailpushdevices_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_mailpushdevices_partners_partnerid`: (partnerid) -> `dbo.partners` (id)

### `dbo.mailtrackingvalues`

- Row count: **0**
- Primary key: `id`
- Columns (22): id (uuid NOT NULL), field (text NOT NULL), fielddesc (text NOT NULL), fieldtype (text), oldvalueinteger (integer), oldvaluedecimal (numeric(18,2)), oldvaluetext (text), oldvaluedatetime (timestamp without time zone), newvalueinteger (integer), newvaluedecimal (numeric(18,2)), newvaluetext (text), newvaluedatetime (timestamp without time zone), mailmessageid (uuid NOT NULL), tracksequence (integer NOT NULL), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone), newvalueguid (uuid), newvaluestring (text), oldvalueguid (uuid), oldvaluestring (text)
- Key foreign keys:
  - `fk_mailtrackingvalues_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_mailtrackingvalues_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_mailtrackingvalues_mailmessages_mailmessageid`: (mailmessageid) -> `dbo.mailmessages` (id)

### `dbo.marketingcampaignactivities`

- Row count: **0**
- Primary key: `id`
- Columns (19): id (uuid NOT NULL), name (text NOT NULL), campaignid (uuid NOT NULL), condition (text), activitytype (text), content (text), intervaltype (text), intervalnumber (integer), sequence (integer), triggertype (text), jobid (text), messageid (uuid), actiontype (text), parentid (uuid), audiencefilter (text), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_marketingcampaignactivities_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_marketingcampaignactivities_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_marketingcampaignactivities_marketingcampaignactivities_pare`: (parentid) -> `dbo.marketingcampaignactivities` (id)
  - `fk_marketingcampaignactivities_marketingcampaigns_campaignid`: (campaignid) -> `dbo.marketingcampaigns` (id)
  - `fk_marketingcampaignactivities_marketingmessages_messageid`: (messageid) -> `dbo.marketingmessages` (id)

### `dbo.marketingcampaignactivityfacebooktagrels`

- Row count: **0**
- Primary key: `activityid, tagid`
- Columns (2): activityid (uuid NOT NULL), tagid (uuid NOT NULL)
- Key foreign keys:
  - `fk_marketingcampaignactivityfacebooktagrels_facebooktags_tagid`: (tagid) -> `dbo.facebooktags` (id)
  - `fk_marketingcampaignactivityfacebooktagrels_marketingcampaignac`: (activityid) -> `dbo.marketingcampaignactivities` (id)

### `dbo.marketingcampaigns`

- Row count: **0**
- Primary key: `id`
- Columns (9): id (uuid NOT NULL), name (text NOT NULL), state (text), datestart (timestamp without time zone), facebookpageid (uuid), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_marketingcampaigns_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_marketingcampaigns_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_marketingcampaigns_facebookpages_facebookpageid`: (facebookpageid) -> `dbo.facebookpages` (id)

### `dbo.marketingmessagebuttons`

- Row count: **0**
- Primary key: `id`
- Columns (10): id (uuid NOT NULL), type (text), url (text), title (text), payload (text), messageid (uuid NOT NULL), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_marketingmessagebuttons_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_marketingmessagebuttons_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_marketingmessagebuttons_marketingmessages_messageid`: (messageid) -> `dbo.marketingmessages` (id)

### `dbo.marketingmessages`

- Row count: **0**
- Primary key: `id`
- Columns (8): id (uuid NOT NULL), type (text NOT NULL), template (text NOT NULL), text (text), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_marketingmessages_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_marketingmessages_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)

### `dbo.marketingtraces`

- Row count: **0**
- Primary key: `id`
- Columns (12): id (uuid NOT NULL), activityid (uuid NOT NULL), sent (timestamp without time zone), exception (timestamp without time zone), read (timestamp without time zone), delivery (timestamp without time zone), messageid (text), userprofileid (uuid), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_marketingtraces_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_marketingtraces_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_marketingtraces_facebookuserprofiles_userprofileid`: (userprofileid) -> `dbo.facebookuserprofiles` (id)
  - `fk_marketingtraces_marketingcampaignactivities_activityid`: (activityid) -> `dbo.marketingcampaignactivities` (id)

### `dbo.medicineorderlines`

- Row count: **0**
- Primary key: `id`
- Columns (12): id (uuid NOT NULL), quantity (numeric(18,2) NOT NULL), price (numeric(18,2) NOT NULL), amounttotal (numeric(18,2) NOT NULL), medicineorderid (uuid NOT NULL), toathuoclineid (uuid NOT NULL), productid (uuid), productuomid (uuid), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_medicineorderlines_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_medicineorderlines_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_medicineorderlines_medicineorders_medicineorderid`: (medicineorderid) -> `dbo.medicineorders` (id)
  - `fk_medicineorderlines_products_productid`: (productid) -> `dbo.products` (id)
  - `fk_medicineorderlines_toathuoclines_toathuoclineid`: (toathuoclineid) -> `dbo.toathuoclines` (id)
  - `fk_medicineorderlines_uoms_productuomid`: (productuomid) -> `dbo.uoms` (id)

### `dbo.medicineorders`

- Row count: **0**
- Primary key: `id`
- Columns (19): id (uuid NOT NULL), name (text), journalid (uuid NOT NULL), partnerid (uuid NOT NULL), toathuocid (uuid NOT NULL), orderdate (timestamp without time zone NOT NULL), employeeid (uuid), companyid (uuid NOT NULL), amount (numeric(18,2) NOT NULL), state (text), note (text), moveid (uuid), accountpaymentid (uuid), stockpickingoutgoingid (uuid), stockpickingincomingid (uuid), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_medicineorders_accountjournals_journalid`: (journalid) -> `dbo.accountjournals` (id)
  - `fk_medicineorders_accountmoves_moveid`: (moveid) -> `dbo.accountmoves` (id)
  - `fk_medicineorders_accountpayments_accountpaymentid`: (accountpaymentid) -> `dbo.accountpayments` (id)
  - `fk_medicineorders_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_medicineorders_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_medicineorders_companies_companyid`: (companyid) -> `dbo.companies` (id)
  - `fk_medicineorders_employees_employeeid`: (employeeid) -> `dbo.employees` (id)
  - `fk_medicineorders_partners_partnerid`: (partnerid) -> `dbo.partners` (id)
  - ... and 3 more

### `dbo.memberlevels`

- Row count: **0**
- Primary key: `id`
- Columns (9): id (uuid NOT NULL), name (text NOT NULL), point (numeric(18,2) NOT NULL), color (text), companyid (uuid NOT NULL), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_memberlevels_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_memberlevels_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_memberlevels_companies_companyid`: (companyid) -> `dbo.companies` (id)

### `dbo.notifyconfigs`

- Row count: **0**
- Primary key: `id`
- Columns (9): id (uuid NOT NULL), notifytype (text NOT NULL), notifytiming (integer NOT NULL), notifyintervalvalue (integer NOT NULL), notifyintervalunit (text NOT NULL), datecreated (timestamp without time zone), createdbyid (text), lastupdated (timestamp without time zone), writebyid (text)
- Key foreign keys:
  - `fk_notifyconfigs_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_notifyconfigs_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)

### `dbo.onlinesurveyquestionanswers`

- Row count: **0**
- Primary key: `id`
- Columns (9): id (uuid NOT NULL), questionid (uuid NOT NULL), sequence (integer), value (text NOT NULL), valueimage (text), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_onlinesurveyquestionanswers_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_onlinesurveyquestionanswers_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_onlinesurveyquestionanswers_onlinesurveyquestions_questionid`: (questionid) -> `dbo.onlinesurveyquestions` (id)

### `dbo.onlinesurveyquestions`

- Row count: **0**
- Primary key: `id`
- Columns (11): id (uuid NOT NULL), title (text NOT NULL), surveyid (uuid NOT NULL), sequence (integer), questiontype (text), numericalboxstyle (text), pointscale (integer), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_onlinesurveyquestions_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_onlinesurveyquestions_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_onlinesurveyquestions_onlinesurveysurveys_surveyid`: (surveyid) -> `dbo.onlinesurveysurveys` (id)

### `dbo.onlinesurveysurveys`

- Row count: **0**
- Primary key: `id`
- Columns (16): id (uuid NOT NULL), title (text NOT NULL), color (integer), backgroundimage (text), active (boolean NOT NULL), logo (text), userid (text), questionslayout (text), progressionmode (text), accesstoken (text), state (text), companyid (uuid), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_onlinesurveysurveys_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_onlinesurveysurveys_aspnetusers_userid`: (userid) -> `dbo.aspnetusers` (id)
  - `fk_onlinesurveysurveys_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_onlinesurveysurveys_companies_companyid`: (companyid) -> `dbo.companies` (id)

### `dbo.onlinesurveyuserinputemployeerels`

- Row count: **0**
- Primary key: `userinputid, employeeid`
- Columns (2): userinputid (uuid NOT NULL), employeeid (uuid NOT NULL)
- Key foreign keys:
  - `fk_onlinesurveyuserinputemployeerels_employees_employeeid`: (employeeid) -> `dbo.employees` (id)
  - `fk_onlinesurveyuserinputemployeerels_onlinesurveyuserinputs_use`: (userinputid) -> `dbo.onlinesurveyuserinputs` (id)

### `dbo.onlinesurveyuserinputlines`

- Row count: **0**
- Primary key: `id`
- Columns (12): id (uuid NOT NULL), userinputid (uuid NOT NULL), questionid (uuid NOT NULL), questionsequence (integer NOT NULL), answertype (text), valuetextbox (text), valuenumericalbox (double precision), answerid (uuid), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_onlinesurveyuserinputlines_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_onlinesurveyuserinputlines_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_onlinesurveyuserinputlines_onlinesurveyquestionanswers_answe`: (answerid) -> `dbo.onlinesurveyquestionanswers` (id)
  - `fk_onlinesurveyuserinputlines_onlinesurveyquestions_questionid`: (questionid) -> `dbo.onlinesurveyquestions` (id)
  - `fk_onlinesurveyuserinputlines_onlinesurveyuserinputs_userinputi`: (userinputid) -> `dbo.onlinesurveyuserinputs` (id)

### `dbo.onlinesurveyuserinputproductrels`

- Row count: **0**
- Primary key: `userinputid, productid`
- Columns (2): userinputid (uuid NOT NULL), productid (uuid NOT NULL)
- Key foreign keys:
  - `fk_onlinesurveyuserinputproductrels_onlinesurveyuserinputs_user`: (userinputid) -> `dbo.onlinesurveyuserinputs` (id)
  - `fk_onlinesurveyuserinputproductrels_products_productid`: (productid) -> `dbo.products` (id)

### `dbo.onlinesurveyuserinputs`

- Row count: **0**
- Primary key: `id`
- Columns (15): id (uuid NOT NULL), partnerid (uuid), surveyid (uuid NOT NULL), datestart (timestamp without time zone), dateend (timestamp without time zone), accesstoken (text), state (text), phone (text), lastdisplayedquestionid (uuid), istest (boolean NOT NULL), companyid (uuid), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_onlinesurveyuserinputs_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_onlinesurveyuserinputs_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_onlinesurveyuserinputs_companies_companyid`: (companyid) -> `dbo.companies` (id)
  - `fk_onlinesurveyuserinputs_onlinesurveyquestions_lastdisplayedqu`: (lastdisplayedquestionid) -> `dbo.onlinesurveyquestions` (id)
  - `fk_onlinesurveyuserinputs_onlinesurveysurveys_surveyid`: (surveyid) -> `dbo.onlinesurveysurveys` (id)
  - `fk_onlinesurveyuserinputs_partners_partnerid`: (partnerid) -> `dbo.partners` (id)

### `dbo.outboxstates`

- Row count: **0**
- Primary key: `id`
- Columns (6): id (uuid NOT NULL), rowversion (bytea), delivered (timestamp without time zone), lastsequenceid (uuid), created (timestamp without time zone NOT NULL), lockid (uuid)
- Key foreign keys:
  - (none)

### `dbo.partneradvances`

- Row count: **13591**
- Primary key: `id`
- Columns (17): id (uuid NOT NULL), name (text), date (timestamp without time zone NOT NULL), amount (numeric(18,2) NOT NULL), partnerid (uuid NOT NULL), journalid (uuid), companyid (uuid), type (text), state (text), note (text), moveid (uuid), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone), destinationaccountid (uuid), accountpaymentid (uuid)
- Key foreign keys:
  - `fk_partneradvances_accountaccounts_destinationaccountid`: (destinationaccountid) -> `dbo.accountaccounts` (id)
  - `fk_partneradvances_accountjournals_journalid`: (journalid) -> `dbo.accountjournals` (id)
  - `fk_partneradvances_accountmoves_moveid`: (moveid) -> `dbo.accountmoves` (id)
  - `fk_partneradvances_accountpayments_accountpaymentid`: (accountpaymentid) -> `dbo.accountpayments` (id)
  - `fk_partneradvances_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_partneradvances_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_partneradvances_companies_companyid`: (companyid) -> `dbo.companies` (id)
  - `fk_partneradvances_partners_partnerid`: (partnerid) -> `dbo.partners` (id)

### `dbo.partnerallowcompanyrels`

- Row count: **22041**
- Primary key: `partnerid, companyid`
- Columns (5): partnerid (uuid NOT NULL), companyid (uuid NOT NULL), createdbyid (text), datecreated (timestamp without time zone), note (text)
- Key foreign keys:
  - `fk_partnerallowcompanyrels_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_partnerallowcompanyrels_companies_companyid`: (companyid) -> `dbo.companies` (id)
  - `fk_partnerallowcompanyrels_partners_partnerid`: (partnerid) -> `dbo.partners` (id)

### `dbo.partnercategories`

- Row count: **12**
- Primary key: `id`
- Columns (12): id (uuid NOT NULL), name (text NOT NULL), parentid (uuid), completename (text), active (boolean NOT NULL), parentleft (integer), parentright (integer), color (text), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_partnercategories_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_partnercategories_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_partnercategories_partnercategories_parentid`: (parentid) -> `dbo.partnercategories` (id)

### `dbo.partnercontactstatuses`

- Row count: **0**
- Primary key: `id`
- Columns (7): id (uuid NOT NULL), name (text NOT NULL), datecreated (timestamp without time zone), createdbyid (text), lastupdated (timestamp without time zone), writebyid (text), active (boolean NOT NULL)
- Key foreign keys:
  - `fk_partnercontactstatuses_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_partnercontactstatuses_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)

### `dbo.partnercustomerstatuschangelogs`

- Row count: **0**
- Primary key: `id`
- Columns (14): id (uuid NOT NULL), partnerid (uuid NOT NULL), userid (text), date (timestamp without time zone NOT NULL), fromstatus (text), tostatus (text), resid (uuid), resname (text), resmodel (text), description (text), datecreated (timestamp without time zone), createdbyid (text), lastupdated (timestamp without time zone), writebyid (text)
- Key foreign keys:
  - `fk_partnercustomerstatuschangelogs_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_partnercustomerstatuschangelogs_aspnetusers_userid`: (userid) -> `dbo.aspnetusers` (id)
  - `fk_partnercustomerstatuschangelogs_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_partnercustomerstatuschangelogs_partners_partnerid`: (partnerid) -> `dbo.partners` (id)

### `dbo.partnerdebtadjustments`

- Row count: **0**
- Primary key: `id`
- Columns (14): id (uuid NOT NULL), date (timestamp without time zone NOT NULL), amountdebttotal (numeric(18,2) NOT NULL), amountadjusttotal (numeric(18,2) NOT NULL), partnertype (text), partnerid (uuid NOT NULL), companyid (uuid NOT NULL), moveid (uuid), state (text), note (text), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_partnerdebtadjustments_accountmoves_moveid`: (moveid) -> `dbo.accountmoves` (id)
  - `fk_partnerdebtadjustments_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_partnerdebtadjustments_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_partnerdebtadjustments_companies_companyid`: (companyid) -> `dbo.companies` (id)
  - `fk_partnerdebtadjustments_partners_partnerid`: (partnerid) -> `dbo.partners` (id)

### `dbo.partnerhistoryrels`

- Row count: **0**
- Primary key: `partnerid, historyid`
- Columns (2): partnerid (uuid NOT NULL), historyid (uuid NOT NULL)
- Key foreign keys:
  - `fk_partnerhistoryrels_histories_historyid`: (historyid) -> `dbo.histories` (id)
  - `fk_partnerhistoryrels_partners_partnerid`: (partnerid) -> `dbo.partners` (id)

### `dbo.partnerimages`

- Row count: **0**
- Primary key: `id`
- Columns (11): id (uuid NOT NULL), name (text NOT NULL), note (text), date (timestamp without time zone), partnerid (uuid), dotkhamid (uuid), uploadid (text NOT NULL), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_partnerimages_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_partnerimages_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_partnerimages_dotkhams_dotkhamid`: (dotkhamid) -> `dbo.dotkhams` (id)
  - `fk_partnerimages_partners_partnerid`: (partnerid) -> `dbo.partners` (id)

### `dbo.partnerlinkcompanies`

- Row count: **0**
- Primary key: `id`
- Columns (10): id (uuid NOT NULL), name (text), partnerid (uuid NOT NULL), date (timestamp without time zone NOT NULL), userid (text), companyid (uuid NOT NULL), datecreated (timestamp without time zone), createdbyid (text), lastupdated (timestamp without time zone), writebyid (text)
- Key foreign keys:
  - `fk_partnerlinkcompanies_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_partnerlinkcompanies_aspnetusers_userid`: (userid) -> `dbo.aspnetusers` (id)
  - `fk_partnerlinkcompanies_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_partnerlinkcompanies_companies_companyid`: (companyid) -> `dbo.companies` (id)
  - `fk_partnerlinkcompanies_partners_partnerid`: (partnerid) -> `dbo.partners` (id)

### `dbo.partnermappsidfacebookpages`

- Row count: **0**
- Primary key: `id`
- Columns (8): id (uuid NOT NULL), partnerid (uuid NOT NULL), pageid (text), psid (text), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_partnermappsidfacebookpages_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_partnermappsidfacebookpages_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_partnermappsidfacebookpages_partners_partnerid`: (partnerid) -> `dbo.partners` (id)

### `dbo.partnerpartnercategoryrel`

- Row count: **4364**
- Primary key: `categoryid, partnerid`
- Columns (2): categoryid (uuid NOT NULL), partnerid (uuid NOT NULL)
- Key foreign keys:
  - `fk_partnerpartnercategoryrel_partnercategories_categoryid`: (categoryid) -> `dbo.partnercategories` (id)
  - `fk_partnerpartnercategoryrel_partners_partnerid`: (partnerid) -> `dbo.partners` (id)

### `dbo.partnerprofilesummaries`

- Row count: **11942**
- Primary key: `id`
- Columns (11): id (uuid NOT NULL), partnerid (uuid NOT NULL), amounttreatmenttotal (numeric(18,2) NOT NULL), datecreated (timestamp without time zone), createdbyid (text), lastupdated (timestamp without time zone), writebyid (text), amountrevenuetotal (numeric(18,2) NOT NULL), amountorderresidualtotal (numeric(18,2) NOT NULL), amountdebittotal (numeric(18,2) NOT NULL), recenttreatmentdate (timestamp without time zone)
- Key foreign keys:
  - `fk_partnerprofilesummaries_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_partnerprofilesummaries_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_partnerprofilesummaries_partners_partnerid`: (partnerid) -> `dbo.partners` (id)

### `dbo.partnerreturnmarketinglogs`

- Row count: **0**
- Primary key: `id`
- Columns (13): id (uuid NOT NULL), partnerid (uuid NOT NULL), userid (text), date (timestamp without time zone NOT NULL), reason (text), fromcompanyid (uuid), tocompanyid (uuid), frommarketinguserid (text), tomarketinguserid (text), datecreated (timestamp without time zone), createdbyid (text), lastupdated (timestamp without time zone), writebyid (text)
- Key foreign keys:
  - `fk_partnerreturnmarketinglogs_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_partnerreturnmarketinglogs_aspnetusers_frommarketinguserid`: (frommarketinguserid) -> `dbo.aspnetusers` (id)
  - `fk_partnerreturnmarketinglogs_aspnetusers_tomarketinguserid`: (tomarketinguserid) -> `dbo.aspnetusers` (id)
  - `fk_partnerreturnmarketinglogs_aspnetusers_userid`: (userid) -> `dbo.aspnetusers` (id)
  - `fk_partnerreturnmarketinglogs_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_partnerreturnmarketinglogs_companies_fromcompanyid`: (fromcompanyid) -> `dbo.companies` (id)
  - `fk_partnerreturnmarketinglogs_companies_tocompanyid`: (tocompanyid) -> `dbo.companies` (id)
  - `fk_partnerreturnmarketinglogs_partners_partnerid`: (partnerid) -> `dbo.partners` (id)

### `dbo.partners`

- Row count: **31922**
- Primary key: `id`
- Columns (87): id (uuid NOT NULL), displayname (text), name (text NOT NULL), namenosign (text), street (text), phone (text), email (text), supplier (boolean NOT NULL), customer (boolean NOT NULL), isagent (boolean NOT NULL), isinsurance (boolean NOT NULL), companyid (uuid), ref (text), comment (text), active (boolean NOT NULL), employee (boolean NOT NULL), gender (text), jobtitle (text), birthyear (integer), birthmonth (integer), birthday (integer), medicalhistory (text), citycode (text), cityname (text), districtcode (text), districtname (text), wardcode (text), wardname (text), barcode (text), fax (text), sourceid (uuid), referraluserid (text), note (text), avatar (text), zaloid (text), date (timestamp without time zone), titleid (uuid), agentid (uuid), weight (numeric(18,2)), healthinsurancecardnumber (text), calendarlastnotifack (timestamp without time zone), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone), iscompany (boolean NOT NULL), ishead (boolean NOT NULL), hotline (text), website (text), countryid (uuid), stateid (uuid), type (text), userid (text), stageid (uuid), sequencenumber (integer), sequenceprefix (text), birthdaycustomerstate (integer), customerthankstate (integer), emergencyphone (text), lasttreatmentcompletedate (timestamp without time zone), treatmentstatus (text), taxcode (text), unitaddress (text), unitname (text), customername (text), invoicereceivingmethod (text), isbusinessinvoice (boolean NOT NULL), personaladdress (text), personalname (text), receiveremail (text), receiverzalonumber (text), personalidentitycard (text), personaltaxcode (text), citycodev2 (text), citynamev2 (text), identitynumber (text), usedaddressv2 (boolean), wardcodev2 (text), wardnamev2 (text), age (integer), contactstatusid (uuid), customerstatus (text), marketingstaffid (text), potentiallevel (text), marketingteamid (uuid), saleteamid (uuid), isdeleted (boolean NOT NULL)
- Key foreign keys:
  - `fk_partners_agents_agentid`: (agentid) -> `dbo.agents` (id)
  - `fk_partners_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_partners_aspnetusers_marketingstaffid`: (marketingstaffid) -> `dbo.aspnetusers` (id)
  - `fk_partners_aspnetusers_referraluserid`: (referraluserid) -> `dbo.aspnetusers` (id)
  - `fk_partners_aspnetusers_userid`: (userid) -> `dbo.aspnetusers` (id)
  - `fk_partners_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_partners_companies_companyid`: (companyid) -> `dbo.companies` (id)
  - `fk_partners_countries_countryid`: (countryid) -> `dbo.countries` (id)
  - ... and 7 more

### `dbo.partnerserviceinterestrels`

- Row count: **0**
- Primary key: `partnerid, productid`
- Columns (2): partnerid (uuid NOT NULL), productid (uuid NOT NULL)
- Key foreign keys:
  - `fk_partnerserviceinterestrels_partners_partnerid`: (partnerid) -> `dbo.partners` (id)
  - `fk_partnerserviceinterestrels_products_productid`: (productid) -> `dbo.products` (id)

### `dbo.partnersources`

- Row count: **11**
- Primary key: `id`
- Columns (9): id (uuid NOT NULL), name (text), type (text), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone), iscollaborators (boolean NOT NULL), isactive (boolean NOT NULL)
- Key foreign keys:
  - `fk_partnersources_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_partnersources_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)

### `dbo.partnersubscriptions`

- Row count: **3776**
- Primary key: `id`
- Columns (8): id (uuid NOT NULL), partnerid (uuid NOT NULL), devicetoken (text), platform (integer NOT NULL), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_partnersubscriptions_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_partnersubscriptions_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_partnersubscriptions_partners_partnerid`: (partnerid) -> `dbo.partners` (id)

### `dbo.partnertitles`

- Row count: **5**
- Primary key: `id`
- Columns (6): id (uuid NOT NULL), name (text NOT NULL), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_partnertitles_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_partnertitles_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)

### `dbo.paymentquotations`

- Row count: **0**
- Primary key: `id`
- Columns (11): id (uuid NOT NULL), sequence (integer NOT NULL), discountpercenttype (text), payment (numeric(18,2)), amount (numeric(18,2)), date (timestamp without time zone), quotationid (uuid NOT NULL), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_paymentquotations_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_paymentquotations_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_paymentquotations_quotations_quotationid`: (quotationid) -> `dbo.quotations` (id)

### `dbo.paymentrequests`

- Row count: **0**
- Primary key: `id`
- Columns (16): id (uuid NOT NULL), name (text), requestdate (timestamp without time zone NOT NULL), requesttype (text), amount (numeric(18,2) NOT NULL), communication (text), companyid (uuid), journalid (uuid NOT NULL), destinationcompanyid (uuid), destinationjournalid (uuid NOT NULL), state (text), datecreated (timestamp without time zone), createdbyid (text), lastupdated (timestamp without time zone), writebyid (text), employeeid (uuid)
- Key foreign keys:
  - `fk_paymentrequests_accountjournals_destinationjournalid`: (destinationjournalid) -> `dbo.accountjournals` (id)
  - `fk_paymentrequests_accountjournals_journalid`: (journalid) -> `dbo.accountjournals` (id)
  - `fk_paymentrequests_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_paymentrequests_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_paymentrequests_companies_companyid`: (companyid) -> `dbo.companies` (id)
  - `fk_paymentrequests_companies_destinationcompanyid`: (destinationcompanyid) -> `dbo.companies` (id)
  - `fk_paymentrequests_employees_employeeid`: (employeeid) -> `dbo.employees` (id)

### `dbo.phieuthuchis`

- Row count: **0**
- Primary key: `id`
- Columns (26): id (uuid NOT NULL), companyid (uuid), date (timestamp without time zone NOT NULL), journalid (uuid NOT NULL), state (text), name (text), type (text), accounttype (text), amount (numeric(18,2) NOT NULL), communication (text), reason (text), payerreceiver (text), address (text), loaithuchiid (uuid), partnertype (text), partnerid (uuid), agentid (uuid), accountid (uuid), isaccounting (boolean), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone), currencyid (uuid), householdbusinessid (uuid), accountpaymentid (uuid)
- Key foreign keys:
  - `fk_phieuthuchis_accountaccounts_accountid`: (accountid) -> `dbo.accountaccounts` (id)
  - `fk_phieuthuchis_accountjournals_journalid`: (journalid) -> `dbo.accountjournals` (id)
  - `fk_phieuthuchis_accountpayments_accountpaymentid`: (accountpaymentid) -> `dbo.accountpayments` (id)
  - `fk_phieuthuchis_agents_agentid`: (agentid) -> `dbo.agents` (id)
  - `fk_phieuthuchis_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_phieuthuchis_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_phieuthuchis_companies_companyid`: (companyid) -> `dbo.companies` (id)
  - `fk_phieuthuchis_currencies_currencyid`: (currencyid) -> `dbo.currencies` (id)
  - ... and 3 more

### `dbo.printpapersizes`

- Row count: **2**
- Primary key: `id`
- Columns (17): id (uuid NOT NULL), name (text), paperformat (text), issize (boolean NOT NULL), topmargin (integer NOT NULL), bottommargin (integer NOT NULL), leftmargin (integer NOT NULL), rightmargin (integer NOT NULL), headerspacing (integer NOT NULL), orientation (text), headerline (boolean NOT NULL), customwidth (integer), customheight (integer), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_printpapersizes_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_printpapersizes_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)

### `dbo.printtemplateconfigs`

- Row count: **9**
- Primary key: `id`
- Columns (11): id (uuid NOT NULL), content (text), type (text), printpapersizeid (uuid), printtemplateid (uuid), isdefault (boolean NOT NULL), companyid (uuid), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_printtemplateconfigs_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_printtemplateconfigs_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_printtemplateconfigs_companies_companyid`: (companyid) -> `dbo.companies` (id)
  - `fk_printtemplateconfigs_printpapersizes_printpapersizeid`: (printpapersizeid) -> `dbo.printpapersizes` (id)
  - `fk_printtemplateconfigs_printtemplates_printtemplateid`: (printtemplateid) -> `dbo.printtemplates` (id)

### `dbo.printtemplateconfigv2s`

- Row count: **0**
- Primary key: `id`
- Columns (9): id (uuid NOT NULL), type (text), name (text), printpapersizeid (uuid), printtemplateid (uuid), datecreated (timestamp without time zone), createdbyid (text), lastupdated (timestamp without time zone), writebyid (text)
- Key foreign keys:
  - `fk_printtemplateconfigv2s_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_printtemplateconfigv2s_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_printtemplateconfigv2s_printpapersizes_printpapersizeid`: (printpapersizeid) -> `dbo.printpapersizes` (id)
  - `fk_printtemplateconfigv2s_printtemplates_printtemplateid`: (printtemplateid) -> `dbo.printtemplates` (id)

### `dbo.printtemplates`

- Row count: **49**
- Primary key: `id`
- Columns (9): id (uuid NOT NULL), content (text), type (text), model (text), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone), name (text)
- Key foreign keys:
  - `fk_printtemplates_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_printtemplates_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)

### `dbo.productappointmentrels`

- Row count: **18844**
- Primary key: `productid, appoinmentid`
- Columns (2): productid (uuid NOT NULL), appoinmentid (uuid NOT NULL)
- Key foreign keys:
  - `fk_productappointmentrels_appointments_appoinmentid`: (appoinmentid) -> `dbo.appointments` (id)
  - `fk_productappointmentrels_products_productid`: (productid) -> `dbo.products` (id)

### `dbo.productboms`

- Row count: **0**
- Primary key: `id`
- Columns (10): id (uuid NOT NULL), productid (uuid NOT NULL), materialproductid (uuid), productuomid (uuid NOT NULL), quantity (numeric(18,2) NOT NULL), sequence (integer NOT NULL), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_productboms_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_productboms_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_productboms_products_materialproductid`: (materialproductid) -> `dbo.products` (id)
  - `fk_productboms_products_productid`: (productid) -> `dbo.products` (id)
  - `fk_productboms_uoms_productuomid`: (productuomid) -> `dbo.uoms` (id)

### `dbo.productcategories`

- Row count: **17**
- Primary key: `id`
- Columns (17): id (uuid NOT NULL), name (text NOT NULL), completename (text), parentid (uuid), parentleft (integer), parentright (integer), sequence (integer), servicecateg (boolean NOT NULL), medicinecateg (boolean NOT NULL), labocateg (boolean NOT NULL), productcateg (boolean NOT NULL), stepcateg (boolean NOT NULL), type (text), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_productcategories_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_productcategories_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_productcategories_productcategories_parentid`: (parentid) -> `dbo.productcategories` (id)

### `dbo.productcompanyrels`

- Row count: **0**
- Primary key: `productid, companyid`
- Columns (3): productid (uuid NOT NULL), companyid (uuid NOT NULL), standardprice (double precision NOT NULL)
- Key foreign keys:
  - `fk_productcompanyrels_companies_companyid`: (companyid) -> `dbo.companies` (id)
  - `fk_productcompanyrels_products_productid`: (productid) -> `dbo.products` (id)

### `dbo.productpricehistories`

- Row count: **554**
- Primary key: `id`
- Columns (10): id (uuid NOT NULL), datetime (timestamp without time zone), cost (double precision NOT NULL), productid (uuid NOT NULL), companyid (uuid NOT NULL), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone), issecondary (boolean NOT NULL)
- Key foreign keys:
  - `fk_productpricehistories_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_productpricehistories_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_productpricehistories_companies_companyid`: (companyid) -> `dbo.companies` (id)
  - `fk_productpricehistories_products_productid`: (productid) -> `dbo.products` (id)

### `dbo.productpricelistitems`

- Row count: **0**
- Primary key: `id`
- Columns (26): id (uuid NOT NULL), productid (uuid), categid (uuid), appliedon (text), minquantity (integer NOT NULL), sequence (integer NOT NULL), base (text), pricelistid (uuid), pricesurcharge (numeric(18,2)), pricediscount (numeric(18,2)), priceround (numeric(18,2)), priceminmargin (numeric(18,2)), pricemaxmargin (numeric(18,2)), datestart (timestamp without time zone), dateend (timestamp without time zone), computeprice (text), fixedprice (numeric(18,2)), percentprice (numeric(18,2)), fixedamountprice (numeric(18,2)), companyid (uuid), partnercategid (uuid), cardtypeid (uuid), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_productpricelistitems_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_productpricelistitems_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_productpricelistitems_cardtypes_cardtypeid`: (cardtypeid) -> `dbo.cardtypes` (id)
  - `fk_productpricelistitems_companies_companyid`: (companyid) -> `dbo.companies` (id)
  - `fk_productpricelistitems_partnercategories_partnercategid`: (partnercategid) -> `dbo.partnercategories` (id)
  - `fk_productpricelistitems_productcategories_categid`: (categid) -> `dbo.productcategories` (id)
  - `fk_productpricelistitems_productpricelists_pricelistid`: (pricelistid) -> `dbo.productpricelists` (id)
  - `fk_productpricelistitems_products_productid`: (productid) -> `dbo.products` (id)

### `dbo.productpricelists`

- Row count: **1**
- Primary key: `id`
- Columns (16): id (uuid NOT NULL), name (text NOT NULL), active (boolean NOT NULL), sequence (integer NOT NULL), companyid (uuid), datestart (timestamp without time zone), dateend (timestamp without time zone), partnercategid (uuid), cardtypeid (uuid), discountpolicy (text), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone), type (text), hidden (boolean NOT NULL)
- Key foreign keys:
  - `fk_productpricelists_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_productpricelists_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_productpricelists_cardtypes_cardtypeid`: (cardtypeid) -> `dbo.cardtypes` (id)
  - `fk_productpricelists_companies_companyid`: (companyid) -> `dbo.companies` (id)
  - `fk_productpricelists_partnercategories_partnercategid`: (partnercategid) -> `dbo.partnercategories` (id)

### `dbo.productrequestlines`

- Row count: **0**
- Primary key: `id`
- Columns (11): id (uuid NOT NULL), productid (uuid), productuomid (uuid), requestid (uuid NOT NULL), saleorderlineid (uuid), productqty (numeric(18,2) NOT NULL), sequence (integer NOT NULL), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_productrequestlines_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_productrequestlines_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_productrequestlines_productrequests_requestid`: (requestid) -> `dbo.productrequests` (id)
  - `fk_productrequestlines_products_productid`: (productid) -> `dbo.products` (id)
  - `fk_productrequestlines_saleorderlines_saleorderlineid`: (saleorderlineid) -> `dbo.saleorderlines` (id)
  - `fk_productrequestlines_uoms_productuomid`: (productuomid) -> `dbo.uoms` (id)

### `dbo.productrequests`

- Row count: **0**
- Primary key: `id`
- Columns (13): id (uuid NOT NULL), name (text), userid (text), date (timestamp without time zone NOT NULL), employeeid (uuid), pickingid (uuid), state (text), saleorderid (uuid), companyid (uuid), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_productrequests_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_productrequests_aspnetusers_userid`: (userid) -> `dbo.aspnetusers` (id)
  - `fk_productrequests_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_productrequests_companies_companyid`: (companyid) -> `dbo.companies` (id)
  - `fk_productrequests_employees_employeeid`: (employeeid) -> `dbo.employees` (id)
  - `fk_productrequests_saleorders_saleorderid`: (saleorderid) -> `dbo.saleorders` (id)
  - `fk_productrequests_stockpickings_pickingid`: (pickingid) -> `dbo.stockpickings` (id)

### `dbo.products`

- Row count: **443**
- Primary key: `id`
- Columns (38): id (uuid NOT NULL), name (text NOT NULL), namenosign (text), categid (uuid), listprice (numeric(18,2) NOT NULL), saleok (boolean NOT NULL), ketoaok (boolean NOT NULL), active (boolean NOT NULL), uompoid (uuid NOT NULL), uomid (uuid NOT NULL), type (text), purchaseok (boolean NOT NULL), description (text), ketoanote (text), companyid (uuid), defaultcode (text), nameget (text), islabo (boolean NOT NULL), type2 (text), purchaseprice (numeric(18,2)), laboprice (numeric(18,2)), firm (text), mininventory (numeric(18,2)), origin (text), expiry (numeric(18,2)), uomname (text), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone), pharmacycode (text), activeelement (text), declaredprice (numeric(18,2)), dosageform (text), drugadministration (text), importer (text), saleprice (numeric(18,2)), taxid (uuid)
- Key foreign keys:
  - `fk_products_accounttaxes_taxid`: (taxid) -> `dbo.accounttaxes` (id)
  - `fk_products_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_products_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_products_companies_companyid`: (companyid) -> `dbo.companies` (id)
  - `fk_products_productcategories_categid`: (categid) -> `dbo.productcategories` (id)

### `dbo.productsteps`

- Row count: **14**
- Primary key: `id`
- Columns (13): id (uuid NOT NULL), name (text NOT NULL), order (integer NOT NULL), note (text), productid (uuid), active (boolean NOT NULL), default (boolean NOT NULL), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone), defaultrequiredexecutioncount (integer), defaultrevenuepercentconfig (double precision)
- Key foreign keys:
  - `fk_productsteps_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_productsteps_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_productsteps_products_productid`: (productid) -> `dbo.products` (id)

### `dbo.productstockinventorycriteriarels`

- Row count: **0**
- Primary key: `productid, stockinventorycriteriaid`
- Columns (2): productid (uuid NOT NULL), stockinventorycriteriaid (uuid NOT NULL)
- Key foreign keys:
  - `fk_productstockinventorycriteriarels_products_productid`: (productid) -> `dbo.products` (id)
  - `fk_productstockinventorycriteriarels_stockinventorycriterias_st`: (stockinventorycriteriaid) -> `dbo.stockinventorycriterias` (id)

### `dbo.productuomlines`

- Row count: **3**
- Primary key: `id`
- Columns (13): id (uuid NOT NULL), productid (uuid NOT NULL), uomid (uuid NOT NULL), uomname (text), uomtype (text), active (boolean NOT NULL), isdefault (boolean NOT NULL), amountofconversion (double precision NOT NULL), sequence (integer), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_productuomlines_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_productuomlines_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_productuomlines_products_productid`: (productid) -> `dbo.products` (id)
  - `fk_productuomlines_uoms_uomid`: (uomid) -> `dbo.uoms` (id)

### `dbo.productuomrels`

- Row count: **216**
- Primary key: `uomid, productid`
- Columns (2): productid (uuid NOT NULL), uomid (uuid NOT NULL)
- Key foreign keys:
  - `fk_productuomrels_products_productid`: (productid) -> `dbo.products` (id)

### `dbo.promotionprogramcompanyrels`

- Row count: **0**
- Primary key: `promotionprogramid, companyid`
- Columns (2): promotionprogramid (uuid NOT NULL), companyid (uuid NOT NULL)
- Key foreign keys:
  - `fk_promotionprogramcompanyrels_companies_companyid`: (companyid) -> `dbo.companies` (id)
  - `fk_promotionprogramcompanyrels_promotionprograms_promotionprogr`: (promotionprogramid) -> `dbo.promotionprograms` (id)

### `dbo.promotionprograms`

- Row count: **0**
- Primary key: `id`
- Columns (10): id (uuid NOT NULL), name (text NOT NULL), active (boolean NOT NULL), datefrom (timestamp without time zone), dateto (timestamp without time zone), maximumusenumber (integer), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_promotionprograms_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_promotionprograms_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)

### `dbo.promotionruleproductcategoryrels`

- Row count: **0**
- Primary key: `ruleid, categid`
- Columns (3): ruleid (uuid NOT NULL), categid (uuid NOT NULL), discountlineproductid (uuid)
- Key foreign keys:
  - `fk_promotionruleproductcategoryrels_productcategories_categid`: (categid) -> `dbo.productcategories` (id)
  - `fk_promotionruleproductcategoryrels_products_discountlineproduc`: (discountlineproductid) -> `dbo.products` (id)
  - `fk_promotionruleproductcategoryrels_promotionrules_ruleid`: (ruleid) -> `dbo.promotionrules` (id)

### `dbo.promotionruleproductrels`

- Row count: **0**
- Primary key: `ruleid, productid`
- Columns (3): ruleid (uuid NOT NULL), productid (uuid NOT NULL), discountlineproductid (uuid)
- Key foreign keys:
  - `fk_promotionruleproductrels_products_discountlineproductid`: (discountlineproductid) -> `dbo.products` (id)
  - `fk_promotionruleproductrels_products_productid`: (productid) -> `dbo.products` (id)
  - `fk_promotionruleproductrels_promotionrules_ruleid`: (ruleid) -> `dbo.promotionrules` (id)

### `dbo.promotionrules`

- Row count: **0**
- Primary key: `id`
- Columns (12): id (uuid NOT NULL), programid (uuid NOT NULL), minquantity (numeric(18,2)), discounttype (text), discountpercentage (numeric(18,2)), discountfixedamount (numeric(18,2)), discountapplyon (text), discountlineproductid (uuid), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_promotionrules_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_promotionrules_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_promotionrules_products_discountlineproductid`: (discountlineproductid) -> `dbo.products` (id)
  - `fk_promotionrules_promotionprograms_programid`: (programid) -> `dbo.promotionprograms` (id)

### `dbo.purchaseorderlines`

- Row count: **0**
- Primary key: `id`
- Columns (22): id (uuid NOT NULL), name (text), sequence (integer), productqty (numeric(18,2) NOT NULL), productuomqty (numeric(18,2)), productuomid (uuid), productid (uuid), pricesubtotal (numeric(18,2)), pricetotal (numeric(18,2)), pricetax (numeric(18,2)), partnerid (uuid), priceunit (numeric(18,2) NOT NULL), orderid (uuid NOT NULL), state (text), dateplanned (timestamp without time zone), discount (numeric(18,2)), companyid (uuid), qtyinvoiced (numeric(18,2)), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_purchaseorderlines_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_purchaseorderlines_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_purchaseorderlines_companies_companyid`: (companyid) -> `dbo.companies` (id)
  - `fk_purchaseorderlines_partners_partnerid`: (partnerid) -> `dbo.partners` (id)
  - `fk_purchaseorderlines_products_productid`: (productid) -> `dbo.products` (id)
  - `fk_purchaseorderlines_purchaseorders_orderid`: (orderid) -> `dbo.purchaseorders` (id)
  - `fk_purchaseorderlines_uoms_productuomid`: (productuomid) -> `dbo.uoms` (id)

### `dbo.purchaseorders`

- Row count: **0**
- Primary key: `id`
- Columns (27): id (uuid NOT NULL), name (text NOT NULL), partnerref (text), partnerid (uuid NOT NULL), dateorder (timestamp without time zone NOT NULL), dateapprove (timestamp without time zone), pickingtypeid (uuid NOT NULL), pickingid (uuid), amountpayment (numeric(18,2)), journalid (uuid), amounttotal (numeric(18,2)), amountresidual (numeric(18,2)), amountuntaxed (numeric(18,2)), amounttax (numeric(18,2)), origin (text), dateplanned (timestamp without time zone), notes (text), companyid (uuid NOT NULL), invoicestatus (text), userid (text), type (text), state (text), refundorderid (uuid), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_purchaseorders_accountjournals_journalid`: (journalid) -> `dbo.accountjournals` (id)
  - `fk_purchaseorders_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_purchaseorders_aspnetusers_userid`: (userid) -> `dbo.aspnetusers` (id)
  - `fk_purchaseorders_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_purchaseorders_companies_companyid`: (companyid) -> `dbo.companies` (id)
  - `fk_purchaseorders_partners_partnerid`: (partnerid) -> `dbo.partners` (id)
  - `fk_purchaseorders_purchaseorders_refundorderid`: (refundorderid) -> `dbo.purchaseorders` (id)
  - `fk_purchaseorders_stockpickings_pickingid`: (pickingid) -> `dbo.stockpickings` (id)
  - ... and 1 more

### `dbo.quotationlines`

- Row count: **649**
- Primary key: `id`
- Columns (32): id (uuid NOT NULL), name (text), productid (uuid), qty (integer NOT NULL), discountamountpercent (numeric(18,2)), discountamountfixed (numeric(18,2)), discounttype (text), amount (numeric(18,2)), subprice (numeric(18,2)), amountdiscounttotal (double precision), diagnostic (text), productuomid (uuid), toothcategoryid (uuid), quotationid (uuid NOT NULL), employeeid (uuid), assistantid (uuid), counselorid (uuid), advisoryid (uuid), toothtype (text), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone), toothprocedureid (uuid), amountdiscount (double precision NOT NULL), isglobaldiscount (boolean NOT NULL), isrewardline (boolean NOT NULL), toothrange (text), toothtypefilter (integer NOT NULL), promotionprogramid (uuid), sequence (integer), discountamountfixed2 (numeric(18,2))
- Key foreign keys:
  - `fk_quotationlines_advisory_advisoryid`: (advisoryid) -> `dbo.advisory` (id)
  - `fk_quotationlines_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_quotationlines_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_quotationlines_employees_assistantid`: (assistantid) -> `dbo.employees` (id)
  - `fk_quotationlines_employees_counselorid`: (counselorid) -> `dbo.employees` (id)
  - `fk_quotationlines_employees_employeeid`: (employeeid) -> `dbo.employees` (id)
  - `fk_quotationlines_products_productid`: (productid) -> `dbo.products` (id)
  - `fk_quotationlines_quotations_quotationid`: (quotationid) -> `dbo.quotations` (id)
  - ... and 4 more

### `dbo.quotationlinetoothrels`

- Row count: **0**
- Primary key: `quotationlineid, toothid`
- Columns (2): quotationlineid (uuid NOT NULL), toothid (uuid NOT NULL)
- Key foreign keys:
  - `fk_quotationlinetoothrels_quotationlines_quotationlineid`: (quotationlineid) -> `dbo.quotationlines` (id)
  - `fk_quotationlinetoothrels_teeth_toothid`: (toothid) -> `dbo.teeth` (id)

### `dbo.quotationpromotionlines`

- Row count: **0**
- Primary key: `id`
- Columns (17): id (uuid NOT NULL), quotationlineid (uuid NOT NULL), promotionid (uuid), priceunit (double precision NOT NULL), amount (numeric(18,2) NOT NULL), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone), cardcardid (uuid), discountfixed (numeric(18,2)), discountpercent (numeric(18,2)), discounttype (text), name (text), salecouponprogramid (uuid), servicecardcardid (uuid), type (text)
- Key foreign keys:
  - `fk_quotationpromotionlines_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_quotationpromotionlines_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_quotationpromotionlines_cardcards_cardcardid`: (cardcardid) -> `dbo.cardcards` (id)
  - `fk_quotationpromotionlines_quotationlines_quotationlineid`: (quotationlineid) -> `dbo.quotationlines` (id)
  - `fk_quotationpromotionlines_quotationpromotions_promotionid`: (promotionid) -> `dbo.quotationpromotions` (id)
  - `fk_quotationpromotionlines_salecouponprograms_salecouponprogram`: (salecouponprogramid) -> `dbo.salecouponprograms` (id)
  - `fk_quotationpromotionlines_servicecardcards_servicecardcardid`: (servicecardcardid) -> `dbo.servicecardcards` (id)

### `dbo.quotationpromotions`

- Row count: **0**
- Primary key: `id`
- Columns (16): id (uuid NOT NULL), name (text), amount (numeric(18,2) NOT NULL), quotationid (uuid), quotationlineid (uuid), discounttype (text), discountpercent (numeric(18,2)), discountfixed (numeric(18,2)), salecouponprogramid (uuid), type (text), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone), cardcardid (uuid), servicecardcardid (uuid)
- Key foreign keys:
  - `fk_quotationpromotions_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_quotationpromotions_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_quotationpromotions_cardcards_cardcardid`: (cardcardid) -> `dbo.cardcards` (id)
  - `fk_quotationpromotions_quotationlines_quotationlineid`: (quotationlineid) -> `dbo.quotationlines` (id)
  - `fk_quotationpromotions_quotations_quotationid`: (quotationid) -> `dbo.quotations` (id)
  - `fk_quotationpromotions_salecouponprograms_salecouponprogramid`: (salecouponprogramid) -> `dbo.salecouponprograms` (id)
  - `fk_quotationpromotions_servicecardcards_servicecardcardid`: (servicecardcardid) -> `dbo.servicecardcards` (id)

### `dbo.quotations`

- Row count: **75**
- Primary key: `id`
- Columns (22): id (uuid NOT NULL), name (text), partnerid (uuid NOT NULL), employeeid (uuid), datequotation (timestamp without time zone NOT NULL), dateapplies (integer NOT NULL), dateendquotation (timestamp without time zone), note (text), totalamount (numeric(18,2)), state (text), companyid (uuid NOT NULL), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone), saleorderid (uuid), discountamountfixed (numeric(18,2)), discountamountpercent (numeric(18,2)), discounttype (text), userid (text), pricelistid (uuid), validstate (text NOT NULL)
- Key foreign keys:
  - `fk_quotations_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_quotations_aspnetusers_userid`: (userid) -> `dbo.aspnetusers` (id)
  - `fk_quotations_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_quotations_companies_companyid`: (companyid) -> `dbo.companies` (id)
  - `fk_quotations_employees_employeeid`: (employeeid) -> `dbo.employees` (id)
  - `fk_quotations_partners_partnerid`: (partnerid) -> `dbo.partners` (id)
  - `fk_quotations_productpricelists_pricelistid`: (pricelistid) -> `dbo.productpricelists` (id)
  - `fk_quotations_saleorders_saleorderid`: (saleorderid) -> `dbo.saleorders` (id)

### `dbo.ratingratings`

- Row count: **0**
- Primary key: `id`
- Columns (13): id (uuid NOT NULL), rating (double precision NOT NULL), feedback (text), ratingtext (text), createdate (timestamp without time zone), messageid (uuid), resmodel (text), resid (uuid), partnerid (uuid), datecreated (timestamp without time zone), createdbyid (text), lastupdated (timestamp without time zone), writebyid (text)
- Key foreign keys:
  - `fk_ratingratings_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_ratingratings_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_ratingratings_mailmessages_messageid`: (messageid) -> `dbo.mailmessages` (id)
  - `fk_ratingratings_partners_partnerid`: (partnerid) -> `dbo.partners` (id)

### `dbo.reportviewingconfigs`

- Row count: **0**
- Primary key: `id`
- Columns (10): id (uuid NOT NULL), roleid (text), reportcode (text), limitedquantity (integer NOT NULL), limitedtype (text), customtype (text), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_reportviewingconfigs_aspnetroles_roleid`: (roleid) -> `dbo.aspnetroles` (id)
  - `fk_reportviewingconfigs_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_reportviewingconfigs_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)

### `dbo.resbanks`

- Row count: **53**
- Primary key: `id`
- Columns (8): id (uuid NOT NULL), name (text NOT NULL), active (boolean NOT NULL), bic (text), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_resbanks_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_resbanks_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)

### `dbo.rescompanyusersrels`

- Row count: **384**
- Primary key: `companyid, userid`
- Columns (2): companyid (uuid NOT NULL), userid (text NOT NULL)
- Key foreign keys:
  - `fk_rescompanyusersrels_aspnetusers_userid`: (userid) -> `dbo.aspnetusers` (id)
  - `fk_rescompanyusersrels_companies_companyid`: (companyid) -> `dbo.companies` (id)

### `dbo.resconfigsettings`

- Row count: **5**
- Primary key: `id`
- Columns (28): id (uuid NOT NULL), companyid (uuid NOT NULL), groupdiscountpersoline (boolean), groupsalecouponpromotion (boolean), groupuom (boolean), grouployaltycard (boolean), loyaltypointexchangerate (numeric(18,2)), groupmulticompany (boolean), companyshareproduct (boolean), companysharepartner (boolean), productlistpricerestrictcompany (boolean), groupservicecard (boolean), grouptcare (boolean), tcarerunat (timestamp without time zone), groupmedicine (boolean), groupsms (boolean), groupsurvey (boolean), groupinsurance (boolean), grouponlinesurvey (boolean), notallowexportinventorynegative (boolean NOT NULL), allowcalendaralarm (boolean NOT NULL), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone), groupheadoffice (boolean), groupmulticurrency (boolean), groupsalerefund (boolean NOT NULL)
- Key foreign keys:
  - `fk_resconfigsettings_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_resconfigsettings_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_resconfigsettings_companies_companyid`: (companyid) -> `dbo.companies` (id)

### `dbo.resgroupimpliedrels`

- Row count: **16**
- Primary key: `gid, hid`
- Columns (2): gid (uuid NOT NULL), hid (uuid NOT NULL)
- Key foreign keys:
  - `fk_resgroupimpliedrels_resgroups_gid`: (gid) -> `dbo.resgroups` (id)
  - `fk_resgroupimpliedrels_resgroups_hid`: (hid) -> `dbo.resgroups` (id)

### `dbo.resgroups`

- Row count: **35**
- Primary key: `id`
- Columns (8): id (uuid NOT NULL), name (text NOT NULL), categoryid (uuid), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone), comment (text)
- Key foreign keys:
  - `fk_resgroups_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_resgroups_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_resgroups_irmodulecategories_categoryid`: (categoryid) -> `dbo.irmodulecategories` (id)

### `dbo.resgroupsusersrels`

- Row count: **1032**
- Primary key: `groupid, userid`
- Columns (2): groupid (uuid NOT NULL), userid (text NOT NULL)
- Key foreign keys:
  - `fk_resgroupsusersrels_aspnetusers_userid`: (userid) -> `dbo.aspnetusers` (id)
  - `fk_resgroupsusersrels_resgroups_groupid`: (groupid) -> `dbo.resgroups` (id)

### `dbo.resinsurancepaymentlines`

- Row count: **0**
- Primary key: `id`
- Columns (10): id (uuid NOT NULL), saleorderlineid (uuid NOT NULL), resinsurancepaymentid (uuid NOT NULL), paytype (text), percent (numeric(18,2)), fixedamount (numeric(18,2)), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_resinsurancepaymentlines_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_resinsurancepaymentlines_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_resinsurancepaymentlines_resinsurancepayments_resinsurancepa`: (resinsurancepaymentid) -> `dbo.resinsurancepayments` (id)
  - `fk_resinsurancepaymentlines_saleorderlines_saleorderlineid`: (saleorderlineid) -> `dbo.saleorderlines` (id)

### `dbo.resinsurancepayments`

- Row count: **0**
- Primary key: `id`
- Columns (13): id (uuid NOT NULL), amount (numeric(18,2) NOT NULL), date (timestamp without time zone NOT NULL), orderid (uuid), resinsuranceid (uuid), saleorderpaymentid (uuid), companyid (uuid NOT NULL), note (text), state (text), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_resinsurancepayments_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_resinsurancepayments_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_resinsurancepayments_companies_companyid`: (companyid) -> `dbo.companies` (id)
  - `fk_resinsurancepayments_resinsurances_resinsuranceid`: (resinsuranceid) -> `dbo.resinsurances` (id)
  - `fk_resinsurancepayments_saleorderpayments_saleorderpaymentid`: (saleorderpaymentid) -> `dbo.saleorderpayments` (id)
  - `fk_resinsurancepayments_saleorders_orderid`: (orderid) -> `dbo.saleorders` (id)

### `dbo.resinsurances`

- Row count: **0**
- Primary key: `id`
- Columns (16): id (uuid NOT NULL), name (text), date (timestamp without time zone), avatar (text), representative (text), phone (text), email (text), address (text), note (text), companyid (uuid), partnerid (uuid), isactive (boolean NOT NULL), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_resinsurances_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_resinsurances_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_resinsurances_companies_companyid`: (companyid) -> `dbo.companies` (id)
  - `fk_resinsurances_partners_partnerid`: (partnerid) -> `dbo.partners` (id)

### `dbo.resourcecalendarattendances`

- Row count: **0**
- Primary key: `id`
- Columns (14): id (uuid NOT NULL), name (text NOT NULL), dayofweek (text NOT NULL), datefrom (timestamp without time zone), dateto (timestamp without time zone), sequence (integer NOT NULL), hourfrom (double precision NOT NULL), hourto (double precision NOT NULL), calendarid (uuid NOT NULL), dayperiod (text NOT NULL), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_resourcecalendarattendances_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_resourcecalendarattendances_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_resourcecalendarattendances_resourcecalendars_calendarid`: (calendarid) -> `dbo.resourcecalendars` (id)

### `dbo.resourcecalendarleaves`

- Row count: **0**
- Primary key: `id`
- Columns (10): id (uuid NOT NULL), name (text), companyid (uuid), calendarid (uuid), datefrom (timestamp without time zone NOT NULL), dateto (timestamp without time zone NOT NULL), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_resourcecalendarleaves_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_resourcecalendarleaves_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_resourcecalendarleaves_companies_companyid`: (companyid) -> `dbo.companies` (id)
  - `fk_resourcecalendarleaves_resourcecalendars_calendarid`: (calendarid) -> `dbo.resourcecalendars` (id)

### `dbo.resourcecalendars`

- Row count: **0**
- Primary key: `id`
- Columns (8): id (uuid NOT NULL), name (text NOT NULL), companyid (uuid), hoursperday (numeric(18,2)), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_resourcecalendars_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_resourcecalendars_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_resourcecalendars_companies_companyid`: (companyid) -> `dbo.companies` (id)

### `dbo.respartnerbanks`

- Row count: **0**
- Primary key: `id`
- Columns (13): id (uuid NOT NULL), accountholdername (text), accountnumber (text NOT NULL), partnerid (uuid NOT NULL), bankid (uuid NOT NULL), sequence (integer NOT NULL), companyid (uuid), branch (text), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone), active (boolean NOT NULL)
- Key foreign keys:
  - `fk_respartnerbanks_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_respartnerbanks_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_respartnerbanks_companies_companyid`: (companyid) -> `dbo.companies` (id)
  - `fk_respartnerbanks_partners_partnerid`: (partnerid) -> `dbo.partners` (id)
  - `fk_respartnerbanks_resbanks_bankid`: (bankid) -> `dbo.resbanks` (id)

### `dbo.rewardproductrels`

- Row count: **0**
- Primary key: `programrewardid, productid`
- Columns (2): programrewardid (uuid NOT NULL), productid (uuid NOT NULL)
- Key foreign keys:
  - `fk_rewardproductrels_products_productid`: (productid) -> `dbo.products` (id)
  - `fk_rewardproductrels_salecouponprogramrewards_programrewardid`: (programrewardid) -> `dbo.salecouponprogramrewards` (id)

### `dbo.routinglines`

- Row count: **0**
- Primary key: `id`
- Columns (10): id (uuid NOT NULL), routingid (uuid NOT NULL), name (text), productid (uuid), sequence (integer NOT NULL), note (text), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_routinglines_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_routinglines_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_routinglines_products_productid`: (productid) -> `dbo.products` (id)
  - `fk_routinglines_routings_routingid`: (routingid) -> `dbo.routings` (id)

### `dbo.routings`

- Row count: **0**
- Primary key: `id`
- Columns (7): id (uuid NOT NULL), name (text), productid (uuid NOT NULL), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_routings_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_routings_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_routings_products_productid`: (productid) -> `dbo.products` (id)

### `dbo.rulegrouprels`

- Row count: **0**
- Primary key: `ruleid, groupid`
- Columns (2): ruleid (uuid NOT NULL), groupid (uuid NOT NULL)
- Key foreign keys:
  - `fk_rulegrouprels_irrules_ruleid`: (ruleid) -> `dbo.irrules` (id)
  - `fk_rulegrouprels_resgroups_groupid`: (groupid) -> `dbo.resgroups` (id)

### `dbo.salarypayments`

- Row count: **0**
- Primary key: `id`
- Columns (16): id (uuid NOT NULL), companyid (uuid), date (timestamp without time zone NOT NULL), journalid (uuid NOT NULL), state (text), name (text), type (text), amount (numeric(18,2) NOT NULL), employeeid (uuid), reason (text), moveid (uuid), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone), destinationaccountid (uuid)
- Key foreign keys:
  - `fk_salarypayments_accountaccounts_destinationaccountid`: (destinationaccountid) -> `dbo.accountaccounts` (id)
  - `fk_salarypayments_accountjournals_journalid`: (journalid) -> `dbo.accountjournals` (id)
  - `fk_salarypayments_accountmoves_moveid`: (moveid) -> `dbo.accountmoves` (id)
  - `fk_salarypayments_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_salarypayments_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_salarypayments_companies_companyid`: (companyid) -> `dbo.companies` (id)
  - `fk_salarypayments_employees_employeeid`: (employeeid) -> `dbo.employees` (id)

### `dbo.salecouponhistories`

- Row count: **0**
- Primary key: `id`
- Columns (11): id (uuid NOT NULL), cardid (uuid), description (text NOT NULL), issued (numeric(18,2) NOT NULL), used (numeric(18,2) NOT NULL), saleorderid (uuid), datecreated (timestamp without time zone), createdbyid (text), lastupdated (timestamp without time zone), writebyid (text), salecouponprogramid (uuid)
- Key foreign keys:
  - `fk_salecouponhistories_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_salecouponhistories_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_salecouponhistories_salecouponprograms_salecouponprogramid`: (salecouponprogramid) -> `dbo.salecouponprograms` (id)
  - `fk_salecouponhistories_salecoupons_cardid`: (cardid) -> `dbo.salecoupons` (id)
  - `fk_salecouponhistories_saleorders_saleorderid`: (saleorderid) -> `dbo.saleorders` (id)

### `dbo.salecouponprogramcardtyperels`

- Row count: **0**
- Primary key: `programid, cardtypeid`
- Columns (2): programid (uuid NOT NULL), cardtypeid (uuid NOT NULL)
- Key foreign keys:
  - `fk_salecouponprogramcardtyperels_cardtypes_cardtypeid`: (cardtypeid) -> `dbo.cardtypes` (id)
  - `fk_salecouponprogramcardtyperels_salecouponprograms_programid`: (programid) -> `dbo.salecouponprograms` (id)

### `dbo.salecouponprogramcompanyapplieds`

- Row count: **0**
- Primary key: `programid, companyid`
- Columns (2): programid (uuid NOT NULL), companyid (uuid NOT NULL)
- Key foreign keys:
  - `fk_salecouponprogramcompanyapplieds_companies_companyid`: (companyid) -> `dbo.companies` (id)
  - `fk_salecouponprogramcompanyapplieds_salecouponprograms_programi`: (programid) -> `dbo.salecouponprograms` (id)

### `dbo.salecouponprogrammemberlevelrels`

- Row count: **0**
- Primary key: `programid, memberlevelid`
- Columns (2): programid (uuid NOT NULL), memberlevelid (uuid NOT NULL)
- Key foreign keys:
  - `fk_salecouponprogrammemberlevelrels_memberlevels_memberlevelid`: (memberlevelid) -> `dbo.memberlevels` (id)
  - `fk_salecouponprogrammemberlevelrels_salecouponprograms_programi`: (programid) -> `dbo.salecouponprograms` (id)

### `dbo.salecouponprogrampartnerrels`

- Row count: **0**
- Primary key: `programid, partnerid`
- Columns (2): programid (uuid NOT NULL), partnerid (uuid NOT NULL)
- Key foreign keys:
  - `fk_salecouponprogrampartnerrels_partners_partnerid`: (partnerid) -> `dbo.partners` (id)
  - `fk_salecouponprogrampartnerrels_salecouponprograms_programid`: (programid) -> `dbo.salecouponprograms` (id)

### `dbo.salecouponprogramproductcategoryrels`

- Row count: **0**
- Primary key: `programid, productcategoryid`
- Columns (2): programid (uuid NOT NULL), productcategoryid (uuid NOT NULL)
- Key foreign keys:
  - `fk_salecouponprogramproductcategoryrels_productcategories_produ`: (productcategoryid) -> `dbo.productcategories` (id)
  - `fk_salecouponprogramproductcategoryrels_salecouponprograms_prog`: (programid) -> `dbo.salecouponprograms` (id)

### `dbo.salecouponprogramproductrels`

- Row count: **0**
- Primary key: `programid, productid`
- Columns (2): programid (uuid NOT NULL), productid (uuid NOT NULL)
- Key foreign keys:
  - `fk_salecouponprogramproductrels_products_productid`: (productid) -> `dbo.products` (id)
  - `fk_salecouponprogramproductrels_salecouponprograms_programid`: (programid) -> `dbo.salecouponprograms` (id)

### `dbo.salecouponprogramrewardproductcategoryrels`

- Row count: **0**
- Primary key: `programrewardid, productcategoryid`
- Columns (2): programrewardid (uuid NOT NULL), productcategoryid (uuid NOT NULL)
- Key foreign keys:
  - `fk_salecouponprogramrewardproductcategoryrels_productcategories`: (productcategoryid) -> `dbo.productcategories` (id)
  - `fk_salecouponprogramrewardproductcategoryrels_salecouponprogram`: (programrewardid) -> `dbo.salecouponprogramrewards` (id)

### `dbo.salecouponprogramrewardproductrels`

- Row count: **0**
- Primary key: `programrewardid, productid`
- Columns (2): programrewardid (uuid NOT NULL), productid (uuid NOT NULL)
- Key foreign keys:
  - `fk_salecouponprogramrewardproductrels_products_productid`: (productid) -> `dbo.products` (id)
  - `fk_salecouponprogramrewardproductrels_salecouponprogramrewards_`: (programrewardid) -> `dbo.salecouponprogramrewards` (id)

### `dbo.salecouponprogramrewards`

- Row count: **0**
- Primary key: `id`
- Columns (16): id (uuid NOT NULL), programid (uuid NOT NULL), active (boolean), rewardtype (text), description (text), discountmode (text), discount (double precision), isapplymaxdiscount (boolean NOT NULL), discountmaxamount (numeric(18,2)), requiredpoints (double precision), discountlineproductid (uuid), rewardproductqty (integer), datecreated (timestamp without time zone), createdbyid (text), lastupdated (timestamp without time zone), writebyid (text)
- Key foreign keys:
  - `fk_salecouponprogramrewards_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_salecouponprogramrewards_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_salecouponprogramrewards_products_discountlineproductid`: (discountlineproductid) -> `dbo.products` (id)
  - `fk_salecouponprogramrewards_salecouponprograms_programid`: (programid) -> `dbo.salecouponprograms` (id)

### `dbo.salecouponprogramrulecardtyperels`

- Row count: **0**
- Primary key: `programruleid, cardtypeid`
- Columns (2): programruleid (uuid NOT NULL), cardtypeid (uuid NOT NULL)
- Key foreign keys:
  - `fk_salecouponprogramrulecardtyperels_cardtypes_cardtypeid`: (cardtypeid) -> `dbo.cardtypes` (id)
  - `fk_salecouponprogramrulecardtyperels_salecouponprogramrules_pro`: (programruleid) -> `dbo.salecouponprogramrules` (id)

### `dbo.salecouponprogramrulepartnerrels`

- Row count: **0**
- Primary key: `programruleid, partnerid`
- Columns (2): partnerid (uuid NOT NULL), programruleid (uuid NOT NULL)
- Key foreign keys:
  - `fk_salecouponprogramrulepartnerrels_partners_partnerid`: (partnerid) -> `dbo.partners` (id)
  - `fk_salecouponprogramrulepartnerrels_salecouponprogramrules_prog`: (programruleid) -> `dbo.salecouponprogramrules` (id)

### `dbo.salecouponprogramruleproductrels`

- Row count: **0**
- Primary key: `programruleid, productid`
- Columns (2): programruleid (uuid NOT NULL), productid (uuid NOT NULL)
- Key foreign keys:
  - `fk_salecouponprogramruleproductrels_products_productid`: (productid) -> `dbo.products` (id)
  - `fk_salecouponprogramruleproductrels_salecouponprogramrules_prog`: (programruleid) -> `dbo.salecouponprogramrules` (id)

### `dbo.salecouponprogramrules`

- Row count: **0**
- Primary key: `id`
- Columns (13): id (uuid NOT NULL), programid (uuid NOT NULL), description (text), minimumqty (integer), isapplydayofweek (boolean NOT NULL), days (text), isapplyminimumdiscount (boolean NOT NULL), minimumamount (numeric(18,2)), ruletype (text), datecreated (timestamp without time zone), createdbyid (text), lastupdated (timestamp without time zone), writebyid (text)
- Key foreign keys:
  - `fk_salecouponprogramrules_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_salecouponprogramrules_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_salecouponprogramrules_salecouponprograms_programid`: (programid) -> `dbo.salecouponprograms` (id)

### `dbo.salecouponprograms`

- Row count: **0**
- Primary key: `id`
- Columns (42): id (uuid NOT NULL), name (text NOT NULL), active (boolean NOT NULL), ispaused (boolean NOT NULL), sequence (integer), maximumusenumber (integer), ruleminquantity (integer), companyid (uuid), discounttype (text), discountpercentage (numeric(18,2)), discountfixedamount (numeric(18,2)), discountlineproductid (uuid), validityduration (integer), notincremental (boolean), applypartneron (text), rewardtype (text), programtype (text), promocodeusage (text), promocode (text), promoapplicability (text), isapplyminimumdiscount (boolean NOT NULL), ruleminimumamount (numeric(18,2)), isapplymaxdiscount (boolean NOT NULL), discountmaxamount (numeric(18,2)), rewardproductid (uuid), rewardproductquantity (integer), ruledatefrom (timestamp without time zone), ruledateto (timestamp without time zone), rewarddescription (text), discountapplyon (text), isapplydayofweek (boolean NOT NULL), days (text), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone), discountlimitedbalance (numeric(18,2)), promocodegenerationtype (text), promocodetype (text), filebase64name (text), numberofcodesgenerate (integer), promocodeprefix (text)
- Key foreign keys:
  - `fk_salecouponprograms_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_salecouponprograms_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_salecouponprograms_companies_companyid`: (companyid) -> `dbo.companies` (id)
  - `fk_salecouponprograms_products_discountlineproductid`: (discountlineproductid) -> `dbo.products` (id)
  - `fk_salecouponprograms_products_rewardproductid`: (rewardproductid) -> `dbo.products` (id)

### `dbo.salecoupons`

- Row count: **0**
- Primary key: `id`
- Columns (14): id (uuid NOT NULL), code (text NOT NULL), programid (uuid), state (text), dateexpired (timestamp without time zone), saleorderid (uuid), partnerid (uuid), orderid (uuid), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone), balance (numeric(18,2)), initialamount (numeric(18,2))
- Key foreign keys:
  - `fk_salecoupons_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_salecoupons_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_salecoupons_partners_partnerid`: (partnerid) -> `dbo.partners` (id)
  - `fk_salecoupons_salecouponprograms_programid`: (programid) -> `dbo.salecouponprograms` (id)
  - `fk_salecoupons_saleorders_orderid`: (orderid) -> `dbo.saleorders` (id)
  - `fk_salecoupons_saleorders_saleorderid`: (saleorderid) -> `dbo.saleorders` (id)

### `dbo.saleorderlinecommissionhistories`

- Row count: **10214**
- Primary key: `id`
- Columns (12): id (uuid NOT NULL), date (timestamp without time zone), saleorderlineid (uuid), saleorderpaymentid (uuid), profitamount (numeric(18,2)), totalpayment (numeric(18,2)), costamount (numeric(18,2)), previousprofit (numeric(18,2)), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_saleorderlinecommissionhistories_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_saleorderlinecommissionhistories_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_saleorderlinecommissionhistories_saleorderlines_saleorderlin`: (saleorderlineid) -> `dbo.saleorderlines` (id)
  - `fk_saleorderlinecommissionhistories_saleorderpayments_saleorder`: (saleorderpaymentid) -> `dbo.saleorderpayments` (id)

### `dbo.saleorderlineinvoice2rels`

- Row count: **52941**
- Primary key: `orderlineid, invoicelineid`
- Columns (2): orderlineid (uuid NOT NULL), invoicelineid (uuid NOT NULL)
- Key foreign keys:
  - `fk_saleorderlineinvoice2rels_saleorderlines_orderlineid`: (orderlineid) -> `dbo.saleorderlines` (id)

### `dbo.saleorderlineinvoicerels`

- Row count: **0**
- Primary key: `orderlineid, invoicelineid`
- Columns (2): orderlineid (uuid NOT NULL), invoicelineid (uuid NOT NULL)
- Key foreign keys:
  - `fk_saleorderlineinvoicerels_accountinvoicelines_invoicelineid`: (invoicelineid) -> `dbo.accountinvoicelines` (id)
  - `fk_saleorderlineinvoicerels_saleorderlines_orderlineid`: (orderlineid) -> `dbo.saleorderlines` (id)

### `dbo.saleorderlinepartnercommissions`

- Row count: **0**
- Primary key: `id`
- Columns (8): id (uuid NOT NULL), employeeid (uuid), saleorderlineid (uuid NOT NULL), commissionid (uuid), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_saleorderlinepartnercommissions_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_saleorderlinepartnercommissions_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_saleorderlinepartnercommissions_commissions_commissionid`: (commissionid) -> `dbo.commissions` (id)
  - `fk_saleorderlinepartnercommissions_employees_employeeid`: (employeeid) -> `dbo.employees` (id)
  - `fk_saleorderlinepartnercommissions_saleorderlines_saleorderline`: (saleorderlineid) -> `dbo.saleorderlines` (id)

### `dbo.saleorderlinepaymentrels`

- Row count: **0**
- Primary key: `id`
- Columns (8): id (uuid NOT NULL), saleorderlineid (uuid NOT NULL), paymentid (uuid NOT NULL), amountprepaid (numeric(18,2)), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_saleorderlinepaymentrels_accountpayments_paymentid`: (paymentid) -> `dbo.accountpayments` (id)
  - `fk_saleorderlinepaymentrels_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_saleorderlinepaymentrels_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_saleorderlinepaymentrels_saleorderlines_saleorderlineid`: (saleorderlineid) -> `dbo.saleorderlines` (id)

### `dbo.saleorderlineproductrequesteds`

- Row count: **0**
- Primary key: `id`
- Columns (8): id (uuid NOT NULL), saleorderlineid (uuid NOT NULL), productid (uuid NOT NULL), requestedquantity (numeric(18,2) NOT NULL), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_saleorderlineproductrequesteds_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_saleorderlineproductrequesteds_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_saleorderlineproductrequesteds_products_productid`: (productid) -> `dbo.products` (id)
  - `fk_saleorderlineproductrequesteds_saleorderlines_saleorderlinei`: (saleorderlineid) -> `dbo.saleorderlines` (id)

### `dbo.saleorderlines`

- Row count: **58357**
- Primary key: `id`
- Columns (65): id (uuid NOT NULL), priceunit (numeric(18,2) NOT NULL), productuomqty (numeric(18,2) NOT NULL), productstandardprice (double precision), name (text NOT NULL), state (text), orderpartnerid (uuid), orderid (uuid NOT NULL), productuomid (uuid), discount (numeric(18,2) NOT NULL), productid (uuid), companyid (uuid), pricesubtotal (numeric(18,2) NOT NULL), pricetax (numeric(18,2) NOT NULL), pricetotal (numeric(18,2) NOT NULL), salesmanid (text), note (text), invoicestatus (text), qtytoinvoice (numeric(18,2)), qtyinvoiced (numeric(18,2)), amounttoinvoice (numeric(18,2)), amountinvoiced (numeric(18,2)), toothcategoryid (uuid), toothtype (text), diagnostic (text), sequence (integer), promotionprogramid (uuid), promotionid (uuid), couponid (uuid), isrewardline (boolean NOT NULL), discounttype (text), discountfixed (numeric(18,2)), pricereduce (numeric(18,2)), amountpaid (numeric(18,2)), amountresidual (numeric(18,2)), amountdiscounttotal (double precision), amountinsurancepaidtotal (numeric(18,2)), insuranceid (uuid), iscancelled (boolean NOT NULL), employeeid (uuid), assistantid (uuid), counselorid (uuid), advisoryid (uuid), isactive (boolean NOT NULL), date (timestamp without time zone), datedone (timestamp without time zone), agentid (uuid), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone), giftcardid (uuid), amountdiscount (double precision NOT NULL), quotationlineid (uuid), isdownpayment (boolean NOT NULL), toothrange (text), toothtypefilter (integer NOT NULL), isglobaldiscount (boolean NOT NULL), treatmentplan (text), lastserviceuserdate (timestamp without time zone), qtydelivered (double precision), taxid (uuid), discountfixedamount (numeric(18,2)), amounteinvoiced (numeric(18,2)), isdeleted (boolean NOT NULL)
- Key foreign keys:
  - `fk_saleorderlines_accounttaxes_taxid`: (taxid) -> `dbo.accounttaxes` (id)
  - `fk_saleorderlines_advisory_advisoryid`: (advisoryid) -> `dbo.advisory` (id)
  - `fk_saleorderlines_agents_agentid`: (agentid) -> `dbo.agents` (id)
  - `fk_saleorderlines_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_saleorderlines_aspnetusers_salesmanid`: (salesmanid) -> `dbo.aspnetusers` (id)
  - `fk_saleorderlines_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_saleorderlines_companies_companyid`: (companyid) -> `dbo.companies` (id)
  - `fk_saleorderlines_employees_assistantid`: (assistantid) -> `dbo.employees` (id)
  - ... and 13 more

### `dbo.saleorderlinesaleproductionrels`

- Row count: **0**
- Primary key: `orderlineid, saleproductionid`
- Columns (2): orderlineid (uuid NOT NULL), saleproductionid (uuid NOT NULL)
- Key foreign keys:
  - `fk_saleorderlinesaleproductionrels_saleorderlines_orderlineid`: (orderlineid) -> `dbo.saleorderlines` (id)
  - `fk_saleorderlinesaleproductionrels_saleproductions_saleproducti`: (saleproductionid) -> `dbo.saleproductions` (id)

### `dbo.saleorderlinetoothrels`

- Row count: **64**
- Primary key: `salelineid, toothid`
- Columns (2): salelineid (uuid NOT NULL), toothid (uuid NOT NULL)
- Key foreign keys:
  - `fk_saleorderlinetoothrels_saleorderlines_salelineid`: (salelineid) -> `dbo.saleorderlines` (id)
  - `fk_saleorderlinetoothrels_teeth_toothid`: (toothid) -> `dbo.teeth` (id)

### `dbo.saleordernocodepromoprograms`

- Row count: **0**
- Primary key: `orderid, programid`
- Columns (2): orderid (uuid NOT NULL), programid (uuid NOT NULL)
- Key foreign keys:
  - `fk_saleordernocodepromoprograms_salecouponprograms_programid`: (programid) -> `dbo.salecouponprograms` (id)
  - `fk_saleordernocodepromoprograms_saleorders_orderid`: (orderid) -> `dbo.saleorders` (id)

### `dbo.saleorderpaymentaccountmoverels`

- Row count: **49536**
- Primary key: `saleorderpaymentid, moveid`
- Columns (2): saleorderpaymentid (uuid NOT NULL), moveid (uuid NOT NULL)
- Key foreign keys:
  - `fk_saleorderpaymentaccountmoverels_accountmoves_moveid`: (moveid) -> `dbo.accountmoves` (id)
  - `fk_saleorderpaymentaccountmoverels_saleorderpayments_saleorderp`: (saleorderpaymentid) -> `dbo.saleorderpayments` (id)

### `dbo.saleorderpaymentaccountpaymentrels`

- Row count: **54144**
- Primary key: `saleorderpaymentid, paymentid`
- Columns (2): saleorderpaymentid (uuid NOT NULL), paymentid (uuid NOT NULL)
- Key foreign keys:
  - `fk_saleorderpaymentaccountpaymentrels_accountpayments_paymentid`: (paymentid) -> `dbo.accountpayments` (id)
  - `fk_saleorderpaymentaccountpaymentrels_saleorderpayments_saleord`: (saleorderpaymentid) -> `dbo.saleorderpayments` (id)

### `dbo.saleorderpaymenthistorylinedotkhamproductlinerels`

- Row count: **0**
- Primary key: `historylineid, dotkhamproductlineid`
- Columns (2): historylineid (uuid NOT NULL), dotkhamproductlineid (uuid NOT NULL)
- Key foreign keys:
  - `fk_saleorderpaymenthistorylinedotkhamproductlinerels_dotkhampro`: (dotkhamproductlineid) -> `dbo.dotkhamproductlines` (id)
  - `fk_saleorderpaymenthistorylinedotkhamproductlinerels_saleorderp`: (historylineid) -> `dbo.saleorderpaymenthistorylines` (id)

### `dbo.saleorderpaymenthistorylines`

- Row count: **52108**
- Primary key: `id`
- Columns (10): id (uuid NOT NULL), saleorderlineid (uuid), saleorderpaymentid (uuid NOT NULL), amount (numeric(18,2) NOT NULL), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone), type (text), name (text)
- Key foreign keys:
  - `fk_saleorderpaymenthistorylines_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_saleorderpaymenthistorylines_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_saleorderpaymenthistorylines_saleorderlines_saleorderlineid`: (saleorderlineid) -> `dbo.saleorderlines` (id)
  - `fk_saleorderpaymenthistorylines_saleorderpayments_saleorderpaym`: (saleorderpaymentid) -> `dbo.saleorderpayments` (id)

### `dbo.saleorderpaymentjournallineallocations`

- Row count: **0**
- Primary key: `id`
- Columns (8): id (uuid NOT NULL), lineid (uuid NOT NULL), type (text), amount (numeric(18,2) NOT NULL), datecreated (timestamp without time zone), createdbyid (text), lastupdated (timestamp without time zone), writebyid (text)
- Key foreign keys:
  - `fk_saleorderpaymentjournallineallocations_aspnetusers_createdby`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_saleorderpaymentjournallineallocations_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_saleorderpaymentjournallineallocations_saleorderpaymentjourn`: (lineid) -> `dbo.saleorderpaymentjournallines` (id)

### `dbo.saleorderpaymentjournallines`

- Row count: **54144**
- Primary key: `id`
- Columns (12): id (uuid NOT NULL), journalid (uuid NOT NULL), saleorderpaymentid (uuid NOT NULL), insuranceid (uuid), amount (numeric(18,2) NOT NULL), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone), currencyid (uuid), accountpaymentid (uuid), type (text)
- Key foreign keys:
  - `fk_saleorderpaymentjournallines_accountjournals_journalid`: (journalid) -> `dbo.accountjournals` (id)
  - `fk_saleorderpaymentjournallines_accountpayments_accountpaymenti`: (accountpaymentid) -> `dbo.accountpayments` (id)
  - `fk_saleorderpaymentjournallines_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_saleorderpaymentjournallines_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_saleorderpaymentjournallines_currencies_currencyid`: (currencyid) -> `dbo.currencies` (id)
  - `fk_saleorderpaymentjournallines_resinsurances_insuranceid`: (insuranceid) -> `dbo.resinsurances` (id)
  - `fk_saleorderpaymentjournallines_saleorderpayments_saleorderpaym`: (saleorderpaymentid) -> `dbo.saleorderpayments` (id)

### `dbo.saleorderpaymentoutstandings`

- Row count: **0**
- Primary key: `saleorderpaymentid, accountmovelineid`
- Columns (2): saleorderpaymentid (uuid NOT NULL), accountmovelineid (uuid NOT NULL)
- Key foreign keys:
  - `fk_saleorderpaymentoutstandings_accountmovelines_accountmovelin`: (accountmovelineid) -> `dbo.accountmovelines` (id)
  - `fk_saleorderpaymentoutstandings_saleorderpayments_saleorderpaym`: (saleorderpaymentid) -> `dbo.saleorderpayments` (id)

### `dbo.saleorderpaymentrels`

- Row count: **0**
- Primary key: `paymentid, saleorderid`
- Columns (2): saleorderid (uuid NOT NULL), paymentid (uuid NOT NULL)
- Key foreign keys:
  - `fk_saleorderpaymentrels_accountpayments_paymentid`: (paymentid) -> `dbo.accountpayments` (id)
  - `fk_saleorderpaymentrels_saleorders_saleorderid`: (saleorderid) -> `dbo.saleorders` (id)

### `dbo.saleorderpayments`

- Row count: **50659**
- Primary key: `id`
- Columns (17): id (uuid NOT NULL), name (text), amount (numeric(18,2) NOT NULL), date (timestamp without time zone NOT NULL), moveid (uuid), companyid (uuid NOT NULL), note (text), orderid (uuid), state (text), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone), isrefund (boolean NOT NULL), partnerid (uuid), origin (text), dotkhamid (uuid)
- Key foreign keys:
  - `fk_saleorderpayments_accountmoves_moveid`: (moveid) -> `dbo.accountmoves` (id)
  - `fk_saleorderpayments_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_saleorderpayments_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_saleorderpayments_companies_companyid`: (companyid) -> `dbo.companies` (id)
  - `fk_saleorderpayments_dotkhams_dotkhamid`: (dotkhamid) -> `dbo.dotkhams` (id)
  - `fk_saleorderpayments_partners_partnerid`: (partnerid) -> `dbo.partners` (id)
  - `fk_saleorderpayments_saleorders_orderid`: (orderid) -> `dbo.saleorders` (id)

### `dbo.saleorderpromotionlines`

- Row count: **40**
- Primary key: `id`
- Columns (17): id (uuid NOT NULL), saleorderlineid (uuid NOT NULL), promotionid (uuid), priceunit (double precision NOT NULL), amount (numeric(18,2) NOT NULL), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone), cardcardid (uuid), discountfixed (numeric(18,2)), discountpercent (numeric(18,2)), discounttype (text), name (text), salecouponprogramid (uuid), servicecardcardid (uuid), type (text)
- Key foreign keys:
  - `fk_saleorderpromotionlines_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_saleorderpromotionlines_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_saleorderpromotionlines_cardcards_cardcardid`: (cardcardid) -> `dbo.cardcards` (id)
  - `fk_saleorderpromotionlines_salecouponprograms_salecouponprogram`: (salecouponprogramid) -> `dbo.salecouponprograms` (id)
  - `fk_saleorderpromotionlines_saleorderlines_saleorderlineid`: (saleorderlineid) -> `dbo.saleorderlines` (id)
  - `fk_saleorderpromotionlines_saleorderpromotions_promotionid`: (promotionid) -> `dbo.saleorderpromotions` (id)
  - `fk_saleorderpromotionlines_servicecardcards_servicecardcardid`: (servicecardcardid) -> `dbo.servicecardcards` (id)

### `dbo.saleorderpromotions`

- Row count: **49**
- Primary key: `id`
- Columns (17): id (uuid NOT NULL), name (text), amount (numeric(18,2) NOT NULL), saleorderid (uuid), saleorderlineid (uuid), discounttype (text), discountpercent (numeric(18,2)), discountfixed (numeric(18,2)), salecouponprogramid (uuid), type (text), servicecardcardid (uuid), cardcardid (uuid), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone), salecouponid (uuid)
- Key foreign keys:
  - `fk_saleorderpromotions_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_saleorderpromotions_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_saleorderpromotions_cardcards_cardcardid`: (cardcardid) -> `dbo.cardcards` (id)
  - `fk_saleorderpromotions_salecouponprograms_salecouponprogramid`: (salecouponprogramid) -> `dbo.salecouponprograms` (id)
  - `fk_saleorderpromotions_salecoupons_salecouponid`: (salecouponid) -> `dbo.salecoupons` (id)
  - `fk_saleorderpromotions_saleorderlines_saleorderlineid`: (saleorderlineid) -> `dbo.saleorderlines` (id)
  - `fk_saleorderpromotions_saleorders_saleorderid`: (saleorderid) -> `dbo.saleorders` (id)
  - `fk_saleorderpromotions_servicecardcards_servicecardcardid`: (servicecardcardid) -> `dbo.servicecardcards` (id)

### `dbo.saleorders`

- Row count: **56622**
- Primary key: `id`
- Columns (40): id (uuid NOT NULL), dateorder (timestamp without time zone NOT NULL), datedone (timestamp without time zone), partnerid (uuid NOT NULL), amounttax (numeric(18,2)), amountuntaxed (numeric(18,2)), amounttotal (numeric(18,2)), note (text), state (text), name (text NOT NULL), companyid (uuid NOT NULL), userid (text), invoicestatus (text), residual (numeric(18,2)), cardid (uuid), pricelistid (uuid), type (text), isquotation (boolean), quoteid (uuid), orderid (uuid), doctorid (uuid), codepromoprogramid (uuid), isfast (boolean NOT NULL), journalid (uuid), quotationid (uuid), totalpaid (numeric(18,2)), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone), discountfixed (numeric(18,2)), discountpercent (numeric(18,2)), discounttype (text), sequencenumber (integer), sequenceprefix (text), appointmentid (uuid), leadid (uuid), isoldflow (boolean), paymentstate (text), isdeleted (boolean NOT NULL)
- Key foreign keys:
  - `fk_saleorders_accountjournals_journalid`: (journalid) -> `dbo.accountjournals` (id)
  - `fk_saleorders_appointments_appointmentid`: (appointmentid) -> `dbo.appointments` (id)
  - `fk_saleorders_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_saleorders_aspnetusers_userid`: (userid) -> `dbo.aspnetusers` (id)
  - `fk_saleorders_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_saleorders_cardcards_cardid`: (cardid) -> `dbo.cardcards` (id)
  - `fk_saleorders_companies_companyid`: (companyid) -> `dbo.companies` (id)
  - `fk_saleorders_crmleads_leadid`: (leadid) -> `dbo.crmleads` (id)
  - ... and 7 more

### `dbo.saleorderservicecardcardrels`

- Row count: **0**
- Primary key: `id`
- Columns (8): id (uuid NOT NULL), saleorderid (uuid NOT NULL), cardid (uuid NOT NULL), amount (numeric(18,2)), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_saleorderservicecardcardrels_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_saleorderservicecardcardrels_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_saleorderservicecardcardrels_saleorders_saleorderid`: (saleorderid) -> `dbo.saleorders` (id)
  - `fk_saleorderservicecardcardrels_servicecardcards_cardid`: (cardid) -> `dbo.servicecardcards` (id)

### `dbo.saleordertransfercompanies`

- Row count: **0**
- Primary key: `id`
- Columns (10): id (uuid NOT NULL), fromcompanyid (uuid NOT NULL), tocompanyid (uuid NOT NULL), saleorderid (uuid NOT NULL), transferdate (timestamp without time zone NOT NULL), reason (text), datecreated (timestamp without time zone), createdbyid (text), lastupdated (timestamp without time zone), writebyid (text)
- Key foreign keys:
  - `fk_saleordertransfercompanies_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_saleordertransfercompanies_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_saleordertransfercompanies_companies_fromcompanyid`: (fromcompanyid) -> `dbo.companies` (id)
  - `fk_saleordertransfercompanies_companies_tocompanyid`: (tocompanyid) -> `dbo.companies` (id)
  - `fk_saleordertransfercompanies_saleorders_saleorderid`: (saleorderid) -> `dbo.saleorders` (id)

### `dbo.saleproductionlineproductrequestlinerels`

- Row count: **0**
- Primary key: `saleproductionlineid, productrequestlineid`
- Columns (2): saleproductionlineid (uuid NOT NULL), productrequestlineid (uuid NOT NULL)
- Key foreign keys:
  - `fk_saleproductionlineproductrequestlinerels_productrequestlines`: (productrequestlineid) -> `dbo.productrequestlines` (id)
  - `fk_saleproductionlineproductrequestlinerels_saleproductionlines`: (saleproductionlineid) -> `dbo.saleproductionlines` (id)

### `dbo.saleproductionlines`

- Row count: **0**
- Primary key: `id`
- Columns (10): id (uuid NOT NULL), saleproductionid (uuid NOT NULL), productid (uuid NOT NULL), productuomid (uuid), quantity (numeric(18,2) NOT NULL), quantityrequested (numeric(18,2) NOT NULL), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_saleproductionlines_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_saleproductionlines_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_saleproductionlines_products_productid`: (productid) -> `dbo.products` (id)
  - `fk_saleproductionlines_saleproductions_saleproductionid`: (saleproductionid) -> `dbo.saleproductions` (id)
  - `fk_saleproductionlines_uoms_productuomid`: (productuomid) -> `dbo.uoms` (id)

### `dbo.saleproductions`

- Row count: **0**
- Primary key: `id`
- Columns (8): id (uuid NOT NULL), productid (uuid), quantity (numeric(18,2) NOT NULL), companyid (uuid), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_saleproductions_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_saleproductions_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_saleproductions_companies_companyid`: (companyid) -> `dbo.companies` (id)
  - `fk_saleproductions_products_productid`: (productid) -> `dbo.products` (id)

### `dbo.salesettings`

- Row count: **1**
- Primary key: `id`
- Columns (6): id (uuid NOT NULL), pointexchangerate (numeric(18,2)), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_salesettings_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_salesettings_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)

### `dbo.sampleprescriptionlines`

- Row count: **0**
- Primary key: `id`
- Columns (15): id (uuid NOT NULL), prescriptionid (uuid NOT NULL), productid (uuid NOT NULL), productuomid (uuid), sequence (integer), numberoftimes (integer NOT NULL), numberofdays (integer NOT NULL), amountoftimes (numeric(18,2) NOT NULL), quantity (numeric(18,2) NOT NULL), useat (text), note (text), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_sampleprescriptionlines_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_sampleprescriptionlines_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_sampleprescriptionlines_products_productid`: (productid) -> `dbo.products` (id)
  - `fk_sampleprescriptionlines_sampleprescriptions_prescriptionid`: (prescriptionid) -> `dbo.sampleprescriptions` (id)
  - `fk_sampleprescriptionlines_uoms_productuomid`: (productuomid) -> `dbo.uoms` (id)

### `dbo.sampleprescriptions`

- Row count: **0**
- Primary key: `id`
- Columns (8): id (uuid NOT NULL), name (text), note (text), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone), companyid (uuid)
- Key foreign keys:
  - `fk_sampleprescriptions_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_sampleprescriptions_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_sampleprescriptions_companies_companyid`: (companyid) -> `dbo.companies` (id)

### `dbo.scheduledjobs`

- Row count: **0**
- Primary key: `id`
- Columns (10): id (uuid NOT NULL), jobid (text), isactive (boolean NOT NULL), resid (uuid), resmodel (text), datecreated (timestamp without time zone), createdbyid (text), lastupdated (timestamp without time zone), writebyid (text), typecode (text)
- Key foreign keys:
  - `fk_scheduledjobs_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_scheduledjobs_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)

### `dbo.servicecardcards`

- Row count: **0**
- Primary key: `id`
- Columns (16): id (uuid NOT NULL), name (text NOT NULL), cardtypeid (uuid NOT NULL), partnerid (uuid), activateddate (timestamp without time zone), expireddate (timestamp without time zone), amount (numeric(18,2)), residual (numeric(18,2)), state (text), salelineid (uuid), barcode (text), companyid (uuid), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_servicecardcards_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_servicecardcards_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_servicecardcards_companies_companyid`: (companyid) -> `dbo.companies` (id)
  - `fk_servicecardcards_partners_partnerid`: (partnerid) -> `dbo.partners` (id)
  - `fk_servicecardcards_servicecardorderlines_salelineid`: (salelineid) -> `dbo.servicecardorderlines` (id)
  - `fk_servicecardcards_servicecardtypes_cardtypeid`: (cardtypeid) -> `dbo.servicecardtypes` (id)

### `dbo.servicecardorderlineinvoicerels`

- Row count: **0**
- Primary key: `orderlineid, invoicelineid`
- Columns (2): orderlineid (uuid NOT NULL), invoicelineid (uuid NOT NULL)
- Key foreign keys:
  - `fk_servicecardorderlineinvoicerels_accountmovelines_invoiceline`: (invoicelineid) -> `dbo.accountmovelines` (id)
  - `fk_servicecardorderlineinvoicerels_servicecardorderlines_orderl`: (orderlineid) -> `dbo.servicecardorderlines` (id)

### `dbo.servicecardorderlines`

- Row count: **0**
- Primary key: `id`
- Columns (19): id (uuid NOT NULL), priceunit (numeric(18,2) NOT NULL), productuomqty (numeric(18,2) NOT NULL), state (text), orderpartnerid (uuid), orderid (uuid NOT NULL), discount (numeric(18,2) NOT NULL), cardtypeid (uuid NOT NULL), companyid (uuid), pricesubtotal (numeric(18,2) NOT NULL), pricetotal (numeric(18,2) NOT NULL), salesmanid (text), sequence (integer), discounttype (text), discountfixed (numeric(18,2)), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_servicecardorderlines_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_servicecardorderlines_aspnetusers_salesmanid`: (salesmanid) -> `dbo.aspnetusers` (id)
  - `fk_servicecardorderlines_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_servicecardorderlines_companies_companyid`: (companyid) -> `dbo.companies` (id)
  - `fk_servicecardorderlines_partners_orderpartnerid`: (orderpartnerid) -> `dbo.partners` (id)
  - `fk_servicecardorderlines_servicecardorders_orderid`: (orderid) -> `dbo.servicecardorders` (id)
  - `fk_servicecardorderlines_servicecardtypes_cardtypeid`: (cardtypeid) -> `dbo.servicecardtypes` (id)

### `dbo.servicecardorderpaymentrels`

- Row count: **0**
- Primary key: `paymentid, cardorderid`
- Columns (2): cardorderid (uuid NOT NULL), paymentid (uuid NOT NULL)
- Key foreign keys:
  - `fk_servicecardorderpaymentrels_accountpayments_paymentid`: (paymentid) -> `dbo.accountpayments` (id)
  - `fk_servicecardorderpaymentrels_servicecardorders_cardorderid`: (cardorderid) -> `dbo.servicecardorders` (id)

### `dbo.servicecardorderpayments`

- Row count: **0**
- Primary key: `id`
- Columns (8): id (uuid NOT NULL), orderid (uuid NOT NULL), amount (numeric(18,2) NOT NULL), journalid (uuid NOT NULL), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_servicecardorderpayments_accountjournals_journalid`: (journalid) -> `dbo.accountjournals` (id)
  - `fk_servicecardorderpayments_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_servicecardorderpayments_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_servicecardorderpayments_servicecardorders_orderid`: (orderid) -> `dbo.servicecardorders` (id)

### `dbo.servicecardorders`

- Row count: **0**
- Primary key: `id`
- Columns (15): id (uuid NOT NULL), name (text NOT NULL), partnerid (uuid NOT NULL), dateorder (timestamp without time zone NOT NULL), userid (text), state (text), companyid (uuid NOT NULL), amounttotal (numeric(18,2)), amountresidual (numeric(18,2)), amountrefund (numeric(18,2)), accountmoveid (uuid), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_servicecardorders_accountmoves_accountmoveid`: (accountmoveid) -> `dbo.accountmoves` (id)
  - `fk_servicecardorders_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_servicecardorders_aspnetusers_userid`: (userid) -> `dbo.aspnetusers` (id)
  - `fk_servicecardorders_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_servicecardorders_companies_companyid`: (companyid) -> `dbo.companies` (id)
  - `fk_servicecardorders_partners_partnerid`: (partnerid) -> `dbo.partners` (id)

### `dbo.servicecardtypes`

- Row count: **0**
- Primary key: `id`
- Columns (15): id (uuid NOT NULL), name (text NOT NULL), type (text), price (numeric(18,2)), amount (numeric(18,2)), period (text), nbrperiod (integer), productid (uuid), companyid (uuid), active (boolean NOT NULL), productpricelistid (uuid), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_servicecardtypes_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_servicecardtypes_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_servicecardtypes_companies_companyid`: (companyid) -> `dbo.companies` (id)
  - `fk_servicecardtypes_productpricelists_productpricelistid`: (productpricelistid) -> `dbo.productpricelists` (id)
  - `fk_servicecardtypes_products_productid`: (productid) -> `dbo.products` (id)

### `dbo.setupchamcongs`

- Row count: **0**
- Primary key: `id`
- Columns (9): id (uuid NOT NULL), onestandardworkhour (numeric(18,2) NOT NULL), halfstandardworkhour (numeric(18,2) NOT NULL), differencetime (numeric(18,2) NOT NULL), companyid (uuid), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_setupchamcongs_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_setupchamcongs_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_setupchamcongs_companies_companyid`: (companyid) -> `dbo.companies` (id)

### `dbo.smsaccounts`

- Row count: **0**
- Primary key: `id`
- Columns (17): id (uuid NOT NULL), name (text), displayname (text), companyid (uuid), provider (text), brandname (text), clientid (text), clientsecret (text), apikey (text), secretkey (text), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone), vmgtoken (text), apidomain (text), isdefault (boolean NOT NULL)
- Key foreign keys:
  - `fk_smsaccounts_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_smsaccounts_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_smsaccounts_companies_companyid`: (companyid) -> `dbo.companies` (id)

### `dbo.smsappointmentautomationconfigs`

- Row count: **0**
- Primary key: `id`
- Columns (14): id (uuid NOT NULL), companyid (uuid), smsaccountid (uuid), smscampaignid (uuid), timebeforsend (integer NOT NULL), typetimebeforsend (text), body (text), active (boolean NOT NULL), templateid (uuid), lastcron (timestamp without time zone), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_smsappointmentautomationconfigs_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_smsappointmentautomationconfigs_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_smsappointmentautomationconfigs_companies_companyid`: (companyid) -> `dbo.companies` (id)
  - `fk_smsappointmentautomationconfigs_smsaccounts_smsaccountid`: (smsaccountid) -> `dbo.smsaccounts` (id)
  - `fk_smsappointmentautomationconfigs_smscampaign_smscampaignid`: (smscampaignid) -> `dbo.smscampaign` (id)
  - `fk_smsappointmentautomationconfigs_smstemplates_templateid`: (templateid) -> `dbo.smstemplates` (id)

### `dbo.smsbirthdayautomationconfigs`

- Row count: **0**
- Primary key: `id`
- Columns (13): id (uuid NOT NULL), companyid (uuid), smsaccountid (uuid), smscampaignid (uuid), scheduletime (timestamp without time zone), daybeforesend (integer NOT NULL), body (text), active (boolean NOT NULL), templateid (uuid), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_smsbirthdayautomationconfigs_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_smsbirthdayautomationconfigs_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_smsbirthdayautomationconfigs_companies_companyid`: (companyid) -> `dbo.companies` (id)
  - `fk_smsbirthdayautomationconfigs_smsaccounts_smsaccountid`: (smsaccountid) -> `dbo.smsaccounts` (id)
  - `fk_smsbirthdayautomationconfigs_smscampaign_smscampaignid`: (smscampaignid) -> `dbo.smscampaign` (id)
  - `fk_smsbirthdayautomationconfigs_smstemplates_templateid`: (templateid) -> `dbo.smstemplates` (id)

### `dbo.smscampaign`

- Row count: **0**
- Primary key: `id`
- Columns (14): id (uuid NOT NULL), name (text), companyid (uuid), limitmessage (integer NOT NULL), dateend (timestamp without time zone), datestart (timestamp without time zone), typedate (text), state (text), defaulttype (text), usercampaign (boolean NOT NULL), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_smscampaign_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_smscampaign_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_smscampaign_companies_companyid`: (companyid) -> `dbo.companies` (id)

### `dbo.smscareafterorderautomationconfigs`

- Row count: **0**
- Primary key: `id`
- Columns (17): id (uuid NOT NULL), name (text), companyid (uuid), smsaccountid (uuid), smscampaignid (uuid), scheduletime (timestamp without time zone), body (text), timebeforsend (integer NOT NULL), typetimebeforsend (text), active (boolean NOT NULL), templateid (uuid), applyon (text), lastcron (timestamp without time zone), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_smscareafterorderautomationconfigs_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_smscareafterorderautomationconfigs_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_smscareafterorderautomationconfigs_companies_companyid`: (companyid) -> `dbo.companies` (id)
  - `fk_smscareafterorderautomationconfigs_smsaccounts_smsaccountid`: (smsaccountid) -> `dbo.smsaccounts` (id)
  - `fk_smscareafterorderautomationconfigs_smscampaign_smscampaignid`: (smscampaignid) -> `dbo.smscampaign` (id)
  - `fk_smscareafterorderautomationconfigs_smstemplates_templateid`: (templateid) -> `dbo.smstemplates` (id)

### `dbo.smscomposers`

- Row count: **0**
- Primary key: `id`
- Columns (22): id (uuid NOT NULL), compositionmode (text), resmodel (text), resids (text), body (text), templateid (uuid), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone), massforcesend (boolean NOT NULL), masskeeplog (boolean NOT NULL), massmaillingid (uuid), smsaccountid (uuid), smscampaignid (uuid), mailactivitytypeid (uuid), baseautomationv2id (uuid), delivered (timestamp without time zone), lastsequenceid (uuid), lockid (uuid), rowversion (bytea), removed (boolean NOT NULL)
- Key foreign keys:
  - `fk_smscomposers_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_smscomposers_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_smscomposers_baseautomationv2s_baseautomationv2id`: (baseautomationv2id) -> `dbo.baseautomationv2s` (id)
  - `fk_smscomposers_mailactivitytypes_mailactivitytypeid`: (mailactivitytypeid) -> `dbo.mailactivitytypes` (id)
  - `fk_smscomposers_smsaccounts_smsaccountid`: (smsaccountid) -> `dbo.smsaccounts` (id)
  - `fk_smscomposers_smscampaign_smscampaignid`: (smscampaignid) -> `dbo.smscampaign` (id)
  - `fk_smscomposers_smsmessagedetails_lastsequenceid`: (lastsequenceid) -> `dbo.smsmessagedetails` (id)
  - `fk_smscomposers_smsmessages_massmaillingid`: (massmaillingid) -> `dbo.smsmessages` (id)
  - ... and 1 more

### `dbo.smsconfigproductcategoryrels`

- Row count: **0**
- Primary key: `smsconfigid, productcategoryid`
- Columns (2): smsconfigid (uuid NOT NULL), productcategoryid (uuid NOT NULL)
- Key foreign keys:
  - `fk_smsconfigproductcategoryrels_productcategories_productcatego`: (productcategoryid) -> `dbo.productcategories` (id)
  - `fk_smsconfigproductcategoryrels_smscareafterorderautomationconf`: (smsconfigid) -> `dbo.smscareafterorderautomationconfigs` (id)

### `dbo.smsconfigproductrels`

- Row count: **0**
- Primary key: `smsconfigid, productid`
- Columns (2): smsconfigid (uuid NOT NULL), productid (uuid NOT NULL)
- Key foreign keys:
  - `fk_smsconfigproductrels_products_productid`: (productid) -> `dbo.products` (id)
  - `fk_smsconfigproductrels_smscareafterorderautomationconfigs_smsc`: (smsconfigid) -> `dbo.smscareafterorderautomationconfigs` (id)

### `dbo.smsmessageappointmentrels`

- Row count: **0**
- Primary key: `appointmentid, smsmessageid`
- Columns (2): smsmessageid (uuid NOT NULL), appointmentid (uuid NOT NULL)
- Key foreign keys:
  - `fk_smsmessageappointmentrels_appointments_appointmentid`: (appointmentid) -> `dbo.appointments` (id)
  - `fk_smsmessageappointmentrels_smsmessages_smsmessageid`: (smsmessageid) -> `dbo.smsmessages` (id)

### `dbo.smsmessagedetails`

- Row count: **0**
- Primary key: `id`
- Columns (20): id (uuid NOT NULL), body (text), number (text), cost (numeric(18,2) NOT NULL), date (timestamp without time zone), partnerid (uuid), smsaccountid (uuid), state (text), errorcode (text), smsmessageid (uuid), smscampaignid (uuid), companyid (uuid), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone), mailmessageid (uuid), baseautomationv2id (uuid), rowversion (bytea), composerid (uuid)
- Key foreign keys:
  - `fk_smsmessagedetails_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_smsmessagedetails_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_smsmessagedetails_baseautomationv2s_baseautomationv2id`: (baseautomationv2id) -> `dbo.baseautomationv2s` (id)
  - `fk_smsmessagedetails_companies_companyid`: (companyid) -> `dbo.companies` (id)
  - `fk_smsmessagedetails_mailmessages_mailmessageid`: (mailmessageid) -> `dbo.mailmessages` (id)
  - `fk_smsmessagedetails_partners_partnerid`: (partnerid) -> `dbo.partners` (id)
  - `fk_smsmessagedetails_smsaccounts_smsaccountid`: (smsaccountid) -> `dbo.smsaccounts` (id)
  - `fk_smsmessagedetails_smscampaign_smscampaignid`: (smscampaignid) -> `dbo.smscampaign` (id)
  - ... and 2 more

### `dbo.smsmessagepartnerrels`

- Row count: **0**
- Primary key: `partnerid, smsmessageid`
- Columns (2): partnerid (uuid NOT NULL), smsmessageid (uuid NOT NULL)
- Key foreign keys:
  - `fk_smsmessagepartnerrels_partners_partnerid`: (partnerid) -> `dbo.partners` (id)
  - `fk_smsmessagepartnerrels_smsmessages_smsmessageid`: (smsmessageid) -> `dbo.smsmessages` (id)

### `dbo.smsmessages`

- Row count: **0**
- Primary key: `id`
- Columns (16): id (uuid NOT NULL), name (text), companyid (uuid), smscampaignid (uuid), date (timestamp without time zone), scheduledate (timestamp without time zone), smstemplateid (uuid), body (text), smsaccountid (uuid), state (text), resmodel (text), rescount (integer), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_smsmessages_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_smsmessages_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_smsmessages_companies_companyid`: (companyid) -> `dbo.companies` (id)
  - `fk_smsmessages_smsaccounts_smsaccountid`: (smsaccountid) -> `dbo.smsaccounts` (id)
  - `fk_smsmessages_smscampaign_smscampaignid`: (smscampaignid) -> `dbo.smscampaign` (id)
  - `fk_smsmessages_smstemplates_smstemplateid`: (smstemplateid) -> `dbo.smstemplates` (id)

### `dbo.smsmessagesaleorderlinerels`

- Row count: **0**
- Primary key: `saleorderlineid, smsmessageid`
- Columns (2): smsmessageid (uuid NOT NULL), saleorderlineid (uuid NOT NULL)
- Key foreign keys:
  - `fk_smsmessagesaleorderlinerels_saleorderlines_saleorderlineid`: (saleorderlineid) -> `dbo.saleorderlines` (id)
  - `fk_smsmessagesaleorderlinerels_smsmessages_smsmessageid`: (smsmessageid) -> `dbo.smsmessages` (id)

### `dbo.smsmessagesaleorderrels`

- Row count: **0**
- Primary key: `saleorderid, smsmessageid`
- Columns (2): smsmessageid (uuid NOT NULL), saleorderid (uuid NOT NULL)
- Key foreign keys:
  - `fk_smsmessagesaleorderrels_saleorders_saleorderid`: (saleorderid) -> `dbo.saleorders` (id)
  - `fk_smsmessagesaleorderrels_smsmessages_smsmessageid`: (smsmessageid) -> `dbo.smsmessages` (id)

### `dbo.smstemplates`

- Row count: **0**
- Primary key: `id`
- Columns (9): id (uuid NOT NULL), name (text), companyid (uuid), body (text), type (text), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_smstemplates_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_smstemplates_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_smstemplates_companies_companyid`: (companyid) -> `dbo.companies` (id)

### `dbo.smsthankscustomerautomationconfigs`

- Row count: **0**
- Primary key: `id`
- Columns (14): id (uuid NOT NULL), companyid (uuid), smsaccountid (uuid), smscampaignid (uuid), body (text), timebeforsend (integer NOT NULL), typetimebeforsend (text), active (boolean NOT NULL), templateid (uuid), lastcron (timestamp without time zone), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_smsthankscustomerautomationconfigs_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_smsthankscustomerautomationconfigs_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_smsthankscustomerautomationconfigs_companies_companyid`: (companyid) -> `dbo.companies` (id)
  - `fk_smsthankscustomerautomationconfigs_smsaccounts_smsaccountid`: (smsaccountid) -> `dbo.smsaccounts` (id)
  - `fk_smsthankscustomerautomationconfigs_smscampaign_smscampaignid`: (smscampaignid) -> `dbo.smscampaign` (id)
  - `fk_smsthankscustomerautomationconfigs_smstemplates_templateid`: (templateid) -> `dbo.smstemplates` (id)

### `dbo.socialaccountmembers`

- Row count: **0**
- Primary key: `id`
- Columns (8): id (uuid NOT NULL), userid (text), role (text), socialaccountid (uuid NOT NULL), datecreated (timestamp without time zone), createdbyid (text), lastupdated (timestamp without time zone), writebyid (text)
- Key foreign keys:
  - `fk_socialaccountmembers_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_socialaccountmembers_aspnetusers_userid`: (userid) -> `dbo.aspnetusers` (id)
  - `fk_socialaccountmembers_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_socialaccountmembers_socialaccounts_socialaccountid`: (socialaccountid) -> `dbo.socialaccounts` (id)

### `dbo.socialaccounts`

- Row count: **0**
- Primary key: `id`
- Columns (22): id (uuid NOT NULL), token (text), name (text), description (text), category (text), oatype (text), avatar (text), cover (text), isverified (boolean NOT NULL), shopdomain (text), adminphones (text), datecreated (timestamp without time zone), createdbyid (text), lastupdated (timestamp without time zone), writebyid (text), accountid (text), refreshtoken (text), tokenvalidity (timestamp without time zone), isdisconnected (boolean NOT NULL), chatomniid (text), active (boolean NOT NULL), type (integer NOT NULL)
- Key foreign keys:
  - `fk_socialaccounts_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_socialaccounts_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)

### `dbo.states`

- Row count: **3654**
- Primary key: `id`
- Columns (8): id (uuid NOT NULL), code (text), name (text), countryid (uuid NOT NULL), datecreated (timestamp without time zone), createdbyid (text), lastupdated (timestamp without time zone), writebyid (text)
- Key foreign keys:
  - `fk_states_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_states_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_states_countries_countryid`: (countryid) -> `dbo.countries` (id)

### `dbo.stockinventory`

- Row count: **18**
- Primary key: `id`
- Columns (17): id (uuid NOT NULL), name (text), date (timestamp without time zone NOT NULL), note (text), state (text), locationid (uuid NOT NULL), productid (uuid), categoryid (uuid), criteriaid (uuid), filter (text), companyid (uuid NOT NULL), exhausted (boolean), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone), active (boolean)
- Key foreign keys:
  - `fk_stockinventory_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_stockinventory_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_stockinventory_companies_companyid`: (companyid) -> `dbo.companies` (id)
  - `fk_stockinventory_productcategories_categoryid`: (categoryid) -> `dbo.productcategories` (id)
  - `fk_stockinventory_products_productid`: (productid) -> `dbo.products` (id)
  - `fk_stockinventory_stockinventorycriterias_criteriaid`: (criteriaid) -> `dbo.stockinventorycriterias` (id)
  - `fk_stockinventory_stocklocations_locationid`: (locationid) -> `dbo.stocklocations` (id)

### `dbo.stockinventorycriterias`

- Row count: **1**
- Primary key: `id`
- Columns (7): id (uuid NOT NULL), name (text), note (text), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_stockinventorycriterias_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_stockinventorycriterias_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)

### `dbo.stockinventoryline`

- Row count: **1430**
- Primary key: `id`
- Columns (13): id (uuid NOT NULL), locationid (uuid NOT NULL), productid (uuid NOT NULL), productuomid (uuid NOT NULL), productqty (numeric(18,2)), theoreticalqty (numeric(18,2)), inventoryid (uuid), companyid (uuid), sequence (integer), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_stockinventoryline_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_stockinventoryline_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_stockinventoryline_companies_companyid`: (companyid) -> `dbo.companies` (id)
  - `fk_stockinventoryline_products_productid`: (productid) -> `dbo.products` (id)
  - `fk_stockinventoryline_stockinventory_inventoryid`: (inventoryid) -> `dbo.stockinventory` (id)
  - `fk_stockinventoryline_stocklocations_locationid`: (locationid) -> `dbo.stocklocations` (id)

### `dbo.stocklocations`

- Row count: **23**
- Primary key: `id`
- Columns (15): id (uuid NOT NULL), usage (text NOT NULL), name (text NOT NULL), parentlocationid (uuid), completename (text), active (boolean NOT NULL), scraplocation (boolean NOT NULL), parentleft (integer), parentright (integer), companyid (uuid), nameget (text), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_stocklocations_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_stocklocations_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_stocklocations_companies_companyid`: (companyid) -> `dbo.companies` (id)
  - `fk_stocklocations_stocklocations_parentlocationid`: (parentlocationid) -> `dbo.stocklocations` (id)

### `dbo.stockmovemoverels`

- Row count: **0**
- Primary key: `moveorigid, movedestid`
- Columns (2): movedestid (uuid NOT NULL), moveorigid (uuid NOT NULL)
- Key foreign keys:
  - `fk_stockmovemoverels_stockmoves_movedestid`: (movedestid) -> `dbo.stockmoves` (id)
  - `fk_stockmovemoverels_stockmoves_moveorigid`: (moveorigid) -> `dbo.stockmoves` (id)

### `dbo.stockmoves`

- Row count: **1670**
- Primary key: `id`
- Columns (32): id (uuid NOT NULL), note (text), state (text), name (text NOT NULL), dateexpected (timestamp without time zone), pickingtypeid (uuid), partnerid (uuid), productuomqty (double precision NOT NULL), productqty (double precision), productuomid (uuid), productid (uuid NOT NULL), locationid (uuid NOT NULL), locationdestid (uuid NOT NULL), warehouseid (uuid), pickingid (uuid), date (timestamp without time zone NOT NULL), priceunit (double precision), companyid (uuid NOT NULL), sequence (integer NOT NULL), origin (text), purchaselineid (uuid), inventoryid (uuid), backdate (timestamp without time zone), datedone (timestamp without time zone), value (numeric(18,2)), uomprice (double precision), totalamount (numeric(18,2)), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone), originreturnedmoveid (uuid)
- Key foreign keys:
  - `fk_stockmoves_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_stockmoves_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_stockmoves_companies_companyid`: (companyid) -> `dbo.companies` (id)
  - `fk_stockmoves_partners_partnerid`: (partnerid) -> `dbo.partners` (id)
  - `fk_stockmoves_products_productid`: (productid) -> `dbo.products` (id)
  - `fk_stockmoves_purchaseorderlines_purchaselineid`: (purchaselineid) -> `dbo.purchaseorderlines` (id)
  - `fk_stockmoves_stockinventory_inventoryid`: (inventoryid) -> `dbo.stockinventory` (id)
  - `fk_stockmoves_stocklocations_locationdestid`: (locationdestid) -> `dbo.stocklocations` (id)
  - ... and 5 more

### `dbo.stockpickings`

- Row count: **58**
- Primary key: `id`
- Columns (20): id (uuid NOT NULL), partnerid (uuid), pickingtypeid (uuid NOT NULL), note (text), state (text), date (timestamp without time zone), datedone (timestamp without time zone), name (text), companyid (uuid NOT NULL), locationid (uuid NOT NULL), locationdestid (uuid NOT NULL), origin (text), backdate (timestamp without time zone), totalamount (numeric(18,2)), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone), active (boolean), householdbusinessid (uuid)
- Key foreign keys:
  - `fk_stockpickings_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_stockpickings_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_stockpickings_companies_companyid`: (companyid) -> `dbo.companies` (id)
  - `fk_stockpickings_householdbusinesses_householdbusinessid`: (householdbusinessid) -> `dbo.householdbusinesses` (id)
  - `fk_stockpickings_partners_partnerid`: (partnerid) -> `dbo.partners` (id)
  - `fk_stockpickings_stocklocations_locationdestid`: (locationdestid) -> `dbo.stocklocations` (id)
  - `fk_stockpickings_stocklocations_locationid`: (locationid) -> `dbo.stocklocations` (id)
  - `fk_stockpickings_stockpickingtypes_pickingtypeid`: (pickingtypeid) -> `dbo.stockpickingtypes` (id)

### `dbo.stockpickingtypes`

- Row count: **16**
- Primary key: `id`
- Columns (16): id (uuid NOT NULL), code (text NOT NULL), sequence (integer NOT NULL), defaultlocationdestid (uuid), warehouseid (uuid), irsequenceid (uuid NOT NULL), active (boolean NOT NULL), name (text NOT NULL), defaultlocationsrcid (uuid), returnpickingtypeid (uuid), usecreatelots (boolean), useexistinglots (boolean), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_stockpickingtypes_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_stockpickingtypes_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_stockpickingtypes_irsequences_irsequenceid`: (irsequenceid) -> `dbo.irsequences` (id)
  - `fk_stockpickingtypes_stocklocations_defaultlocationdestid`: (defaultlocationdestid) -> `dbo.stocklocations` (id)
  - `fk_stockpickingtypes_stocklocations_defaultlocationsrcid`: (defaultlocationsrcid) -> `dbo.stocklocations` (id)
  - `fk_stockpickingtypes_stockpickingtypes_returnpickingtypeid`: (returnpickingtypeid) -> `dbo.stockpickingtypes` (id)
  - `fk_stockpickingtypes_stockwarehouses_warehouseid`: (warehouseid) -> `dbo.stockwarehouses` (id)

### `dbo.stockquantmoverel`

- Row count: **1267**
- Primary key: `moveid, quantid`
- Columns (2): quantid (uuid NOT NULL), moveid (uuid NOT NULL)
- Key foreign keys:
  - `fk_stockquantmoverel_stockmoves_moveid`: (moveid) -> `dbo.stockmoves` (id)
  - `fk_stockquantmoverel_stockquants_quantid`: (quantid) -> `dbo.stockquants` (id)

### `dbo.stockquants`

- Row count: **815**
- Primary key: `id`
- Columns (14): id (uuid NOT NULL), qty (double precision NOT NULL), cost (double precision), locationid (uuid NOT NULL), productid (uuid NOT NULL), indate (timestamp without time zone), companyid (uuid NOT NULL), negativemoveid (uuid), propagatedfromid (uuid), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone), issecondary (boolean NOT NULL)
- Key foreign keys:
  - `fk_stockquants_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_stockquants_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_stockquants_companies_companyid`: (companyid) -> `dbo.companies` (id)
  - `fk_stockquants_products_productid`: (productid) -> `dbo.products` (id)
  - `fk_stockquants_stocklocations_locationid`: (locationid) -> `dbo.stocklocations` (id)
  - `fk_stockquants_stockmoves_negativemoveid`: (negativemoveid) -> `dbo.stockmoves` (id)
  - `fk_stockquants_stockquants_propagatedfromid`: (propagatedfromid) -> `dbo.stockquants` (id)

### `dbo.stockvaluationlayers`

- Row count: **907**
- Primary key: `id`
- Columns (18): id (uuid NOT NULL), productid (uuid NOT NULL), companyid (uuid NOT NULL), quantity (double precision NOT NULL), unitcost (numeric(18,2) NOT NULL), remainingqty (double precision NOT NULL), remainingvalue (numeric(18,2) NOT NULL), description (text), value (numeric(18,2) NOT NULL), stockmoveid (uuid), layerid (uuid), roundingadjustment (text), date (timestamp without time zone), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone), issecondary (boolean NOT NULL)
- Key foreign keys:
  - `fk_stockvaluationlayers_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_stockvaluationlayers_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_stockvaluationlayers_companies_companyid`: (companyid) -> `dbo.companies` (id)
  - `fk_stockvaluationlayers_products_productid`: (productid) -> `dbo.products` (id)
  - `fk_stockvaluationlayers_stockmoves_stockmoveid`: (stockmoveid) -> `dbo.stockmoves` (id)
  - `fk_stockvaluationlayers_stockvaluationlayers_layerid`: (layerid) -> `dbo.stockvaluationlayers` (id)

### `dbo.stockwarehouses`

- Row count: **8**
- Primary key: `id`
- Columns (17): id (uuid NOT NULL), name (text NOT NULL), active (boolean NOT NULL), companyid (uuid NOT NULL), partnerid (uuid), viewlocationid (uuid NOT NULL), locationid (uuid NOT NULL), code (text), intypeid (uuid), outtypeid (uuid), receptionsteps (text), deliverysteps (text), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone), isewarehouse (boolean)
- Key foreign keys:
  - `fk_stockwarehouses_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_stockwarehouses_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_stockwarehouses_companies_companyid`: (companyid) -> `dbo.companies` (id)
  - `fk_stockwarehouses_partners_partnerid`: (partnerid) -> `dbo.partners` (id)
  - `fk_stockwarehouses_stocklocations_locationid`: (locationid) -> `dbo.stocklocations` (id)
  - `fk_stockwarehouses_stocklocations_viewlocationid`: (viewlocationid) -> `dbo.stocklocations` (id)
  - `fk_stockwarehouses_stockpickingtypes_intypeid`: (intypeid) -> `dbo.stockpickingtypes` (id)
  - `fk_stockwarehouses_stockpickingtypes_outtypeid`: (outtypeid) -> `dbo.stockpickingtypes` (id)

### `dbo.surveyanswers`

- Row count: **0**
- Primary key: `id`
- Columns (9): id (uuid NOT NULL), name (text), questionid (uuid NOT NULL), score (numeric(18,2)), sequence (integer), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_surveyanswers_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_surveyanswers_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_surveyanswers_surveyquestions_questionid`: (questionid) -> `dbo.surveyquestions` (id)

### `dbo.surveyassignments`

- Row count: **0**
- Primary key: `id`
- Columns (14): id (uuid NOT NULL), employeeid (uuid NOT NULL), saleorderid (uuid NOT NULL), status (text), companyid (uuid), completedate (timestamp without time zone), userinputid (uuid), partnerid (uuid), assigndate (timestamp without time zone), userid (text), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_surveyassignments_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_surveyassignments_aspnetusers_userid`: (userid) -> `dbo.aspnetusers` (id)
  - `fk_surveyassignments_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_surveyassignments_companies_companyid`: (companyid) -> `dbo.companies` (id)
  - `fk_surveyassignments_employees_employeeid`: (employeeid) -> `dbo.employees` (id)
  - `fk_surveyassignments_partners_partnerid`: (partnerid) -> `dbo.partners` (id)
  - `fk_surveyassignments_saleorders_saleorderid`: (saleorderid) -> `dbo.saleorders` (id)
  - `fk_surveyassignments_surveyuserinputs_userinputid`: (userinputid) -> `dbo.surveyuserinputs` (id)

### `dbo.surveycallcontents`

- Row count: **0**
- Primary key: `id`
- Columns (8): id (uuid NOT NULL), name (text), date (timestamp without time zone), assignmentid (uuid), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_surveycallcontents_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_surveycallcontents_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_surveycallcontents_surveyassignments_assignmentid`: (assignmentid) -> `dbo.surveyassignments` (id)

### `dbo.surveyquestions`

- Row count: **0**
- Primary key: `id`
- Columns (10): id (uuid NOT NULL), name (text), type (text), companyid (uuid), sequence (integer), active (boolean NOT NULL), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_surveyquestions_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_surveyquestions_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_surveyquestions_companies_companyid`: (companyid) -> `dbo.companies` (id)

### `dbo.surveytags`

- Row count: **0**
- Primary key: `id`
- Columns (7): id (uuid NOT NULL), name (text NOT NULL), color (text), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_surveytags_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_surveytags_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)

### `dbo.surveyuserinputlines`

- Row count: **0**
- Primary key: `id`
- Columns (10): id (uuid NOT NULL), score (numeric(18,2)), valuetext (text), userinputid (uuid NOT NULL), answerid (uuid), questionid (uuid), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_surveyuserinputlines_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_surveyuserinputlines_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_surveyuserinputlines_surveyanswers_answerid`: (answerid) -> `dbo.surveyanswers` (id)
  - `fk_surveyuserinputlines_surveyquestions_questionid`: (questionid) -> `dbo.surveyquestions` (id)
  - `fk_surveyuserinputlines_surveyuserinputs_userinputid`: (userinputid) -> `dbo.surveyuserinputs` (id)

### `dbo.surveyuserinputs`

- Row count: **0**
- Primary key: `id`
- Columns (8): id (uuid NOT NULL), score (numeric(18,2)), maxscore (numeric(18,2)), note (text), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_surveyuserinputs_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_surveyuserinputs_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)

### `dbo.surveyuserinputsurveytagrels`

- Row count: **0**
- Primary key: `userinputid, surveytagid`
- Columns (2): userinputid (uuid NOT NULL), surveytagid (uuid NOT NULL)
- Key foreign keys:
  - `fk_surveyuserinputsurveytagrels_surveytags_surveytagid`: (surveytagid) -> `dbo.surveytags` (id)
  - `fk_surveyuserinputsurveytagrels_surveyuserinputs_userinputid`: (userinputid) -> `dbo.surveyuserinputs` (id)

### `dbo.tcarecampaigns`

- Row count: **0**
- Primary key: `id`
- Columns (15): id (uuid NOT NULL), name (text NOT NULL), graphxml (text), shedulestartnumber (numeric(18,2) NOT NULL), shedulestarttype (text), state (text), recurringjobid (text), tcarescenarioid (uuid), active (boolean NOT NULL), tagid (uuid), facebookpageid (uuid), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_tcarecampaigns_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_tcarecampaigns_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_tcarecampaigns_facebookpages_facebookpageid`: (facebookpageid) -> `dbo.facebookpages` (id)
  - `fk_tcarecampaigns_partnercategories_tagid`: (tagid) -> `dbo.partnercategories` (id)
  - `fk_tcarecampaigns_tcarescenarios_tcarescenarioid`: (tcarescenarioid) -> `dbo.tcarescenarios` (id)

### `dbo.tcareconfigs`

- Row count: **0**
- Primary key: `id`
- Columns (9): id (uuid NOT NULL), jobcampaignhour (integer), jobcampaignminute (integer), jobmessagingminute (integer), jobmessageminute (integer), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_tcareconfigs_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_tcareconfigs_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)

### `dbo.tcaremessages`

- Row count: **0**
- Primary key: `id`
- Columns (18): id (uuid NOT NULL), profilepartnerid (uuid), channelsocicalid (uuid), campaignid (uuid), partnerid (uuid), tcaremessagingid (uuid), messagecontent (text), state (text), scheduleddate (timestamp without time zone), sent (timestamp without time zone), opened (timestamp without time zone), delivery (timestamp without time zone), failurereason (text), messageid (text), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_tcaremessages_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_tcaremessages_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_tcaremessages_facebookpages_channelsocicalid`: (channelsocicalid) -> `dbo.facebookpages` (id)
  - `fk_tcaremessages_facebookuserprofiles_profilepartnerid`: (profilepartnerid) -> `dbo.facebookuserprofiles` (id)
  - `fk_tcaremessages_partners_partnerid`: (partnerid) -> `dbo.partners` (id)
  - `fk_tcaremessages_tcarecampaigns_campaignid`: (campaignid) -> `dbo.tcarecampaigns` (id)
  - `fk_tcaremessages_tcaremessagings_tcaremessagingid`: (tcaremessagingid) -> `dbo.tcaremessagings` (id)

### `dbo.tcaremessagetemplates`

- Row count: **0**
- Primary key: `id`
- Columns (9): id (uuid NOT NULL), name (text NOT NULL), content (text), type (text), couponprogramid (uuid), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_tcaremessagetemplates_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_tcaremessagetemplates_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_tcaremessagetemplates_salecouponprograms_couponprogramid`: (couponprogramid) -> `dbo.salecouponprograms` (id)

### `dbo.tcaremessagingpartnerrels`

- Row count: **0**
- Primary key: `messagingid, partnerid`
- Columns (2): messagingid (uuid NOT NULL), partnerid (uuid NOT NULL)
- Key foreign keys:
  - `fk_tcaremessagingpartnerrels_partners_partnerid`: (partnerid) -> `dbo.partners` (id)
  - `fk_tcaremessagingpartnerrels_tcaremessagings_messagingid`: (messagingid) -> `dbo.tcaremessagings` (id)

### `dbo.tcaremessagings`

- Row count: **0**
- Primary key: `id`
- Columns (12): id (uuid NOT NULL), scheduledate (timestamp without time zone), content (text), tcarecampaignid (uuid NOT NULL), facebookpageid (uuid), state (text), messagingmodel (text), couponprogramid (uuid), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_tcaremessagings_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_tcaremessagings_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_tcaremessagings_facebookpages_facebookpageid`: (facebookpageid) -> `dbo.facebookpages` (id)
  - `fk_tcaremessagings_salecouponprograms_couponprogramid`: (couponprogramid) -> `dbo.salecouponprograms` (id)
  - `fk_tcaremessagings_tcarecampaigns_tcarecampaignid`: (tcarecampaignid) -> `dbo.tcarecampaigns` (id)

### `dbo.tcareproperties`

- Row count: **0**
- Primary key: `id`
- Columns (14): id (uuid NOT NULL), ruleid (uuid NOT NULL), name (text), type (text NOT NULL), valuetext (text), valueinteger (integer), valuedatetime (timestamp without time zone), valuedecimal (numeric(18,2)), valuedouble (double precision), valuereference (text), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_tcareproperties_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_tcareproperties_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_tcareproperties_tcarerules_ruleid`: (ruleid) -> `dbo.tcarerules` (id)

### `dbo.tcarerules`

- Row count: **0**
- Primary key: `id`
- Columns (7): id (uuid NOT NULL), campaignid (uuid NOT NULL), type (text NOT NULL), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_tcarerules_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_tcarerules_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_tcarerules_tcarecampaigns_campaignid`: (campaignid) -> `dbo.tcarecampaigns` (id)

### `dbo.tcarescenarios`

- Row count: **0**
- Primary key: `id`
- Columns (15): id (uuid NOT NULL), name (text), channelsocialid (uuid), channaltype (text), type (text), autocustomtype (text), customday (integer), custommonth (integer), customhour (integer), customminute (integer), jobid (text), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_tcarescenarios_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_tcarescenarios_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_tcarescenarios_facebookpages_channelsocialid`: (channelsocialid) -> `dbo.facebookpages` (id)

### `dbo.teeth`

- Row count: **52**
- Primary key: `id`
- Columns (9): id (uuid NOT NULL), name (text NOT NULL), categoryid (uuid NOT NULL), vitriham (text), position (text), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_teeth_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_teeth_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_teeth_toothcategories_categoryid`: (categoryid) -> `dbo.toothcategories` (id)

### `dbo.toathuoclines`

- Row count: **0**
- Primary key: `id`
- Columns (17): id (uuid NOT NULL), name (text), toathuocid (uuid NOT NULL), productid (uuid NOT NULL), productuomid (uuid), sequence (integer), numberoftimes (integer NOT NULL), numberofdays (integer NOT NULL), amountoftimes (numeric(18,2) NOT NULL), quantity (numeric(18,2) NOT NULL), useat (text), note (text), toinvoicequantity (numeric(18,2)), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_toathuoclines_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_toathuoclines_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_toathuoclines_products_productid`: (productid) -> `dbo.products` (id)
  - `fk_toathuoclines_toathuocs_toathuocid`: (toathuocid) -> `dbo.toathuocs` (id)
  - `fk_toathuoclines_uoms_productuomid`: (productuomid) -> `dbo.uoms` (id)

### `dbo.toathuocs`

- Row count: **0**
- Primary key: `id`
- Columns (20): id (uuid NOT NULL), name (text NOT NULL), partnerid (uuid NOT NULL), date (timestamp without time zone NOT NULL), note (text), dotkhamid (uuid), userid (text), companyid (uuid NOT NULL), employeeid (uuid), saleorderid (uuid), reexaminationdate (timestamp without time zone), diagnostic (text), invoicestatus (text), formoftreatment (text), relativename (text), partnerphone (text), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_toathuocs_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_toathuocs_aspnetusers_userid`: (userid) -> `dbo.aspnetusers` (id)
  - `fk_toathuocs_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_toathuocs_companies_companyid`: (companyid) -> `dbo.companies` (id)
  - `fk_toathuocs_dotkhams_dotkhamid`: (dotkhamid) -> `dbo.dotkhams` (id)
  - `fk_toathuocs_employees_employeeid`: (employeeid) -> `dbo.employees` (id)
  - `fk_toathuocs_partners_partnerid`: (partnerid) -> `dbo.partners` (id)
  - `fk_toathuocs_saleorders_saleorderid`: (saleorderid) -> `dbo.saleorders` (id)

### `dbo.toothcategories`

- Row count: **2**
- Primary key: `id`
- Columns (7): id (uuid NOT NULL), name (text NOT NULL), sequence (integer), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_toothcategories_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_toothcategories_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)

### `dbo.toothdiagnosis`

- Row count: **300**
- Primary key: `id`
- Columns (8): id (uuid NOT NULL), name (text NOT NULL), companyid (uuid), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone), code (text)
- Key foreign keys:
  - `fk_toothdiagnosis_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_toothdiagnosis_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_toothdiagnosis_companies_companyid`: (companyid) -> `dbo.companies` (id)

### `dbo.toothdiagnosisproductrels`

- Row count: **0**
- Primary key: `toothdiagnosisid, productid`
- Columns (2): toothdiagnosisid (uuid NOT NULL), productid (uuid NOT NULL)
- Key foreign keys:
  - `fk_toothdiagnosisproductrels_products_productid`: (productid) -> `dbo.products` (id)
  - `fk_toothdiagnosisproductrels_toothdiagnosis_toothdiagnosisid`: (toothdiagnosisid) -> `dbo.toothdiagnosis` (id)

### `dbo.toothinitials`

- Row count: **0**
- Primary key: `id`
- Columns (15): id (uuid NOT NULL), toothname (text), partnerid (uuid NOT NULL), ismissing (boolean NOT NULL), isprimary (boolean NOT NULL), protate (integer NOT NULL), occlusal (integer NOT NULL), mesial (integer NOT NULL), mesialtip (integer NOT NULL), facial (integer NOT NULL), facialtip (integer NOT NULL), datecreated (timestamp without time zone), createdbyid (text), lastupdated (timestamp without time zone), writebyid (text)
- Key foreign keys:
  - `fk_toothinitials_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_toothinitials_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_toothinitials_partners_partnerid`: (partnerid) -> `dbo.partners` (id)

### `dbo.toothprocedures`

- Row count: **536**
- Primary key: `id`
- Columns (30): id (uuid NOT NULL), date (timestamp without time zone NOT NULL), description (text), partnerid (uuid NOT NULL), diagnosisid (uuid), productid (uuid), toothsurface (text), priceunit (numeric(18,2) NOT NULL), prognosis (text), priority (text), companyid (uuid), state (text), datecreated (timestamp without time zone), createdbyid (text), lastupdated (timestamp without time zone), writebyid (text), salelineid (uuid), toothname (text), doctorid (uuid), procstatus (integer NOT NULL), toothrange (text), unitqty (integer NOT NULL), userid (text), amountdiscount (numeric(18,2) NOT NULL), amounttotal (numeric(18,2) NOT NULL), discountfixed (numeric(18,2)), discountpercent (numeric(18,2)), discounttype (text), toothtype (text), toothtypefilter (integer NOT NULL)
- Key foreign keys:
  - `fk_toothprocedures_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_toothprocedures_aspnetusers_userid`: (userid) -> `dbo.aspnetusers` (id)
  - `fk_toothprocedures_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_toothprocedures_companies_companyid`: (companyid) -> `dbo.companies` (id)
  - `fk_toothprocedures_employees_doctorid`: (doctorid) -> `dbo.employees` (id)
  - `fk_toothprocedures_partners_partnerid`: (partnerid) -> `dbo.partners` (id)
  - `fk_toothprocedures_products_productid`: (productid) -> `dbo.products` (id)
  - `fk_toothprocedures_saleorderlines_salelineid`: (salelineid) -> `dbo.saleorderlines` (id)
  - ... and 1 more

### `dbo.uomcategories`

- Row count: **5**
- Primary key: `id`
- Columns (7): id (uuid NOT NULL), name (text NOT NULL), measuretype (text NOT NULL), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_uomcategories_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_uomcategories_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)

### `dbo.uoms`

- Row count: **418**
- Primary key: `id`
- Columns (12): id (uuid NOT NULL), name (text NOT NULL), rounding (numeric(18,2) NOT NULL), active (boolean NOT NULL), factor (double precision NOT NULL), uomtype (text NOT NULL), categoryid (uuid NOT NULL), measuretype (text), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_uoms_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_uoms_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_uoms_uomcategories_categoryid`: (categoryid) -> `dbo.uomcategories` (id)

### `dbo.userbackupcodes`

- Row count: **0**
- Primary key: `id`
- Columns (11): id (uuid NOT NULL), userid (text NOT NULL), codehash (text), used (boolean NOT NULL), usedat (timestamp without time zone), datecreated (timestamp without time zone), createdbyid (text), lastupdated (timestamp without time zone), writebyid (text), hashcode (bytea), enscryptcode (text)
- Key foreign keys:
  - `fk_userbackupcodes_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_userbackupcodes_aspnetusers_userid`: (userid) -> `dbo.aspnetusers` (id)
  - `fk_userbackupcodes_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)

### `dbo.userdevices`

- Row count: **1689**
- Primary key: `id`
- Columns (22): id (uuid NOT NULL), userid (text NOT NULL), devicename (text), deviceid (text), devicetype (text), platform (text), browser (text), useragent (text), lastactivity (timestamp without time zone), note (text), datecreated (timestamp without time zone), createdbyid (text), lastupdated (timestamp without time zone), writebyid (text), city (text), country (text), firstactivity (timestamp without time zone), ipaddress (text), revoked (boolean), sessionidentifier (text), istrusteddevice (boolean NOT NULL), trusteduntil (timestamp without time zone)
- Key foreign keys:
  - `fk_userdevices_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_userdevices_aspnetusers_userid`: (userid) -> `dbo.aspnetusers` (id)
  - `fk_userdevices_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)

### `dbo.userrefreshtokens`

- Row count: **20873**
- Primary key: `id`
- Columns (8): id (uuid NOT NULL), token (text NOT NULL), userid (text), expiration (timestamp without time zone), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_userrefreshtokens_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_userrefreshtokens_aspnetusers_userid`: (userid) -> `dbo.aspnetusers` (id)
  - `fk_userrefreshtokens_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)

### `dbo.workentrytypes`

- Row count: **0**
- Primary key: `id`
- Columns (13): id (uuid NOT NULL), name (text), code (text), sequence (integer), active (boolean NOT NULL), ishastimekeeping (boolean NOT NULL), color (text), rounddays (text), rounddaystype (text), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_workentrytypes_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_workentrytypes_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)

### `dbo.zalooaconfigs`

- Row count: **0**
- Primary key: `id`
- Columns (10): id (uuid NOT NULL), name (text NOT NULL), accesstoken (text), avatar (text), autosendbirthdaymessage (boolean NOT NULL), birthdaymessagecontent (text), createdbyid (text), writebyid (text), datecreated (timestamp without time zone), lastupdated (timestamp without time zone)
- Key foreign keys:
  - `fk_zalooaconfigs_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_zalooaconfigs_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)

### `dbo.zalotemplates`

- Row count: **0**
- Primary key: `id`
- Columns (11): id (uuid NOT NULL), name (text), templateid (integer), socialaccountid (uuid), datecreated (timestamp without time zone), createdbyid (text), lastupdated (timestamp without time zone), writebyid (text), previewurl (text), price (numeric(18,2) NOT NULL), resmodel (text)
- Key foreign keys:
  - `fk_zalotemplates_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_zalotemplates_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_zalotemplates_socialaccounts_socialaccountid`: (socialaccountid) -> `dbo.socialaccounts` (id)

### `dbo.znscomposers`

- Row count: **0**
- Primary key: `id`
- Columns (10): id (uuid NOT NULL), compositionmode (text), resmodel (text), resids (text), templateid (uuid), datecreated (timestamp without time zone), createdbyid (text), lastupdated (timestamp without time zone), writebyid (text), baseautomationv2id (uuid)
- Key foreign keys:
  - `fk_znscomposers_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_znscomposers_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_znscomposers_baseautomationv2s_baseautomationv2id`: (baseautomationv2id) -> `dbo.baseautomationv2s` (id)
  - `fk_znscomposers_zalotemplates_templateid`: (templateid) -> `dbo.zalotemplates` (id)

### `dbo.znsmessages`

- Row count: **0**
- Primary key: `id`
- Columns (19): id (uuid NOT NULL), number (text), state (text), templateid (uuid), failurereason (text), datecreated (timestamp without time zone), createdbyid (text), lastupdated (timestamp without time zone), writebyid (text), socialaccountid (uuid), templatedata (text), znstemplateid (text), partnerid (uuid), failuretype (text), mailmessageid (uuid), trackingid (text), errorcode (integer), baseautomationv2id (uuid), rowversion (bytea)
- Key foreign keys:
  - `fk_znsmessages_aspnetusers_createdbyid`: (createdbyid) -> `dbo.aspnetusers` (id)
  - `fk_znsmessages_aspnetusers_writebyid`: (writebyid) -> `dbo.aspnetusers` (id)
  - `fk_znsmessages_baseautomationv2s_baseautomationv2id`: (baseautomationv2id) -> `dbo.baseautomationv2s` (id)
  - `fk_znsmessages_mailmessages_mailmessageid`: (mailmessageid) -> `dbo.mailmessages` (id)
  - `fk_znsmessages_partners_partnerid`: (partnerid) -> `dbo.partners` (id)
  - `fk_znsmessages_socialaccounts_socialaccountid`: (socialaccountid) -> `dbo.socialaccounts` (id)
  - `fk_znsmessages_zalotemplates_templateid`: (templateid) -> `dbo.zalotemplates` (id)
