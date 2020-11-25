# Protocole de transmission de messages textuels unicode simples (STUMTP)

Il s'agit d'une surcouche du protocole TCP
adaptée au module socket de Python qui
a pour but de permettre la transmission
de messages textuels unicode entre un
serveur et des clients

## Problèmatique

Comme les messages sont envoyés decoupés
en paquets, il faut déterminer quel est
nombre de paquets à recevoir exactement
pour recevoir le message en entier et
seulement le message.

## Format des messages

C'est pourquoi dans l'envoi, les messages
sont immédiatement suivis du caractère
"FIN DE TEXTE", EOT, caractère 3 de la
table ASCII ("\3" en Python), pour marquer la fin du
message. Ceci permet d'être sûr que le
message a été reçu en entier et qu'il n'y
a pas à attendre d'autres paquets

## Envoi des messages

Pour envoyer les messages, il faut
envoyer la concatenation du message même
avec le caractère EOT

## Réception des messages

Pour recevoir le message, il faut
revecoir des paquets et les décoder tant
que le dernier paquets reçu ne se termine
pas par le caractère EOT.

Il faut ensuite concaténer tous les
paquets reçus puis supprimer le dernier
caractère, qui est le caractère EOT.

Le message complet peut ensuite être
transmis aux couches supérieures de
l'application

