# Tietokantasovellusharjoitustyö: Keskustelusovellus

## Sovelluksen tarkoitus

Harjoitustyössäni toteutan keskustelusovelluksen, jossa käyttäjät voivat kirjautua, lukea keskusteluja, kommentoida olemassa olevia keskusteluja ja luoda uusia aloituksia.

## Toteutetut ominaisuudet

* Käyttäjä voi rekisteröidä uuden tunnuksen ja siihen liittyvän salasanan
* Käyttäjä voi kirjautua sisään tunnuksella ja salasanalla
* Sisäänkirjautunut käyttäjä voi lukea olemassa olevia keskusteluja
* Sisäänkirjautunut käyttäjä voi kommentoida olemassa olevia keskusteluja
* Käyttäjä voi poistaa oman kommenttinsa
* Käyttäjä voi muokata omaa kommenttiaan

## Keskeiset ominaisuudet (suunnitelma)

Sovellus tulee sisältämään seuraavat toiminnot:
* Käyttäjä voi rekisteröidä uuden tunnuksen ja siihen liittyvän salasanan
* Käyttäjä voi kirjautua sisään tunnuksella ja salasanalla
* Sisäänkirjautunut käyttäjä voi lukea olemassa olevia keskusteluja
* Sisäänkirjautunut käyttäjä voi kommentoida olemassa olevia keskusteluja
* Sisäänkirjautunut käyttäjä voi aloittaa uuden keskustelun
* Käyttäjä voi poistaa oman kommenttinsa
* Käyttäjä voi muokata omaa kommenttiaan tai keskustelunaloitustaan

## Sivunäkymät (suunnitelma)

Sovelluksessa tulee olemaan seuraavat näkymät:
* Uloskirjautuneelle käyttäjälle näkyy kirjautumis-/rekisteröintisivu
* Sisäänkirjautuneelle käyttäjälle näkyy viimeisimpien keskustelunaloitusten lista
* Keskustelun otsikkoa klikkaamalla saa näkyviin kyseisen keskustelun sivun, jolla näkyvät myös aloitukseen tulleet kommentit
* Kirjautunut käyttäjä voi tarkastella omia tietojaan profiilisivulta


## Käyttöohje paikalliseen testaukseen

Kloonaa tämä repositorio omalle koneellesi ja siirry sen juurikansioon. Luo kansioon .env-tiedosto ja määritä sen sisältö seuraavanlaiseksi:

```
DATABASE_URL=<tietokannan-paikallinen-osoite>
SECRET_KEY=<salainen-avain>
```
Seuraavaksi aktivoi virtuaaliympäristö ja asenna sovelluksen riippuvuudet komennoilla
```
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install -r ./requirements.txt
```

Määritä vielä tietokannan skeema komennolla
```
$ psql < schema.sql
```
Nyt voit käynnistää sovelluksen komennolla
```
$ flask run
```
Kehitysaikainen käynnistys, jossa muutokset päivittyvät sivun päivittyessä:
```
$ flask run --debug
```
