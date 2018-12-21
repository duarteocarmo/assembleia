import json
from bs4 import BeautifulSoup
import requests
import re
import os


def scrape_intervenções_url(url):

    try:
        # request the url from the website
        response = requests.get(url, timeout=5)

    except requests.Timeout as e:
        print("Timeout Error")
        print(str(e))
        return None

    # get the html content of the response
    html = response.content

    # parse it
    soup = BeautifulSoup(html, "html.parser")

    # find the text
    text = soup.find("div", attrs={"id": "pageTextRaw"})

    # start cleaning the text
    cleantext = text.get_text()

    ## remove page indicator
    cleantext = re.sub(r"Página (.*)\n", "", cleantext)
    # remove headers, clean text
    cleantext = re.sub(r"(\n)+[0-9]+ DE .* DE 20[0-9]+([0-9]+)", "", cleantext)
    cleantext = re.sub(r"(\n)+([0-9]+) . SÉRIE .* NÚMERO ([0-9]+)", "", cleantext)

    cleantext = re.sub("as([A-Z])", " \\1", cleantext)
    cleantext = re.sub("asSr", "Sr", cleantext)
    cleantext = re.sub("Sr. ª", "Sr.ª", cleantext)
    cleantext = re.sub(r"Sr\.ª([A-Z])", "Sr.ª \\1", cleantext)
    cleantext = re.sub(r"A Sr\.[^ª]", "A Sr.ª ", cleantext)

    cleantext = re.sub(
        r"((O Sr\.|A Sr\.ª|Vozes do) [^:.]*(:|\.) —)", "BREAKHERE!!!\\1", cleantext
    )
    cleantext = re.split("BREAKHERE!!!", cleantext)

    # keep only the debate
    cleantext = cleantext[1:]

    # prepare output
    sessiondict = dict()
    sessiondict["intervenções"] = dict()

    # define list of parties
    parties = ["PS", "PSD", "CDS-PP", "PCP", "Os Verdes", "PAN", "BE"]

    for id, intervention in enumerate(cleantext):

        # get information on the speaker
        splitintervention = re.split(r"(:|\.) —", intervention)
        infoorador = splitintervention[0]

        party = [item for item in parties if "(" + item + ")" in infoorador]
        assert len(party) <= 1
        party = "".join(party)

        orador = re.sub("(" + party + ")", "", infoorador)
        orador = orador.replace("()", "").strip()
        orador = re.sub("^(O Sr. |A Sr.ª)", "", orador)
        orador = orador.strip()

        # get the speech
        discurso = " ".join(splitintervention[2:])
        discurso = discurso.replace("\n", "").strip()
        discurso = re.sub(" +", " ", discurso)

        # put everything together
        sessiondict["intervenções"][id] = dict()
        sessiondict["intervenções"][id]["orador"] = orador
        sessiondict["intervenções"][id]["partido"] = party
        sessiondict["intervenções"][id]["discurso"] = discurso

    return sessiondict


# scrape information on legislative session
url = "http://debates.parlamento.pt/catalogo/r3/dar/01/13/01"


def get_links_legislative_session(url):
    try:
        # request the url from the website
        response = requests.get(url, timeout=5)

    except requests.Timeout as e:
        print("Timeout Error")
        print(str(e))
        # return None

    # get the html content of the response
    html = response.content

    # parse it
    soup = BeautifulSoup(html, "html.parser")

    # find the tables
    tables = soup.findAll("div", attrs={"class": "small-12 large-6 columns end"})

    # parse the tables and store in an inelegant list of lists!
    output = []
    for table in tables:
        rows = table.findAll("tr")
        for row in rows:
            thisrow = []
            cells = row.findAll("td")
            for cell in cells:
                if cell.find("a"):
                    link = cell.find("a")["href"]
                    thisrow.append(link)
                else:
                    link = ""
                thisrow.append(cell.get_text().strip())

            output.append(thisrow)

    output = [item for item in output if item]
    return output


# loop through all in a legislative session
série = 1
legislatura = 13
sessão = 3

url_sessão = (
    "http://debates.parlamento.pt/catalogo/r3/dar"
    + "/{0:0=2d}".format(série)
    + "/{0:0=2d}".format(legislatura)
    + "/{0:0=2d}".format(sessão)
)

pubs = get_links_legislative_session(url_sessão)

for pub in pubs:
    url_número = (
        "http://debates.parlamento.pt" + pub[0] + "?sft=true&org=PLC&plcdf=true"
    )
    número = re.sub(r"[^0-9]", "", pub[1])
    data = pub[2]
    num_páginas = pub[3]
    output = dict()
    output["série"] = série
    output["legislatura"] = legislatura
    output["sessão"] = sessão
    output["número"] = número
    output["data"] = data
    output["num_páginas"] = num_páginas

    print(número, url_número)
    output.update(scrape_intervenções_url(url_número))

    with open(
        os.path.join(
            "..",
            "data",
            "debates",
            str(série)
            + "_"
            + str(legislatura)
            + "_"
            + str(sessão)
            + "_"
            + número
            + ".json",
        ),
        "w",
        encoding="utf-8",
    ) as outfile:
        json.dump(output, outfile, ensure_ascii=False, indent=4, separators=(",", ": "))
