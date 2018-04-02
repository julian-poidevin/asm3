#!/usr/bin/python

import configuration
import financial
import re
import utils
from i18n import _, add_days, now

# Look up tables map
# tablename : ( tablelabel, namefield, namelabel, descfield, hasspecies, haspfspecies, haspfbreed, hasapcolour, hasdefaultcost, hasunits, hassite, canadd, candelete, canretire,(foreignkeys) )
LOOKUP_TABLES = {
    "lksaccounttype":   (_("Account Types"), "AccountType", _("Type"), "", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, ("accounts.AccountType",)),
    "lkanimalflags":    (_("Animal Flags"), "Flag", _("Flag"), "", 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, ""),
    "animaltype":       (_("Animal Types"), "AnimalType", _("Type"), "AnimalDescription", 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, ("animal.AnimalTypeID",)),
    "basecolour":       (_("Colors"), "BaseColour", _("Color"), "BaseColourDescription", 0, 0, 0, 1, 0, 0, 0, 1, 1, 1, ("animal.BaseColourID", "animallost.BaseColourID", "animalfound.BaseColourID")),
    "breed":            (_("Breeds"), "BreedName", _("Breed"), "BreedDescription", 1, 0, 1, 0, 0, 0, 0, 1, 1, 1, ("animal.BreedID", "animal.Breed2ID", "animallost.BreedID", "animalfound.BreedID")),
    "lkcoattype":       (_("Coat Types"), "CoatType", _("Coat Type"), "", 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, ("animal.CoatType",)),
    "citationtype":     (_("Citation Types"), "CitationName", _("Citation Type"), "CitationDescription", 0, 0, 0, 0, 1, 0, 0, 1, 1, 1, ("ownercitation.CitationTypeID",)),
    "costtype":         (_("Cost Types"), "CostTypeName", _("Cost Type"), "CostTypeDescription", 0, 0, 0, 0, 1, 0, 0, 1, 1, 1, ("animalcost.CostTypeID",)),
    "deathreason":      (_("Death Reasons"), "ReasonName", _("Reason"), "ReasonDescription", 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, ("animal.PTSReasonID",)),
    "diet":             (_("Diets"), "DietName", _("Diet"), "DietDescription", 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, ("animaldiet.DietID",)),
    "donationpayment":  (_("Payment Methods"), "PaymentName", _("Type"), "PaymentDescription", 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, ("ownerdonation.DonationPaymentID",)),
    "donationtype":     (_("Payment Types"), "DonationName", _("Type"), "DonationDescription", 0, 0, 0, 0, 1, 0, 0, 1, 1, 1, ("ownerdonation.DonationTypeID", "accounts.DonationTypeID")),
    "entryreason":      (_("Entry Reasons"), "ReasonName", _("Reason"), "ReasonDescription", 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, ("animal.EntryReasonID", "adoption.ReturnedReasonID") ),
    "incidentcompleted":(_("Incident Completed Types"), "CompletedName", _("Completed Type"), "CompletedDescription", 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, ("animalcontrol.IncidentCompletedID",)),
    "incidenttype":     (_("Incident Types"), "IncidentName", _("Type"), "IncidentDescription", 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, ("animalcontrol.IncidentTypeID",)),
    "internallocation": (_("Internal Locations"), "LocationName", _("Location"), "LocationDescription", 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, ("animal.ShelterLocation",)),
    "jurisdiction":     (_("Jurisdictions"), "JurisdictionName", _("Jurisdiction"), "JurisdictionDescription", 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, ("animalcontrol.JurisdictionID","owner.JurisdictionID")),
    "licencetype":      (_("License Types"), "LicenceTypeName", _("Type"), "LicenceTypeDescription", 0, 0, 0, 0, 1, 0, 0, 1, 1, 1, ("ownerlicence.LicenceTypeID",)),
    "logtype":          (_("Log Types"), "LogTypeName", _("Type"), "LogTypeDescription", 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, ("log.LogTypeID",)),
    "lksmovementtype":  (_("Movement Types"), "MovementType", _("Type"), "", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, ("adoption.MovementType", "animal.ActiveMovementType",)),
    "lkownerflags":     (_("Person Flags"), "Flag", _("Flag"), "", 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, ""),
    "lksrotatype":      (_("Rota Types"), "RotaType", _("Type"), "", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, ("ownerrota.RotaTypeID",)),
    "lksex":            (_("Sexes"), "Sex", _("Sex"), "", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, ("animal.Sex", "animallost.Sex", "animalfound.Sex")),
    "lksize":           (_("Sizes"), "Size", _("Size"), "", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, ("animal.Size",)),
    "lksyesno":         (_("Yes/No"), "Name", _("Yes/No"), "", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, ("animal.Neutered",)),
    "lksynun":          (_("Yes/No/Unknown"), "Name", _("Yes/No/Unknown"), "", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, ("animal.IsHouseTrained",)),
    "lksposneg":        (_("Positive/Negative"), "Name", _("Positive/Negative"), "", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, ("animal.CombiTestResult",)),
    "pickuplocation":   (_("Pickup Locations"), "LocationName", _("Location"), "LocationDescription", 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, ("animal.PickupLocationID",)),
    "reservationstatus": (_("Reservation Statuses"), "StatusName", _("Status"), "StatusDescription", 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, ("adoption.ReservationStatusID",)),
    "site":             (_("Sites"), "SiteName", _("Site"), "", 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, ("users.SiteID","internallocation.SiteID")),
    "species":          (_("Species"), "SpeciesName", _("Species"), "SpeciesDescription", 0, 1, 0, 0, 0, 0, 0, 1, 1, 1, ("animal.SpeciesID", "animallost.AnimalTypeID", "animalfound.AnimalTypeID")),
    "stocklocation":    (_("Stock Locations"), "LocationName", _("Location"), "LocationDescription", 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, ("stocklevel.StockLocationID",)),
    "stockusagetype":   (_("Stock Usage Type"), "UsageTypeName", _("Usage Type"), "UsageTypeDescription", 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, ("stockusage.StockUsageTypeID",)),
    "lkurgency":        (_("Urgencies"), "Urgency", _("Urgency"), "", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, ("animalwaitinglist.Urgency",)),
    "testtype":         (_("Test Types"), "TestName", _("Type"), "TestDescription", 0, 0, 0, 0, 1, 0, 0, 1, 1, 1, ("animaltest.TestTypeID",)),
    "testresult":       (_("Test Results"), "ResultName", _("Result"), "ResultDescription", 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, ("animaltest.TestResultID",)),
    "transporttype":    (_("Transport Types"), "TransportTypeName", _("Type"), "TransportTypeDescription", 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, ("animaltransport.TransportTypeID",)),
    "traptype":         (_("Trap Types"), "TrapTypeName", _("Type"), "TrapTypeDescription", 0, 0, 0, 0, 1, 0, 0, 1, 1, 1, ("ownertraploan.TrapTypeID",)),
    "vaccinationtype":  (_("Vaccination Types"), "VaccinationType", _("Type"), "VaccinationDescription", 0, 0, 0, 0, 1, 0, 0, 1, 1, 1, ("animalvaccination.VaccinationID",)),
    "voucher":          (_("Voucher Types"), "VoucherName", _("Type"), "VoucherDescription", 0, 0, 0, 0, 1, 0, 0, 1, 1, 1, ("ownervoucher.VoucherID",)),
    "lkworktype":       (_("Work Types"), "WorkType", _("Type"), "", 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, ("ownerrota.WorkTypeID",))
}
LOOKUP_TABLELABEL = 0
LOOKUP_NAMEFIELD = 1
LOOKUP_NAMELABEL = 2
LOOKUP_DESCFIELD = 3
LOOKUP_HASSPECIES = 4
LOOKUP_HASPFSPECIES = 5
LOOKUP_HASPFBREED = 6
LOOKUP_HASAPCOLOUR = 7
LOOKUP_HASCOST = 8
LOOKUP_HASUNITS = 9
LOOKUP_HASSITE = 10
LOOKUP_CANADD = 11
LOOKUP_CANDELETE = 12
LOOKUP_CANRETIRE = 13
LOOKUP_FOREIGNKEYS = 14

