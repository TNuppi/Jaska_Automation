# GUI

Käyttöliittymä on toteutettu **NiceGUI**-kirjastolla. Käyttöliittymä toimii selaimessa ja on oletuksena käytettävissä osoitteessa  
[http://localhost:8080](http://localhost:8080).

GUI koostuu useista moduuleista, joista kukin vastaa omasta näkymästään ja toiminnallisuudestaan.

---

## gui/__init__.py

Vastaa **GUI-paketin julkisesta rajapinnasta** ja toimii paketin sisäänrakennetun käyttöliittymäfunktion esittelijänä.  
Moduuli huolehtii:

- `start_gui`-funktion tuomisesta suoraan paketin tasolle.
- Paketin dokumentaation (docstring) esittelystä, joka kertoo, että kyseessä on **robotin graafinen käyttöliittymä**.
- Rajaa paketin julkisen rajapinnan määrittelemällä:

```python
__all__ = ["start_gui"]

```
## gui/app.py

Vastaa käyttöliittymän käynnistämisestä ja sovelluksen yleisestä rakenteesta.  
Moduuli huolehtii:
- alisivujen ohjauksesta ja navigoinnista
- pysyvistä käyttöliittymäelementeistä, kuten:
  - hätäseis-reset
  - ohjelman pysäytys

---

## gui/pages/config.py

Vastaa **Config**-sivun toiminnallisuudesta.  
Sivulla voidaan muokata ohjelman toimintaan vaikuttavia vakionopeuksia ja muita asetuksia ohjelman ollessa käynnissä.

---

## gui/pages/control.py

Vastaa **Control**-sivusta.  
Sivulla voidaan valita robotin ohjaustila:

- **Manuaaliohjaus**
  - eteen- ja taakseajo
  - käännökset vasemmalle ja oikealle

- **Automaattiohjaus**
  - tavoitematkan asetus
  - liikkeen käynnistys ja pysäytys
  - kuljettujen matkojen nollaus

---

## gui/pages/dashboard.py

Vastaa **Dashboard**-sivusta, joka näyttää robotin tilatietoja reaaliajassa.  
Sivulla esitetään muun muassa:
- aktiivinen ohjaustila
- käynnissä oleva liike
- akkujen 1 ja 2 jännitteet
- kuljettu matka
- nopeus ja suuntima
- estehavainto (lähellä / edessä)

---

## gui/pages/errors.py

Vastaa **Errors**-sivusta.  
Sivulla näytetään järjestelmän havaitsemat virhe- ja varoitustilat.

---

## gui/pages/state.py

Vastaa **State**-sivusta.  
Tämä sivu ei ole tällä hetkellä käytössä.

