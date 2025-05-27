## 📌 Syfte

Syftet med projektet var att bygga ett program som automatiskt klipper ut sekvenser från YouTube-videor baserat på angivna fraser i transkriptionen. Tanken är att användare snabbt ska kunna extrahera relevanta delar ur videor utan att behöva titta igenom allt manuellt — till exempel för utbildning, research eller sociala medier.

---

## 🧪 Felsökning och Utvärdering

Under projektets gång har jag stött på flera utmaningar, särskilt kopplade till hantering av API\:er, timing i videoklippning samt frontend-backend-kommunikation. Jag har arbetat iterativt och testdrivet:

* Jag började med att sätta upp en **FastAPI-backend** som kunde ta emot en YouTube-länk, hämta transkriptionen och identifiera fraser.
* En tidig bugg uppstod när vissa videor saknade transkription — detta löste jag genom att införa felhantering som ger tydlig återkoppling till användaren.
* Jag testade och förbättrade klippningslogiken genom att köra manuella fall och justera marginalerna kring timestamps.
* Jag använde print-debugging, `curl`-tester och verktyg som Postman för att verifiera mina endpoints.
* I frontend-delen (Next.js) testade jag olika gränssnitt för att låta användaren ange fraser och visualisera resultatet på ett enkelt sätt.
* Jag utvärderade prestanda och förbättrade användarflödet genom att exempelvis lägga till laddningsindikatorer och göra felmeddelanden mer begripliga.

Jag har lärt mig mycket om hur man bygger ett fullstack-projekt från grunden, hur man bryter ner problem i mindre delar, samt hur viktigt det är att felsöka systematiskt.

---

## 🚀 Körning

Projektet finns på GitHub:

🔗 **[https://github.com/ditt-användarnamn/alfred](https://github.com/ditt-användarnamn/alfred)**

För att köra programmet:

1. Klona projektet från GitHub.
2. Starta backend (FastAPI) med `uvicorn main:app --reload`.
3. Starta frontend (Next.js) med `npm run dev`.
4. Gå till webbsidan och testa genom att ange en YouTube-länk + fras.