# Database of microchip manufacturer prefixes. locales is a space separated list of
# locales the pattern is valid for (blank is all locales)
MICROCHIP_MANUFACTURERS = [
    { "length": 16, "regex": r"^AVID", "name": "AVID", "locales": "" },
    { "length": 14, "regex": r"^TR", "name": "AKC Reunite", "locales": "" },
    { "length": 9,  "regex": r"^\d+$", "name": "AVID", "locales": "" },
    { "length": 11, "regex": r"^\d{3}\*\d{3}\*\d{3}", "name": "AVID", "locales": "" },
    { "length": 11, "regex": r"^\d{3}\-\d{3}\-\d{3}", "name": "AVID", "locales": "" },
    { "length": 10, "regex": r"^0A1", "name": "24PetWatch", "locales": "" },
    { "length": 10, "regex": r"0D", "name": "Banfield", "locales": "" },
    { "length": 10, "regex": r"^0A0", "name": "Microchip ID", "locales": "" },
    { "length": 10, "regex": r"^0006", "name": "AKC Reunite", "locales": "" },
    { "length": 10, "regex": r"^0007", "name": "AKC Reunite", "locales": "" },
    { "length": 10, "regex": r"^0C0", "name": "M4S ID", "locales": "" },
    { "length": 10, "regex": r"^1\d+A", "name": "AVID Europe", "locales": "" }, 
    { "length": 10, "regex": r"^4", "name": "HomeAgain", "locales": "" }, 
    { "length": 15, "regex": r"^360981", "name": "Novartis", "locales": "" },
    { "length": 15, "regex": r"^578098", "name": "Kruuse Norge", "locales": "" },
    { "length": 15, "regex": r"^578077", "name": "AVID Friendchip Norway", "locales": "" },
    { "length": 15, "regex": r"^578094", "name": "AVID Friendchip Norway", "locales": "" },
    { "length": 15, "regex": r"^688", "name": "Serbia", "locales": "" },
    { "length": 15, "regex": r"^90007400", "name": "SmartTag", "locales": "" },
    { "length": 15, "regex": r"^90007900", "name": "PetLog", "locales": "en_GB" },
    { "length": 15, "regex": r"^900008", "name": "Orthana Intertrade", "locales": "" },
    { "length": 15, "regex": r"^900023", "name": "Asian Information Technology", "locales": "" },
    { "length": 15, "regex": r"^900026", "name": "Petsafe", "locales": "" },
    { "length": 15, "regex": r"^900042", "name": "Royal Tag", "locales": "" },
    { "length": 15, "regex": r"^900088", "name": "Insprovet", "locales": "" },
    { "length": 15, "regex": r"^900118", "name": "SmartChip", "locales": "" },
    { "length": 15, "regex": r"^900128", "name": "Gepe-Geimuplast", "locales": "" },
    { "length": 15, "regex": r"^900138", "name": "ID-Ology", "locales": "" },
    { "length": 15, "regex": r"^900139", "name": "SmartTag", "locales": "" },
    { "length": 15, "regex": r"^900164", "name": "Save This Life", "locales": "" },
    { "length": 15, "regex": r"^900182", "name": "Petlog", "locales": "" },
    { "length": 15, "regex": r"^900141", "name": "SmartTag", "locales": "" },
    { "length": 15, "regex": r"^900", "name": "BCDS", "locales": "" },
    { "length": 15, "regex": r"^911002", "name": "911PetChip", "locales": "" },
    { "length": 15, "regex": r"^939", "name": "M4S ID", "locales": "" },
    { "length": 15, "regex": r"^9410000", "name": "PetKey", "locales": "" },
    { "length": 15, "regex": r"^941", "name": "Felixcan", "locales": "" },
    { "length": 15, "regex": r"^943", "name": "BCDS", "locales": "" },
    { "length": 15, "regex": r"^945", "name": "BCDS", "locales": "" },
    { "length": 15, "regex": r"^952", "name": "M4S ID", "locales": "" },
    { "length": 15, "regex": r"^953", "name": "Virbac/PetLog", "locales": "en_GB" },
    { "length": 15, "regex": r"^95301", "name": "Australasian Animal Registry", "locales": "en_AU" },
    { "length": 15, "regex": r"^955", "name": "Biolog-ID", "locales": "" },
    { "length": 15, "regex": r"^956", "name": "AKC Reunite", "locales": "" },
    { "length": 15, "regex": r"^965", "name": "4D Technology/Petsafe", "locales": "" },
    { "length": 15, "regex": r"^960011", "name": "PetProtect", "locales": "" },
    { "length": 15, "regex": r"^965", "name": "Microchip ID", "locales": "" },
    { "length": 15, "regex": r"^966", "name": "Petlog", "locales": "" },
    { "length": 15, "regex": r"^968", "name": "AKC CAR", "locales": "" },
    { "length": 15, "regex": r"^972", "name": "Planet ID", "locales": "" },
    { "length": 15, "regex": r"^977", "name": "AVID Europe", "locales": "" },
    { "length": 15, "regex": r"^978", "name": "Chevillot/Back Home", "locales": "" },
    { "length": 15, "regex": r"^980000", "name": "Agrident", "locales": "" },
    { "length": 15, "regex": r"^98101", "name": "DataMARS/Banfield", "locales": "" },
    { "length": 15, "regex": r"^98102", "name": "DataMARS/PetLink", "locales": "" },
    { "length": 15, "regex": r"^981", "name": "DataMARS/Bayer ResQ", "locales": "" },
    { "length": 15, "regex": r"^982009", "name": "Allflex", "locales": "" },
    { "length": 15, "regex": r"^982", "name": "24PetWatch", "locales": "" },
    { "length": 15, "regex": r"^984", "name": "Nedap", "locales": "" },
    { "length": 15, "regex": r"^9851", "name": "Anibase/Identichip", "locales": "en_GB" },
    { "length": 15, "regex": r"^985", "name": "HomeAgain", "locales": "" },
    { "length": 15, "regex": r"^9861", "name": "Anibase/Identichip", "locales": "en_GB" },
    { "length": 15, "regex": r"^99000000", "name": "nanoChip", "locales": "" },
    { "length": 15, "regex": r"^99100100", "name": "HomeSafe", "locales": "en_AU" },
    { "length": 15, "regex": r"^999", "name": "Transponder Test", "locales": ""}
]

