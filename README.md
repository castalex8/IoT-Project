# IoT-Project
Descrizione generale:

Smart locker (es. Amazon Locker per il ritiro dei prodotti acquistati) per libri. Sistema di locker distribuiti nelle università, nelle città. Gli utenti possono mettere a disposizione i libri di cui non hanno bisogno in modo da condividerli con altri.

Il singolo locker è composto da armadietti intelligenti (comandati da un microcontrollore) + bridge connesso alla rete con interfaccia per interagire. Comunicazione locker-cloud: -- database per registrare i libri nel sistema: disponibilità dei libri, posizione dei locker dove ritirare i libri di interesse -- analisi delle preferenze degli utenti in relazione ai libri con AI (es. sistemi di raccomandazione: consigliati Netflix, Amazon, ecc.) -- validazione utente

Azioni possibili: -- sistema deve riconoscere l'utente e i libri -- sistema deve accettare libri dall'utente -- utente può ritirare libri di suo interesse -- cloud memorizzerà disponibilità, stato dei libri e degli utenti -- client (bot telegram) per login, cercare libri, vedere la disponibilità

Serve Broker MQTT
