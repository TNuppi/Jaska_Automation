# GUI

Käyttöliittymä on toteutettu **NiceGUI**-kirjastolla. Käyttöliittymä toimii selaimessa ja on oletuksena käytettävissä osoitteessa  
[http://localhost:8080](http://localhost:8080).

GUI koostuu useista moduuleista, joista kukin vastaa omasta näkymästään ja toiminnallisuudestaan.

---

## app.py

Vastaa käyttöliittymän käynnistämisestä ja sovelluksen yleisestä rakenteesta.  
Moduuli huolehtii:
- alisivujen ohjauksesta ja navigoinnista
- pysyvistä käyttöliittymäelementeistä, kuten:
  - hätäseis-reset
  - ohjelman pysäytys

---

## config.py

Vastaa **Config**-sivun toiminnallisuudesta.  
Sivulla voidaan muokata ohjelman toimintaan vaikuttavia vakionopeuksia ja muita asetuksia ohjelman ollessa käynnissä.

---

## control.py

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

## dashboard.py

Vastaa **Dashboard**-sivusta, joka näyttää robotin tilatietoja reaaliajassa.  
Sivulla esitetään muun muassa:
- aktiivinen ohjaustila
- käynnissä oleva liike
- akkujen 1 ja 2 jännitteet
- kuljettu matka
- nopeus ja suuntima
- estehavainto (lähellä / edessä)

---

## errors.py

Vastaa **Errors**-sivusta.  
Sivulla näytetään järjestelmän havaitsemat virhe- ja varoitustilat.

---

## state.py

Vastaa **State**-sivusta.  
Tämä sivu ei ole tällä hetkellä käytössä.