VISUAL_THEMES = [
    ( "asm", "ASM" ),
    ( "black-tie", "Black Tie" ),
    ( "blitzer", "Blitzer" ),
    ( "cupertino", "Cupertino") ,
    ( "dark-hive", "Dark Hive"), 
    ( "dot-luv", "Dot Luv"),
    ( "eggplant", "Eggplant"),
    ( "excite-bike", "Excite Bike"),
    ( "flick", "Flick"),
    ( "hot-sneaks", "Hot Sneaks"),
    ( "humanity", "Humanity"),
    ( "le-frog", "Le Frog"),
    ( "mint-choc", "Mint Choc"),
    ( "overcast", "Overcast"),
    ( "pepper-grinder", "Pepper Grinder"),
    ( "redmond", "Redmond"),
    ( "smoothness", "Smoothness"),
    ( "south-street", "South Street"),
    ( "start", "Start"),
    ( "sunny", "Sunny"),
    ( "swanky-purse", "Swanky Purse"),
    ( "trontastic", "Trontastic"),
    ( "ui-darkness", "UI Darkness"),
    ( "ui-lightness", "UI Lightness"),
    ( "vader", "Vader")
]

PETFINDER_BREEDS = (
    "Affenpinscher",
    "Afghan Hound",
    "Airedale Terrier",
    "Akbash",
    "Akita",
    "Alaskan Malamute",
    "American Bulldog",
    "American Eskimo Dog",
    "American Staffordshire Terrier",
    "American Water Spaniel",
    "Anatolian Shepherd",
    "Appenzell Mountain Dog",
    "Australian Cattle Dog/Blue Heeler",
    "Australian Kelpie",
    "Australian Shepherd",
    "Australian Terrier",
    "Basenji",
    "Basset Hound",
    "Beagle",
    "Bearded Collie",
    "Beauceron",
    "Bedlington Terrier",
    "Belgian Shepherd Dog Sheepdog",
    "Belgian Shepherd Laekenois",
    "Belgian Shepherd Malinois",
    "Belgian Shepherd Tervuren ",
    "Bernese Mountain Dog",
    "Bichon Frise",
    "Black and Tan Coonhound",
    "Black Labrador Retriever",
    "Black Mouth Cur",
    "Bloodhound",
    "Bluetick Coonhound",
    "Border Collie",
    "Border Terrier",
    "Borzoi",
    "Boston Terrier",
    "Bouvier des Flanders",
    "Boykin Spaniel",
    "Boxer",
    "Briard",
    "Brittany Spaniel",
    "Brussels Griffon",
    "Bull Terrier",
    "Bullmastiff",
    "Cairn Terrier",
    "Canaan Dog",
    "Cane Corso Mastiff",
    "Carolina Dog",
    "Catahoula Leopard Dog",
    "Cattle Dog",
    "Cavalier King Charles Spaniel",
    "Chesapeake Bay Retriever",
    "Chihuahua",
    "Chinese Crested Dog",
    "Chinese Foo Dog",
    "Chocolate Labrador Retriever",
    "Chow Chow",
    "Clumber Spaniel",
    "Cockapoo",
    "Cocker Spaniel",
    "Collie",
    "Coonhound",
    "Corgi",
    "Coton de Tulear",
    "Dachshund",
    "Dalmatian",
    "Dandie Dinmont Terrier",
    "Doberman Pinscher",
    "Dogo Argentino",
    "Dogue de Bordeaux",
    "Dutch Shepherd",
    "English Bulldog",
    "English Cocker Spaniel",
    "English Coonhound",
    "English Pointer",
    "English Setter",
    "English Shepherd",
    "English Springer Spaniel",
    "English Toy Spaniel",
    "Entlebucher",
    "Eskimo Dog",
    "Feist",
    "Field Spaniel",
    "Fila Brasileiro",
    "Finnish Lapphund",
    "Finnish Spitz",
    "Flat-coated Retriever",
    "Fox Terrier",
    "Foxhound",
    "French Bulldog",
    "German Pinscher",
    "German Shepherd Dog",
    "German Shorthaired Pointer",
    "German Wirehaired Pointer",
    "Glen of Imaal Terrier",
    "Golden Retriever",
    "Gordon Setter",
    "Great Dane",
    "Great Pyrenees",
    "Greater Swiss Mountain Dog",
    "Greyhound",
    "Harrier",
    "Havanese",
    "Hound",
    "Hovawart",
    "Husky",
    "Ibizan Hound",
    "Illyrian Sheepdog",
    "Irish Setter",
    "Irish Terrier",
    "Irish Water Spaniel",
    "Irish Wolfhound",
    "Italian Greyhound",
    "Italian Spinone",
    "Jack Russell Terrier",
    "Japanese Chin",
    "Jindo",
    "Kai Dog",
    "Karelian Bear Dog",
    "Keeshond",
    "Kerry Blue Terrier",
    "Kishu",
    "Komondor",
    "Kuvasz",
    "Kyi Leo",
    "Labrador Retriever",
    "Lakeland Terrier",
    "Lancashire Heeler",
    "Lhasa Apso",
    "Leonberger",
    "Lowchen",
    "Maltese",
    "Manchester Terrier",
    "Maremma Sheepdog",
    "Mastiff",
    "McNab",
    "Miniature Pinscher",
    "Mixed Breed",
    "Mountain Cur",
    "Mountain Dog",
    "Munsterlander",
    "Neapolitan Mastiff",
    "New Guinea Singing Dog",
    "Newfoundland Dog",
    "Norfolk Terrier",
    "Norwich Terrier",
    "Norwegian Buhund",
    "Norwegian Elkhound",
    "Norwegian Lundehund",
    "Nova Scotia Duck-Tolling Retriever",
    "Old English Sheepdog",
    "Otterhound",
    "Papillon",
    "Patterdale Terrier (Fell Terrier)",
    "Pekingese",
    "Peruvian Inca Orchid",
    "Petit Basset Griffon Vendeen",
    "Pharaoh Hound",
    "Pit Bull Terrier",
    "Plott Hound",
    "Podengo Portugueso",
    "Pointer",
    "Polish Lowland Sheepdog",
    "Pomeranian",
    "Poodle",
    "Portuguese Water Dog",
    "Presa Canario",
    "Pug",
    "Puli",
    "Pumi",
    "Rat Terrier",
    "Redbone Coonhound",
    "Retriever",
    "Rhodesian Ridgeback",
    "Rottweiler",
    "Saluki",
    "Saint Bernard St. Bernard",
    "Samoyed",
    "Schipperke",
    "Schnauzer",
    "Scottish Deerhound",
    "Scottish Terrier Scottie",
    "Sealyham Terrier",
    "Setter",
    "Shar Pei",
    "Sheep Dog",
    "Shepherd",
    "Shetland Sheepdog Sheltie",
    "Shiba Inu",
    "Shih Tzu",
    "Siberian Husky",
    "Silky Terrier",
    "Skye Terrier",
    "Sloughi",
    "Smooth Fox Terrier",
    "Spaniel",
    "Spitz",
    "Staffordshire Bull Terrier",
    "South Russian Ovcharka",
    "Swedish Vallhund",
    "Terrier",
    "Thai Ridgeback",
    "Tibetan Mastiff",
    "Tibetan Spaniel",
    "Tibetan Terrier",
    "Tosa Inu",
    "Toy Fox Terrier",
    "Treeing Walker Coonhound",
    "Vizsla",
    "Weimaraner",
    "Welsh Corgi",
    "Welsh Terrier",
    "Welsh Springer Spaniel",
    "West Highland White Terrier Westie",
    "Wheaten Terrier",
    "Whippet",
    "White German Shepherd",
    "Wire-haired Pointing Griffon",
    "Wirehaired Terrier",
    "Yellow Labrador Retriever",
    "Yorkshire Terrier Yorkie",
    "Xoloitzcuintle/Mexican Hairless",
    "Abyssinian",
    "American Curl",
    "American Shorthair",
    "American Wirehair",
    "Applehead Siamese",
    "Balinese",
    "Bengal",
    "Birman",
    "Bobtail",
    "Bombay",
    "British Shorthair",
    "Burmese",
    "Burmilla",
    "Calico",
    "Canadian Hairless",
    "Chartreux",
    "Chinchilla",
    "Cornish Rex",
    "Cymric",
    "Devon Rex",
    "Dilute Calico",
    "Dilute Tortoiseshell",
    "Domestic Long Hair",
    "Domestic Long Hair-black",
    "Domestic Long Hair - buff",
    "Domestic Long Hair-gray",
    "Domestic Long Hair - orange",
    "Domestic Long Hair - orange and white",
    "Domestic Long Hair - gray and white",
    "Domestic Long Hair-white",
    "Domestic Long Hair-black and white",
    "Domestic Medium Hair",
    "Domestic Medium Hair-black",
    "Domestic Medium Hair - buff",
    "Domestic Medium Hair-gray",
    "Domestic Medium Hair - gray and white",
    "Domestic Medium Hair-white",
    "Domestic Medium Hair-orange",
    "Domestic Medium Hair - orange and white",
    "Domestic Medium Hair-black and white",
    "Domestic Short Hair",
    "Domestic Short Hair-black",
    "Domestic Short Hair - buff",
    "Domestic Short Hair-black and white",
    "Domestic Short Hair-gray",
    "Domestic Short Hair - gray and white",
    "Domestic Short Hair-mitted",
    "Domestic Short Hair-orange",
    "Domestic Short Hair - orange and white",
    "Domestic Short Hair-white",
    "Egyptian Mau",
    "Exotic Shorthair",
    "Extra-Toes Cat (Hemingway Polydactyl)",
    "Havana",
    "Himalayan",
    "Japanese Bobtail",
    "Javanese",
    "Korat",
    "Maine Coon",
    "Manx",
    "Munchkin",
    "Nebelung", 
    "Norwegian Forest Cat",
    "Ocicat",
    "Oriental Long Hair",
    "Oriental Short Hair",
    "Oriental Tabby",
    "Persian",
    "Pixie-Bob",
    "Ragamuffin",
    "Ragdoll",
    "Russian Blue",
    "Scottish Fold",
    "Selkirk Rex",
    "Siamese",
    "Siberian",
    "Singapura",
    "Snowshoe",
    "Somali",
    "Sphynx (hairless cat)",
    "Tabby",
    "Tabby - Orange",
    "Tabby - Grey",
    "Tabby - Brown",
    "Tabby - white",
    "Tabby - buff",
    "Tabby - black",
    "Tiger",
    "Tonkinese",
    "Torbie",
    "Tortoiseshell",
    "Turkish Angora",
    "Turkish Van",
    "Tuxedo",
    "American",
    "American Fuzzy Lop",
    "American Sable",
    "Angora Rabbit",
    "Belgian Hare",
    "Beveren",
    "Britannia Petite",
    "Bunny Rabbit",
    "Californian",
    "Champagne D'Argent",
    "Checkered Giant",
    "Chinchilla",
    "Cinnamon",
    "Creme D'Argent",
    "Dutch",
    "Dwarf",
    "Dwarf Eared",
    "English Lop",
    "English Spot",
    "Flemish Giant",
    "Florida White",
    "French-Lop",
    "Harlequin",
    "Havana",
    "Himalayan",
    "Holland Lop",
    "Hotot",
    "Jersey Wooly",
    "Lilac",
    "Lionhead",
    "Lop Eared",
    "Mini-Lop",
    "Mini Rex",
    "Netherland Dwarf",
    "New Zealand",
    "Palomino",
    "Polish",
    "Rex",
    "Rhinelander",
    "Satin",
    "Silver",
    "Silver Fox",
    "Silver Marten",
    "Tan",
    "Appaloosa",
    "Arabian",
    "Clydesdale",
    "Donkey/Mule",
    "Draft",
    "Gaited ",
    "Grade",
    "Missouri Foxtrotter",
    "Morgan",
    "Mustang",
    "Paint/Pinto",
    "Palomino",
    "Paso Fino",
    "Percheron",
    "Peruvian Paso",
    "Pony",
    "Quarterhorse",
    "Saddlebred",
    "Standardbre",
    "Thoroughbred",
    "Tennessee Walker",
    "Warmblood",
    "Chinchilla",
    "Degu",
    "Ferret",
    "Gerbil",
    "Guinea Pig",
    "Hamster",
    "Hedgehog",
    "Mouse",
    "Prairie Dog",
    "Rat",
    "Skunk",
    "Sugar Glider",
    "Pot Bellied",
    "Vietnamese Pot Bellied",
    "Asian Box",
    "Ball Python",
    "Bearded Dragon",
    "Boa",
    "Boa Constrictor",
    "Box",
    "Bull Frog",
    "Burmese Python",
    "Chameleon",
    "Corn Snake",
    "Corn/Rat",
    "Eastern Box",
    "Fire-bellied",
    "Fire-bellied Newt",
    "Fire Salamander",
    "Florida Box",
    "Frog",
    "Garter/Ribbon",
    "Gecko",
    "Goldfish",
    "Hermit Crab",
    "Horned Frog",
    "Iguana",
    "King/Milk",
    "Leopard Frog",
    "Lizard",
    "Monitor",
    "Oregon Newt",
    "Ornamental Box",
    "Paddle Tailed Newt",
    "Python",
    "Red-eared Slider",
    "Red Foot",
    "Russian",
    "Snake",
    "Sulcata",
    "Tarantula",
    "Three Toed Box",
    "Tiger Salamander",
    "Tortoise",
    "Tree Frog",
    "Toad",
    "Turtle",
    "Uromastyx",
    "Yellow-Bellied Slider", 
    "Fish",
    "Freshwater Fish",
    "Saltwater Fish",
    "African Grey",
    "Amazon",
    "Brotogeris",
    "Budgie/Budgerigar",
    "Caique",
    "Canary",
    "Chicken",
    "Cockatiel",
    "Cockatoo",
    "Conure",
    "Dove",
    "Duck",
    "Eclectus",
    "Emu",
    "Finch",
    "Goose",
    "Guinea fowl",
    "Kakariki",
    "Lory/Lorikeet",
    "Lovebird",
    "Macaw",
    "Mynah",
    "Ostrich",
    "Parakeet (Other)",
    "Parrot (Other)",
    "Parrotlet",
    "Peacock/Pea fowl",
    "Pheasant",
    "Pigeon",
    "Pionus",
    "Poicephalus/Senegal",
    "Quaker Parakeet",
    "Rhea",
    "Ringneck/Psittacula",
    "Rosella",
    "Softbill (Other)",
    "Swan",
    "Toucan",
    "Turkey",
    "Cow",
    "Goat",
    "Sheep",
    "Llama",
    "Pig (Farm)"
)

