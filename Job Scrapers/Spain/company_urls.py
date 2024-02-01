from googlesearch import search

companies = [
    "System73", "Bo Growth", "SDG Group", "Plexus", "Amadeus",
    "Novatec Software Engineering España SL", "Ibermática", "Swiss RE",
    "EY", "Oxigent", "OpenNebula Systems", "Bunge", "Deloitte", "e-Frontiers",
    "N26", "INTEL", "ToBeIT", "Globant", "Nutanix", "Ubisoft", "We Bring",
    "ELCA Security", "Guidewire Software", "PANEL Sistemas Informáticos",
    "Idential", "TD SYNNEX", "Amaris Consulting", "Verne Group", "United ITs",
    "zooplus SE", "King", "Joboss", "Sabio Group", "Flywire", "Getronics",
    "OpenNebula Systems", "Sanofi", "Tupl", "SIX", "Devoteam", "NN Group",
    "Sirt", "SDG Group", "OpenNebula Systems", "Sanofi", "Criteo",
    "Prodware Group", "Vodafone", "Visio Tech Security", "amaris", "RS Group",
    "Plexus", "Open-Xchange GmbH", "Chakray", "Deloitte", "Swiss RE",
    "Michael Page España", "Sabio Group", "CIB labs", "Santander", "Ambientjobs",
    "AstraZeneca", "Iriusrisk", "Foot Analytifcs S.L.", "B. Braun Medical S.A.",
    "My Cloud Door", "KAPSCH", "Apple", "Deloitte", "Norconsulting", "iptiQ",
    "Swiss RE", "FIS Global", "Solera", "INTEL", "Michael Page España", "DGTLS GmbH",
    "Swiss RE", "Capgemini", "SDG Group", "GMV", "Carto", "Santander", "Devoteam",
    "Michael Page España", "Ericsson", "Civir", "Roche", "audiense", "Manning Global",
    "My Cloud Door", "Prodware Group", "Akkodis", "Deloitte", "Orange Quarter",
    "iTalenters", "Enverus", "Deloitte", "Page Personnel España",
    "Nigel Frank International Limited", "Amaris Consulting", "Geko Cloud",
    "Oxigent", "FCM Lab", "Proceq", "NPAW", "Tramuntana Selecció SL", "Quantion",
    "ELCA Security", "WATA Factory", "ELCA Informatique SA", "Alight", "Ambit BST",
    "Page Personnel España", "Somm Excellence Alliance", "Alovia Consulting",
    "Michael Page España", "Blackmouth Games",
    "Barcelona Supercomputing Center-Centro Nacional de...", "Novatec Software Engineering España SL",
    "Awin", "Rock Recruiters", "Page Personnel España", "Oxigent", "Roche", "MediaMarkt",
    "Zartis", "Roche", "Quanta", "Galeo Tech", "BANCO SANTANDER S.A.", "Start People",
    "Nearby Computing", "Thomas Morgan International", "FRG Technology Consulting",
    "Boehringer Ingelheim España, S.A.", "Accenture", "Galeo Tech", "Deloitte",
    "Tech Rise People", "FlexiDAO", "IKERLAN", "Alight", "Q-tech", "Idential", "Bitpanda",
    "IRB Barcelona", "DoiT International", "UST", "Remy Robotics", "Kapres Technology, S.L.",
    "MediaMarkt", "Geko Cloud", "Veeva Systems", "Unit4", "Alight", "Rastreator.com",
    "Tech Rise People", "Swiss RE", "Accenture", "Touchpoint Resource Ltd", "AG SOLUTION",
    "Kapres Technology, S.L.", "HUB Talent", "Accenture", "Swiss RE", "Bit2Me", "Client Server",
    "The Workshop", "The White Team", "KPMG Asesores Madrid", "Repsol", "Alovia Consulting",
    "Appfire", "Push Technology", "Avanade", "Robert Walters", "Amazon Spain Services, S.L.U.",
    "Sirt", "Bunge", "etalentum", "BIP - Business Integration Partners", "Sopra Steria",
    "e-Frontiers", "Ikigai Talent Goup", "Hasten group", "Novatec Software Engineering España SL",
    "MAPFRE", "Wunderman Thompson MAP", "Michael Page España", "AL-AGEDI Business Consultancy",
    "iTalenters", "Santander", "Check Point Software Technologies Ltd.", "Astrata Europe",
    "SELECCIÓN -IT", "Seidor", "Vodafone", "Roche", "Krimda Consulting", "Roche", "Veeva Systems",
    "Roche", "Roche", "Hamilton Barnes Associates", "SoftwareOne", "NTT DATA", "UST",
    "Novatec Software Engineering España SL", "EPAM Systems", "Lognext", "Iriusrisk", "Swiss RE",
    "Roche", "Boston Consulting Group", "EY", "BIP - Business Integration Partners",
    "CAPITOLE CONSULTING", "UVE Solutions", "Kapres Technology, S.L.", "BIP - Business Integration Partners",
    "Thomas Morgan International", "PPG Industries", "Accenture", "EY", "Schneider Electric", "amaris"
]

company_urls = {}

for company in companies:
    try:
        # Searching for the official website using Bing (you can adjust the search engine if needed)
        search_query = f"{company} official website"
        search_results = search(search_query, num=1, stop=1)

        # Extracting the first result URL
        company_url = next(search_results, None)
        company_urls[company] = company_url
    except Exception as e:
        print(f"Error searching for {company} URL: {e}")

# Print the results
for company, url in company_urls.items():
    print(f"{company}: {url}")