PETFINDER_SPECIES = (
    "Barnyard", "Bird", "Cat", "Dog", "Horse", "Pig", "Rabbit",
    "Reptile", "Scales, Fins & Other", "Small&Furry"
)

ADOPTAPET_COLOURS = (
    "-- Dogs --",
    "Black",
    "Black - with Tan, Yellow or Fawn",
    "Black - with White",
    "Brindle",
    "Brindle - with White",
    "Brown/Chocolate",
    "Brown/Chocolate - with Black",
    "Brown/Chocolate - with White",
    "Red/Golden/Orange/Chestnut",
    "Red/Golden/Orange/Chestnut - with Black",
    "Red/Golden/Orange/Chestnut - with White",
    "Silver & Tan (Yorkie colors)",
    "Tan/Yellow/Fawn",
    "Tan/Yellow/Fawn - with White",
    "Tricolor (Tan/Brown & Black & White)",
    "White",
    "White - with Black",
    "White - with Brown or Chocolate",
    "Black - with Brown, Red, Golden, Orange or Chestnut",
    "Black - with Gray or Silver",
    "Brown/Chocolate - with Tan",
    "Gray/Blue/Silver/Salt & Pepper",
    "Gray/Silver/Salt & Pepper - with White",
    "Gray/Silver/Salt & Pepper - with Black",
    "Merle",
    "Tan/Yellow/Fawn - with Black",
    "White - with Tan, Yellow or Fawn",
    "White - with Red, Golden, Orange or Chestnut",
    "White - with Gray or Silver",
    "-- Cats --",
    "Black (All)",
    "Cream or Ivory",
    "Cream or Ivory (Mostly)",
    "Spotted Tabby/Leopard Spotted",
    "Black (Mostly)",
    "Black & White or Tuxedo",
    "Brown or Chocolate",
    "Brown or Chocolate (Mostly)",
    "Brown Tabby",
    "Calico or Dilute Calico",
    "Gray or Blue ",
    "Gray or Blue (Mostly)",
    "Gray, Blue or Silver Tabby",
    "Orange or Red",
    "Orange or Red (Mostly)",
    "Orange or Red Tabby",
    "Tan or Fawn ",
    "Tan or Fawn (Mostly)",
    "Tan or Fawn Tabby",
    "Tiger Striped",
    "Tortoiseshell",
    "White",
    "White (Mostly)",
    "-- Horses --",
    "Palomino",
    "Gray",
    "Dun",
    "Cremello",
    "Chestnut/Sorrel",
    "Champagne",
    "Buckskin",
    "Black",
    "Bay",
    "Appy",
    "Grullo",
    "White",
    "Roan",
    "Perlino",
    "Paint",
    "-- Birds --",
    "Gray",
    "Green",
    "Olive",
    "Orange",
    "Pink",
    "Purple/Violet",
    "Red",
    "Rust",
    "Tan",
    "Buff",
    "Yellow",
    "White",
    "Black",
    "Blue",
    "Brown",
    "-- Rabbits --",
    "Sable",
    "Albino or Red-Eyed White",
    "Blue",
    "Black",
    "Blond/Golden",
    "Chinchilla",
    "Chocolate",
    "Cinnamon",
    "Copper",
    "Cream",
    "Dutch",
    "Fawn",
    "Grey/Silver",
    "Harlequin",
    "Lilac",
    "Multi",
    "Orange",
    "Red",
    "Agouti",
    "Siamese",
    "Tan",
    "Tortoise",
    "Tri-color",
    "White",
    "-- Small Animals --",
    "Yellow",
    "White",
    "Tortoiseshell",
    "Tan or Beige",
    "Silver or Gray",
    "Sable",
    "Red",
    "Orange",
    "Multi",
    "Lilac",
    "Golden",
    "Cream",
    "Calico",
    "Buff",
    "Brown or Chocolate",
    "Blonde",
    "Black",
    "Albino or Red-Eyed White"
)

def add_message(dbo, createdby, email, message, forname = "*", priority = 0, expires = None, added = None):
    if added is None: added = dbo.today()
    if expires is None: expires = dbo.today(offset=7)
    l = dbo.locale
    mid = dbo.insert("messages", {
        "Added":        added,
        "Expires":      expires,
        "CreatedBy":    createdby,
        "Priority":     priority,
        "ForName":      forname,
        "Message":      message
    })
    # If email is set, we email the message to everyone that it would match
    if email == 1:
        utils.send_user_email(dbo, createdby, forname, _("Message from {0}", l).format(createdby), message)
    return mid

def delete_message(dbo, mid):
    dbo.delete("messages", mid)

def get_account_types(dbo):
    return dbo.query("SELECT * FROM lksaccounttype ORDER BY AccountType")

def get_additionalfield_links(dbo):
    return dbo.query("SELECT * FROM lksfieldlink ORDER BY LinkType")

def get_additionalfield_types(dbo):
    return dbo.query("SELECT * FROM lksfieldtype ORDER BY FieldType")

def get_animal_flags(dbo):
    return dbo.query("SELECT * FROM lkanimalflags ORDER BY Flag")

def get_animal_types(dbo):
    return dbo.query("SELECT * FROM animaltype ORDER BY AnimalType")

def get_animaltype_name(dbo, aid):
    if id is None: return ""
    return dbo.query_string("SELECT AnimalType FROM animaltype WHERE ID = ?", [aid])

def get_basecolours(dbo):
    return dbo.query("SELECT * FROM basecolour ORDER BY BaseColour")

def get_basecolour_name(dbo, cid):
    if id is None: return ""
    return dbo.query_string("SELECT BaseColour FROM basecolour WHERE ID = ?", [cid])

def get_breeds(dbo):
    return dbo.query("SELECT * FROM breed ORDER BY BreedName")

def get_breeds_by_species(dbo):
    return dbo.query("SELECT breed.*, species.SpeciesName FROM breed " \
        "LEFT OUTER JOIN species ON breed.SpeciesID = species.ID " \
        "ORDER BY species.SpeciesName, breed.BreedName")

def get_breed_name(dbo, bid):
    if id is None: return ""
    return dbo.query_string("SELECT BreedName FROM breed WHERE ID = ?", [bid])

def get_citation_types(dbo):
    return dbo.query("SELECT * FROM citationtype ORDER BY CitationName")

def get_coattypes(dbo):
    return dbo.query("SELECT * FROM lkcoattype ORDER BY CoatType")

def get_costtypes(dbo):
    return dbo.query("SELECT * FROM costtype ORDER BY CostTypeName")

def get_coattype_name(dbo, cid):
    if id is None: return ""
    return dbo.query_string("SELECT CoatTypeName FROM lkcoattype WHERE ID = ?", [cid])

def get_deathreasons(dbo):
    return dbo.query("SELECT * FROM deathreason ORDER BY ReasonName")

def get_deathreason_name(dbo, rid):
    if id is None: return ""
    return dbo.query_string("SELECT ReasonName FROM deathreason WHERE ID = ?", [rid])

def get_diets(dbo):
    return dbo.query("SELECT * FROM diet ORDER BY DietName")

def get_donation_default(dbo, donationtypeid):
    return dbo.query_int("SELECT DefaultCost FROM donationtype WHERE ID = ?", [donationtypeid])

def get_donation_frequencies(dbo):
    return dbo.query("SELECT * FROM lksdonationfreq ORDER BY ID")

def get_donation_types(dbo):
    return dbo.query("SELECT * FROM donationtype ORDER BY DonationName")

def get_donationtype_name(dbo, did):
    if did is None: return ""
    return dbo.query_string("SELECT DonationName FROM donationtype WHERE ID = ?", [did])

def get_entryreasons(dbo):
    return dbo.query("SELECT * FROM entryreason ORDER BY ReasonName")

def get_entryreason_name(dbo, rid):
    if rid is None: return ""
    return dbo.query_string("SELECT ReasonName FROM entryreason WHERE ID = ?", [rid])

def get_incident_completed_types(dbo):
    return dbo.query("SELECT * FROM incidentcompleted ORDER BY CompletedName")

def get_incident_types(dbo):
    return dbo.query("SELECT * FROM incidenttype ORDER BY IncidentName")

def get_internal_locations(dbo, locationfilter = "", siteid = 0):
    clauses = []
    if locationfilter != "": clauses.append("ID IN (%s)" % locationfilter)
    if siteid != 0: clauses.append("SiteID = %s" % siteid)
    c = " AND ".join(clauses)
    if c != "": c = "WHERE %s" % c
    return dbo.query("SELECT * FROM internallocation %s ORDER BY LocationName" % c)

def get_internallocation_name(dbo, lid):
    if lid is None: return ""
    return dbo.query_string("SELECT LocationName FROM internallocation WHERE ID = ?", [lid])

def get_jurisdictions(dbo):
    return dbo.query("SELECT * FROM jurisdiction ORDER BY JurisdictionName")

def get_licence_types(dbo):
    return dbo.query("SELECT * FROM licencetype ORDER BY LicenceTypeName")

def get_messages(dbo, user, roles, superuser):
    """
    Returns a list of messages for the user given.
    user: The user to get messages for
    roles: A pipe separated list of roles the user is in (session.roles)
    superuser: 1 if the user is a superuser
    """
    messages = dbo.query("SELECT * FROM messages WHERE Expires >= ? ORDER BY Added DESC", [dbo.today()])
    rv = []
    # Add messages our user can see
    for m in messages:
        if m.FORNAME == "*":
            rv.append(m)
        elif m.FORNAME == user:
            rv.append(m)
        elif m.CREATEDBY == user:
            rv.append(m)
        #elif superuser == 1:
        #    rv.append(m)
        elif roles is not None and roles.find(m.FORNAME) != -1:
            rv.append(m)
    return rv

def get_log_types(dbo):
    return dbo.query("SELECT * FROM logtype ORDER BY LogTypeName")

def get_logtype_name(dbo, tid):
    if tid is None: return ""
    return dbo.query_string("SELECT LogTypeName FROM logtype WHERE ID = ?", [tid])

def get_lookup(dbo, tablename, namefield):
    if tablename == "breed":
        return dbo.query("SELECT b.*, s.SpeciesName FROM breed b LEFT OUTER JOIN species s ON s.ID = b.SpeciesID ORDER BY b.BreedName")
    return dbo.query("SELECT * FROM %s ORDER BY %s" % ( tablename, namefield ))

def insert_lookup(dbo, lookup, name, desc="", speciesid=0, pfbreed="", pfspecies="", apcolour="", units="", site=1, defaultcost=0, retired=0):
    t = LOOKUP_TABLES[lookup]
    sql = ""
    nid = 0
    if lookup == "basecolour":
        return dbo.insert("basecolour", {
            "BaseColour":               name,
            "BaseColourDescription":    desc,
            "AdoptAPetColour":          apcolour,
            "IsRetired":                retired
        })
    elif lookup == "breed":
        return dbo.insert("breed", {
            "BreedName":        name,
            "BreedDescription": desc,
            "PetFinderBreed":   pfbreed,
            "SpeciesID":        speciesid,
            "IsRetired":        retired
        })
    elif lookup == "internallocation":
        return dbo.insert("internallocation", {
            "LocationName":         name,
            "LocationDescription":  desc,
            "Units":                units,
            "SiteID":               site,
            "IsRetired":            retired
        })
    elif lookup == "species":
        return dbo.insert("species", {
            "SpeciesName":          name,
            "SpeciesDescription":   desc,
            "PetFinderSpecies":     pfspecies,
            "IsRetired":            retired
        })
    elif lookup == "donationtype" or lookup == "costtype" or lookup == "testtype" or lookup == "voucher" or lookup == "vaccinationtype" \
        or lookup == "traptype" or lookup == "licencetype" or lookup == "citationtype":
        nid = dbo.insert(lookup, {
            t[LOOKUP_NAMEFIELD]:    name,
            t[LOOKUP_DESCFIELD]:    desc,
            "DefaultCost":          defaultcost,
            "IsRetired":            retired
        })
        # Create a matching account if we have a donation type
        if lookup == "donationtype" and configuration.create_donation_trx(dbo):
            financial.insert_account_from_donationtype(dbo, nid, name, desc)
        # Same goes for cost type
        if lookup == "costtype" and configuration.create_cost_trx(dbo):
            financial.insert_account_from_costtype(dbo, nid, name, desc)
        return nid
    elif lookup == "lkownerflags" or lookup == "lkanimalflags":
        return dbo.insert(lookup, {
            t[LOOKUP_NAMEFIELD]:    name.replace(",", " ").replace("|", " ") # sanitise bad values for flags
        })
    elif t[LOOKUP_DESCFIELD] == "":
        # No description
        if t[LOOKUP_CANRETIRE] == 1:
            return dbo.insert(lookup, { t[LOOKUP_NAMEFIELD]: name, "IsRetired": retired })    
        else:
            return dbo.insert(lookup, { t[LOOKUP_NAMEFIELD]: name })    
    else:
        # Name/Description
        nid = db.get_id(dbo, lookup)
        if t[LOOKUP_CANRETIRE] == 1:
            return dbo.insert(lookup, { t[LOOKUP_NAMEFIELD]: name, t[LOOKUP_DESCFIELD]: desc, "IsRetired": retired })    
        else:
            return dbo.insert(lookup, { t[LOOKUP_NAMEFIELD]: name, t[LOOKUP_DESCFIELD]: desc })    

def update_lookup(dbo, iid, lookup, name, desc="", speciesid=0, pfbreed="", pfspecies="", apcolour="", units="", site=1, defaultcost=0, retired=0):
    t = LOOKUP_TABLES[lookup]
    sql = ""
    if lookup == "basecolour":
        dbo.update("basecolour", iid, { 
            "BaseColour":               name,
            "BaseColourDescription":    desc,
            "AdoptAPetColour":          apcolour,
            "IsRetired":                retired
        })
    elif lookup == "breed":
        dbo.update("breed", iid, {
            "BreedName":            name,
            "BreedDescription":     desc,
            "PetFinderBreed":       pfbreed,
            "SpeciesID":            speciesid,
            "IsRetired":            retired
        })
    elif lookup == "internallocation":
        dbo.update("internallocation", iid, {
            "LocationName":         name,
            "LocationDescription":  desc,
            "Units":                units,
            "SiteID":               site,
            "IsRetired":            retired
        })
    elif lookup == "species":
        dbo.update("species", iid, {
            "SpeciesName":          name,
            "SpeciesDescription":   desc,
            "PetFinderSpecies":     pfspecies,
            "IsRetired":            retired
        })
    elif lookup == "donationtype" or lookup == "costtype" or lookup == "testtype" or lookup == "voucher" or lookup == "vaccinationtype" \
        or lookup == "traptype" or lookup == "licencetype" or lookup == "citationtype":
        dbo.update(lookup, iid, {
            t[LOOKUP_NAMEFIELD]:    name,
            t[LOOKUP_DESCFIELD]:    desc,
            "DefaultCost":          defaultcost,
            "IsRetired":            retired
        })
    elif lookup == "lkownerflags" or lookup == "lkanimalflags":
        dbo.update(lookup, iid, {
            t[LOOKUP_NAMEFIELD]:    name.replace(",", " ").replace("|", " ") # sanitise bad values for flags
        })
    elif t[LOOKUP_DESCFIELD] == "":
        # No description
        if t[LOOKUP_CANRETIRE] == 1:
            dbo.update(lookup, iid, { t[LOOKUP_NAMEFIELD]: name, "IsRetired": retired })
        else:
            dbo.update(lookup, iid, { t[LOOKUP_NAMEFIELD]: name })
    else:
        # Name/Description
        if t[LOOKUP_CANRETIRE] == 1:
            dbo.update(lookup, iid, { t[LOOKUP_NAMEFIELD]: name, t[LOOKUP_DESCFIELD]: desc, "IsRetired": retired })
        else:
            dbo.update(lookup, iid, { t[LOOKUP_NAMEFIELD]: name, t[LOOKUP_DESCFIELD]: desc })

def update_lookup_retired(dbo, lookup, iid, retired):
    """ Updates lookup item with ID=iid, setting IsRetired=retired """
    dbo.update(lookup, iid, { "IsRetired": retired })

def delete_lookup(dbo, lookup, iid):
    l = dbo.locale
    t = LOOKUP_TABLES[lookup]
    for fv in t[LOOKUP_FOREIGNKEYS]:
        table, field = fv.split(".")
        if 0 < dbo.query_int("SELECT COUNT(*) FROM %s WHERE %s = %s" % (table, field, iid)):
            raise utils.ASMValidationError(_("This item is referred to in the database ({0}) and cannot be deleted until it is no longer in use.", l).format(fv))
    dbo.delete(lookup, iid)

def get_microchip_manufacturer(l, chipno):
    """
    Figures out the microchip manufacturer of chipno. 
    Returns a blank for a blank chip number and does validation for a chip number
        with no matching manufacturer.
    """
    mf = None
    if chipno is None or chipno == "": return ""
    for m in MICROCHIP_MANUFACTURERS:
        if len(chipno) == m["length"] and re.compile(m["regex"]).match(chipno):
            if m["locales"] == "" or l in m["locales"].split(" "):
                mf = m["name"]
                break
    if mf is None and (len(chipno) != 9 and len(chipno) != 10 and len(chipno) != 15):
        return _("Invalid microchip number length", l)
    if mf is None:
        return _("Unknown microchip brand", l)
    return mf

def get_movementtype_name(dbo, mid):
    if mid is None: return ""
    return dbo.query_string("SELECT MovementType FROM lksmovementtype WHERE ID = ?", [mid])

def get_movement_types(dbo):
    return dbo.query("SELECT * FROM lksmovementtype ORDER BY ID")

def get_payment_types(dbo):
    return dbo.query("SELECT * FROM donationpayment ORDER BY PaymentName")

def get_person_flags(dbo):
    return dbo.query("SELECT * FROM lkownerflags ORDER BY Flag")

def get_pickup_locations(dbo):
    return dbo.query("SELECT * FROM pickuplocation ORDER BY LocationName")

def get_posneg(dbo):
    return dbo.query("SELECT * FROM lksposneg ORDER BY Name")

def get_reservation_statuses(dbo):
    return dbo.query("SELECT * FROM reservationstatus ORDER BY StatusName")

def get_rota_types(dbo):
    return dbo.query("SELECT * FROM lksrotatype ORDER BY ID")

def get_sex_name(dbo, sid):
    if id is None: return ""
    return dbo.query_string("SELECT Sex FROM lksex WHERE ID = ?", [sid])

def get_sexes(dbo):
    return dbo.query("SELECT * FROM lksex ORDER BY Sex")

def get_sites(dbo):
    return dbo.query("SELECT * FROM site ORDER BY SiteName")

def get_site_name(dbo, sid):
    if sid is None: return ""
    return dbo.query_string("SELECT SiteName FROM site WHERE ID = ?", [sid])

def get_size_name(dbo, sid):
    if sid is None: return ""
    return dbo.query_string("SELECT Size FROM lksize WHERE ID = ?", [sid])

def get_species(dbo):
    return dbo.query("SELECT * FROM species ORDER BY SpeciesName")

def get_species_name(dbo, sid):
    if id is None: return ""
    return dbo.query_string("SELECT SpeciesName FROM species WHERE ID = ?", [sid])

def get_sizes(dbo):
    return dbo.query("SELECT * FROM lksize ORDER BY Size")

def get_stock_locations(dbo):
    return dbo.query("SELECT * FROM stocklocation ORDER BY LocationName")

def get_stock_location_name(dbo, slid):
    if slid is None: return ""
    return db.query_string(dbo, "SELECT LocationName FROM stocklocation WHERE ID = %d" % slid)

def get_stock_usage_types(dbo):
    return dbo.query("SELECT * FROM stockusagetype ORDER BY UsageTypeName")

def get_trap_types(dbo):
    return dbo.query("SELECT * FROM traptype ORDER BY TrapTypeName")

def get_urgencies(dbo):
    return dbo.query("SELECT * FROM lkurgency ORDER BY ID")

def get_urgency_name(dbo, uid):
    if id is None: return ""
    return dbo.query_string("SELECT Urgency FROM lkurgency WHERE ID = ?", [uid])

def get_test_types(dbo):
    return dbo.query("SELECT * FROM testtype ORDER BY TestName")

def get_test_results(dbo):
    return dbo.query("SELECT * FROM testresult ORDER BY ResultName")

def get_transport_types(dbo):
    return dbo.query("SELECT * FROM transporttype ORDER BY TransportTypeName")

def get_vaccination_types(dbo):
    return dbo.query("SELECT * FROM vaccinationtype ORDER BY VaccinationType")

def get_voucher_types(dbo):
    return dbo.query("SELECT * FROM voucher ORDER BY VoucherName")

def get_work_types(dbo):
    return dbo.query("SELECT * FROM lkworktype ORDER BY ID")

def get_yesno(dbo):
    return dbo.query("SELECT * FROM lksyesno ORDER BY Name")

def get_ynun(dbo):
    return dbo.query("SELECT * FROM lksynun ORDER BY Name")


